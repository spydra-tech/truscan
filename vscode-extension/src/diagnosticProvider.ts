import * as vscode from 'vscode';
import * as path from 'path';
import { Scanner } from './scanner';
import { Finding } from './models';
import { logger } from './logger';

export class DiagnosticProvider {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private scanner: Scanner;
    private scanDelay: number = 500;
    private scanTimeouts: Map<string, NodeJS.Timeout> = new Map();

    constructor(
        diagnosticCollection: vscode.DiagnosticCollection,
        scanner: Scanner
    ) {
        this.diagnosticCollection = diagnosticCollection;
        this.scanner = scanner;

        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        this.scanDelay = config.get<number>('scanDelay', 500);
    }

    /**
     * Convert severity string to VS Code DiagnosticSeverity
     */
    private severityToDiagnosticSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity.toLowerCase()) {
            case 'critical':
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'high':
                return vscode.DiagnosticSeverity.Warning;
            case 'medium':
                return vscode.DiagnosticSeverity.Warning;
            case 'low':
            case 'info':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Warning;
        }
    }

    /**
     * Convert Finding to VS Code Diagnostic
     */
    private findingToDiagnostic(finding: Finding, document: vscode.TextDocument): vscode.Diagnostic {
        const location = finding.location;
        const startLine = Math.max(0, location.start_line - 1);
        const endLine = Math.max(0, location.end_line - 1);
        const startChar = Math.max(0, location.start_column - 1);
        const endChar = Math.max(0, location.end_column - 1);

        const range = new vscode.Range(
            startLine,
            startChar,
            endLine,
            endChar
        );

        const severity = this.severityToDiagnosticSeverity(finding.severity);
        const diagnostic = new vscode.Diagnostic(range, finding.message, severity);

        // Add code and source
        diagnostic.code = {
            value: finding.rule_id,
            target: vscode.Uri.parse(`https://cwe.mitre.org/data/definitions/${finding.cwe || '94'}.html`)
        };
        diagnostic.source = 'LLM Security Scanner';

        // Add related information
        if (finding.remediation) {
            diagnostic.relatedInformation = [
                new vscode.DiagnosticRelatedInformation(
                    new vscode.Location(document.uri, range),
                    `Remediation: ${finding.remediation}`
                )
            ];
        }

        // Add tags
        diagnostic.tags = [];
        if (finding.severity === 'critical' || finding.severity === 'error') {
            diagnostic.tags.push(vscode.DiagnosticTag.Unnecessary);
        }

        return diagnostic;
    }

    /**
     * Scan a single file
     */
    async scanFile(document: vscode.TextDocument): Promise<void> {
        logger.log(`scanFile called for: ${document.uri.fsPath}`);
        logger.log(`Language ID: ${document.languageId}`);
        
        // Skip non-Python files for now
        if (document.languageId !== 'python') {
            logger.log(`Skipping non-Python file: ${document.languageId}`);
            return;
        }

        // Clear existing timeout for this file
        const existingTimeout = this.scanTimeouts.get(document.uri.fsPath);
        if (existingTimeout) {
            logger.log('Clearing existing timeout for file');
            clearTimeout(existingTimeout);
        }

        // Debounce scanning
        logger.log(`Setting scan timeout (${this.scanDelay}ms)`);
        const timeout = setTimeout(async () => {
            this.scanTimeouts.delete(document.uri.fsPath);
            logger.log('Scan timeout triggered, starting scan...');

            try {
                logger.log(`Calling scanner.scanFileOrPath for: ${document.uri.fsPath}`);
                const response = await this.scanner.scanFileOrPath(document.uri.fsPath);
                logger.log(`Scanner response received. Success: ${response.success}`);

                if (!response.success || !response.result) {
                    logger.error(`Scan failed: ${response.error || 'Unknown error'}`);
                    vscode.window.showErrorMessage(
                        `LLM Security Scanner error: ${response.error || 'Unknown error'}`
                    );
                    return;
                }

                logger.log(`Scan successful. Findings count: ${response.result.findings.length}`);
                logger.log(`Scanned files: ${response.result.scanned_files.join(', ')}`);

                // Note: Database upload is now handled by a separate command
                // See "Scan and Upload to Database" command

                // Filter findings for this file
                const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
                const workspaceRoot = workspaceFolder?.uri.fsPath || '';
                const relativePath = path.relative(workspaceRoot, document.uri.fsPath);
                
                logger.log(`Workspace root: ${workspaceRoot}`);
                logger.log(`Relative path: ${relativePath}`);
                logger.log(`Total findings: ${response.result.findings.length}`);
                
                const fileFindings = response.result.findings.filter(
                    (f) => {
                        const matches = f.location.file_path === document.uri.fsPath ||
                           f.location.file_path === relativePath ||
                           f.location.file_path === document.uri.fsPath.replace(workspaceRoot + path.sep, '');
                        if (matches) {
                            logger.log(`Finding matches file: ${f.rule_id} at line ${f.location.start_line}`);
                        }
                        return matches;
                    }
                );

                logger.log(`Filtered findings for this file: ${fileFindings.length}`);

                // Convert to diagnostics
                const diagnostics = fileFindings.map((finding) =>
                    this.findingToDiagnostic(finding, document)
                );

                logger.log(`Created ${diagnostics.length} diagnostics`);

                // Update diagnostics
                this.diagnosticCollection.set(document.uri, diagnostics);
                logger.log('Diagnostics updated in Problems panel');

                // Show notification if findings
                if (diagnostics.length > 0) {
                    const criticalCount = diagnostics.filter(
                        (d) => d.severity === vscode.DiagnosticSeverity.Error
                    ).length;
                    if (criticalCount > 0) {
                        vscode.window.showWarningMessage(
                            `LLM Security Scanner found ${criticalCount} critical issue(s) in ${path.basename(document.uri.fsPath)}`
                        );
                    }
                }
            } catch (error: any) {
                logger.error('Exception in scanFile timeout handler', error);
                vscode.window.showErrorMessage(
                    `LLM Security Scanner error: ${error.message}`
                );
            }
        }, this.scanDelay);

        this.scanTimeouts.set(document.uri.fsPath, timeout);
    }

    /**
     * Scan entire workspace
     */
    async scanWorkspace(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showWarningMessage('No workspace folder found');
            return;
        }

        vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: 'Scanning workspace for LLM security vulnerabilities...',
                cancellable: false
            },
            async (progress) => {
                try {
                    progress.report({ increment: 0, message: 'Starting scan...' });

                    const response = await this.scanner.scanWorkspace();

                    if (!response.success || !response.result) {
                        vscode.window.showErrorMessage(
                            `LLM Security Scanner error: ${response.error || 'Unknown error'}`
                        );
                        return;
                    }

                    progress.report({ increment: 50, message: 'Processing results...' });

                    // Group findings by file
                    const findingsByFile = new Map<string, Finding[]>();
                    for (const finding of response.result.findings) {
                        const filePath = finding.location.file_path;
                        if (!findingsByFile.has(filePath)) {
                            findingsByFile.set(filePath, []);
                        }
                        findingsByFile.get(filePath)!.push(finding);
                    }

                    // Create diagnostics for each file
                    for (const [filePath, findings] of findingsByFile) {
                        const uri = vscode.Uri.file(
                            path.join(workspaceFolder.uri.fsPath, filePath)
                        );

                        try {
                            const document = await vscode.workspace.openTextDocument(uri);
                            const diagnostics = findings.map((finding) =>
                                this.findingToDiagnostic(finding, document)
                            );
                            this.diagnosticCollection.set(uri, diagnostics);
                        } catch (error) {
                            // File might not be open, skip
                        }
                    }

                    progress.report({ increment: 100, message: 'Complete' });

                    // Note: Database upload is now handled by a separate command
                    // See "Scan and Upload to Database" command

                    if (response.result) {
                        const totalFindings = response.result.findings.length;
                        const criticalCount = response.result.findings.filter(
                            (f) => f.severity === 'critical' || f.severity === 'error'
                        ).length;

                        if (totalFindings > 0) {
                            vscode.window.showInformationMessage(
                                `LLM Security Scanner: Found ${totalFindings} issue(s) (${criticalCount} critical)`
                            );
                        } else {
                            vscode.window.showInformationMessage(
                                'LLM Security Scanner: No issues found'
                            );
                        }
                    }
                } catch (error: any) {
                    vscode.window.showErrorMessage(
                        `LLM Security Scanner error: ${error.message}`
                    );
                }
            }
        );
    }
}

import * as vscode from 'vscode';
import * as path from 'path';
import { Scanner } from './scanner';
import { DiagnosticProvider } from './diagnosticProvider';
import { DependencyInstaller } from './dependencyInstaller';
import { getPythonPath } from './utils';
import { logger } from './logger';
import { ResultUploader } from './resultUploader';

let diagnosticCollection: vscode.DiagnosticCollection;
let scanner: Scanner;
let diagnosticProvider: DiagnosticProvider;

export async function activate(context: vscode.ExtensionContext) {
    logger.log('LLM Security Scanner extension is now active!');
    logger.show();

    // Get Python path from configuration (with variable resolution)
    const pythonPath = getPythonPath();

    // Install scanner and dependencies automatically so scanning works with no user action
    const installer = new DependencyInstaller();
    
    // If pythonPath points to the old .llm-scan-venv, switch to system Python
    let effectivePythonPath = pythonPath;
    if (pythonPath.includes('.llm-scan-venv')) {
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        effectivePythonPath = 'python3';
        await config.update('pythonPath', effectivePythonPath, vscode.ConfigurationTarget.Workspace);
    }
    
    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'LLM Security Scanner: Installing required dependencies...',
            cancellable: false
        },
        async (progress) => {
            try {
                progress.report({ increment: 0, message: 'Checking semgrep (required dependency)...' });
                
                const installResult = await installer.checkAndInstallDependencies(
                    effectivePythonPath,
                    (message) => progress.report({ message }),
                    true // Always install scanner so scanning works with no user action
                );

                if (installResult.success) {
                    if (installResult.installed.length > 0) {
                        vscode.window.showInformationMessage(
                            `LLM Security Scanner: ${installResult.message}`,
                            'OK'
                        );
                    }
                } else {
                    if (installResult.failed.includes('semgrep')) {
                        vscode.window.showErrorMessage(
                            `LLM Security Scanner: Setup failed. ${installResult.message}`,
                            'View Logs'
                        ).then((selection) => {
                            if (selection === 'View Logs') logger.show();
                        });
                    } else {
                        // Scanner not installed yet (e.g. no workspace); will set up on first scan
                        logger.log('Scanner will be set up automatically when you run a scan.');
                    }
                }
            } catch (error: any) {
                vscode.window.showErrorMessage(
                    `LLM Security Scanner: Error installing dependencies: ${error.message}`
                );
            }
        }
    );

    // Callback for diagnostic provider: ensure scanner is installed in the configured Python environment
    const ensureScannerReady = async (progress?: (message: string) => void): Promise<{ success: boolean; error?: string }> => {
        try {
            const installer = new DependencyInstaller();
            let pythonPath = getPythonPath();
            
            // If pythonPath points to the old .llm-scan-venv, switch to system Python
            if (pythonPath.includes('.llm-scan-venv')) {
                progress?.('Switching from extension venv to system Python...');
                const config = vscode.workspace.getConfiguration('llmSecurityScanner');
                pythonPath = 'python3'; // Use system Python
                await config.update('pythonPath', pythonPath, vscode.ConfigurationTarget.Workspace);
            }
            
            const result = await installer.checkAndInstallDependencies(pythonPath, progress, true);
            return { success: result.success, error: result.message };
        } catch (error: any) {
            logger.error(`ensureScannerReady error: ${error.message}`);
            return { success: false, error: error.message };
        }
    };

    // Initialize components
    diagnosticCollection = vscode.languages.createDiagnosticCollection('llm-security');
    scanner = new Scanner(context);
    diagnosticProvider = new DiagnosticProvider(diagnosticCollection, scanner, ensureScannerReady);

    context.subscriptions.push(diagnosticCollection);

    // Register commands
    const scanWorkspaceCommand = vscode.commands.registerCommand(
        'llmSecurityScanner.scanWorkspace',
        async () => {
            logger.log('Command: Scan Workspace triggered');
            try {
                await diagnosticProvider.scanWorkspace();
                logger.log('Scan workspace command completed');
            } catch (error: any) {
                logger.error('Error in scanWorkspace command', error);
                vscode.window.showErrorMessage(`Scan failed: ${error.message}`);
            }
        }
    );

    const scanFileCommand = vscode.commands.registerCommand(
        'llmSecurityScanner.scanFile',
        async () => {
            logger.log('Command: Scan Current File triggered');
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                logger.log(`Scanning file: ${editor.document.uri.fsPath}`);
                logger.log(`Language: ${editor.document.languageId}`);
                try {
                    await diagnosticProvider.scanFile(editor.document);
                    logger.log('Scan file command completed');
                } catch (error: any) {
                    logger.error('Error in scanFile command', error);
                    vscode.window.showErrorMessage(`Scan failed: ${error.message}`);
                }
            } else {
                logger.warn('No active editor found');
                vscode.window.showWarningMessage('No active editor');
            }
        }
    );

    const clearResultsCommand = vscode.commands.registerCommand(
        'llmSecurityScanner.clearResults',
        () => {
            diagnosticCollection.clear();
            vscode.window.showInformationMessage('LLM Security Scanner results cleared');
        }
    );

    const scanAndUploadCommand = vscode.commands.registerCommand(
        'llmSecurityScanner.scanAndUpload',
        async () => {
            logger.log('Command: Scan and Upload to Database triggered');
            const config = vscode.workspace.getConfiguration('llmSecurityScanner');
            const apiKey = config.get<string>('apiKey', '');
            const applicationId = config.get<string>('applicationId', '');
            const uploadEndpoint = config.get<string>('uploadEndpoint', '');

            // Check if database upload is configured
            if (!apiKey || !applicationId || !uploadEndpoint) {
                const missing = [];
                if (!apiKey) missing.push('apiKey');
                if (!applicationId) missing.push('applicationId');
                if (!uploadEndpoint) missing.push('uploadEndpoint');
                
                const message = `Database upload requires the following settings: ${missing.join(', ')}. Please configure them in VS Code settings.`;
                vscode.window.showWarningMessage(message, 'Open Settings').then(selection => {
                    if (selection === 'Open Settings') {
                        vscode.commands.executeCommand('workbench.action.openSettings', 'llmSecurityScanner');
                    }
                });
                logger.warn(message);
                return;
            }

            try {
                // Show progress
                await vscode.window.withProgress(
                    {
                        location: vscode.ProgressLocation.Notification,
                        title: 'LLM Security Scanner: Scanning and uploading...',
                        cancellable: false
                    },
                    async (progress) => {
                        progress.report({ increment: 0, message: 'Scanning workspace...' });
                        
                        // First, scan the workspace
                        await diagnosticProvider.scanWorkspace();
                        
                        progress.report({ increment: 50, message: 'Uploading results to database...' });
                        
                        // Get the scan result (we need to scan again or get cached result)
                        // For now, we'll scan again to get fresh results
                        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
                        if (!workspaceFolder) {
                            throw new Error('No workspace folder found');
                        }

                        const scanResponse = await scanner.scanFileOrPath(workspaceFolder.uri.fsPath);
                        
                        if (!scanResponse.success || !scanResponse.result) {
                            throw new Error(scanResponse.error || 'Scan failed');
                        }

                        // Upload results
                        const uploadResult = await ResultUploader.uploadResults(scanResponse.result);
                        
                        progress.report({ increment: 100, message: 'Complete' });

                        if (uploadResult.success) {
                            vscode.window.showInformationMessage(
                                `✓ ${uploadResult.message}`,
                                'OK'
                            );
                        } else {
                            vscode.window.showWarningMessage(
                                `⚠ ${uploadResult.message}`,
                                'View Logs',
                                'Open Settings'
                            ).then(selection => {
                                if (selection === 'View Logs') {
                                    logger.show();
                                } else if (selection === 'Open Settings') {
                                    vscode.commands.executeCommand('workbench.action.openSettings', 'llmSecurityScanner');
                                }
                            });
                        }
                    }
                );
            } catch (error: any) {
                logger.error('Error in scanAndUpload command', error);
                vscode.window.showErrorMessage(
                    `Scan and upload failed: ${error.message}`,
                    'View Logs'
                ).then(selection => {
                    if (selection === 'View Logs') {
                        logger.show();
                    }
                });
            }
        }
    );

    const generateEvalTestsCommand = vscode.commands.registerCommand(
        'llmSecurityScanner.generateEvalTests',
        async () => {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showWarningMessage('Open a workspace folder first.');
                return;
            }
            const config = vscode.workspace.getConfiguration('llmSecurityScanner');
            const aiProvider = config.get<string>('aiProvider', 'openai')?.trim() || '';
            const aiModel = config.get<string>('aiModel', 'gpt-4')?.trim() || '';
            if (!aiProvider || !aiModel) {
                vscode.window.showWarningMessage(
                    'Generate Eval Tests requires AI settings. Set aiProvider and aiModel in LLM Security Scanner settings (and aiApiKey or OPENAI_API_KEY / ANTHROPIC_API_KEY).',
                    'Open Settings'
                ).then(selection => {
                    if (selection === 'Open Settings') {
                        vscode.commands.executeCommand('workbench.action.openSettings', 'llmSecurityScanner');
                    }
                });
                return;
            }
            const defaultPath = path.join(workspaceFolder.uri.fsPath, 'eval_tests.json');

            const uri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file(defaultPath),
                saveLabel: 'Save Eval Tests',
                filters: { JSON: ['json'] }
            });
            if (!uri) {
                return;
            }
            const outputPath = uri.fsPath;

            try {
                await vscode.window.withProgress(
                    {
                        location: vscode.ProgressLocation.Notification,
                        title: 'LLM Security Scanner: Generating eval tests...',
                        cancellable: false
                    },
                    async (progress) => {
                        progress.report({ increment: 0, message: 'Extracting tools and calling AI...' });
                        const result = await scanner.generateEvalTests(workspaceFolder.uri.fsPath, outputPath);
                        progress.report({ increment: 100, message: 'Done' });
                        if (result.success && result.outputPath) {
                            vscode.window.showInformationMessage(
                                `Eval tests saved to ${path.basename(result.outputPath)}`,
                                'Open File'
                            ).then(selection => {
                                if (selection === 'Open File') {
                                    vscode.window.showTextDocument(vscode.Uri.file(result.outputPath!));
                                }
                            });
                        } else {
                            vscode.window.showErrorMessage(
                                result.error || 'Eval test generation failed',
                                'View Logs'
                            ).then(selection => {
                                if (selection === 'View Logs') {
                                    logger.show();
                                }
                            });
                        }
                    }
                );
            } catch (error: any) {
                logger.error('generateEvalTests error', error);
                vscode.window.showErrorMessage(`Generate eval tests failed: ${error.message}`);
            }
        }
    );

    const installDependenciesCommand = vscode.commands.registerCommand(
        'llmSecurityScanner.installDependencies',
        async () => {
            const pythonPath = getPythonPath();
            const installer = new DependencyInstaller();

            vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'LLM Security Scanner: Installing dependencies...',
                    cancellable: false
                },
                async (progress) => {
                    try {
                        progress.report({ increment: 0, message: 'Checking dependencies...' });
                        
                        const installResult = await installer.checkAndInstallDependencies(
                            pythonPath,
                            (message) => progress.report({ message }),
                            true // Always install trusys-llm-scan when manually triggered
                        );

                        if (installResult.success) {
                            if (installResult.installed.length > 0) {
                                vscode.window.showInformationMessage(
                                    `LLM Security Scanner: ${installResult.message}`,
                                    'OK'
                                );
                            } else {
                                vscode.window.showInformationMessage(
                                    'LLM Security Scanner: All dependencies are already installed',
                                    'OK'
                                );
                            }
                        } else {
                            vscode.window.showErrorMessage(
                                `LLM Security Scanner: Failed to install some dependencies. ${installResult.message}`,
                                'OK'
                            );
                        }
                    } catch (error: any) {
                        vscode.window.showErrorMessage(
                            `LLM Security Scanner: Error installing dependencies: ${error.message}`
                        );
                    }
                }
            );
        }
    );

    context.subscriptions.push(
        scanWorkspaceCommand,
        scanFileCommand,
        scanAndUploadCommand,
        clearResultsCommand,
        generateEvalTestsCommand,
        installDependenciesCommand
    );

    // Auto-scan on file save
    const onSaveDisposable = vscode.workspace.onDidSaveTextDocument(async (document) => {
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        if (config.get<boolean>('scanOnSave', true)) {
            await diagnosticProvider.scanFile(document);
        }
    });

    // Auto-scan on file open
    const onOpenDisposable = vscode.workspace.onDidOpenTextDocument(async (document) => {
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        if (config.get<boolean>('scanOnOpen', true)) {
            await diagnosticProvider.scanFile(document);
        }
    });

    context.subscriptions.push(onSaveDisposable, onOpenDisposable);

    // Initial scan of open files
    vscode.workspace.textDocuments.forEach(async (document) => {
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        if (config.get<boolean>('scanOnOpen', true)) {
            await diagnosticProvider.scanFile(document);
        }
    });

    // Auto-scan sample files if in development/extension workspace
    scanSampleFiles(context, diagnosticProvider);

    // Show status message
    vscode.window.showInformationMessage('LLM Security Scanner is active');
}

/**
 * Scan all sample files in the samples/ directory if it exists
 */
async function scanSampleFiles(
    context: vscode.ExtensionContext,
    diagnosticProvider: DiagnosticProvider
): Promise<void> {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        return;
    }

    const samplesPath = vscode.Uri.joinPath(workspaceFolder.uri, 'samples');
    
    try {
        // Check if samples directory exists
        const samplesDir = await vscode.workspace.fs.readDirectory(samplesPath);
        
        // Filter for Python files
        const pythonFiles = samplesDir
            .filter(([name, type]) => 
                type === vscode.FileType.File && 
                name.endsWith('.py') &&
                !name.startsWith('__')
            )
            .map(([name]) => vscode.Uri.joinPath(samplesPath, name));

        if (pythonFiles.length === 0) {
            logger.log('No sample Python files found in samples/ directory');
            return;
        }

        logger.log(`Found ${pythonFiles.length} sample files to scan`);
        
        // Wait a bit for dependencies to install if needed
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Scan all sample files
        vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: `Scanning ${pythonFiles.length} sample files...`,
                cancellable: false
            },
            async (progress) => {
                for (let i = 0; i < pythonFiles.length; i++) {
                    const file = pythonFiles[i];
                    progress.report({
                        increment: 100 / pythonFiles.length,
                        message: `Scanning ${path.basename(file.fsPath)}...`
                    });

                    try {
                        const document = await vscode.workspace.openTextDocument(file);
                        await diagnosticProvider.scanFile(document);
                        logger.log(`Scanned sample file: ${file.fsPath}`);
                    } catch (error: any) {
                        logger.error(`Error scanning sample file ${file.fsPath}`, error);
                    }
                }

                progress.report({ increment: 100, message: 'Complete' });
                logger.log(`Completed scanning ${pythonFiles.length} sample files`);
            }
        );
    } catch (error: any) {
        // samples/ directory doesn't exist or can't be read - that's okay
        logger.log('No samples/ directory found (this is normal for non-development workspaces)');
    }
}

export function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
}

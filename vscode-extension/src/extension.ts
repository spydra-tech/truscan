import * as vscode from 'vscode';
import * as path from 'path';
import { Scanner } from './scanner';
import { DiagnosticProvider } from './diagnosticProvider';
import { DependencyInstaller } from './dependencyInstaller';
import { getPythonPath } from './utils';
import { logger } from './logger';

let diagnosticCollection: vscode.DiagnosticCollection;
let scanner: Scanner;
let diagnosticProvider: DiagnosticProvider;

export async function activate(context: vscode.ExtensionContext) {
    logger.log('LLM Security Scanner extension is now active!');
    logger.show();

    // Get Python path from configuration (with variable resolution)
    const pythonPath = getPythonPath();
    const config = vscode.workspace.getConfiguration('llmSecurityScanner');
    const autoInstall = config.get<boolean>('autoInstallDependencies', true);

    // Check and install dependencies if enabled
    if (autoInstall) {
        const installer = new DependencyInstaller();
        
        // Check dependencies first (quick check)
        const checkResult = await installer.checkDependencies(pythonPath);
        
        if (!checkResult.allInstalled) {
            // Show progress notification and install
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
                            (message) => progress.report({ message })
                        );

                        if (installResult.success) {
                            // If virtual environment was created, update Python path setting
                            if (installResult.pythonPath && installResult.venvPath) {
                                const config = vscode.workspace.getConfiguration('llmSecurityScanner');
                                await config.update('pythonPath', installResult.pythonPath, vscode.ConfigurationTarget.Workspace);
                                
                                vscode.window.showInformationMessage(
                                    `LLM Security Scanner: ${installResult.message}`,
                                    'OK'
                                );
                            } else if (installResult.installed.length > 0) {
                                vscode.window.showInformationMessage(
                                    `LLM Security Scanner: ${installResult.message}`,
                                    'OK'
                                );
                            }
                        } else {
                            vscode.window.showErrorMessage(
                                `LLM Security Scanner: Failed to install some dependencies. ${installResult.message}`,
                                'View Details'
                            ).then(selection => {
                                if (selection === 'View Details') {
                                    vscode.window.showWarningMessage(
                                        `Failed to install: ${installResult.failed.join(', ')}\n\n` +
                                        `Please install manually:\n` +
                                        `${pythonPath} -m pip install semgrep\n` +
                                        `${pythonPath} -m pip install -e /path/to/code-scan2`,
                                        'OK'
                                    );
                                }
                            });
                        }
                    } catch (error: any) {
                        vscode.window.showErrorMessage(
                            `LLM Security Scanner: Error installing dependencies: ${error.message}`
                        );
                    }
                }
            );
        }
    }

    // Initialize components
    diagnosticCollection = vscode.languages.createDiagnosticCollection('llm-security');
    scanner = new Scanner(context);
    diagnosticProvider = new DiagnosticProvider(diagnosticCollection, scanner);

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
                            (message) => progress.report({ message })
                        );

                        if (installResult.success) {
                            // If virtual environment was created, update Python path setting
                            if (installResult.pythonPath && installResult.venvPath) {
                                const config = vscode.workspace.getConfiguration('llmSecurityScanner');
                                await config.update('pythonPath', installResult.pythonPath, vscode.ConfigurationTarget.Workspace);
                                
                                vscode.window.showInformationMessage(
                                    `LLM Security Scanner: ${installResult.message}`,
                                    'OK'
                                );
                            } else if (installResult.installed.length > 0) {
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

    context.subscriptions.push(scanWorkspaceCommand, scanFileCommand, clearResultsCommand, installDependenciesCommand);

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

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { resolvePathVariables } from './utils';

export interface InstallResult {
    success: boolean;
    message: string;
    installed: string[];
    failed: string[];
    venvPath?: string; // Path to created virtual environment
    pythonPath?: string; // Python path to use (may be venv Python)
}

export class DependencyInstaller {
    /**
     * Check if a Python package is installed
     */
    private async checkPackageInstalled(pythonPath: string, packageName: string): Promise<boolean> {
        return new Promise((resolve) => {
            // First try pip show
            const checkProcess = spawn(pythonPath, ['-m', 'pip', 'show', packageName], {
                env: { ...process.env },
                shell: false
            });

            const timeout = setTimeout(() => {
                checkProcess.kill();
                resolve(false);
            }, 5000);

            let stdout = '';
            checkProcess.stdout.on('data', (data: Buffer) => {
                stdout += data.toString();
            });

            checkProcess.on('close', (code: number | null) => {
                clearTimeout(timeout);
                if (code === 0 && stdout.includes('Name:')) {
                    resolve(true);
                    return;
                }

                // If pip show fails, try importing the module directly as fallback
                let moduleName = packageName;
                if (packageName === 'trusys-llm-scan') {
                    moduleName = 'llm_scan';
                } else if (packageName === 'semgrep') {
                    moduleName = 'semgrep';
                }

                const importProcess = spawn(pythonPath, ['-c', `import ${moduleName}; print("OK")`], {
                    env: { ...process.env },
                    shell: false
                });

                const importTimeout = setTimeout(() => {
                    importProcess.kill();
                    resolve(false);
                }, 5000);

                let importStderr = '';
                importProcess.stderr.on('data', (data: Buffer) => {
                    importStderr += data.toString();
                });

                importProcess.on('close', (importCode: number | null) => {
                    clearTimeout(importTimeout);
                    resolve(importCode === 0);
                });
            });
        });
    }

    /**
     * Check if error indicates externally-managed environment
     */
    private isExternallyManagedError(error: string): boolean {
        return error.includes('externally-managed-environment') || 
               error.includes('externally managed');
    }

    /**
     * Create a virtual environment
     */
    private async createVirtualEnvironment(
        pythonPath: string,
        venvPath: string
    ): Promise<{ success: boolean; error?: string; venvPythonPath?: string }> {
        return new Promise((resolve) => {
            const venvProcess = spawn(pythonPath, ['-m', 'venv', venvPath], {
                env: { ...process.env },
                shell: false
            });

            const timeout = setTimeout(() => {
                venvProcess.kill();
                resolve({
                    success: false,
                    error: 'Virtual environment creation timed out'
                });
            }, 30000);

            let stderr = '';
            venvProcess.stderr.on('data', (data: Buffer) => {
                stderr += data.toString();
            });

            venvProcess.on('close', (code: number | null) => {
                clearTimeout(timeout);
                if (code !== 0) {
                    resolve({
                        success: false,
                        error: stderr.substring(0, 500) || 'Failed to create virtual environment'
                    });
                } else {
                    // Determine venv Python path based on platform
                    const isWindows = process.platform === 'win32';
                    const venvPythonPath = isWindows
                        ? path.join(venvPath, 'Scripts', 'python.exe')
                        : path.join(venvPath, 'bin', 'python');
                    
                    resolve({
                        success: true,
                        venvPythonPath
                    });
                }
            });
        });
    }

    /**
     * Install a Python package using pip
     */
    private async installPackage(
        pythonPath: string,
        packageName: string,
        installPath?: string
    ): Promise<{ success: boolean; error?: string; externallyManaged?: boolean }> {
        return new Promise((resolve) => {
            const args = ['-m', 'pip', 'install'];
            
            if (installPath) {
                // Install from local path in editable mode
                args.push('-e', installPath);
            } else {
                // Install from PyPI
                args.push(packageName);
            }

            const installProcess = spawn(pythonPath, args, {
                env: { ...process.env },
                shell: false
            });

            const timeout = setTimeout(() => {
                installProcess.kill();
                resolve({
                    success: false,
                    error: 'Installation timed out after 60 seconds'
                });
            }, 60000); // 60 second timeout for installation

            let stderr = '';
            installProcess.stderr.on('data', (data: Buffer) => {
                stderr += data.toString();
            });

            installProcess.on('close', (code: number | null) => {
                clearTimeout(timeout);
                if (code !== 0) {
                    const externallyManaged = this.isExternallyManagedError(stderr);
                    resolve({
                        success: false,
                        error: stderr.substring(0, 500) || 'Installation failed',
                        externallyManaged
                    });
                } else {
                    resolve({ success: true });
                }
            });
        });
    }

    /**
     * Find the project root directory (where setup.py or pyproject.toml exists)
     */
    private findProjectRoot(): string | null {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return null;
        }

        let workspaceRoot = workspaceFolder.uri.fsPath;

        // Check if setup.py or pyproject.toml exists in workspace root
        const setupPy = path.join(workspaceRoot, 'setup.py');
        const pyprojectToml = path.join(workspaceRoot, 'pyproject.toml');
        
        if (fs.existsSync(setupPy) || fs.existsSync(pyprojectToml)) {
            return workspaceRoot;
        }

        // Check parent directory (in case workspace is in a subdirectory)
        const parentDir = path.dirname(workspaceRoot);
        const parentSetupPy = path.join(parentDir, 'setup.py');
        const parentPyprojectToml = path.join(parentDir, 'pyproject.toml');
        
        if (fs.existsSync(parentSetupPy) || fs.existsSync(parentPyprojectToml)) {
            return parentDir;
        }

        return null;
    }

    /**
     * Check and install all required dependencies
     * @param pythonPath - Path to Python interpreter
     * @param progress - Progress callback
     * @param installLlmScan - Whether to install trusys-llm-scan (optional). semgrep is always installed.
     */
    async checkAndInstallDependencies(
        pythonPath: string,
        progress?: (message: string) => void,
        installLlmScan: boolean = true
    ): Promise<InstallResult> {
        const result: InstallResult = {
            success: true,
            message: '',
            installed: [],
            failed: []
        };

        // Resolve path variables
        let effectivePythonPath = resolvePathVariables(pythonPath);
        
        // If path points to old .llm-scan-venv and it doesn't exist, switch to system Python
        if (effectivePythonPath.includes('.llm-scan-venv')) {
            if (!fs.existsSync(effectivePythonPath)) {
                progress?.('Old extension venv not found; using system Python...');
                effectivePythonPath = 'python3';
                const config = vscode.workspace.getConfiguration('llmSecurityScanner');
                await config.update('pythonPath', 'python3', vscode.ConfigurationTarget.Workspace);
            } else {
                // Venv exists but we don't want to use it - switch to system Python
                progress?.('Switching from extension venv to system Python...');
                effectivePythonPath = 'python3';
                const config = vscode.workspace.getConfiguration('llmSecurityScanner');
                await config.update('pythonPath', 'python3', vscode.ConfigurationTarget.Workspace);
            }
        }
        
        // Check if resolved path exists (for file paths, not command names like 'python3')
        if (effectivePythonPath.includes('/') || effectivePythonPath.includes('\\')) {
            if (!fs.existsSync(effectivePythonPath)) {
                result.success = false;
                result.message = `Python path "${effectivePythonPath}" (resolved from "${pythonPath}") does not exist.\n\n` +
                    `Please check your VS Code setting: llmSecurityScanner.pythonPath\n` +
                    `If using variables like \${workspaceFolder}, make sure you have a workspace folder open.`;
                result.failed.push('python');
                return result;
            }
        }
        
        progress?.('Checking Python dependencies...');

        // Always check and install semgrep (required dependency)
        const semgrepInstalled = await this.checkPackageInstalled(effectivePythonPath, 'semgrep');
        if (!semgrepInstalled) {
            progress?.('Installing semgrep (required dependency)...');
            const semgrepResult = await this.installPackage(effectivePythonPath, 'semgrep');
            
            if (semgrepResult.success) {
                result.installed.push('semgrep');
                progress?.('✓ semgrep installed successfully');
            } else {
                result.failed.push('semgrep');
                result.success = false;
                const errorDetail = semgrepResult.error ? `: ${semgrepResult.error.substring(0, 300)}` : '';
                result.message += `Failed to install semgrep (required dependency)${errorDetail}\n` +
                    `Please install manually: ${effectivePythonPath} -m pip install semgrep\n`;
            }
        } else {
            progress?.('✓ semgrep is already installed');
        }

        // Check and install scanner (required when installLlmScan is true)
        if (installLlmScan) {
            const llmScanInstalled = await this.checkPackageInstalled(effectivePythonPath, 'trusys-llm-scan');
            if (!llmScanInstalled) {
                progress?.('Installing LLM Security Scanner...');
                const projectRoot = this.findProjectRoot();
                let installAttempted = false;
                if (projectRoot) {
                    installAttempted = true;
                    const installResult = await this.installPackage(effectivePythonPath, 'trusys-llm-scan', projectRoot);
                    if (installResult.success) {
                        result.installed.push('trusys-llm-scan (from local source)');
                        progress?.('✓ Scanner installed from workspace');
                    } else {
                        result.failed.push('trusys-llm-scan');
                        const errorDetail = installResult.error ? `: ${installResult.error.substring(0, 300)}` : '';
                        result.message += `Scanner installation failed${errorDetail}\n` +
                            `Please install manually: ${effectivePythonPath} -m pip install -e ${projectRoot}\n`;
                    }
                } else {
                    installAttempted = true;
                    const installResult = await this.installPackage(effectivePythonPath, 'trusys-llm-scan');
                    if (installResult.success) {
                        result.installed.push('trusys-llm-scan (from PyPI)');
                        progress?.('✓ Scanner installed from PyPI');
                    } else {
                        result.failed.push('trusys-llm-scan');
                        const errorDetail = installResult.error ? `: ${installResult.error.substring(0, 300)}` : '';
                        result.message += `Scanner installation failed${errorDetail}\n` +
                            `Please install manually: ${effectivePythonPath} -m pip install trusys-llm-scan\n`;
                    }
                }
                // Verify installation succeeded
                if (installAttempted && !result.failed.includes('trusys-llm-scan')) {
                    const verifyInstalled = await this.checkPackageInstalled(effectivePythonPath, 'trusys-llm-scan');
                    if (!verifyInstalled) {
                        result.failed.push('trusys-llm-scan');
                        result.message += 'Scanner installation reported success but package not found after install.\n';
                    }
                }
            } else {
                progress?.('✓ Scanner is already installed');
            }
        }

        if (result.installed.length > 0) {
            result.message = `Ready. Installed: ${result.installed.join(', ')}`;
        } else if (result.failed.length === 0) {
            result.message = 'Scanner is ready';
        }
        
        result.success = !result.failed.includes('semgrep') && !result.failed.includes('trusys-llm-scan');
        return result;
    }

    /**
     * Quick check if all dependencies are installed (without installing)
     */
    async checkDependencies(pythonPath: string): Promise<{ allInstalled: boolean; missing: string[] }> {
        const missing: string[] = [];

        const semgrepInstalled = await this.checkPackageInstalled(pythonPath, 'semgrep');
        if (!semgrepInstalled) {
            missing.push('semgrep');
        }

        const llmScanInstalled = await this.checkPackageInstalled(pythonPath, 'trusys-llm-scan');
        if (!llmScanInstalled) {
            missing.push('trusys-llm-scan');
        }

        return {
            allInstalled: missing.length === 0,
            missing
        };
    }
}

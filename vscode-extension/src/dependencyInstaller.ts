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
                if (packageName === 'llm-scan') {
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
     * @param installLlmScan - Whether to install llm-scan (optional). semgrep is always installed.
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
        
        let venvCreated = false;

        progress?.('Checking Python dependencies...');

        // Always check and install semgrep (required dependency)
        const semgrepInstalled = await this.checkPackageInstalled(effectivePythonPath, 'semgrep');
        if (!semgrepInstalled) {
            progress?.('Installing semgrep (required dependency)...');
            const semgrepResult = await this.installPackage(effectivePythonPath, 'semgrep');
            
            if (semgrepResult.success) {
                result.installed.push('semgrep');
                progress?.('semgrep installed successfully');
            } else if (semgrepResult.externallyManaged) {
                // Externally managed environment - create venv
                progress?.('Detected externally-managed Python environment. Creating virtual environment...');
                
                const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
                if (!workspaceFolder) {
                    result.failed.push('semgrep');
                    result.success = false;
                    result.message += 'Cannot create virtual environment: No workspace folder found.\n';
                    return result;
                }

                const venvPath = path.join(workspaceFolder.uri.fsPath, '.llm-scan-venv');
                const venvResult = await this.createVirtualEnvironment(pythonPath, venvPath);
                
                if (venvResult.success && venvResult.venvPythonPath) {
                    effectivePythonPath = venvResult.venvPythonPath;
                    result.venvPath = venvPath;
                    result.pythonPath = venvResult.venvPythonPath;
                    venvCreated = true;
                    progress?.('Virtual environment created. Installing dependencies...');
                    
                    // Retry semgrep installation in venv (REQUIRED)
                    progress?.('Installing semgrep in virtual environment...');
                    const retryResult = await this.installPackage(effectivePythonPath, 'semgrep');
                    if (retryResult.success) {
                        result.installed.push('semgrep');
                        progress?.('✓ semgrep installed in virtual environment');
                    } else {
                        result.failed.push('semgrep');
                        result.success = false;
                        result.message += `Failed to install semgrep (required dependency) in virtual environment: ${retryResult.error}\n`;
                    }
                } else {
                    result.failed.push('semgrep');
                    result.success = false;
                    result.message += `Failed to create virtual environment: ${venvResult.error}\n`;
                    return result;
                }
            } else {
                result.failed.push('semgrep');
                result.success = false;
                result.message += `Failed to install semgrep (required dependency): ${semgrepResult.error}\n` +
                    `Please install manually: ${effectivePythonPath} -m pip install semgrep\n`;
            }
        } else {
            progress?.('✓ semgrep is already installed');
        }

        // Check llm_scan (optional - only if installLlmScan is true)
        // Note: semgrep is always installed above (required), llm-scan is optional
        if (installLlmScan) {
            const llmScanInstalled = await this.checkPackageInstalled(effectivePythonPath, 'llm-scan');
            if (!llmScanInstalled) {
                progress?.('Installing llm-scan (optional - can be installed manually if needed)...');
                
                // Try to find project root for local installation
                const projectRoot = this.findProjectRoot();
                
                if (projectRoot) {
                    // Install from local path
                    const installResult = await this.installPackage(effectivePythonPath, 'llm-scan', projectRoot);
                    if (installResult.success) {
                        result.installed.push('llm-scan (from local source)');
                        progress?.('✓ llm-scan installed from local source');
                    } else if (installResult.externallyManaged && !venvCreated) {
                        // Should not happen if we already created venv, but handle it
                        result.failed.push('llm-scan');
                        // Don't mark as failure - llm-scan is optional, semgrep is required
                        result.message += `Note: llm-scan installation failed (optional). You can install manually if needed.\n`;
                    } else {
                        result.failed.push('llm-scan');
                        // Don't mark as failure - llm-scan is optional
                        result.message += `Note: llm-scan installation failed (optional): ${installResult.error}\n`;
                    }
                } else {
                    // Try installing from PyPI (if published)
                    const installResult = await this.installPackage(effectivePythonPath, 'llm-scan');
                    if (installResult.success) {
                        result.installed.push('llm-scan (from PyPI)');
                        progress?.('✓ llm-scan installed from PyPI');
                    } else {
                        result.failed.push('llm-scan');
                        // Don't mark as failure - llm-scan is optional
                        result.message += `Note: llm-scan not found in PyPI (optional). Install manually if needed:\n` +
                            `  ${effectivePythonPath} -m pip install -e /path/to/code-scan2\n`;
                    }
                }
            } else {
                progress?.('✓ llm-scan is already installed');
            }
        } else {
            progress?.('Skipping llm-scan installation (autoInstallDependencies is disabled)');
        }

        if (venvCreated) {
            result.message = `Created virtual environment at ${result.venvPath}. `;
            if (result.installed.length > 0) {
                result.message += `Successfully installed: ${result.installed.join(', ')}. `;
            }
            result.message += `VS Code will use the virtual environment Python: ${result.pythonPath}`;
        } else if (result.installed.length > 0) {
            result.message = `Successfully installed: ${result.installed.join(', ')}`;
        } else if (result.failed.length === 0) {
            result.message = 'All dependencies are already installed (semgrep is ready)';
        }
        
        // If semgrep failed but llm-scan succeeded, still mark as partial success
        // semgrep is required, llm-scan is optional
        if (result.failed.includes('semgrep')) {
            result.success = false; // semgrep failure is critical
        } else if (result.failed.includes('llm-scan') && result.installed.includes('semgrep')) {
            // semgrep succeeded, llm-scan failed - this is okay
            result.success = true;
        }

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

        const llmScanInstalled = await this.checkPackageInstalled(pythonPath, 'llm-scan');
        if (!llmScanInstalled) {
            missing.push('llm-scan');
        }

        return {
            allInstalled: missing.length === 0,
            missing
        };
    }
}

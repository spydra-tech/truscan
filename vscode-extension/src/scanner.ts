import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { Finding, ScanResponse } from './models';
import { resolvePathVariables } from './utils';
import { logger } from './logger';

export class Scanner {
    private context: vscode.ExtensionContext;
    private scanCache: Map<string, { timestamp: number; findings: Finding[] }> = new Map();

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    /**
     * Find the project root directory (where setup.py or pyproject.toml exists)
     */
    private findProjectRoot(workspaceRoot?: string): string | null {
        if (!workspaceRoot) {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                return null;
            }
            workspaceRoot = workspaceFolder.uri.fsPath;
        }

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

        return workspaceRoot; // Fallback to workspace root
    }

    /**
     * Verify Python environment has llm_scan installed
     */
    async verifyPythonEnvironment(pythonPath: string, workspaceRoot?: string): Promise<{ valid: boolean; error?: string }> {
        // Resolve path variables
        const resolvedPath = resolvePathVariables(pythonPath);
        
        // Check if resolved path exists (for file paths, not command names like 'python3')
        if (resolvedPath.includes('/') || resolvedPath.includes('\\')) {
            if (!fs.existsSync(resolvedPath)) {
                return {
                    valid: false,
                    error: `Python path "${resolvedPath}" (resolved from "${pythonPath}") does not exist.\n\n` +
                        `Please check your VS Code setting: llmSecurityScanner.pythonPath\n` +
                        `If using variables like \${workspaceFolder}, make sure you have a workspace folder open.`
                };
            }
        }
        
        return new Promise((resolve) => {
            // First, verify Python is accessible with a quick version check
            const versionCheck = spawn(resolvedPath, ['--version'], {
                env: { ...process.env },
                shell: false
            });

            const versionTimeout = setTimeout(() => {
                versionCheck.kill();
                resolve({
                    valid: false,
                    error: `Python at "${resolvedPath}" (resolved from "${pythonPath}") is not accessible or timed out.\n\n` +
                        `Please check the Python path in VS Code settings (llmSecurityScanner.pythonPath).`
                });
            }, 10000); // 10 second timeout for version check

            let versionStderr = '';
            versionCheck.stderr.on('data', (data: Buffer) => {
                versionStderr += data.toString();
            });

            versionCheck.on('close', (versionCode: number | null) => {
                clearTimeout(versionTimeout);
                
                if (versionCode !== 0) {
                    resolve({
                        valid: false,
                        error: `Python at "${resolvedPath}" (resolved from "${pythonPath}") is not accessible. Error: ${versionStderr.substring(0, 200) || 'Python not found'}\n\n` +
                            `Please verify the Python path in VS Code settings (llmSecurityScanner.pythonPath)`
                    });
                    return;
                }

                // Python is accessible, now check for llm_scan
                const checkProcess = spawn(resolvedPath, ['-m', 'llm_scan.runner', '--help'], {
                    env: { ...process.env },
                    shell: false
                });

                const timeout = setTimeout(() => {
                    checkProcess.kill();
                    resolve({
                        valid: false,
                        error: `Python environment check timed out after 20 seconds. This may indicate:\n` +
                            `1. The llm_scan module is taking too long to import\n` +
                            `2. Network issues if downloading dependencies\n` +
                            `3. Python environment issues\n\n` +
                            `Try running manually: ${resolvedPath} -m llm_scan.runner --help`
                    });
                }, 20000); // Increased to 20 seconds

                let stderr = '';
                checkProcess.stderr.on('data', (data: Buffer) => {
                    stderr += data.toString();
                });

                checkProcess.on('close', (code: number | null) => {
                    clearTimeout(timeout);
                    if (code !== 0) {
                        if (stderr.includes('No module named') || stderr.includes('ModuleNotFoundError')) {
                            if (stderr.includes('llm_scan')) {
                                const projectRoot = this.findProjectRoot(workspaceRoot);
                                const installPath = projectRoot || '/path/to/code-scan2';
                                let fullMsg = `llm_scan package not found in Python environment at "${resolvedPath}".\n\n`;
                                fullMsg += `To install: ${pythonPath} -m pip install -e ${installPath}\n\nOr run **LLM Security: Install Dependencies** from the Command Palette (Ctrl+Shift+P / Cmd+Shift+P).`;
                                logger.log(fullMsg);
                                resolve({
                                    valid: false,
                                    error: `llm_scan package not found in Python at "${resolvedPath}". Run **LLM Security: Install Dependencies** from the Command Palette, or see Output for manual install.`
                                });
                            } else if (stderr.includes('semgrep')) {
                                resolve({
                                    valid: false,
                                    error: `semgrep package not found in Python environment at "${resolvedPath}".\n\n` +
                                        `Install it with:\n` +
                                        `  ${resolvedPath} -m pip install semgrep`
                                });
                            } else {
                                resolve({
                                    valid: false,
                                    error: `Python module error: ${stderr.substring(0, 200)}`
                                });
                            }
                        } else {
                            resolve({
                                valid: false,
                                error: `Python check failed: ${stderr.substring(0, 200)}`
                            });
                        }
                    } else {
                        resolve({ valid: true });
                    }
                });
            });
        });
    }

    /**
     * Scan a single file or directory
     */
    async scanFileOrPath(filePath: string): Promise<ScanResponse> {
        logger.log(`scanFileOrPath called with: ${filePath}`);
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        let pythonPathRaw = config.get<string>('pythonPath', 'python3');
        let pythonPath = resolvePathVariables(pythonPathRaw);
        
        // If path points to old .llm-scan-venv, switch to system Python and update setting
        if (pythonPath.includes('.llm-scan-venv')) {
            logger.log('Python path was .llm-scan-venv; switching to python3');
            await config.update('pythonPath', 'python3', vscode.ConfigurationTarget.Workspace);
            pythonPathRaw = 'python3';
            pythonPath = 'python3';
        }
        
        logger.log(`Python path (raw): ${pythonPathRaw}`);
        logger.log(`Python path (resolved): ${pythonPath}`);
        
        // Check if resolved path exists (for file paths, not command names like 'python3')
        if (pythonPath.includes('/') || pythonPath.includes('\\')) {
            if (!fs.existsSync(pythonPath)) {
                logger.error(`Python path does not exist: ${pythonPath}`);
                return {
                    success: false,
                    error: `Python path "${pythonPath}" (resolved from "${pythonPathRaw}") does not exist.\n\n` +
                        `Please check your VS Code setting: llmSecurityScanner.pythonPath\n` +
                        `If using variables like \${workspaceFolder}, make sure you have a workspace folder open.`
                };
            }
        }
        const rulesDir = config.get<string>('rulesDirectory', '');
        const includePatterns = config.get<string[]>('includePatterns', ['*.py']);
        const excludePatterns = config.get<string[]>('excludePatterns', [
            '**/__pycache__/**',
            '**/node_modules/**',
            '**/.venv/**',
            '**/venv/**'
        ]);
        const severityFilter = config.get<string[]>('severityFilter', ['critical', 'high', 'medium']);

        // Determine workspace root first (needed for environment check)
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(
            vscode.Uri.file(filePath)
        );
        if (!workspaceFolder) {
            return {
                success: false,
                error: 'No workspace folder found'
            };
        }

        const workspaceRoot = workspaceFolder.uri.fsPath;

        // Verify Python environment first (with workspace root for better error messages)
        logger.log('Verifying Python environment...');
        const envCheck = await this.verifyPythonEnvironment(pythonPath, workspaceRoot);
        if (!envCheck.valid) {
            logger.error(`Python environment validation failed: ${envCheck.error}`);
            return {
                success: false,
                error: envCheck.error || 'Python environment validation failed'
            };
        }
        logger.log('Python environment validated successfully');

        // Check cache
        try {
            const fileStat = fs.statSync(filePath);
            const cached = this.scanCache.get(filePath);
            if (cached && cached.timestamp >= fileStat.mtimeMs) {
                return {
                    success: true,
                    result: {
                        findings: cached.findings,
                        scanned_files: [filePath],
                        rules_loaded: [],
                        scan_duration_seconds: 0,
                        metadata: {}
                    }
                };
            }
        } catch (error) {
            // File doesn't exist or can't be accessed, continue with scan
        }
        // Determine the path to scan
        // If filePath is within workspace, use relative path; otherwise use absolute
        let scanPath: string;
        try {
            const relative = path.relative(workspaceRoot, filePath);
            logger.log(`Calculated relative path: ${relative}`);
            // If path is outside workspace or relative calculation failed, use absolute
            if (relative.startsWith('..') || path.isAbsolute(relative) || relative === '') {
                scanPath = filePath;
                logger.log(`Using absolute path: ${scanPath}`);
            } else {
                scanPath = relative;
                logger.log(`Using relative path: ${scanPath}`);
            }
        } catch (error) {
            // Fallback to absolute path
            logger.warn(`Error calculating relative path, using absolute: ${error}`);
            scanPath = filePath;
        }
        
        // Handle Windows paths
        if (process.platform === 'win32') {
            scanPath = scanPath.replace(/\\/g, '/');
        }

        // Ensure path is not empty
        if (!scanPath || scanPath.trim() === '') {
            logger.error('Scan path is empty!');
            return {
                success: false,
                error: 'Invalid scan path: path is empty'
            };
        }
        
        logger.log(`Final scan path: ${scanPath}`);

        // Run scanner using installed package
        return new Promise((resolve) => {
            // Determine rules directory
            let finalRulesDir = rulesDir;
            if (!finalRulesDir) {
                // Try workspace-relative path first
                const workspaceRulesPath = path.join(workspaceRoot, 'llm_scan', 'rules', 'python');
                logger.log(`Checking for workspace rules at: ${workspaceRulesPath}`);
                if (fs.existsSync(workspaceRulesPath)) {
                    finalRulesDir = workspaceRulesPath;
                    logger.log(`Using workspace rules directory: ${finalRulesDir}`);
                } else {
                    // Fall back to default (package will use its own rules)
                    finalRulesDir = '';
                    logger.log('No workspace rules found, using package default rules');
                }
            } else {
                logger.log(`Using configured rules directory: ${finalRulesDir}`);
            }

            // Use resolved path for spawning process
            const resolvedPythonPath = resolvePathVariables(pythonPath);
            
            const args = [
                '-m',
                'llm_scan.runner',
                scanPath,  // Path is a positional argument
                '--format',
                'json'
            ];
            
            // Add rules directory if specified
            if (finalRulesDir) {
                args.push('--rules', finalRulesDir);
            }

            // Add severity filters (each needs its own --severity flag)
            if (severityFilter.length > 0) {
                for (const severity of severityFilter) {
                    args.push('--severity', severity);
                }
            }

            // Add include patterns
            if (includePatterns.length > 0) {
                for (const pattern of includePatterns) {
                    args.push('--include', pattern);
                }
            }

            // Add exclude patterns
            if (excludePatterns.length > 0) {
                for (const pattern of excludePatterns) {
                    args.push('--exclude', pattern);
                }
            }

            logger.log(`Command: ${resolvedPythonPath} ${args.join(' ')}`);
            logger.log(`Working directory: ${workspaceRoot}`);
            logger.log(`Scan path: ${scanPath}`);
            logger.log(`Rules directory: ${finalRulesDir || 'default (package rules)'}`);
            logger.log(`Severity filter: ${severityFilter.join(', ') || 'none'}`);
            logger.log(`Include patterns: ${includePatterns.join(', ') || 'none'}`);
            logger.log(`Exclude patterns: ${excludePatterns.join(', ') || 'none'}`);
            
            const childProcess = spawn(resolvedPythonPath, args, {
                cwd: workspaceRoot,
                env: { ...process.env },
                shell: false
            });
            
            logger.log('Process spawned, waiting for output...');

            // Set timeout for the process (30 seconds)
            const timeout = setTimeout(() => {
                childProcess.kill();
                resolve({
                    success: false,
                    error: 'Scanner process timed out after 30 seconds'
                });
            }, 30000);

            let stdout = '';
            let stderr = '';

            childProcess.stdout.on('data', (data: Buffer) => {
                const chunk = data.toString();
                stdout += chunk;
                logger.log(`Stdout chunk (${chunk.length} chars): ${chunk.substring(0, 200)}`);
            });

            childProcess.stderr.on('data', (data: Buffer) => {
                const chunk = data.toString();
                stderr += chunk;
                // Only log non-debug stderr
                if (!chunk.includes('DEBUG') && !chunk.includes('INFO')) {
                    logger.warn(`Stderr chunk: ${chunk.substring(0, 200)}`);
                }
            });

            childProcess.on('close', (code: number | null) => {
                clearTimeout(timeout);
                logger.log(`Process closed with exit code: ${code}`);
                logger.log(`Stdout length: ${stdout.length} characters`);
                logger.log(`Stderr length: ${stderr.length} characters`);
                
                // Log stdout preview
                if (stdout.length > 0) {
                    logger.log(`Stdout preview (first 500 chars): ${stdout.substring(0, 500)}`);
                }
                
                // Log stderr preview (filter debug logs)
                const stderrFiltered = stderr.split('\n').filter(line => 
                    !line.includes('DEBUG') && !line.includes('INFO')
                ).join('\n');
                if (stderrFiltered.length > 0) {
                    logger.log(`Stderr preview (filtered, first 500 chars): ${stderrFiltered.substring(0, 500)}`);
                }
                
                // Try to parse JSON output first, regardless of exit code
                // Exit code 1 means "findings found", not necessarily an error
                let jsonParsed = false;
                try {
                    // Parse JSON output (may have leading text or debug logs)
                    const jsonStart = stdout.indexOf('{');
                    const jsonEnd = stdout.lastIndexOf('}') + 1;
                    logger.log(`JSON start index: ${jsonStart}, end index: ${jsonEnd}`);
                    if (jsonStart !== -1 && jsonEnd > 0) {
                        const jsonStr = stdout.substring(jsonStart, jsonEnd);
                        logger.log(`Extracted JSON string length: ${jsonStr.length}`);
                        logger.log(`JSON preview: ${jsonStr.substring(0, 1000)}`);
                        const result = JSON.parse(jsonStr);
                        jsonParsed = true;
                        
                        // Handle both formats: direct format and SARIF-like format with "runs" array
                        let scanData: any;
                        if (result.runs && Array.isArray(result.runs) && result.runs.length > 0) {
                            // SARIF-like format with runs array
                            scanData = result.runs[0];
                            logger.log('Detected SARIF-like format with runs array');
                        } else {
                            // Direct format
                            scanData = result;
                            logger.log('Detected direct format');
                        }
                        
                        logger.log(`JSON parsed successfully. Findings: ${scanData.findings?.length || 0}`);
                        logger.log(`Scanned files: ${JSON.stringify(scanData.scanned_files || [])}`);
                        logger.log(`Rules loaded: ${scanData.rules_loaded?.length || 0}`);
                        if (scanData.findings && scanData.findings.length > 0) {
                            logger.log(`First finding: ${JSON.stringify(scanData.findings[0], null, 2)}`);
                        }

                        // Convert to ScanResponse format
                        const response: ScanResponse = {
                            success: true,
                            result: {
                                findings: scanData.findings || [],
                                scanned_files: scanData.scanned_files || [scanPath],
                                rules_loaded: scanData.rules_loaded || [],
                                scan_duration_seconds: scanData.scan_duration_seconds || 0,
                                metadata: scanData.metadata || {}
                            }
                        };

                        // Update cache
                        if (response.result) {
                            this.scanCache.set(filePath, {
                                timestamp: Date.now(),
                                findings: response.result.findings
                            });
                            logger.log('Results cached');
                        }

                        logger.log('Scan completed successfully');
                        
                        // Note: Database upload is now handled by a separate command
                        // See "Scan and Upload to Database" command
                        
                        resolve(response);
                        return;
                    } else {
                        logger.warn('No JSON found in stdout');
                    }
                } catch (error: any) {
                    // JSON parsing failed, continue to error handling
                    logger.error('JSON parsing failed', error);
                    logger.log(`Stdout preview: ${stdout.substring(0, 500)}`);
                }

                // If we couldn't parse JSON, treat it as an error
                if (code !== 0 || !jsonParsed) {
                    // Check for specific error conditions
                    if (stderr.includes('No module named') || stderr.includes('ModuleNotFoundError')) {
                        let errorMsg = '';
                        if (stderr.includes('semgrep')) {
                            errorMsg = `semgrep package not found in Python environment at "${resolvedPythonPath}".\n\n` +
                                `Install it with:\n` +
                                `  ${resolvedPythonPath} -m pip install semgrep\n\n` +
                                `Note: Make sure you're installing in the same Python environment that VS Code is using.`;
                        } else if (stderr.includes('llm_scan')) {
                            // Try to find the project root for better error message
                            const projectRoot = this.findProjectRoot(workspaceRoot);
                            const installPath = projectRoot || '/path/to/code-scan2';
                            
                            let fullMsg = `llm_scan package not found at "${resolvedPythonPath}".\n\n`;
                            fullMsg += `To install: ${resolvedPythonPath} -m pip install -e ${installPath}\n\nOr run **LLM Security: Install Dependencies** from the Command Palette.`;
                            logger.log(fullMsg);
                            errorMsg = `llm_scan package not found in Python at "${resolvedPythonPath}". Run **LLM Security: Install Dependencies** from the Command Palette, or see Output for details.`;
                        } else {
                            errorMsg = `Python module not found. ${stderr.substring(0, 200)}`;
                        }
                        resolve({
                            success: false,
                            error: errorMsg
                        });
                        return;
                    }

                    // Generic error handling
                    let errorMsg = `Scanner process exited with code ${code}`;
                    if (!jsonParsed) {
                        errorMsg = 'No valid JSON output from scanner';
                        if (stdout.trim()) {
                            errorMsg += `. Output: ${stdout.substring(0, 200)}`;
                        }
                    }
                    
                    if (stderr && !stderr.includes('DEBUG') && !stderr.includes('INFO')) {
                        // Only show stderr if it's not just debug/info logs
                        const errorPreview = stderr.length > 500 ? stderr.substring(0, 500) + '...' : stderr;
                        errorMsg += `\n\nStderr: ${errorPreview}`;
                    }
                    
                    resolve({
                        success: false,
                        error: errorMsg
                    });
                    return;
                }
            });
        });
    }

    /**
     * Scan workspace
     */
    async scanWorkspace(): Promise<ScanResponse> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return {
                success: false,
                error: 'No workspace folder found'
            };
        }

        return this.scanFileOrPath(workspaceFolder.uri.fsPath);
    }

    /**
     * Clear scan cache
     */
    clearCache(): void {
        this.scanCache.clear();
    }

    /**
     * Generate evaluation test cases (extract tools, AI generates prompts, write JSON).
     * Supports FastMCP, LangChain, and LlamaIndex. Requires AI provider config (aiProvider, aiModel, aiApiKey or env).
     * @param frameworkOverride If set, overrides the eval framework setting for this run (mcp | langchain | llamaindex).
     */
    async generateEvalTests(workspaceRoot: string, outputPath: string, frameworkOverride?: 'mcp' | 'langchain' | 'llamaindex'): Promise<{ success: boolean; error?: string; outputPath?: string }> {
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        let pythonPathRaw = config.get<string>('pythonPath', 'python3');
        let pythonPath = resolvePathVariables(pythonPathRaw);
        if (pythonPath.includes('.llm-scan-venv')) {
            await config.update('pythonPath', 'python3', vscode.ConfigurationTarget.Workspace);
            pythonPathRaw = 'python3';
            pythonPath = 'python3';
        }
        const aiProvider = config.get<string>('aiProvider', 'openai');
        const aiModel = config.get<string>('aiModel', 'gpt-4');
        const aiApiKey = config.get<string>('aiApiKey', '');
        const evalMaxPrompts = config.get<number>('evalTestMaxPromptsPerTool', 3);
        const evalFramework = frameworkOverride ?? config.get<string>('evalFramework', 'mcp');

        if (!aiProvider || !aiModel) {
            return { success: false, error: 'Eval test generation requires AI settings. Set llmSecurityScanner.aiProvider and llmSecurityScanner.aiModel (and aiApiKey or OPENAI_API_KEY / ANTHROPIC_API_KEY).' };
        }

        if (pythonPath.includes('/') || pythonPath.includes('\\')) {
            if (!fs.existsSync(pythonPath)) {
                return { success: false, error: `Python path does not exist: ${pythonPath}. Check llmSecurityScanner.pythonPath.` };
            }
        }

        const envCheck = await this.verifyPythonEnvironment(pythonPath, workspaceRoot);
        if (!envCheck.valid) {
            return { success: false, error: envCheck.error || 'Python environment validation failed.' };
        }

        return new Promise((resolve) => {
            const args = [
                '-m',
                'llm_scan.runner',
                workspaceRoot,
                '--generate-eval-tests',
                '--eval-test-out',
                outputPath,
                '--ai-provider',
                aiProvider,
                '--ai-model',
                aiModel,
                '--eval-test-max-prompts',
                String(evalMaxPrompts),
                '--eval-framework',
                evalFramework === 'langchain' ? 'langchain' : evalFramework === 'llamaindex' ? 'llamaindex' : evalFramework === 'langgraph' ? 'langgraph' : 'mcp'
            ];
            if (aiApiKey && aiApiKey.trim()) {
                args.push('--ai-api-key', aiApiKey.trim());
            }

            logger.log(`Generate eval tests: ${pythonPath} ${args.join(' ')}`);
            const childProcess = spawn(pythonPath, args, {
                cwd: workspaceRoot,
                env: { ...process.env },
                shell: false
            });

            const timeout = setTimeout(() => {
                childProcess.kill();
                resolve({ success: false, error: 'Eval test generation timed out after 90 seconds.' });
            }, 90000);

            let stderr = '';
            childProcess.stderr.on('data', (data: Buffer) => {
                stderr += data.toString();
            });

            childProcess.on('close', (code: number | null) => {
                clearTimeout(timeout);
                if (code === 0 && fs.existsSync(outputPath)) {
                    resolve({ success: true, outputPath });
                    return;
                }
                const errPreview = stderr.length > 400 ? stderr.substring(0, 400) + '...' : stderr;
                if (stderr.includes('No module named') || stderr.includes('ModuleNotFoundError')) {
                    resolve({ success: false, error: `Scanner or dependencies missing. ${errPreview}` });
                    return;
                }
                if (stderr.includes('API') || stderr.includes('api_key') || stderr.includes('401') || stderr.includes('403')) {
                    resolve({ success: false, error: `AI API error. Check aiApiKey or OPENAI_API_KEY / ANTHROPIC_API_KEY. ${errPreview}` });
                    return;
                }
                resolve({ success: false, error: `Eval test generation failed (exit ${code}). ${errPreview || 'No output.'}` });
            });
        });
    }
}

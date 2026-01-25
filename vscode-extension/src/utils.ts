import * as vscode from 'vscode';
import * as path from 'path';

/**
 * Resolve VS Code variables in a path string
 * Supports: ${workspaceFolder}, ${workspaceRoot}, ${env:VAR_NAME}
 * 
 * Note: If the path is a bare command name (like "python3") without any path separators
 * or variables, it will be returned as-is (not resolved to a file path).
 */
export function resolvePathVariables(pathString: string): string {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    const workspaceRoot = workspaceFolder?.uri.fsPath || '';

    // Check if the path contains variables that need resolution
    const hasVariables = /\$\{workspaceFolder\}|\$\{workspaceRoot\}|\$\{env\:/.test(pathString);
    
    // Check if it's a bare command name (no slashes, no backslashes, no variables, not absolute)
    // Bare command names like "python3", "python", "python.exe" should not be resolved to file paths
    // They should be used as-is so the system can find them via PATH
    const isBareCommand = !pathString.includes('/') && 
                          !pathString.includes('\\') && 
                          !path.isAbsolute(pathString) &&
                          !hasVariables;

    // Early return for bare commands - don't resolve them to file paths
    if (isBareCommand) {
        return pathString;
    }

    // Replace VS Code variables
    let resolved = pathString
        .replace(/\$\{workspaceFolder\}/g, workspaceRoot)
        .replace(/\$\{workspaceRoot\}/g, workspaceRoot)
        .replace(/\$\{env\:([^}]+)\}/g, (match, envVar) => {
            return process.env[envVar] || match;
        });

    // Only resolve to absolute path if:
    // 1. It's not already absolute
    // 2. We have a workspace root
    // 3. It contains path separators or variables (indicating it's meant to be a file path)
    if (!path.isAbsolute(resolved) && workspaceRoot) {
        // Only join if it looks like a path (has separators or was a variable)
        if (resolved.includes('/') || resolved.includes('\\') || hasVariables) {
            resolved = path.join(workspaceRoot, resolved);
        }
    }

    return resolved;
}

/**
 * Get and resolve Python path from configuration
 */
export function getPythonPath(): string {
    const config = vscode.workspace.getConfiguration('llmSecurityScanner');
    const pythonPathRaw = config.get<string>('pythonPath', 'python3');
    return resolvePathVariables(pythonPathRaw);
}

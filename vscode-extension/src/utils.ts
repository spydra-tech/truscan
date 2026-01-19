import * as vscode from 'vscode';
import * as path from 'path';

/**
 * Resolve VS Code variables in a path string
 * Supports: ${workspaceFolder}, ${workspaceRoot}, ${env:VAR_NAME}
 */
export function resolvePathVariables(pathString: string): string {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    const workspaceRoot = workspaceFolder?.uri.fsPath || '';

    // Replace VS Code variables
    let resolved = pathString
        .replace(/\$\{workspaceFolder\}/g, workspaceRoot)
        .replace(/\$\{workspaceRoot\}/g, workspaceRoot)
        .replace(/\$\{env\:([^}]+)\}/g, (match, envVar) => {
            return process.env[envVar] || match;
        });

    // Resolve to absolute path if relative and we have a workspace
    if (!path.isAbsolute(resolved) && workspaceRoot) {
        resolved = path.join(workspaceRoot, resolved);
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

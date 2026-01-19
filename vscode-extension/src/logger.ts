import * as vscode from 'vscode';

class Logger {
    private outputChannel: vscode.OutputChannel;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('LLM Security Scanner');
    }

    log(message: string, ...args: any[]): void {
        const timestamp = new Date().toISOString();
        const formattedMessage = `[${timestamp}] ${message}`;
        this.outputChannel.appendLine(formattedMessage);
        if (args.length > 0) {
            this.outputChannel.appendLine(JSON.stringify(args, null, 2));
        }
        console.log(formattedMessage, ...args);
    }

    error(message: string, error?: any): void {
        const timestamp = new Date().toISOString();
        const formattedMessage = `[${timestamp}] ERROR: ${message}`;
        this.outputChannel.appendLine(formattedMessage);
        if (error) {
            this.outputChannel.appendLine(`Error details: ${error.message || error}`);
            if (error.stack) {
                this.outputChannel.appendLine(error.stack);
            }
        }
        console.error(formattedMessage, error);
    }

    warn(message: string, ...args: any[]): void {
        const timestamp = new Date().toISOString();
        const formattedMessage = `[${timestamp}] WARN: ${message}`;
        this.outputChannel.appendLine(formattedMessage);
        if (args.length > 0) {
            this.outputChannel.appendLine(JSON.stringify(args, null, 2));
        }
        console.warn(formattedMessage, ...args);
    }

    show(): void {
        this.outputChannel.show();
    }

    dispose(): void {
        this.outputChannel.dispose();
    }
}

export const logger = new Logger();

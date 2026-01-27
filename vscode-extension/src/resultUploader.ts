/**
 * Utility for uploading scan results to a REST API server.
 */

import * as vscode from 'vscode';
import { logger } from './logger';
import { ScanResult } from './models';

export class ResultUploader {
    /**
     * Upload scan results to the configured API endpoint.
     * Only uploads if both apiKey and applicationId are configured.
     * Handles errors gracefully and provides user-friendly messages.
     */
    static async uploadResults(result: ScanResult): Promise<{ success: boolean; message: string }> {
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        const apiKey = config.get<string>('apiKey', '');
        const applicationId = config.get<string>('applicationId', '');
        const uploadEndpoint = config.get<string>('uploadEndpoint', '');

        // Check if upload is configured
        if (!apiKey || !applicationId) {
            const message = 'Database upload requires apiKey and applicationId to be configured in settings.';
            logger.log(`Upload skipped: ${message}`);
            return { success: false, message };
        }

        if (!uploadEndpoint) {
            const message = 'Database upload requires uploadEndpoint to be configured in settings.';
            logger.warn(`Upload skipped: ${message}`);
            return { success: false, message };
        }

        try {
            logger.log(`Uploading ${result.findings.length} findings to ${uploadEndpoint}`);

            // Prepare payload
            const payload = {
                application_id: applicationId,
                findings: result.findings,
                scanned_files: result.scanned_files,
                rules_loaded: result.rules_loaded,
                scan_duration_seconds: result.scan_duration_seconds,
                metadata: result.metadata,
            };

            // Prepare headers
            const headers: Record<string, string> = {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`,
            };

            // Send POST request with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

            let response: Response;
            try {
                response = await fetch(uploadEndpoint, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(payload),
                    signal: controller.signal,
                });
                clearTimeout(timeoutId);
            } catch (fetchError: any) {
                clearTimeout(timeoutId);
                
                // Handle timeout
                if (fetchError.name === 'AbortError') {
                    const message = `Upload timed out after 30 seconds. Check if ${uploadEndpoint} is accessible.`;
                    logger.error(message);
                    return { success: false, message };
                }
                
                // Handle network errors
                if (fetchError.message.includes('fetch')) {
                    const message = `Network error: Unable to reach ${uploadEndpoint}. Check your internet connection and server status.`;
                    logger.error(message);
                    return { success: false, message };
                }
                
                throw fetchError;
            }

            if (response.ok) {
                const message = `Successfully uploaded ${result.findings.length} findings to database.`;
                logger.log(`✓ ${message}`);
                return { success: true, message };
            } else {
                // Handle different HTTP error codes gracefully
                let errorMessage = '';
                try {
                    const errorData: any = await response.json().catch(() => null);
                    if (errorData && typeof errorData === 'object' && 'message' in errorData) {
                        errorMessage = errorData.message;
                    } else {
                        errorMessage = await response.text().catch(() => 'Unknown error');
                    }
                } catch {
                    errorMessage = `HTTP ${response.status} ${response.statusText}`;
                }

                let userMessage = '';
                if (response.status === 401) {
                    userMessage = `Authentication failed. Please check your API key in settings.`;
                } else if (response.status === 404) {
                    userMessage = `Upload endpoint not found. Please verify the uploadEndpoint URL: ${uploadEndpoint}`;
                } else if (response.status === 500) {
                    userMessage = `Server error. The database server encountered an error. Please try again later.`;
                } else if (response.status >= 400 && response.status < 500) {
                    userMessage = `Request error (${response.status}): ${errorMessage}`;
                } else {
                    userMessage = `Upload failed with status ${response.status}: ${errorMessage}`;
                }

                logger.error(`Upload failed: ${userMessage}`);
                return { success: false, message: userMessage };
            }
        } catch (error: any) {
            // Handle unexpected errors
            let errorMessage = 'Unknown error occurred during upload.';
            
            if (error.message) {
                if (error.message.includes('ECONNREFUSED')) {
                    errorMessage = `Connection refused. The server at ${uploadEndpoint} is not running or not accessible.`;
                } else if (error.message.includes('ENOTFOUND')) {
                    errorMessage = `Server not found. Please check the uploadEndpoint URL: ${uploadEndpoint}`;
                } else if (error.message.includes('CERT')) {
                    errorMessage = `SSL certificate error. Please check your server's SSL configuration.`;
                } else {
                    errorMessage = `Error: ${error.message}`;
                }
            }
            
            logger.error(`Error uploading results: ${errorMessage}`, error);
            return { success: false, message: errorMessage };
        }
    }
}

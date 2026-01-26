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
     */
    static async uploadResults(result: ScanResult): Promise<boolean> {
        const config = vscode.workspace.getConfiguration('llmSecurityScanner');
        const apiKey = config.get<string>('apiKey', '');
        const applicationId = config.get<string>('applicationId', '');
        const uploadEndpoint = config.get<string>('uploadEndpoint', '');

        // Check if upload is configured
        if (!apiKey || !applicationId) {
            logger.log('Upload skipped: apiKey or applicationId not configured');
            return false;
        }

        if (!uploadEndpoint) {
            logger.warn('Upload skipped: uploadEndpoint not configured');
            return false;
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

            // Send POST request
            const response = await fetch(uploadEndpoint, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                logger.log(`✓ Successfully uploaded results (status: ${response.status})`);
                return true;
            } else {
                const errorText = await response.text().catch(() => 'Unknown error');
                logger.error(
                    `Upload failed with status ${response.status}: ${errorText}`
                );
                return false;
            }
        } catch (error: any) {
            logger.error(`Error uploading results: ${error.message}`, error);
            return false;
        }
    }
}

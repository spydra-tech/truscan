/**
 * Data models matching the scanner's JSON output format
 */

export interface Location {
    file_path: string;
    start_line: number;
    start_column: number;
    end_line: number;
    end_column: number;
    snippet?: string;
}

export interface DataflowStep {
    file_path: string;
    start_line: number;
    start_column: number;
    end_line: number;
    end_column: number;
    message: string;
}

export interface Finding {
    rule_id: string;
    message: string;
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info' | 'error' | 'warning';
    category: string;
    location: Location;
    cwe?: string;
    remediation?: string;
    dataflow_path?: DataflowStep[];
    metadata?: Record<string, any>;
}

export interface ScanResult {
    findings: Finding[];
    scanned_files: string[];
    rules_loaded: string[];
    scan_duration_seconds: number;
    metadata: Record<string, any>;
}

export interface ScanResponse {
    success: boolean;
    result?: ScanResult;
    error?: string;
}

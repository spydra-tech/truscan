// Get scan ID from URL
// URL format: /ui/scans/:scanId
const pathParts = window.location.pathname.split('/').filter(p => p);
let scanId = null;

// Find the scan ID in the path
// Expected path: ['ui', 'scans', 'scan-id-here']
if (pathParts.length >= 3 && pathParts[0] === 'ui' && pathParts[1] === 'scans') {
    scanId = pathParts[2];
} else {
    // Fallback: try to get from last part of path
    const lastPart = pathParts[pathParts.length - 1];
    if (lastPart && lastPart !== 'scan-details.html' && lastPart !== 'ui' && lastPart !== 'scans') {
        scanId = lastPart;
    }
}

console.log('Extracted scan ID from URL:', scanId, 'Path:', window.location.pathname);

// API Key Management
let apiKey = localStorage.getItem('llm_scanner_api_key') || '';

// API Helper
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (apiKey) {
        headers['Authorization'] = `Bearer ${apiKey}`;
    }

    try {
        console.log('Making API call to:', `/ui${endpoint}`);
        const response = await fetch(`/ui${endpoint}`, {
            ...options,
            headers,
        });

        console.log('Response status:', response.status);

        if (response.status === 401) {
            showError('Unauthorized. Please check your API key.');
            return null;
        }

        if (!response.ok) {
            const errorText = await response.text();
            let error;
            try {
                error = JSON.parse(errorText);
            } catch {
                error = { message: errorText || 'Request failed' };
            }
            console.error('API error response:', error);
            throw new Error(error.message || 'Request failed');
        }

        const data = await response.json();
        console.log('API response received');
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        showError(error.message || 'Failed to fetch data. Check console for details.');
        return null;
    }
}

// Show/Hide Loading and Error
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('scanDetails').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    document.getElementById('error').textContent = message;
    document.getElementById('error').style.display = 'block';
    document.getElementById('scanDetails').style.display = 'none';
    hideLoading();
}

// Load Scan Details
async function loadScanDetails() {
    if (!scanId) {
        showError('Scan ID not found in URL. Expected format: /ui/scans/:scanId');
        console.error('Pathname:', window.location.pathname);
        return;
    }

    if (!apiKey) {
        showError('Please set your API key in the dashboard first');
        return;
    }

    showLoading();

    console.log('Loading scan details for:', scanId);
    const data = await apiCall(`/api/scans/${encodeURIComponent(scanId)}`);
    if (!data) {
        console.error('Failed to load scan details');
        return;
    }
    
    console.log('Scan details loaded:', data);

    hideLoading();
    document.getElementById('scanDetails').style.display = 'block';

    const scan = data.scan;

    // Update scan summary
    document.getElementById('scanId').textContent = scan.scan_id;
    document.getElementById('scanStatus').innerHTML = `<span class="severity-badge severity-${scan.status}">${scan.status}</span>`;
    document.getElementById('scanDate').textContent = new Date(scan.created_at).toLocaleString();
    document.getElementById('scanDuration').textContent = scan.scan_duration_seconds ? `${parseFloat(scan.scan_duration_seconds).toFixed(2)}s` : 'N/A';
    document.getElementById('filesScanned').textContent = scan.scanned_files_count;
    document.getElementById('rulesLoaded').textContent = scan.rules_loaded_count;

    // Update severity breakdown
    document.getElementById('criticalCount').textContent = scan.critical_count;
    document.getElementById('highCount').textContent = scan.high_count;
    document.getElementById('mediumCount').textContent = scan.medium_count;
    document.getElementById('lowCount').textContent = scan.low_count;
    document.getElementById('infoCount').textContent = scan.info_count;

    // Store findings globally for filtering
    allFindings = scan.findings || [];

    // Load findings
    loadFindings(allFindings);

    // Setup filters
    const severityFilter = document.getElementById('severityFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (severityFilter) {
        severityFilter.addEventListener('change', () => filterFindings(allFindings));
    }
    if (searchInput) {
        searchInput.addEventListener('input', () => filterFindings(allFindings));
    }
}

// Load Findings Table
function loadFindings(findings, filteredFindings = null) {
    const tbody = document.getElementById('findingsTableBody');
    tbody.innerHTML = '';

    const findingsToShow = filteredFindings || findings;

    if (findingsToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #8b949e;">No findings found</td></tr>';
        return;
    }

    findingsToShow.forEach(finding => {
        const row = document.createElement('tr');
        const hasAi = finding.ai_analysis && Object.keys(finding.ai_analysis).length > 0;
        const aiBadge = hasAi 
            ? `<span class="ai-badge">AI: ${finding.ai_analysis.confidence ? (finding.ai_analysis.confidence * 100).toFixed(0) + '%' : 'Analyzed'}</span>`
            : '<span style="color: #8b949e;">-</span>';

        row.innerHTML = `
            <td><span class="severity-badge severity-${finding.severity}">${finding.severity}</span></td>
            <td><code>${finding.rule_id}</code></td>
            <td><span class="file-path">${finding.file_path}</span></td>
            <td>${finding.start_line}:${finding.start_column}</td>
            <td>${finding.message.substring(0, 100)}${finding.message.length > 100 ? '...' : ''}</td>
            <td>${aiBadge}</td>
            <td></td>
        `;
        
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn btn-secondary';
        viewBtn.style.cssText = 'padding: 4px 8px; font-size: 12px;';
        viewBtn.textContent = 'View';
        viewBtn.addEventListener('click', () => showFindingDetail(finding.id));
        row.querySelector('td:last-child').appendChild(viewBtn);
        
        tbody.appendChild(row);
    });
}

// Filter Findings
let allFindings = [];

function filterFindings(findings) {
    if (!findings) {
        console.warn('No findings provided to filter');
        return;
    }
    
    const severityFilterEl = document.getElementById('severityFilter');
    const searchInputEl = document.getElementById('searchInput');
    
    const severityFilter = severityFilterEl ? severityFilterEl.value : '';
    const searchTerm = searchInputEl ? searchInputEl.value.toLowerCase() : '';

    let filtered = findings;

    if (severityFilter) {
        filtered = filtered.filter(f => f.severity === severityFilter);
    }

    if (searchTerm) {
        filtered = filtered.filter(f => 
            (f.rule_id && f.rule_id.toLowerCase().includes(searchTerm)) ||
            (f.message && f.message.toLowerCase().includes(searchTerm)) ||
            (f.file_path && f.file_path.toLowerCase().includes(searchTerm))
        );
    }

    loadFindings(findings, filtered);
}

// Show Finding Detail Modal
async function showFindingDetail(findingId) {
    console.log('Showing finding detail for ID:', findingId);
    console.log('All findings:', allFindings);
    const finding = allFindings.find(f => f.id === findingId || f.id === parseInt(findingId));
    if (!finding) {
        console.error('Finding not found with ID:', findingId);
        alert('Finding details not found');
        return;
    }

    const modal = document.getElementById('findingModal');
    const details = document.getElementById('findingDetails');

    let aiAnalysisHtml = '';
    if (finding.ai_analysis) {
        const ai = finding.ai_analysis;
        aiAnalysisHtml = `
            <div class="ai-analysis-section">
                <h4>🤖 AI Analysis</h4>
                <div class="detail-row">
                    <div class="detail-label">Confidence:</div>
                    <div class="detail-value">
                        <span class="ai-confidence">${(ai.confidence * 100).toFixed(1)}%</span>
                    </div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Verdict:</div>
                    <div class="detail-value">${ai.is_false_positive ? 'False Positive' : 'True Positive'}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Reasoning:</div>
                    <div class="detail-value">${ai.reasoning || 'N/A'}</div>
                </div>
                ${ai.enhanced_remediation ? `
                <div class="detail-row">
                    <div class="detail-label">Enhanced Remediation:</div>
                    <div class="detail-value">${ai.enhanced_remediation}</div>
                </div>
                ` : ''}
                ${ai.suggested_severity ? `
                <div class="detail-row">
                    <div class="detail-label">Suggested Severity:</div>
                    <div class="detail-value"><span class="severity-badge severity-${ai.suggested_severity}">${ai.suggested_severity}</span></div>
                </div>
                ` : ''}
            </div>
        `;
    }

    details.innerHTML = `
        <h2>Finding Details</h2>
        <div class="finding-detail">
            <div class="detail-row">
                <div class="detail-label">Rule ID:</div>
                <div class="detail-value"><code>${finding.rule_id}</code></div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Severity:</div>
                <div class="detail-value"><span class="severity-badge severity-${finding.severity}">${finding.severity}</span></div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Category:</div>
                <div class="detail-value">${finding.category || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">File:</div>
                <div class="detail-value"><code class="file-path">${finding.file_path}</code></div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Location:</div>
                <div class="detail-value">Line ${finding.start_line}:${finding.start_column} - ${finding.end_line}:${finding.end_column}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Message:</div>
                <div class="detail-value">${finding.message}</div>
            </div>
            ${finding.snippet ? `
            <div class="detail-row">
                <div class="detail-label">Code Snippet:</div>
                <div class="detail-value">
                    <pre class="code-snippet">${escapeHtml(finding.snippet)}</pre>
                </div>
            </div>
            ` : ''}
            ${finding.cwe ? `
            <div class="detail-row">
                <div class="detail-label">CWE:</div>
                <div class="detail-value"><code>${finding.cwe}</code></div>
            </div>
            ` : ''}
            ${finding.remediation ? `
            <div class="detail-row">
                <div class="detail-label">Remediation:</div>
                <div class="detail-value">${finding.remediation}</div>
            </div>
            ` : ''}
            <div class="detail-row">
                <div class="detail-label">Source:</div>
                <div class="detail-value">${finding.source || 'semgrep'}</div>
            </div>
            ${finding.ai_filtered ? `
            <div class="detail-row">
                <div class="detail-label">AI Filtered:</div>
                <div class="detail-value"><span class="ai-badge ai-filtered">Yes</span></div>
            </div>
            ` : ''}
            ${aiAnalysisHtml}
        </div>
    `;

    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('findingModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Set up event listeners
window.addEventListener('DOMContentLoaded', () => {
    // Close modal button
    const closeModalBtn = document.getElementById('closeModalBtn');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    // Close modal when clicking outside
    const modal = document.getElementById('findingModal');
    if (modal) {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

    // Load scan details
    if (scanId) {
        loadScanDetails();
    } else {
        showError('Scan ID not found in URL');
    }
});

// API Key Management
let apiKey = localStorage.getItem('llm_scanner_api_key') || '';

function setApiKey() {
    const input = document.getElementById('apiKeyInput');
    apiKey = input.value.trim();
    if (apiKey) {
        localStorage.setItem('llm_scanner_api_key', apiKey);
        loadDashboard();
    } else {
        alert('Please enter an API key');
    }
}

// Load API key from storage on page load
window.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    const setApiKeyBtn = document.getElementById('setApiKeyBtn');
    if (setApiKeyBtn) {
        setApiKeyBtn.addEventListener('click', setApiKey);
    }

    // Allow Enter key to submit API key
    const apiKeyInput = document.getElementById('apiKeyInput');
    if (apiKeyInput) {
        apiKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                setApiKey();
            }
        });
    }

    // Load existing API key if available
    if (apiKeyInput && apiKey) {
        apiKeyInput.value = apiKey;
        // Don't auto-load, let user click the button or wait a moment
        setTimeout(() => {
            if (apiKey) {
                loadDashboard();
            } else {
                hideLoading();
                const errorEl = document.getElementById('error');
                if (errorEl) errorEl.style.display = 'none';
            }
        }, 100);
    } else {
        hideLoading();
        const errorEl = document.getElementById('error');
        if (errorEl) errorEl.style.display = 'none';
    }
});

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
        console.log('API response data:', data);
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        showError(error.message || 'Failed to fetch data. Check console for details.');
        return null;
    }
}

// Show/Hide Loading and Error
function showLoading() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const dashboard = document.getElementById('dashboard');
    const welcome = document.getElementById('welcome');
    
    if (loading) loading.style.display = 'block';
    if (error) error.style.display = 'none';
    if (dashboard) dashboard.style.display = 'none';
    if (welcome) welcome.style.display = 'none';
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
}

function showError(message) {
    const error = document.getElementById('error');
    const dashboard = document.getElementById('dashboard');
    const welcome = document.getElementById('welcome');
    
    if (error) {
        error.textContent = message;
        error.style.display = 'block';
    }
    if (dashboard) dashboard.style.display = 'none';
    if (welcome) welcome.style.display = 'none';
    hideLoading();
}

// Load Dashboard
async function loadDashboard() {
    if (!apiKey) {
        showError('Please enter an API key to view the dashboard');
        return;
    }

    showLoading();

    try {
        const data = await apiCall('/api/dashboard');
        if (!data) {
            console.error('Failed to load dashboard data');
            return;
        }

        console.log('Dashboard data loaded:', data);

        hideLoading();
        const dashboard = document.getElementById('dashboard');
        const welcome = document.getElementById('welcome');
        if (dashboard) dashboard.style.display = 'block';
        if (welcome) welcome.style.display = 'none';

        // Update statistics
        const stats = data.statistics || {};
        document.getElementById('totalScans').textContent = stats.total_scans || 0;
        document.getElementById('totalCritical').textContent = stats.total_critical || 0;
        document.getElementById('totalHigh').textContent = stats.total_high || 0;
        document.getElementById('totalMedium').textContent = stats.total_medium || 0;
        document.getElementById('totalFindings').textContent = stats.total_findings || 0;
        document.getElementById('aiAnalyzed').textContent = (data.ai_statistics && data.ai_statistics.findings_with_ai) || 0;

        // Load recent scans
        loadRecentScans(data.recent_scans || []);

        // Load all scans
        loadAllScans();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard: ' + error.message);
    }
}

// Load Recent Scans
function loadRecentScans(scans) {
    const tbody = document.getElementById('scansTableBody');
    if (!tbody) {
        console.error('scansTableBody not found');
        return;
    }
    
    tbody.innerHTML = '';

    if (!scans || scans.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #8b949e;">No scans found</td></tr>';
        return;
    }

    scans.forEach(scan => {
        const row = document.createElement('tr');
        const date = new Date(scan.created_at).toLocaleString();
        const duration = scan.scan_duration_seconds ? `${parseFloat(scan.scan_duration_seconds).toFixed(2)}s` : 'N/A';

        const viewLink = document.createElement('a');
        viewLink.href = `/ui/scans/${scan.scan_id}`;
        viewLink.className = 'btn btn-secondary';
        viewLink.style.cssText = 'padding: 4px 8px; font-size: 12px;';
        viewLink.textContent = 'View';

        row.innerHTML = `
            <td><code class="file-path">${scan.scan_id.substring(0, 8)}...</code></td>
            <td>${date}</td>
            <td><span class="severity-badge severity-${scan.status}">${scan.status}</span></td>
            <td>${scan.findings_count}</td>
            <td><span class="severity-badge severity-critical">${scan.critical_count}</span></td>
            <td><span class="severity-badge severity-high">${scan.high_count}</span></td>
            <td>${duration}</td>
            <td></td>
        `;
        row.querySelector('td:last-child').appendChild(viewLink);
        tbody.appendChild(row);
    });
}

// Load All Scans with Pagination
let currentPage = 1;
const pageSize = 20;

async function loadAllScans(page = 1) {
    currentPage = page;
    const data = await apiCall(`/api/scans?page=${page}&limit=${pageSize}`);
    if (!data) {
        console.error('Failed to load scans');
        return;
    }

    const container = document.getElementById('allScansContainer');
    container.innerHTML = '';

    if (!data.scans || data.scans.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #8b949e;">No scans found</p>';
        return;
    }

    // Create table
    const table = document.createElement('table');
    table.className = 'data-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Scan ID</th>
                <th>Date</th>
                <th>Status</th>
                <th>Findings</th>
                <th>Critical</th>
                <th>High</th>
                <th>Medium</th>
                <th>Duration</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

    const tbody = table.querySelector('tbody');
    data.scans.forEach(scan => {
        const row = document.createElement('tr');
        const date = new Date(scan.created_at).toLocaleString();
        const duration = scan.scan_duration_seconds ? `${parseFloat(scan.scan_duration_seconds).toFixed(2)}s` : 'N/A';

        const viewLink = document.createElement('a');
        viewLink.href = `/ui/scans/${scan.scan_id}`;
        viewLink.className = 'btn btn-secondary';
        viewLink.style.cssText = 'padding: 4px 8px; font-size: 12px;';
        viewLink.textContent = 'View Details';

        row.innerHTML = `
            <td><code class="file-path">${scan.scan_id.substring(0, 12)}...</code></td>
            <td>${date}</td>
            <td><span class="severity-badge severity-${scan.status}">${scan.status}</span></td>
            <td>${scan.findings_count}</td>
            <td><span class="severity-badge severity-critical">${scan.critical_count}</span></td>
            <td><span class="severity-badge severity-high">${scan.high_count}</span></td>
            <td><span class="severity-badge severity-medium">${scan.medium_count}</span></td>
            <td>${duration}</td>
            <td></td>
        `;
        row.querySelector('td:last-child').appendChild(viewLink);
        tbody.appendChild(row);
    });

    container.appendChild(table);

    // Pagination
    renderPagination(data.pagination);
}

function renderPagination(pagination) {
    const paginationDiv = document.getElementById('pagination');
    paginationDiv.innerHTML = '';

    if (pagination.total_pages <= 1) return;

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '← Previous';
    prevBtn.disabled = pagination.page === 1;
    prevBtn.onclick = () => loadAllScans(pagination.page - 1);
    paginationDiv.appendChild(prevBtn);

    // Page numbers
    for (let i = 1; i <= pagination.total_pages; i++) {
        if (i === 1 || i === pagination.total_pages || (i >= pagination.page - 2 && i <= pagination.page + 2)) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = i === pagination.page ? 'active' : '';
            pageBtn.onclick = () => loadAllScans(i);
            paginationDiv.appendChild(pageBtn);
        } else if (i === pagination.page - 3 || i === pagination.page + 3) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.style.padding = '8px';
            paginationDiv.appendChild(ellipsis);
        }
    }

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next →';
    nextBtn.disabled = pagination.page === pagination.total_pages;
    nextBtn.onclick = () => loadAllScans(pagination.page + 1);
    paginationDiv.appendChild(nextBtn);
}

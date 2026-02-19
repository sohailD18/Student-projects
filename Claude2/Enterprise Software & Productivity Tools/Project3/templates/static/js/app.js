// Intelligent Document Classification & Retrieval System - Frontend JavaScript

// API Base URL
const API_BASE = '/api';

// Global state
let currentDocument = null;
let currentPage = 1;
let charts = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    loadDashboard();
    loadCategories();
    setupQuickSearch();
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    const pageTitle = document.getElementById('page-title');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;

            // Update active nav
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Show page
            pages.forEach(p => p.classList.remove('active'));
            document.getElementById(`${page}-page`).classList.add('active');

            // Update title
            pageTitle.textContent = link.textContent.trim();

            // Load page data
            loadPageData(page);
        });
    });
}

function loadPageData(page) {
    switch(page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'documents':
            loadDocuments();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'reports':
            loadReports();
            break;
    }
}

// API Helper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        throw error;
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const data = await apiCall('/dashboard/');

        // Update stats
        document.getElementById('total-docs').textContent = data.total_documents;
        document.getElementById('total-searches').textContent = data.total_searches;
        document.getElementById('total-categories').textContent = data.total_categories;
        document.getElementById('recent-uploads').textContent = data.recent_uploads.length;

        // Category chart
        createCategoryChart(data.documents_by_category);

        // Type chart
        createTypeChart(data.documents_by_type);

        // Recent uploads
        renderDocumentList('recent-uploads-list', data.recent_uploads);

        // Top viewed
        renderDocumentList('top-viewed-list', data.top_viewed);

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');

    if (charts.category) {
        charts.category.destroy();
    }

    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.category_name || 'Uncategorized'),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => d.category_color || '#64748b'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createTypeChart(data) {
    const ctx = document.getElementById('typeChart').getContext('2d');

    if (charts.type) {
        charts.type.destroy();
    }

    const typeColors = {
        'pdf': '#ef4444',
        'docx': '#3b82f6',
        'txt': '#10b981'
    };

    charts.type = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.file_type.toUpperCase()),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => typeColors[d.file_type] || '#64748b'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Documents
async function loadDocuments(page = 1) {
    currentPage = page;

    const categoryFilter = document.getElementById('filter-category').value;
    const typeFilter = document.getElementById('filter-type').value;
    const sortBy = document.getElementById('sort-by').value;

    let url = `/documents/?page=${page}&ordering=${sortBy}`;
    if (categoryFilter) url += `&category=${categoryFilter}`;
    if (typeFilter) url += `&file_type=${typeFilter}`;

    try {
        const data = await apiCall(url);

        renderDocuments(data.results);
        renderPagination(data.count, data.next, data.previous);

    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

function renderDocuments(documents) {
    const container = document.getElementById('documents-list');

    if (!documents || documents.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📄</div>
                <div class="empty-state-text">No documents found</div>
                <small>Upload your first document to get started</small>
            </div>
        `;
        return;
    }

    container.innerHTML = documents.map(doc => createDocumentCard(doc)).join('');
}

function createDocumentCard(doc) {
    const typeIcons = {
        'pdf': '📕',
        'docx': '📘',
        'txt': '📝'
    };

    const categoryBadge = doc.category_name
        ? `<span class="category-badge" style="background-color: ${doc.category_color}">${doc.category_name}</span>`
        : '';

    return `
        <div class="document-card" onclick="showDocumentDetail(${doc.id})">
            <div class="document-card-header">
                <div class="document-card-icon">${typeIcons[doc.file_type] || '📄'}</div>
                <div class="document-card-content">
                    <div class="document-card-title" title="${doc.title}">${doc.title}</div>
                    <div class="document-card-meta">
                        ${doc.file_size_formatted} • ${formatDate(doc.upload_date)}
                    </div>
                </div>
            </div>
            ${categoryBadge}
            <div class="document-card-stats">
                <span>👁 ${doc.view_count} views</span>
                ${doc.confidence_score ? `<span>🎯 ${Math.round(doc.confidence_score * 100)}% confidence</span>` : ''}
            </div>
        </div>
    `;
}

function renderDocumentList(containerId, documents) {
    const container = document.getElementById(containerId);

    if (!documents || documents.length === 0) {
        container.innerHTML = '<small style="color: var(--text-secondary);">No documents yet</small>';
        return;
    }

    container.innerHTML = documents.map(doc => `
        <div class="document-item" onclick="showDocumentDetail(${doc.id})">
            <div class="document-type-icon">
                ${doc.file_type === 'pdf' ? '📕' : doc.file_type === 'docx' ? '📘' : '📝'}
            </div>
            <div class="document-info">
                <div class="document-title">${doc.title}</div>
                <div class="document-meta">${formatDate(doc.upload_date)} • ${doc.view_count} views</div>
            </div>
        </div>
    `).join('');
}

function renderPagination(count, next, previous) {
    const container = document.getElementById('documents-pagination');
    const pageSize = 20;
    const totalPages = Math.ceil(count / pageSize);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = `
        <button ${!previous ? 'disabled' : ''} onclick="loadDocuments(${currentPage - 1})">Previous</button>
    `;

    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadDocuments(${i})">${i}</button>`;
    }

    html += `
        <button ${!next ? 'disabled' : ''} onclick="loadDocuments(${currentPage + 1})">Next</button>
    `;

    container.innerHTML = html;
}

// Search
async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    const categoryFilter = document.getElementById('search-category').value;

    if (!query) {
        showToast('Please enter a search query', 'error');
        return;
    }

    let url = `/search/?query=${encodeURIComponent(query)}&limit=50`;
    if (categoryFilter) url += `&category=${categoryFilter}`;

    try {
        const data = await apiCall(url);
        renderSearchResults(data);
    } catch (error) {
        console.error('Error searching:', error);
    }
}

function renderSearchResults(data) {
    const container = document.getElementById('search-results');

    if (!data.results || data.results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">No results found</div>
                <small>Try different keywords or filters</small>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div style="margin-bottom: 1rem; color: var(--text-secondary);">
            Found ${data.results_count} results for "${data.query}"
        </div>
        ${data.results.map(doc => `
            <div class="search-result-item" onclick="showDocumentDetail(${doc.id})">
                <div style="display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 2rem;">
                        ${doc.file_type === 'pdf' ? '📕' : doc.file_type === 'docx' ? '📘' : '📝'}
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin-bottom: 0.25rem;">${doc.title}</h4>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">
                            ${doc.category_name || 'Uncategorized'} • ${formatDate(doc.upload_date)}
                        </div>
                    </div>
                    <span class="relevance-badge">
                        ${Math.round(doc.relevance_score * 100)}% match
                    </span>
                </div>
                ${doc.description ? `<p style="color: var(--text-secondary); font-size: 0.875rem;">${doc.description}</p>` : ''}
            </div>
        `).join('')}
    `;
}

function setupQuickSearch() {
    const input = document.getElementById('quick-search');
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            quickSearch();
        }
    });
}

function quickSearch() {
    const query = document.getElementById('quick-search').value.trim();
    if (query) {
        document.getElementById('search-input').value = query;
        document.querySelector('[data-page="search"]').click();
        performSearch();
        document.getElementById('quick-search').value = '';
    }
}

// Analytics
async function loadAnalytics() {
    const period = document.getElementById('analytics-period').value;

    try {
        const data = await apiCall(`/analytics/?days=${period}`);

        // Search trends chart
        createSearchTrendsChart(data.search_trends);

        // Access patterns chart
        createAccessPatternsChart(data.access_patterns);

        // Top queries
        renderTopQueries(data.top_queries);

        // Most accessed
        renderMostAccessed(data.most_accessed);

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function createSearchTrendsChart(data) {
    const ctx = document.getElementById('searchTrendsChart').getContext('2d');

    if (charts.searchTrends) {
        charts.searchTrends.destroy();
    }

    charts.searchTrends = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => formatDate(d.date)),
            datasets: [{
                label: 'Searches',
                data: data.map(d => d.count),
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createAccessPatternsChart(data) {
    const ctx = document.getElementById('accessPatternsChart').getContext('2d');

    if (charts.accessPatterns) {
        charts.accessPatterns.destroy();
    }

    const colors = {
        'view': '#2563eb',
        'download': '#10b981',
        'search_result': '#f59e0b'
    };

    charts.accessPatterns = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.access_type.replace('_', ' ')),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => colors[d.access_type] || '#64748b'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function renderTopQueries(queries) {
    const container = document.getElementById('top-queries-list');

    if (!queries || queries.length === 0) {
        container.innerHTML = '<small style="color: var(--text-secondary);">No queries yet</small>';
        return;
    }

    container.innerHTML = queries.map(q => `
        <div class="query-item">
            <span class="query-text">${q.query}</span>
            <div class="query-stats">
                <span>🔍 ${q.count} searches</span>
                <span>📄 ${q.total_results} results</span>
            </div>
        </div>
    `).join('');
}

function renderMostAccessed(docs) {
    const container = document.getElementById('most-accessed-list');

    if (!docs || docs.length === 0) {
        container.innerHTML = '<small style="color: var(--text-secondary);">No access data yet</small>';
        return;
    }

    container.innerHTML = docs.map((doc, index) => `
        <div class="document-item" onclick="showDocumentDetail(${doc.document__id})">
            <div style="font-weight: 600; width: 30px;">#${index + 1}</div>
            <div class="document-info">
                <div class="document-title">${doc.document__title}</div>
                <div class="document-meta">${doc.count} accesses</div>
            </div>
        </div>
    `).join('');
}

// Reports
async function loadReports() {
    try {
        const data = await apiCall('/reports/');

        // Category distribution
        const ctx1 = document.getElementById('reportCategoryChart').getContext('2d');
        if (charts.reportCategory) charts.reportCategory.destroy();
        charts.reportCategory = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: data.category_distribution.map(d => d.category__name || 'Uncategorized'),
                datasets: [{
                    label: 'Documents',
                    data: data.category_distribution.map(d => d.count),
                    backgroundColor: data.category_distribution.map(d => d.category__color || '#64748b')
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } }
            }
        });

        // Type distribution
        const ctx2 = document.getElementById('reportTypeChart').getContext('2d');
        if (charts.reportType) charts.reportType.destroy();
        charts.reportType = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: data.type_distribution.map(d => d.file_type.toUpperCase()),
                datasets: [{
                    label: 'Documents',
                    data: data.type_distribution.map(d => d.count),
                    backgroundColor: ['#ef4444', '#3b82f6', '#10b981']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } }
            }
        });

        // Upload trends
        const ctx3 = document.getElementById('uploadTrendsChart').getContext('2d');
        if (charts.uploadTrends) charts.uploadTrends.destroy();
        charts.uploadTrends = new Chart(ctx3, {
            type: 'line',
            data: {
                labels: data.upload_trends.map(d => formatDate(d.date)),
                datasets: [{
                    label: 'Uploads',
                    data: data.upload_trends.map(d => d.count),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });

        // View trends
        const ctx4 = document.getElementById('viewTrendsChart').getContext('2d');
        if (charts.viewTrends) charts.viewTrends.destroy();
        charts.viewTrends = new Chart(ctx4, {
            type: 'line',
            data: {
                labels: data.view_trends.map(d => formatDate(d.date)),
                datasets: [{
                    label: 'Views',
                    data: data.view_trends.map(d => d.count),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });

    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

// Upload
async function uploadDocument(event) {
    event.preventDefault();

    const title = document.getElementById('upload-title').value;
    const file = document.getElementById('upload-file').files[0];
    const description = document.getElementById('upload-description').value;
    const category = document.getElementById('upload-category').value;

    if (!file) {
        showToast('Please select a file', 'error');
        return;
    }

    // Show progress
    const progressDiv = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const uploadStatus = document.getElementById('upload-status');
    progressDiv.style.display = 'block';
    progressFill.style.width = '0%';
    uploadStatus.textContent = 'Uploading...';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (description) formData.append('description', description);
    if (category) formData.append('category', category);

    try {
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                progressFill.style.width = progress + '%';
            }
        }, 200);

        const response = await fetch(`${API_BASE}/documents/upload/`, {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        progressFill.style.width = '100%';
        uploadStatus.textContent = 'Processing document...';

        // Wait for processing
        await new Promise(resolve => setTimeout(resolve, 2000));

        const result = await response.json();

        uploadStatus.textContent = 'Upload complete!';

        showToast('Document uploaded successfully!', 'success');

        // Reset form
        document.getElementById('upload-form').reset();
        progressDiv.style.display = 'none';

        // Navigate to documents page
        document.querySelector('[data-page="documents"]').click();

    } catch (error) {
        console.error('Error uploading document:', error);
        uploadStatus.textContent = 'Upload failed!';
        showToast('Error uploading document', 'error');
    }
}

// Document Detail
async function showDocumentDetail(id) {
    try {
        const doc = await apiCall(`/documents/${id}/`);
        currentDocument = doc;

        // Track view
        await fetch(`${API_BASE}/documents/${id}/track_view/`, { method: 'POST' });

        const modal = document.getElementById('document-modal');
        const modalBody = document.getElementById('modal-body');
        const modalTitle = document.getElementById('modal-title');

        modalTitle.textContent = doc.title;

        const typeIcons = {
            'pdf': '📕',
            'docx': '📘',
            'txt': '📝'
        };

        modalBody.innerHTML = `
            <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 3rem;">${typeIcons[doc.file_type] || '📄'}</div>
                <div>
                    <h4 style="margin-bottom: 0.5rem;">${doc.title}</h4>
                    <div style="color: var(--text-secondary); font-size: 0.875rem;">
                        ${doc.file_size_formatted} • ${doc.file_type.toUpperCase()} • ${formatDate(doc.upload_date)}
                    </div>
                </div>
            </div>

            ${doc.category_name ? `
                <div style="margin-bottom: 1rem;">
                    <span class="category-badge" style="background-color: ${doc.category_color}; font-size: 0.875rem;">
                        ${doc.category_name}
                    </span>
                    ${doc.confidence_score ? `<span style="margin-left: 0.5rem; color: var(--text-secondary); font-size: 0.875rem;">
                        (Confidence: ${Math.round(doc.confidence_score * 100)}%)
                    </span>` : ''}
                </div>
            ` : ''}

            ${doc.description ? `
                <div style="margin-bottom: 1.5rem;">
                    <h5 style="margin-bottom: 0.5rem;">Description</h5>
                    <p style="color: var(--text-secondary);">${doc.description}</p>
                </div>
            ` : ''}

            <div style="margin-bottom: 1.5rem;">
                <h5 style="margin-bottom: 0.5rem;">Statistics</h5>
                <div style="display: flex; gap: 1rem; color: var(--text-secondary); font-size: 0.875rem;">
                    <span>👁 ${doc.view_count} views</span>
                    <span>📅 Uploaded ${formatDate(doc.upload_date)}</span>
                    ${doc.last_accessed ? `<span>🕒 Last accessed ${formatDate(doc.last_accessed)}</span>` : ''}
                </div>
            </div>

            ${doc.extracted_text ? `
                <div>
                    <h5 style="margin-bottom: 0.5rem;">Extracted Text Preview</h5>
                    <div style="background: var(--background); padding: 1rem; border-radius: 0.5rem; max-height: 200px; overflow-y: auto;">
                        <p style="font-size: 0.875rem; color: var(--text-secondary); white-space: pre-wrap;">${doc.extracted_text.substring(0, 500)}${doc.extracted_text.length > 500 ? '...' : ''}</p>
                    </div>
                </div>
            ` : ''}
        `;

        modal.classList.add('active');

    } catch (error) {
        console.error('Error loading document:', error);
        showToast('Error loading document', 'error');
    }
}

function closeModal() {
    document.getElementById('document-modal').classList.remove('active');
    currentDocument = null;
}

function downloadDocument() {
    if (currentDocument && currentDocument.file) {
        window.open(currentDocument.file, '_blank');
    }
}

// Categories
async function loadCategories() {
    try {
        const categories = await apiCall('/categories/');

        // Update filter dropdowns
        const options = '<option value="">All Categories</option>' +
            categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

        document.getElementById('filter-category').innerHTML = options;
        document.getElementById('search-category').innerHTML = options;
        document.getElementById('upload-category').innerHTML = '<option value="">Auto-classify (Recommended)</option>' +
            categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Utilities
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Close modal on outside click
window.addEventListener('click', (e) => {
    const modal = document.getElementById('document-modal');
    if (e.target === modal) {
        closeModal();
    }
});

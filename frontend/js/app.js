// SOLARGUARD X Application Controller

let digitalTwin = null;
let currentInspectionData = null;
let activeImageMode = 'heatmap';

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDigitalTwin();
    loadDashboardSummary();
    loadAnalyticsData();
    loadModelPerformance();
    initInspectionStudio();
    initPresets();
    initPanelComparison();
});

// View Navigation Router
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.app-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');

            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            sections.forEach(s => s.style.display = 'none');
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.style.display = 'block';
            }

            if (targetId === 'sec-digital-twin') {
                digitalTwin.loadPanels();
            } else if (targetId === 'sec-analytics') {
                loadAnalyticsData();
            } else if (targetId === 'sec-dashboard') {
                loadDashboardSummary();
            }
        });
    });

    // Field Technician Mode Toggle Switch
    const techToggle = document.getElementById('tech-mode-toggle');
    if (techToggle) {
        techToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('technician-mode');
            } else {
                document.body.classList.remove('technician-mode');
            }
        });
    }
}

// Digital Twin Initialization
function initDigitalTwin() {
    digitalTwin = new DigitalTwinGrid('digital-twin-grid', (panelCode) => {
        openPanelDetailModal(panelCode);
    });
    digitalTwin.loadPanels();

    // Filters
    const searchInput = document.getElementById('twin-search');
    const prioFilter = document.getElementById('twin-prio-filter');

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            digitalTwin.loadPanels({ search: searchInput.value, priority: prioFilter.value });
        });
    }
    if (prioFilter) {
        prioFilter.addEventListener('change', () => {
            digitalTwin.loadPanels({ search: searchInput ? searchInput.value : '', priority: prioFilter.value });
        });
    }
}

// Dashboard Stats Loader
async function loadDashboardSummary() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();

        document.getElementById('kpi-total-panels').textContent = data.total_panels;
        document.getElementById('kpi-healthy-panels').textContent = data.healthy_count;
        document.getElementById('kpi-warning-panels').textContent = data.warning_count + data.monitor_count;
        document.getElementById('kpi-critical-panels').textContent = data.critical_count;
        document.getElementById('kpi-avg-health').textContent = `${data.average_health}/100`;
        document.getElementById('kpi-urgent-p1').textContent = data.urgent_p1_count;

        // Render Urgent Panel Table
        const tbody = document.getElementById('recent-urgent-tbody');
        if (tbody) {
            tbody.innerHTML = '';
            data.recent_urgent_panels.forEach(p => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
                tr.style.cursor = 'pointer';
                tr.innerHTML = `
                    <td style="padding: 12px; font-weight: 700;">${p.panel_code}</td>
                    <td style="padding: 12px;">${p.current_health}/100</td>
                    <td style="padding: 12px;">${p.current_risk}/100</td>
                    <td style="padding: 12px; text-transform: capitalize;">${p.current_defect.replace('_', ' ')}</td>
                    <td style="padding: 12px;"><span class="pbadge ${p.current_priority.substring(0,2)}">${p.current_priority}</span></td>
                    <td style="padding: 12px;"><button class="btn-secondary" style="padding: 4px 10px; font-size: 12px;" onclick="openPanelDetailModal('${p.panel_code}')">Inspect</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error('Failed to load dashboard summary:', err);
    }
}

// Analytics Data Loader
async function loadAnalyticsData() {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        renderDefectChart('chart-defect-distribution', data.defect_distribution);
    } catch (err) {
        console.error('Failed to load analytics data:', err);
    }
}

// Model Performance Loader
async function loadModelPerformance() {
    try {
        const res = await fetch('/api/model-performance');
        const data = await res.json();

        document.getElementById('metric-accuracy').textContent = `${(data.accuracy * 100).toFixed(1)}%`;
        document.getElementById('metric-precision').textContent = `${(data.precision * 100).toFixed(1)}%`;
        document.getElementById('metric-recall').textContent = `${(data.recall * 100).toFixed(1)}%`;
        document.getElementById('metric-f1').textContent = `${(data.f1_score * 100).toFixed(1)}%`;
        document.getElementById('metric-iou').textContent = `${(data.segmentation_iou * 100).toFixed(1)}%`;
        document.getElementById('metric-latency').textContent = `${data.inference_latency_ms} ms`;
    } catch (err) {
        console.error('Failed to load model performance metrics:', err);
    }
}

// AI Inspection Studio Handler
function initInspectionStudio() {
    const fileInput = document.getElementById('studio-file-input');
    const dropZone = document.getElementById('studio-dropzone');
    const analyzeBtn = document.getElementById('btn-run-analysis');

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                runInspectionAnalysis(e.target.files[0], null);
            }
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#38bdf8';
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = 'rgba(56, 189, 248, 0.2)';
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'rgba(56, 189, 248, 0.2)';
            if (e.dataTransfer.files.length > 0) {
                runInspectionAnalysis(e.dataTransfer.files[0], null);
            }
        });
    }

    // View Mode Tab Switches (Original, Preprocessed, Bounding Boxes, Mask, Heatmap)
    const tabBtns = document.querySelectorAll('.vtab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeImageMode = btn.getAttribute('data-mode');
            updateStudioDisplayImage();
        });
    });
}

// Preset Loader
async function initPresets() {
    const presetContainer = document.getElementById('preset-buttons-container');
    if (!presetContainer) return;

    try {
        const res = await fetch('/api/demo-presets');
        const data = await res.json();

        presetContainer.innerHTML = '';
        data.presets.forEach(p => {
            const btn = document.createElement('button');
            btn.className = 'btn-secondary';
            btn.style.fontSize = '12px';
            btn.style.padding = '8px 12px';
            btn.innerHTML = `${p.badge} ${p.title}`;
            btn.addEventListener('click', () => {
                runInspectionAnalysis(null, p.id);
            });
            presetContainer.appendChild(btn);
        });
    } catch (err) {
        console.error('Failed to load presets:', err);
    }
}

// Execute Inspection Analysis API
async function runInspectionAnalysis(fileObj, presetKey) {
    const statusText = document.getElementById('studio-status-text');
    if (statusText) statusText.textContent = 'Processing Vision Model & Decision Engine...';

    const formData = new FormData();
    if (fileObj) {
        formData.append('file', fileObj);
    } else if (presetKey) {
        formData.append('preset', presetKey);
    }
    formData.append('panel_code', 'PNL-017');

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        currentInspectionData = data;

        if (statusText) statusText.textContent = `Analysis Complete (${data.inference_latency_ms} ms)`;

        renderStudioResults(data);
    } catch (err) {
        if (statusText) statusText.textContent = `Analysis Failed: ${err.message}`;
    }
}

// Render Studio UI Results
function renderStudioResults(data) {
    updateStudioDisplayImage();

    document.getElementById('res-panel-code').textContent = data.panel_code;
    document.getElementById('res-defect-type').textContent = data.display_name;
    document.getElementById('res-confidence').textContent = `${(data.confidence * 100).toFixed(0)}%`;
    document.getElementById('res-affected-area').textContent = `${data.affected_area_pct}%`;
    document.getElementById('res-health-score').textContent = `${data.health_score}/100 (${data.health_level})`;
    document.getElementById('res-risk-score').textContent = `${data.risk_score}/100 (${data.risk_level})`;
    
    const prioBadge = document.getElementById('res-priority-badge');
    prioBadge.textContent = data.priority_code;
    prioBadge.className = `pbadge ${data.priority_code.substring(0, 2)}`;

    document.getElementById('res-action').textContent = data.recommended_action;
    if (document.getElementById('res-what-damaged')) {
        document.getElementById('res-what-damaged').textContent = data.what_is_damaged;
    }
    if (document.getElementById('res-remediation-method')) {
        document.getElementById('res-remediation-method').textContent = data.remediation_method;
    }
    document.getElementById('res-ai-summary').textContent = data.ai_summary;


    renderPriorityContributionChart('chart-priority-contrib', data.contribution_breakdown);
}

// Update Active Image View
function updateStudioDisplayImage() {
    if (!currentInspectionData) return;
    const imgElem = document.getElementById('studio-display-img');
    if (!imgElem) return;

    if (activeImageMode === 'original') {
        imgElem.src = `data:image/jpeg;base64,${currentInspectionData.original_b64}`;
    } else if (activeImageMode === 'preprocessed') {
        imgElem.src = `data:image/jpeg;base64,${currentInspectionData.preprocessed_b64}`;
    } else if (activeImageMode === 'detection') {
        imgElem.src = `data:image/jpeg;base64,${currentInspectionData.detection_b64}`;
    } else if (activeImageMode === 'segmentation') {
        imgElem.src = `data:image/jpeg;base64,${currentInspectionData.segmentation_b64}`;
    } else { // heatmap
        imgElem.src = `data:image/jpeg;base64,${currentInspectionData.heatmap_b64}`;
    }
}

// Panel Detail Modal Handler
async function openPanelDetailModal(panelCode) {
    const modal = document.getElementById('panel-detail-modal');
    if (!modal) return;

    modal.classList.add('open');

    try {
        const res = await fetch(`/api/panels/${panelCode}`);
        const data = await res.json();
        const p = data.panel;

        document.getElementById('mdl-panel-code').textContent = p.panel_code;
        document.getElementById('mdl-health').textContent = `${p.current_health}/100`;
        document.getElementById('mdl-risk').textContent = `${p.current_risk}/100`;
        document.getElementById('mdl-severity').textContent = `${p.current_severity}/100`;
        document.getElementById('mdl-defect').textContent = p.current_defect.replace('_', ' ');
        document.getElementById('mdl-area').textContent = `${p.affected_area_pct}%`;
        
        const badge = document.getElementById('mdl-prio-badge');
        badge.textContent = p.current_priority;
        badge.className = `pbadge ${p.current_priority.substring(0, 2)}`;

        renderHealthHistoryChart('chart-panel-history', data.history, p.panel_code);
    } catch (err) {
        console.error('Failed to load panel detail:', err);
    }
}

function closePanelModal() {
    const modal = document.getElementById('panel-detail-modal');
    if (modal) modal.classList.remove('open');
}

// Side-by-side Panel Comparison Handler
async function initPanelComparison() {
    const btnCompare = document.getElementById('btn-run-comparison');
    if (!btnCompare) return;

    btnCompare.addEventListener('click', async () => {
        const panelA = document.getElementById('cmp-panel-a').value;
        const panelB = document.getElementById('cmp-panel-b').value;

        try {
            const res = await fetch(`/api/panels/compare?panel_a=${panelA}&panel_b=${panelB}`);
            const data = await res.json();
            renderComparisonChart('chart-comparison', data.panel_a, data.panel_b);
        } catch (err) {
            console.error('Failed to run comparison:', err);
        }
    });
}

// Generate Printable Report
function triggerReportGeneration() {
    const panelCode = currentInspectionData ? currentInspectionData.panel_code : 'PNL-017';
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/api/reports/generate';
    form.target = '_blank';

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'panel_code';
    input.value = panelCode;

    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

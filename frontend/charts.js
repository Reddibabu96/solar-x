// SOLARGUARD X Chart.js Manager

let defectChartInstance = null;
let healthHistoryChartInstance = null;
let priorityContribChartInstance = null;
let comparisonChartInstance = null;

function renderDefectChart(canvasId, distributionData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    if (defectChartInstance) {
        defectChartInstance.destroy();
    }

    const labels = distributionData.map(d => d.defect.replace('_', ' ').toUpperCase());
    const counts = distributionData.map(d => d.count);
    const colors = ['#22c55e', '#38bdf8', '#f97316', '#ef4444', '#eab308', '#a855f7'];

    defectChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#090d16'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter' } } }
            }
        }
    });
}

function renderHealthHistoryChart(canvasId, historyLogs, panelCode = 'PNL-017') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (healthHistoryChartInstance) {
        healthHistoryChartInstance.destroy();
    }

    const labels = historyLogs.map(h => `Day ${h.day_offset}`);
    const scores = historyLogs.map(h => h.health_score);

    healthHistoryChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${panelCode} Health Score (0-100)`,
                data: scores,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: '#facc15'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            },
            plugins: {
                legend: { labels: { color: '#f8fafc' } }
            }
        }
    });
}

function renderPriorityContributionChart(canvasId, breakdown) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (priorityContribChartInstance) {
        priorityContribChartInstance.destroy();
    }

    const labels = ['Severity (+35%)', 'Risk Score (+35%)', 'Health Drop (+20%)', 'Affected Area (+10%)'];
    const values = [
        breakdown.severity_contribution,
        breakdown.risk_contribution,
        breakdown.health_degradation_contribution,
        breakdown.affected_area_contribution
    ];

    priorityContribChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Priority Score Contribution Points',
                data: values,
                backgroundColor: ['#ef4444', '#f97316', '#eab308', '#38bdf8'],
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { min: 0, max: 40, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                y: { grid: { display: false }, ticks: { color: '#f8fafc', font: { weight: '600' } } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderComparisonChart(canvasId, dataA, dataB) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (comparisonChartInstance) {
        comparisonChartInstance.destroy();
    }

    const labels = ['Health Score', 'Severity', 'Risk Score', 'Affected Area %'];

    comparisonChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: dataA.panel_code,
                    data: [dataA.current_health, dataA.current_severity, dataA.current_risk, dataA.affected_area_pct],
                    backgroundColor: '#ef4444'
                },
                {
                    label: dataB.panel_code,
                    data: [dataB.current_health, dataB.current_severity, dataB.current_risk, dataB.affected_area_pct],
                    backgroundColor: '#38bdf8'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#f8fafc' } }
            },
            plugins: {
                legend: { labels: { color: '#f8fafc' } }
            }
        }
    });
}

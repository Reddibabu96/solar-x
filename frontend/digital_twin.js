const API_URL = "https://solar-x.onrender.com";
const API_BASE = window.location.origin.includes('render.com') ? '' : API_URL;

class DigitalTwinGrid {
    constructor(containerId, onPanelClickCallback) {
        self = this;
        this.container = document.getElementById(containerId);
        this.onPanelClick = onPanelClickCallback;
        this.panels = [];
    }

    async loadPanels(filters = {}) {
        let url = `${API_BASE}/api/panels?1=1`;
        if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`;
        if (filters.priority) url += `&priority=${encodeURIComponent(filters.priority)}`;
        if (filters.badge) url += `&badge=${encodeURIComponent(filters.badge)}`;
        if (filters.defect) url += `&defect=${encodeURIComponent(filters.defect)}`;

        try {
            const res = await fetch(url);
            const data = await res.json();
            this.panels = data.panels;
            this.render();
        } catch (err) {
            console.warn('Backend sleeping or offline, rendering fallback digital twin grid:', err);
            this.panels = this.generateFallbackPanels(filters);
            this.render();
        }
    }

    generateFallbackPanels(filters = {}) {
        const panels = [];
        const defects = ['healthy', 'healthy', 'healthy', 'microcrack', 'hotspot', 'crack', 'delamination', 'inactive_region'];
        for (let i = 1; i <= 100; i++) {
            const code = `PNL-${i.toString().padStart(3, '0')}`;
            let defect = i === 17 ? 'hotspot' : i === 31 ? 'inactive_region' : i === 44 ? 'crack' : defects[i % defects.length];
            let health = defect === 'healthy' ? 95 + (i % 5) : defect === 'hotspot' ? 21.4 : defect === 'inactive_region' ? 18.2 : 45.0;
            let badge = health > 75 ? '🟢' : health > 50 ? '🟡' : '🔴';
            let priority = health > 75 ? 'P4 — LOW' : health > 50 ? 'P3 — MEDIUM' : health > 25 ? 'P2 — HIGH' : 'P1 — URGENT';

            if (filters.priority && !priority.includes(filters.priority)) continue;
            if (filters.search && !code.toLowerCase().includes(filters.search.toLowerCase())) continue;

            panels.push({
                panel_code: code,
                current_health: health,
                health_badge: badge,
                current_priority: priority,
                current_defect: defect
            });
        }
        return panels;
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = '';

        this.panels.forEach(p => {
            const cell = document.createElement('div');
            const prioClass = p.current_priority.substring(0, 2);
            cell.className = `panel-cell ${prioClass}`;
            cell.dataset.code = p.panel_code;

            cell.innerHTML = `
                <span class="panel-cell-badge">${p.health_badge}</span>
                <span class="panel-cell-code">${p.panel_code}</span>
                <span class="panel-cell-health">${Math.round(p.current_health)}/100</span>
            `;

            cell.title = `${p.panel_code} | Health: ${p.current_health}/100 | Priority: ${p.current_priority} | Defect: ${p.current_defect}`;

            cell.addEventListener('click', () => {
                if (this.onPanelClick) {
                    this.onPanelClick(p.panel_code);
                }
            });

            this.container.appendChild(cell);
        });
    }
}

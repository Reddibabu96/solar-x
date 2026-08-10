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
            console.error('Failed to load digital twin panels:', err);
        }
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

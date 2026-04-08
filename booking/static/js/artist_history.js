// Artist History JavaScript - Optimized for Silent Updates & Space Management

document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    setInterval(updateTime, 1000);
    
    const searchInput = document.getElementById('searchInput');
    
    // 1. Silent AJAX Filtering for Buttons
    const filterButtons = document.querySelectorAll('.ajax-filter');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); 
            const url = this.getAttribute('href');

            fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newLog = doc.getElementById('service-log-container').innerHTML;
                    
                    document.getElementById('service-log-container').innerHTML = newLog;
                    
                    filterButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    window.history.pushState({}, '', url);
                    applySearch(); 
                });
        });
    });

    // 2. Real-time Search Logic
    if (searchInput) {
        searchInput.addEventListener('input', applySearch);
    }
});

/**
 * Toggles the visibility of extra content in Watchlist or Performance
 */
function toggleVisibility(id, btn) {
    const content = document.getElementById(id);
    if (content.style.display === "block") {
        content.style.display = "none";
        btn.textContent = btn.textContent.replace("Show Less", "View All");
    } else {
        content.style.display = "block";
        btn.textContent = btn.textContent.replace("View All", "Show Less");
    }
}

/**
 * Apply filtering based on search input
 */
function applySearch() {
    const term = document.getElementById('searchInput').value.toLowerCase().trim();
    const items = document.querySelectorAll('.history-item');
    const list = document.getElementById('historyList');
    let found = 0;

    items.forEach(item => {
        const client = item.dataset.client.toLowerCase();
        const service = item.dataset.service.toLowerCase();
        
        if (client.includes(term) || service.includes(term)) {
            item.style.display = 'block';
            found++;
        } else {
            item.style.display = 'none';
        }
    });

    handleNoResults(found, term, list);
}

function updateTime() {
    const now = new Date();
    const el = document.getElementById('currentTime');
    if (el) el.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function handleNoResults(count, term, container) {
    let msg = document.getElementById('searchNoResults');
    if (count === 0 && term !== '') {
        if (!msg) {
            msg = document.createElement('div');
            msg.id = 'searchNoResults';
            msg.className = 'text-center py-5';
            msg.innerHTML = `<i class="bi bi-search display-4 text-muted"></i><p class="text-muted mt-3">No records match "${term}"</p>`;
            container.appendChild(msg);
        }
    } else if (msg) {
        msg.remove();
    }
}
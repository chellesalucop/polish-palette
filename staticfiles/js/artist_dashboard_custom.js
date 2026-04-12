// =========================
// ARTIST DASHBOARD JAVASCRIPT
// =========================

// Initialize command center when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const rightSidebar = document.getElementById('rightSidebar');
    const rightToggle = document.getElementById('rightSidebarToggle');
    const overlay = document.getElementById('sidebarOverlay');
    const leftSidebar = document.getElementById('artistSidebar');
    const leftToggle = document.getElementById('leftSidebarToggle') || document.getElementById('mobileToggle');
    const mainContent = document.getElementById('mainContent');

    const isMobile = () => window.innerWidth < 992;

    function syncOverlayState() {
        if (!overlay) return;
        const leftOpen = leftSidebar && !leftSidebar.classList.contains('collapsed') && isMobile();
        const rightOpen = rightSidebar && rightSidebar.classList.contains('show') && isMobile();

        if (leftOpen || rightOpen) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    function closeRightSidebar() {
        if (!rightSidebar) return;
        rightSidebar.classList.remove('show');
        if (isMobile()) {
            rightSidebar.classList.add('right-sidebar-collapsed');
        }
        syncOverlayState();
    }

    function closeLeftSidebar() {
        if (!leftSidebar) return;
        leftSidebar.classList.add('collapsed');
        if (mainContent) {
            mainContent.classList.add('sidebar-collapsed');
        }
        if (leftToggle) leftToggle.style.display = '';
        syncOverlayState();
    }

    function toggleLeftSidebar(event) {
        if (!leftSidebar || !isMobile()) return;
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        const willOpen = leftSidebar.classList.contains('collapsed');

        if (willOpen) {
            closeRightSidebar();
            leftSidebar.classList.remove('collapsed');
            if (mainContent) {
                mainContent.classList.remove('sidebar-collapsed');
            }
            if (leftToggle) leftToggle.style.display = 'none';
        } else {
            closeLeftSidebar();
            return;
        }

        syncOverlayState();
    }

    // Watch for sidebar state changes from ANY source (base template JS, overlay, close button)
    // so toggle button always stays in sync
    if (leftSidebar && leftToggle) {
        const observer = new MutationObserver(function() {
            if (!isMobile()) return;
            const isCollapsed = leftSidebar.classList.contains('collapsed');
            leftToggle.style.display = isCollapsed ? '' : 'none';
        });
        observer.observe(leftSidebar, { attributes: true, attributeFilter: ['class'] });
    }

    function toggleRightSidebar() {
        if (!rightSidebar || !isMobile()) return;

        const willShow = !rightSidebar.classList.contains('show');

        if (willShow) {
            closeLeftSidebar();
        }

        rightSidebar.classList.toggle('show', willShow);
        rightSidebar.classList.toggle('right-sidebar-collapsed', !willShow);
        syncOverlayState();
    }

    window.toggleRightSidebar = function() {
        if (!isMobile() || !rightSidebar) return;
        toggleRightSidebar();
    };

    if (rightSidebar && isMobile()) {
        rightSidebar.classList.add('right-sidebar-collapsed');
    }

    if (rightToggle) {
        rightToggle.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            window.toggleRightSidebar();
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function(event) {
            if (rightSidebar && rightSidebar.classList.contains('show')) {
                closeRightSidebar();
                event.stopImmediatePropagation();
            }
        }, true);
    }

    window.addEventListener('resize', function() {
        if (!rightSidebar) return;

        if (isMobile()) {
            if (!rightSidebar.classList.contains('show')) {
                rightSidebar.classList.add('right-sidebar-collapsed');
            }
        } else {
            rightSidebar.classList.remove('show');
            rightSidebar.classList.remove('right-sidebar-collapsed');
        }

        syncOverlayState();
    });

    // Initialize command center when DOM is ready
    if (typeof commandCenter !== 'undefined') {
        commandCenter.initializeCommandCenter();
        commandCenter.initializeCalendar();
        commandCenter.updateDashboardStats();
        commandCenter.startPeriodicUpdates();
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Command Center object for appointment management
window.commandCenter = {
    startSession: function(appointmentId) {
        if (confirm('Are you sure you want to start this session?')) {
            fetch("{% url 'artist_start_session' %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken()
                },
                body: `appointment_id=${appointmentId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message);
                }
            })
            .catch(() => {
                alert('Error starting session.');
            });
        }
    },
    
    finishSession: function(appointmentId) {
        if (confirm('Are you sure you want to finish this session?')) {
            fetch("{% url 'artist_finish_session' %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken()
                },
                body: `appointment_id=${appointmentId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message);
                }
            })
            .catch(() => {
                alert('Error finishing session.');
            });
        }
    },
    
    updateDashboardStats: function() {
        // Placeholder function for updating dashboard statistics
        console.log('Dashboard stats updated');
    },
    
    startPeriodicUpdates: function() {
        // Placeholder function for periodic updates
        console.log('Periodic updates started');
    },
    
    initializeCommandCenter: function() {
        // Initialize command center functionality
        console.log('Command center initialized');
    },
    
    initializeCalendar: function() {
        // Initialize calendar functionality
        console.log('Calendar initialized');
    }
};

function getCSRFToken() {
    // Use global CSRF token
    var tokenInput = document.getElementById('globalCSRFToken');
    return tokenInput ? tokenInput.value : '';
}

// Function to update upcoming log (upcoming_bookings) after approval
function updateUpcomingLog() {
    fetch("{% url 'artist_dashboard' %}", {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the upcoming_bookings section
            const upcomingBookingsContainer = document.getElementById('upcomingBookings');
            if (upcomingBookingsContainer) {
                upcomingBookingsContainer.innerHTML = data.upcoming_bookings_html;
            }
        }
    })
    .catch(error => {
        console.error('Error updating upcoming bookings:', error);
    });
}

// Approval/Reject button handlers
document.addEventListener('DOMContentLoaded', function() {
    // Approval/Reject buttons
    document.querySelectorAll('.approve-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            handleApproveReject('approve_request', btn.dataset.id, btn);
        });
    });
    document.querySelectorAll('.reject-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            handleApproveReject('reject_request', btn.dataset.id, btn);
        });
    });
    
    // Initialize command center when DOM is ready
    if (typeof commandCenter !== 'undefined') {
        commandCenter.initializeCommandCenter();
        commandCenter.initializeCalendar();
        commandCenter.updateDashboardStats();
        commandCenter.startPeriodicUpdates();
    }
});

function handleApproveReject(action, appointmentId, btn) {
    fetch("{% url 'artist_approve_reject' %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        body: `action=${action}&appointment_id=${appointmentId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // Update the upcoming log
            updateUpcomingLog();
            // Optionally remove the appointment card from DOM
            const appointmentCard = btn.closest('.appointment-card');
            if (appointmentCard) {
                appointmentCard.remove();
            }
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error in approval/reject:', error);
        alert('Error processing request. Please try again.');
    });
}

// disable history scroll restoration on dashboard pages
if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
}

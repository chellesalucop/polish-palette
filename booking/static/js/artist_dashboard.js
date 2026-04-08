// Artist Dashboard - Simplified initialization
document.addEventListener('DOMContentLoaded', function() {
    // 1. Digital Clock
    updateTime();
    setInterval(updateTime, 1000);
    
    // 2. Core Modules
    initializeCalendar();
    
    // 3. Auto-refresh calendar every hour
    setInterval(initializeCalendar, 3600000);
    
    // 4. Initialize command center
    initializeCommandCenter();
    
    // 5. Sidebar functionality
    initializeSidebar();
    
    // 6. WebSocket for real-time booking updates
    initializeArtistWebSocket();
});

function initializeArtistWebSocket() {
    const artistId = document.querySelector('[data-artist-id]')?.getAttribute('data-artist-id') || 
                   document.querySelector('meta[name="artist-id"]')?.getAttribute('content') ||
                   "{{ artist.id|default:'' }}";
    
    if (!artistId || artistId === '{{ artist.id|default:\'\' }}') {
        console.log('Artist ID not available, skipping WebSocket connection');
        return;
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/artist/${artistId}/`;
    
    let socket = null;
    let reconnectInterval = null;
    
    function connect() {
        try {
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function() {
                console.log('Artist WebSocket connected');
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                console.log('Artist WebSocket message:', data);
                
                handleRealtimeUpdate(data);
            };
            
            socket.onclose = function(event) {
                console.log('Artist WebSocket disconnected:', event.code, event.reason);
                // Try to reconnect after 3 seconds
                if (!reconnectInterval) {
                    reconnectInterval = setTimeout(connect, 3000);
                }
            };
            
            socket.onerror = function(error) {
                console.error('Artist WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to connect artist WebSocket:', error);
        }
    }
    
    // Initial connection
    connect();
}

function handleRealtimeUpdate(data) {
    console.log('Received real-time update:', data);
    
    switch(data.event) {
        case 'new_booking':
            handleNewBooking(data);
            break;
        case 'booking_status_changed':
            handleBookingStatusChange(data);
            break;
        case 'appointment_approved':
            handleAppointmentApproved(data);
            break;
        case 'rescheduling_started':
        case 'rescheduling_confirmed':
        case 'rescheduling_aborted':
            handleRescheduleUpdate(data);
            break;
        default:
            console.log('Unknown event type:', data.event);
    }
}

function handleNewBooking(data) {
    // Show notification for new booking
    showNotification(`New booking: ${data.service_name} with ${data.client_name}`, 'success');
    
    // Refresh the pending requests section
    refreshPendingRequests();
    
    // Refresh calendar if on calendar view
    if (typeof refreshCalendar === 'function') {
        refreshCalendar();
    }
}

function handleBookingStatusChange(data) {
    // Show notification for status change
    showNotification(`Booking status changed to: ${data.status}`, 'info');
    
    // Refresh relevant sections
    refreshPendingRequests();
    refreshCalendar();
}

function handleAppointmentApproved(data) {
    // Show notification for appointment approval
    showNotification(`Appointment approved: ${data.service_name} with ${data.client_name}`, 'success');
    
    // Refresh both pending requests and session manager
    refreshPendingRequests();
    refreshSessionManager();
    refreshCalendar();
}

function handleRescheduleUpdate(data) {
    // Show notification for reschedule activity
    showNotification(`Reschedule activity: ${data.event}`, 'warning');
    
    // Refresh relevant sections
    refreshPendingRequests();
    refreshCalendar();
}

function refreshPendingRequests() {
    // Fetch updated pending requests via AJAX without page reload
    fetch(window.location.pathname + '?refresh_pending=true', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Update the pending requests section
        const pendingContainer = document.querySelector('.approval-section .list-group');
        if (pendingContainer) {
            // Create a temporary div to parse the HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            
            // Find the new content
            const newContent = tempDiv.querySelector('.list-group') || tempDiv;
            
            if (newContent.innerHTML.trim()) {
                pendingContainer.innerHTML = newContent.innerHTML;
            } else {
                // If no pending requests, show the empty message
                pendingContainer.innerHTML = `
                    <div class="list-group-item text-center py-3 bg-white text-muted">
                        <p class="mb-0">No pending approvals right now.</p>
                    </div>
                `;
            }
        }
        
        // Also refresh session manager if needed
        refreshSessionManager();
    })
    .catch(error => {
        console.error('Error refreshing pending requests:', error);
        // Fallback to page reload if AJAX fails
        window.location.reload();
    });
}

function refreshSessionManager() {
    // Fetch updated session manager content
    fetch(window.location.pathname + '?refresh_session=true', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Update the session manager section
        const sessionContainer = document.querySelector('.command-center-section .active-jobs-list');
        if (sessionContainer) {
            // Create a temporary div to parse the HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            
            // Find the new content
            const newContent = tempDiv.querySelector('.active-jobs-list') || tempDiv;
            
            if (newContent.innerHTML.trim()) {
                sessionContainer.innerHTML = newContent.innerHTML;
            }
        }
    })
    .catch(error => {
        console.error('Error refreshing session manager:', error);
    });
}

function showNotification(message, type = 'info') {
    // Create a toast notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-dismiss="alert" onclick="this.parentElement.remove()">
            <span>&times;</span>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Appointment approval/rejection functions
function approveAppointment(appointmentId) {
    if (!confirm('Are you sure you want to approve this appointment?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('action', 'approve_request');
    formData.append('appointment_id', appointmentId);
    
    fetch('/artist/approve-reject/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            // Refresh the pending requests section
            refreshPendingRequests();
            // Refresh calendar
            if (typeof refreshCalendar === 'function') {
                refreshCalendar();
            }
        } else {
            showNotification(data.message || 'Error approving appointment', 'danger');
        }
    })
    .catch(error => {
        console.error('Error approving appointment:', error);
        showNotification('Error approving appointment', 'danger');
    });
}

function rejectAppointment(appointmentId) {
    if (!confirm('Are you sure you want to reject this appointment?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('action', 'reject_request');
    formData.append('appointment_id', appointmentId);
    
    fetch('/artist/approve-reject/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            // Refresh the pending requests section
            refreshPendingRequests();
            // Refresh calendar
            if (typeof refreshCalendar === 'function') {
                refreshCalendar();
            }
        } else {
            showNotification(data.message || 'Error rejecting appointment', 'danger');
        }
    })
    .catch(error => {
        console.error('Error rejecting appointment:', error);
        showNotification('Error rejecting appointment', 'danger');
    });
}

// Helper function to get CSRF token
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

function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const el = document.getElementById('currentTime');
    if (el) el.textContent = timeString;
}

function initializeCalendar() {
    const calendarGrid = document.getElementById('calendarGrid');
    const monthDisplay = document.getElementById('currentMonth');
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');
    
    if (!calendarGrid || !monthDisplay) return;

    let date = new Date();
    let currMonth = date.getMonth();
    let currYear = date.getFullYear();

    const months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"];

    function renderCalendar() {
        let firstDayofMonth = new Date(currYear, currMonth, 1).getDay();
        let lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate();
        let lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay();
        let lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate();
        
        let html = "";

        // Add Day Headers
        const days = ["S", "M", "T", "W", "T", "F", "S"];
        days.forEach(day => {
            html += `<div class="calendar-day header">${day}</div>`;
        });

        // Previous month padding
        for (let i = firstDayofMonth; i > 0; i--) {
            html += `<div class="calendar-day text-muted" style="opacity:0.3">${lastDateofLastMonth - i + 1}</div>`;
        }

        // Current month days
        for (let i = 1; i <= lastDateofMonth; i++) {
            let isToday = i === date.getDate() && currMonth === new Date().getMonth() 
                        && currYear === new Date().getFullYear() ? "today" : "";
            
            // Check if booked
            let isBooked = checkSidebarForBooking(i, currMonth);
            let bookedClass = isBooked ? "booked" : "";

            html += `<div class="calendar-day ${isToday} ${bookedClass}">${i}</div>`;
        }

        // Next month padding
        for (let i = lastDayofMonth; i < 6; i++) {
            html += `<div class="calendar-day text-muted" style="opacity:0.3">${i - lastDayofMonth + 1}</div>`;
        }

        monthDisplay.innerText = `${months[currMonth]} ${currYear}`;
        calendarGrid.innerHTML = html;
    }

    function checkSidebarForBooking(day, monthIdx) {
        const dates = window.BOOKED_DATES || [];
        const pad = n => n < 10 ? '0' + n : '' + n;
        const target = `${currYear}-${pad(monthIdx + 1)}-${pad(day)}`;
        return dates.indexOf(target) !== -1;
    }

    prevBtn.onclick = () => {
        currMonth--;
        if(currMonth < 0) {
            currMonth = 11;
            currYear--;
        }
        renderCalendar();
    };

    nextBtn.onclick = () => {
        currMonth++;
        if(currMonth > 11) {
            currMonth = 0;
            currYear++;
        }
        renderCalendar();
    };

    renderCalendar();

    // Calendar day click interaction
    calendarGrid.addEventListener('click', function(e) {
        const dayEl = e.target.closest('.calendar-day');
        if (!dayEl || dayEl.classList.contains('header') || dayEl.style.opacity < 1) return;

        // Visual feedback for selection
        document.querySelectorAll('.calendar-day').forEach(d => d.classList.remove('selected-date'));
        dayEl.classList.add('selected-date');

        const day = dayEl.innerText.trim();
        const pad = n => n < 10 ? '0' + n : '' + n;
        const selectedDate = `${currYear}-${pad(currMonth + 1)}-${pad(day)}`;

        filterSidebarByDate(selectedDate);
    });
}

function filterSidebarByDate(dateString) {
    const items = Array.from(document.querySelectorAll('.upcoming-item'));
    const container = document.getElementById('upcomingLogList');
    if (!container || items.length === 0) return;

    items.sort((a, b) => {
        const dateA = a.dataset.date;
        const dateB = b.dataset.date;
        const timeA = a.dataset.time;
        const timeB = b.dataset.time;

        if (dateA === dateString && dateB !== dateString) return -1;
        if (dateA !== dateString && dateB === dateString) return 1;

        if (dateA !== dateB) return dateA.localeCompare(dateB);
        return timeA.localeCompare(timeB);
    });

    items.forEach(item => container.appendChild(item));
}

function initializeCommandCenter() {
    // Command Center object for appointment management
    window.commandCenter = {
        startSession: function(appointmentId) {
            if (confirm('Are you sure you want to start this session?')) {
                fetch("/artist/start-session/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({appointment_id: appointmentId})
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
                fetch("/artist/finish-session/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({appointment_id: appointmentId})
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
    
    // Initialize dashboard statistics
    commandCenter.updateDashboardStats();
    
    // Start periodic updates
    commandCenter.startPeriodicUpdates();
}

function initializeSidebar() {
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
    // so the toggle button always stays in sync
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

    if (leftToggle && leftToggle.id === 'leftSidebarToggle') {
        leftToggle.addEventListener('click', toggleLeftSidebar);
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
}

function handleApproveReject(action, appointmentId, btn, reason = '') {
    // Prevent duplicate submissions for the same appointment
    if (window.rejectionInProgress[appointmentId]) {
        return;
    }
    
    window.rejectionInProgress[appointmentId] = true;
    const requestBody = reason ? `action=${action}&appointment_id=${appointmentId}&rejection_reason=${encodeURIComponent(reason)}` : `action=${action}&appointment_id=${appointmentId}`;
    
    fetch("/artist/approve-reject/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        body: requestBody
    })
    .then(response => response.json())
    .then(data => {
        // Clean up the flag
        delete window.rejectionInProgress[appointmentId];
        
        if (data.success) {
            alert(data.message);
            // Remove the appointment card from DOM
            const card = btn.closest('.list-group-item');
            if (card) {
                card.style.opacity = '0.5';
                card.style.pointerEvents = 'none';
                setTimeout(() => card.remove(), 500);
            }
        } else {
            alert(data.message || 'An error occurred');
        }
    })
    .catch(error => {
        // Clean up the flag on error
        delete window.rejectionInProgress[appointmentId];
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}

function getCSRFToken() {
    // Use the global CSRF token
    var tokenInput = document.getElementById('globalCSRFToken');
    return tokenInput ? tokenInput.value : '';
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
            // Store the current button reference for later use
            window.currentRejectBtn = btn;
            
            // Show rejection modal
            var modal = document.getElementById('rejectionModal');
            var confirmBtn = document.getElementById('confirmRejectBtn');
            var cancelBtn = modal.querySelector('[data-bs-dismiss="modal"]');
            var reasonTextarea = document.getElementById('rejectionReason');
            var charCount = document.getElementById('charCount');
            
            // Reset modal
            reasonTextarea.value = '';
            charCount.textContent = '0/50';
            charCount.style.color = '#6c757d';
            
            // Show modal
            modal.style.display = 'block';
            modal.classList.add('show');
            
            // Remove existing event listeners to prevent duplicates
            confirmBtn.replaceWith(confirmBtn.cloneNode(true));
            cancelBtn.replaceWith(cancelBtn.cloneNode(true));
            
            // Get fresh references after cloning
            confirmBtn = document.getElementById('confirmRejectBtn');
            cancelBtn = modal.querySelector('[data-bs-dismiss="modal"]');
            
            // Handle confirm button - this is where rejection actually happens
            confirmBtn.onclick = function() {
                // Prevent multiple submissions
                if (this.disabled) return;
                this.disabled = true;
                
                var reason = reasonTextarea.value.trim();
                console.log('DEBUG: About to reject with reason:', reason);
                
                if (reason.length === 0) {
                    alert('Please provide a reason for rejection.');
                    this.disabled = false;
                    return;
                }
                if (reason.length > 50) {
                    alert('Rejection reason must be 50 characters or less.');
                    this.disabled = false;
                    return;
                }
                
                // Hide modal
                modal.style.display = 'none';
                modal.classList.remove('show');
                
                // Proceed with rejection only now
                handleApproveReject('reject_request', window.currentRejectBtn.dataset.id, window.currentRejectBtn, reason);
            };
            
            // Handle cancel button
            cancelBtn.onclick = function() {
                modal.style.display = 'none';
                modal.classList.remove('show');
            };
            
            // Character counter
            reasonTextarea.addEventListener('input', function() {
                var remaining = 50 - this.value.length;
                charCount.textContent = remaining + '/50';
                if (remaining < 0) {
                    charCount.style.color = '#dc3545';
                } else {
                    charCount.style.color = '#6c757d';
                }
            });
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

// disable history scroll restoration on dashboard pages
if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
}
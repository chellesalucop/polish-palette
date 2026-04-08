/**
 * Artist Command Center - Manual Session Control System
 * Handles Start/Finish buttons with timing constraints and real-time updates
 */

class CommandCenter {
    constructor() {
        this.sessionTimers = new Map();
        this.sanitationTimer = null;
        this.websocket = null;
        this.init();
    }

    init() {
        this.initializeCommandCenter();
        this.initializeWebSocket();
        this.startTimingChecks();
        this.initializeSanitationTimer();
    }

    /**
     * Initialize command center buttons and timing logic
     */
    initializeCommandCenter() {
        // Initialize Start Session buttons
        document.querySelectorAll('.start-session-btn').forEach(button => {
            const appointmentId = button.dataset.appointmentId;
            const appointmentTime = button.dataset.appointmentTime;
            const appointmentDate = button.dataset.appointmentDate;
            
            this.updateStartButton(button, appointmentTime, appointmentDate);
            
            button.addEventListener('click', () => {
                this.startSession(appointmentId);
            });
        });

        // Initialize Reschedule buttons with 48-hour lock
        document.querySelectorAll('.reschedule-btn').forEach(button => {
            const appointmentId = button.dataset.appointmentId;
            const appointmentDate = button.dataset.appointmentDate;
            const appointmentTime = button.dataset.appointmentTime;
            
            this.updateRescheduleButton(button, appointmentDate, appointmentTime);
            
            button.addEventListener('click', () => {
                this.initiateReschedule(appointmentId);
            });
        });

        // Initialize Finish Session buttons
        document.querySelectorAll('.finish-session-btn').forEach(button => {
            const appointmentId = button.dataset.appointmentId;
            const startTime = button.dataset.startTime;
            
            this.updateFinishButton(button, startTime);
            
            button.addEventListener('click', () => {
                this.finishSession(appointmentId);
            });
        });
    }

    /**
     * Update Start button state based on timing constraints
     */
    updateStartButton(button, appointmentTime, appointmentDate) {
        const appointmentId = button.dataset.appointmentId;
        const statusEl = document.getElementById(`timing-status-${appointmentId}`);
        const btnText = button.querySelector('.btn-text');
        
        const now = new Date();
        const [hours, minutes] = appointmentTime.split(':').map(Number);
        const appointmentDateTime = new Date(appointmentDate);
        appointmentDateTime.setHours(hours, minutes, 0, 0);
        
        const timeDiff = appointmentDateTime - now;
        const minutesUntil = Math.floor(timeDiff / (1000 * 60));
        
        button.disabled = true;
        button.className = 'btn btn-sm start-session-btn';
        
        if (minutesUntil > 15) {
            // Waiting State: Greyed out
            button.classList.add('btn-secondary');
            btnText.textContent = `Available in ${minutesUntil - 15} mins`;
            if (statusEl) statusEl.textContent = `Button unlocks ${minutesUntil - 15} minutes before appointment`;
            
        } else if (minutesUntil >= -10) {
            // Ready State: Pulse animation
            button.disabled = false;
            button.classList.add('btn-primary', 'pulse-animation');
            btnText.textContent = 'Start Session';
            if (statusEl) statusEl.textContent = 'Ready to start session';
            
        } else if (minutesUntil >= -30) {
            // Late State: Red button
            button.disabled = false;
            button.classList.add('btn-danger');
            btnText.textContent = 'Client Late - Start Now?';
            if (statusEl) statusEl.textContent = 'Appointment time passed. Client may be late.';
            
        } else {
            // Very Late: Still allow start but with warning
            button.disabled = false;
            button.classList.add('btn-warning');
            btnText.textContent = 'Start Session (Very Late)';
            if (statusEl) statusEl.textContent = 'Appointment is very late. Consider contacting client.';
        }
    }

    /**
     * Update Reschedule button based on 48-hour lock logic
     */
    updateRescheduleButton(button, appointmentDate, appointmentTime) {
        const appointmentId = button.dataset.appointmentId;
        const statusEl = document.getElementById(`reschedule-status-${appointmentId}`);
        const btnText = button.querySelector('.btn-text');
        const overrideBtn = document.querySelector(`.artist-override-btn[data-appointment-id="${appointmentId}"]`);
        
        const now = new Date();
        const appointmentDateTime = new Date(appointmentDate);
        const [hours, minutes] = appointmentTime.split(':').map(Number);
        appointmentDateTime.setHours(hours, minutes, 0, 0);
        
        // Calculate days difference
        const timeDiff = appointmentDateTime - now;
        const diffInDays = timeDiff / (1000 * 3600 * 24);
        
        button.disabled = true;
        button.className = 'btn btn-outline-warning btn-sm reschedule-btn';
        
        // Hide override button by default
        if (overrideBtn) {
            overrideBtn.style.display = 'none';
        }
        
        if (diffInDays >= 2) {
            // More than 48 hours: Allow rescheduling
            button.disabled = false;
            button.classList.add('pulse-animation');
            btnText.textContent = 'Reschedule';
            if (statusEl) statusEl.textContent = 'Rescheduling available';
            button.title = 'Click to reschedule this appointment';
            
        } else if (diffInDays >= 0) {
            // Within 48 hours: Locked with explanation
            button.classList.add('btn-outline-secondary');
            btnText.textContent = 'Locked';
            if (statusEl) statusEl.textContent = 'Changes within 48 hours require direct artist approval';
            button.title = `Rescheduling is only available up to 48 hours before your appointment (${Math.ceil(diffInDays * 24)} hours remaining)`;
            
            // Show artist override button
            if (overrideBtn) {
                overrideBtn.style.display = 'inline-block';
                overrideBtn.title = 'Artist Override: Bypass 48-hour lock';
            }
            
        } else {
            // Past appointment: Cannot reschedule
            button.classList.add('btn-outline-danger');
            btnText.textContent = 'Expired';
            if (statusEl) statusEl.textContent = 'Appointment time has passed';
            button.title = 'Cannot reschedule past appointments';
        }
    }

    /**
     * Initiate reschedule process (Artist Manual Override)
     */
    initiateReschedule(appointmentId) {
        // Show confirmation dialog for artists
        if (!confirm('As an artist, you can manually reschedule any appointment. Do you want to reschedule this appointment?')) {
            return;
        }
        
        // Redirect to reschedule page or open modal
        window.location.href = `/reschedule/${appointmentId}/`;
    }

    /**
     * Artist Manual Override for 48-hour lock
     */
    artistManualOverride(appointmentId) {
        if (!confirm('Artist Override: You can bypass the 48-hour lock and manually reschedule this appointment. Continue?')) {
            return;
        }
        
        // Redirect to artist reschedule interface
        window.location.href = `/artist/reschedule/${appointmentId}/`;
    }

    /**
     * Add artist note to appointment
     */
    addArtistNote(appointmentId) {
        const note = prompt('Add a note for this appointment:');
        if (note !== null && note.trim() !== '') {
            // Send note to backend
            fetch(`/artist/add_note/${appointmentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ note: note })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    alert('Note added successfully');
                } else {
                    alert('Error adding note: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error adding note:', error);
                alert('Error adding note. Please try again.');
            });
        }
    }

    /**
     * Delete appointment with artist override
     */
    deleteAppointment(appointmentId) {
        if (!confirm('Are you sure you want to delete/cancel this appointment? This action cannot be undone.')) {
            return;
        }
        
        // Send delete request to backend
        fetch(`/artist/delete/${appointmentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // Remove appointment from DOM
                    const appointmentElement = document.getElementById(`appointment-${appointmentId}`);
                    if (appointmentElement) {
                        appointmentElement.remove();
                    }
                    alert('Appointment deleted successfully');
                } else {
                    alert('Error deleting appointment: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error deleting appointment:', error);
                alert('Error deleting appointment. Please try again.');
            });
        }
    }

    /**
     * View client history
     */
    viewClientHistory(clientId) {
        // Open client history in new tab or modal
        window.open(`/artist/client/${clientId}/history/`, '_blank');
    }

    /**
     * Switch between active and completed tabs
     */
    switchTab(tab) {
        const activeContent = document.getElementById('activeContent');
        const completedContent = document.getElementById('completedContent');
        const activeTab = document.getElementById('tabActive');
        const completedTab = document.getElementById('tabCompleted');
        
        // Update tab buttons
        activeTab.classList.remove('active');
        completedTab.classList.remove('active');
        
        if (tab === 'active') {
            activeTab.classList.add('active');
            activeContent.style.display = 'block';
            completedContent.style.display = 'none';
        } else {
            completedTab.classList.add('active');
            activeContent.style.display = 'none';
            completedContent.style.display = 'block';
        }
    }

    /**
     * Toggle artist status (Available/Busy)
     */
    toggleStatus() {
        const statusDot = document.getElementById('mainStatusDot');
        const statusText = document.getElementById('mainStatusText');
        
        if (statusText.textContent.trim() === 'Available') {
            statusDot.style.background = 'var(--accent-orange)';
            statusText.textContent = 'Busy';
            this.showToast('Status Updated', 'You are now marked as Busy', 'warning');
        } else {
            statusDot.style.background = 'var(--accent-green)';
            statusText.textContent = 'Available';
            this.showToast('Status Updated', 'You are now marked as Available', 'success');
        }
    }

    /**
     * Approve appointment
     */
    approveAppointment(appointmentId) {
        if (!confirm('Approve this appointment?')) {
            return;
        }
        
        fetch(`/artist/approve/${appointmentId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                this.showToast('Approved', 'Appointment has been approved', 'success');
                location.reload();
            } else {
                this.showToast('Error', data.message || 'Failed to approve appointment', 'error');
            }
        })
        .catch(error => {
            console.error('Error approving appointment:', error);
            this.showToast('Error', 'Failed to approve appointment', 'error');
        });
    }

    /**
     * View appointment details
     */
    viewDetails(appointmentId) {
        window.open(`/artist/appointment/${appointmentId}/`, '_blank');
    }

    /**
     * View reference files
     */
    viewReference(appointmentId) {
        window.open(`/artist/reference/${appointmentId}/`, '_blank');
    }

    /**
     * View receipt
     */
    viewReceipt(appointmentId) {
        window.open(`/artist/receipt/${appointmentId}/`, '_blank');
    }

    /**
     * Start session
     */
    startSession(appointmentId) {
        if (!confirm('Start this session?')) {
            return;
        }
        
        fetch(`/artist/start_session/${appointmentId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                this.showToast('Session Started', 'Session has been started', 'success');
                location.reload();
            } else {
                this.showToast('Error', data.message || 'Failed to start session', 'error');
            }
        })
        .catch(error => {
            console.error('Error starting session:', error);
            this.showToast('Error', 'Failed to start session', 'error');
        });
    }

    /**
     * Finish session
     */
    finishSession(appointmentId) {
        if (!confirm('Finish this session?')) {
            return;
        }
        
        fetch(`/artist/finish_session/${appointmentId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                this.showToast('Session Finished', 'Session has been completed', 'success');
                location.reload();
            } else {
                this.showToast('Error', data.message || 'Failed to finish session', 'error');
            }
        })
        .catch(error => {
            console.error('Error finishing session:', error);
            this.showToast('Error', 'Failed to finish session', 'error');
        });
    }

    /**
     * Filter command center jobs by status
     */
    filterJobs(status) {
        const jobCards = document.querySelectorAll('.command-job-card');
        const filterButtons = document.querySelectorAll('.command-filters .btn');
        
        // Update active filter button
        filterButtons.forEach(btn => {
            btn.classList.remove('btn-primary', 'btn-outline-primary');
            if (btn.id === `filter${status}`) {
                btn.classList.add('btn-primary');
                btn.classList.remove('btn-outline-primary');
            }
        });
        
        // Filter job cards
        jobCards.forEach(card => {
            if (status === 'all' || card.dataset.status === status) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    /**
     * Open calendar from command center
     */
    openCalendar() {
        window.open('/artist/calendar/', '_blank');
    }

    /**
     * Refresh dashboard from command center
     */
    refreshDashboard() {
        location.reload();
    }

    /**
     * Open settings panel
     */
    openSettings() {
        alert('Settings panel coming soon!');
    }

    /**
     * Toggle notifications
     */
    toggleNotifications() {
        alert('Notifications panel coming soon!');
    }

    /**
     * Show global notification toast
     */
    showToast(title, message, type = 'info') {
        const toastContainer = document.getElementById('globalToastContainer');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        
        if (toastContainer && toastTitle && toastMessage) {
            toastTitle.textContent = title;
            toastMessage.textContent = message;
            
            // Update toast styling based on type
            const toast = toastContainer.querySelector('.global-toast');
            toast.className = `global-toast toast-${type}`;
            
            toastContainer.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                toastContainer.style.display = 'none';
            }, 5000);
        }
    }

    /**
     * Update dashboard statistics
     */
    updateDashboardStats() {
        // Update counts (these would come from backend)
        const todayCount = document.getElementById('todayCount');
        const pendingCount = document.getElementById('pendingCount');
        const activeCount = document.getElementById('activeCount');
        const completedCount = document.getElementById('completedCount');
        const activeJobsCount = document.getElementById('activeJobsCount');
        
        if (todayCount) todayCount.textContent = '3';
        if (pendingCount) pendingCount.textContent = '2';
        if (activeCount) activeCount.textContent = '1';
        if (completedCount) completedCount.textContent = '5';
        if (activeJobsCount) activeJobsCount.textContent = '1';
    }

    /**
     * Initialize calendar functionality
     */
    initializeCalendar() {
        this.currentMonth = new Date();
        this.renderCalendar();
        this.setupCalendarEvents();
    }

    /**
     * Setup calendar event listeners
     */
    setupCalendarEvents() {
        // Navigation buttons
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentMonth.setMonth(this.currentMonth.getMonth() - 1);
            this.renderCalendar();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentMonth.setMonth(this.currentMonth.getMonth() + 1);
            this.renderCalendar();
        });

        // Date click handlers - THE MAIN FEATURE
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('calendar-day') && e.target.dataset.date) {
                const selectedDate = e.target.dataset.date;
                this.filterAppointmentsByDate(selectedDate);
            }
        });

        // Mobile offcanvas
        const mobileCalendarCanvas = document.getElementById('mobileCalendarCanvas');
        if (mobileCalendarCanvas) {
            mobileCalendarCanvas.addEventListener('show.bs.offcanvas', () => {
                this.renderMobileCalendar();
            });
        }
    }

    /**
     * Render calendar with vertical grid layout
     */
    renderCalendar() {
        const calendarGrid = document.getElementById('calendarGrid');
        const currentMonth = document.getElementById('currentMonth');
        
        if (!calendarGrid || !currentMonth) return;
        
        // Get current month and year
        const year = this.currentMonth.getFullYear();
        const month = this.currentMonth.getMonth();
        
        // Update month display
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December'];
        currentMonth.textContent = `${monthNames[month]} ${year}`;
        
        // Get first day of month and days in month
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        // Create calendar grid
        let calendarHTML = '<div class="calendar-grid">';
        
        // Add day headers
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        calendarHTML += '<div class="calendar-header">';
        dayNames.forEach(day => {
            calendarHTML += `<div class="calendar-day-name">${day}</div>`;
        });
        calendarHTML += '</div>';
        
        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            calendarHTML += '<div class="calendar-day other-month"></div>';
        }
        
        // Add days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const date = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isToday = this.isToday(year, month, day);
            const hasAppointments = this.hasAppointmentsForDate(date);
            
            calendarHTML += `
                <div class="calendar-day ${isToday ? 'today' : ''} ${hasAppointments ? 'has-appointments' : ''}" 
                     data-date="${date}">
                    ${day}
                    ${hasAppointments ? '<div class="appointment-dot"></div>' : ''}
                </div>
            `;
        }
        
        // Add empty cells for remaining days
        const totalCells = firstDay + daysInMonth;
        const remainingCells = totalCells % 7 === 0 ? 7 : 7 - (totalCells % 7);
        
        for (let i = 0; i < remainingCells; i++) {
            calendarHTML += '<div class="calendar-day other-month"></div>';
        }
        
        calendarHTML += '</div>';
        
        // Update calendar grid
        calendarGrid.innerHTML = calendarHTML;
    }
    
    /**
     * Check if a date is today
     */
    isToday(year, month, day) {
        const today = new Date();
        return year === today.getFullYear() && 
               month === today.getMonth() && 
               day === today.getDate();
    }
    
    /**
     * Check if date has appointments (mock function for now)
     */
    hasAppointmentsForDate(date) {
        // This would typically check against actual appointment data
        // For now, return some demo dates
        const demoDates = ['2025-03-15', '2025-03-20', '2025-03-25'];
        return demoDates.includes(date);
    }
    filterAppointmentsByDate(selectedDate) {
        // Visual feedback
        this.highlightSelectedDate(selectedDate);
        
        // Show loading state
        this.showCommandCenterLoading();
        
        // Make AJAX request to get filtered appointments
        fetch(`/artist/dashboard/?date=${selectedDate}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update command center with filtered appointments
            this.updateCommandCenterWithDate(data, selectedDate);
            
            // Update section title
            this.updateSectionTitle(selectedDate);
            
            // Hide loading state
            this.hideCommandCenterLoading();
        })
        .catch(error => {
            console.error('Error filtering appointments:', error);
            this.showToast('Error', 'Failed to load appointments for selected date', 'error');
            this.hideCommandCenterLoading();
        });
    }

    /**
     * Highlight selected date in calendar
     */
    highlightSelectedDate(selectedDate) {
        // Remove previous highlights
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('active-date', 'selected-date');
        });
        
        // Add highlight to selected date
        document.querySelectorAll('.calendar-day').forEach(day => {
            if (day.dataset.date === selectedDate) {
                day.classList.add('active-date', 'selected-date');
            }
        });
    }

    /**
     * Show loading state in command center
     */
    showCommandCenterLoading() {
        const commandCenter = document.querySelector('.command-center');
        const activeJobsList = document.querySelector('.active-jobs-list');
        
        if (commandCenter && activeJobsList) {
            commandCenter.style.opacity = '0.5';
            activeJobsList.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <div class="spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                    <p class="mb-0 mt-2">Loading appointments for selected date...</p>
                </div>
            `;
        }
    }

    /**
     * Hide loading state in command center
     */
    hideCommandCenterLoading() {
        const commandCenter = document.querySelector('.command-center');
        const activeJobsList = document.querySelector('.active-jobs-list');
        
        if (commandCenter && activeJobsList) {
            commandCenter.style.opacity = '1';
        }
    }

    /**
     * Update command center with filtered appointments
     */
    updateCommandCenterWithDate(appointments, selectedDate) {
        const activeJobsList = document.querySelector('.active-jobs-list');
        
        if (!activeJobsList) return;
        
        if (appointments.length === 0) {
            activeJobsList.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-calendar-x display-4"></i>
                    <p class="mb-0 mt-2">No appointments scheduled for ${selectedDate}</p>
                </div>
            `;
        } else {
            // Generate appointment cards
            let appointmentsHTML = '';
            appointments.forEach(appointment => {
                appointmentsHTML += this.generateAppointmentCard(appointment);
            });
            
            activeJobsList.innerHTML = appointmentsHTML;
        }
    }

    /**
     * Generate appointment card HTML
     */
    generateAppointmentCard(appointment) {
        const statusBadge = this.getStatusBadge(appointment.status);
        const actionButtons = this.generateActionButtons(appointment);
        
        return `
            <div class="appointment-card p-3 mb-3 border-start border-primary" data-status="${appointment.status}">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <span class="fw-bold text-primary">${appointment.client_name}</span>
                        <span class="badge bg-secondary ms-2">${appointment.time}</span>
                        ${statusBadge}
                    </div>
                    ${actionButtons}
                </div>
                
                <div class="mb-2">
                    <small class="text-muted">Service: ${appointment.service_name}</small>
                </div>
                
                ${appointment.notes ? `
                    <div class="mb-2">
                        <small class="text-muted">Notes: ${appointment.notes}</small>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Get status badge HTML
     */
    getStatusBadge(status) {
        const badges = {
            'Approved': '<span class="badge bg-primary">Confirmed</span>',
            'On-going': '<span class="badge bg-warning">In Progress</span>',
            'Completed': '<span class="badge bg-success">Completed</span>',
            'Cancelled': '<span class="badge bg-danger">Cancelled</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
    }

    /**
     * Generate action buttons
     */
    generateActionButtons(appointment) {
        let buttons = '';
        
        if (appointment.status === 'Approved') {
            buttons = `
                <div class="d-flex gap-2">
                    <button class="btn btn-primary btn-sm" onclick="commandCenter.startSession(${appointment.id})">
                        <i class="bi bi-play-circle me-1"></i>
                        Start Session
                    </button>
                    <button class="btn btn-outline-warning btn-sm" onclick="commandCenter.initiateReschedule(${appointment.id})">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Reschedule
                    </button>
                </div>
            `;
        } else if (appointment.status === 'On-going') {
            buttons = `
                <button class="btn btn-success btn-sm" onclick="commandCenter.finishSession(${appointment.id})">
                    <i class="bi bi-check-circle me-1"></i>
                    Finish & Sanitize
                </button>
            `;
        }
        
        return buttons;
    }

    /**
     * Update section title
     */
    updateSectionTitle(selectedDate) {
        const titleElement = document.querySelector('#current-view-title');
        if (titleElement) {
            const formattedDate = new Date(selectedDate).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            titleElement.textContent = `Schedule for ${formattedDate}`;
        }
    }

    /**
     * Mobile offcanvas toggle
     */
    toggleMobileCalendar() {
        const offcanvas = new bootstrap.Offcanvas(document.getElementById('mobileCalendarCanvas'));
        offcanvas.toggle();
    }

    /**
     * Refresh dashboard
     */
    refreshDashboard() {
        location.reload();
    }

    /**
     * Get CSRF token from cookies
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }

    /**
     * Update Finish button based on session duration
     */
    updateFinishButton(button, startTime) {
        const appointmentId = button.dataset.appointmentId;
        const statusEl = document.getElementById(`finish-status-${appointmentId}`);
        const btnText = button.querySelector('.btn-text');
        
        if (!startTime) {
            button.disabled = false;
            btnText.textContent = 'Finish & Sanitize';
            if (statusEl) statusEl.textContent = 'Session in progress...';
            return;
        }
        
        const startTimestamp = parseInt(startTime);
        const now = Math.floor(Date.now() / 1000);
        const elapsedMinutes = Math.floor((now - startTimestamp) / 60);
        
        button.disabled = elapsedMinutes < 15;
        button.className = 'btn btn-sm finish-session-btn';
        
        if (elapsedMinutes < 15) {
            button.classList.add('btn-secondary');
            btnText.textContent = `Finish in ${15 - elapsedMinutes} mins`;
            if (statusEl) statusEl.textContent = 'Minimum session time: 15 minutes (prevents accidental clicks)';
        } else {
            button.classList.add('btn-success');
            btnText.textContent = 'Finish & Sanitize';
            if (statusEl) statusEl.textContent = 'Session ready to finish';
        }
    }

    /**
     * Start a session
     */
    async startSession(appointmentId) {
        const button = document.querySelector(`[data-appointment-id="${appointmentId}"].start-session-btn`);
        if (!button) return;
        
        // Disable button and show loading
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split fa-spin me-1"></i> Starting...';
        
        try {
            const response = await fetch('/artist/start-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ appointment_id: appointmentId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Start session timer
                this.startSessionTimer(appointmentId, data.start_time);
                
                // Update UI
                this.updateAppointmentUI(appointmentId, 'On-going');
                
                // Show success message
                this.showNotification('Session started successfully!', 'success');
                
                // Refresh page after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
                
            } else {
                throw new Error(data.message || 'Failed to start session');
            }
            
        } catch (error) {
            console.error('Start session error:', error);
            this.showNotification(error.message, 'error');
            
            // Restore button
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-play-circle me-1"></i> Start Session';
        }
    }

    /**
     * Finish a session
     */
    async finishSession(appointmentId) {
        const button = document.querySelector(`[data-appointment-id="${appointmentId}"].finish-session-btn`);
        if (!button) return;
        
        // Disable button and show loading
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split fa-spin me-1"></i> Finishing...';
        
        try {
            const response = await fetch('/artist/finish-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ appointment_id: appointmentId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Stop session timer
                this.stopSessionTimer(appointmentId);
                
                // Start sanitation timer
                this.startSanitationTimer();
                
                // Update UI
                this.updateAppointmentUI(appointmentId, 'Finished');
                
                // Show success message
                this.showNotification('Session completed! Sanitation timer started.', 'success');
                
                // Refresh page after a short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
                
            } else {
                throw new Error(data.message || 'Failed to finish session');
            }
            
        } catch (error) {
            console.error('Finish session error:', error);
            this.showNotification(error.message, 'error');
            
            // Restore button
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-check-circle me-1"></i> Finish & Sanitize';
        }
    }

    /**
     * Start session timer
     */
    startSessionTimer(appointmentId, startTime) {
        const timerEl = document.getElementById(`timer-${appointmentId}`);
        const progressEl = document.getElementById(`progress-${appointmentId}`);
        
        if (!timerEl || !progressEl) return;
        
        const startTimestamp = new Date(startTime).getTime();
        
        this.sessionTimers.set(appointmentId, setInterval(() => {
            const now = Date.now();
            const elapsed = now - startTimestamp;
            const elapsedSeconds = Math.floor(elapsed / 1000);
            const elapsedMinutes = Math.floor(elapsedSeconds / 60);
            
            // Format timer display
            const hours = Math.floor(elapsedSeconds / 3600);
            const minutes = Math.floor((elapsedSeconds % 3600) / 60);
            const seconds = elapsedSeconds % 60;
            
            timerEl.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Update progress bar (40 minutes = 100%)
            const progressPercent = Math.min((elapsedMinutes / 40) * 100, 100);
            progressEl.style.width = `${progressPercent}%`;
            
            // Change color if overtime
            if (elapsedMinutes > 40) {
                progressEl.className = 'progress-bar bg-warning';
            }
            if (elapsedMinutes > 50) {
                progressEl.className = 'progress-bar bg-danger';
            }
            
        }, 1000));
    }

    /**
     * Stop session timer
     */
    stopSessionTimer(appointmentId) {
        if (this.sessionTimers.has(appointmentId)) {
            clearInterval(this.sessionTimers.get(appointmentId));
            this.sessionTimers.delete(appointmentId);
        }
    }

    /**
     * Initialize sanitation timer
     */
    initializeSanitationTimer() {
        const countdownEl = document.getElementById('sanitation-countdown');
        const progressEl = document.getElementById('sanitation-progress');
        
        if (!countdownEl || !progressEl) return;
        
        // Check if artist is in cleaning state
        const artistStatus = document.querySelector('[data-artist-status]');
        if (!artistStatus || artistStatus.dataset.artistStatus !== 'Cleaning') return;
        
        this.startSanitationTimer();
    }

    /**
     * Start sanitation timer (20 minutes)
     */
    startSanitationTimer() {
        const countdownEl = document.getElementById('sanitation-countdown');
        const progressEl = document.getElementById('sanitation-progress');
        
        if (!countdownEl || !progressEl) return;
        
        let remainingSeconds = 20 * 60; // 20 minutes
        
        // Clear existing timer
        if (this.sanitationTimer) {
            clearInterval(this.sanitationTimer);
        }
        
        this.sanitationTimer = setInterval(() => {
            remainingSeconds--;
            
            const minutes = Math.floor(remainingSeconds / 60);
            const seconds = remainingSeconds % 60;
            
            countdownEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            const progressPercent = (remainingSeconds / (20 * 60)) * 100;
            progressEl.style.width = `${progressPercent}%`;
            
            if (remainingSeconds <= 0) {
                clearInterval(this.sanitationTimer);
                this.showNotification('Sanitation complete! You are now available.', 'success');
                
                // Update artist status
                this.updateArtistStatus('Available');
                
                // Refresh page
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        }, 1000);
    }

    /**
     * Start periodic timing checks
     */
    startTimingChecks() {
        // Update button states every 30 seconds
        setInterval(() => {
            document.querySelectorAll('.start-session-btn').forEach(button => {
                const appointmentTime = button.dataset.appointmentTime;
                const appointmentDate = button.dataset.appointmentDate;
                this.updateStartButton(button, appointmentTime, appointmentDate);
            });
            
            document.querySelectorAll('.reschedule-btn').forEach(button => {
                const appointmentDate = button.dataset.appointmentDate;
                const appointmentTime = button.dataset.appointmentTime;
                this.updateRescheduleButton(button, appointmentDate, appointmentTime);
            });
            
            document.querySelectorAll('.finish-session-btn').forEach(button => {
                const startTime = button.dataset.startTime;
                this.updateFinishButton(button, startTime);
            });
        }, 30000);
    }

    /**
     * Initialize WebSocket for real-time updates
     */
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/artist/`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('Artist WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => {
                    this.initializeWebSocket();
                }, 5000);
            };
            
        } catch (error) {
            console.error('WebSocket initialization error:', error);
        }
    }

    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'CLIENT_UPDATE':
                // Handle client status updates
                console.log('Client update:', data);
                break;
            case 'SYSTEM_NOTIFICATION':
                this.showNotification(data.message, data.level || 'info');
                break;
            default:
                console.log('Unknown WebSocket message:', data);
        }
    }

    /**
     * Update appointment UI
     */
    updateAppointmentUI(appointmentId, newStatus) {
        const appointmentEl = document.getElementById(`appointment-${appointmentId}`);
        if (!appointmentEl) return;
        
        // Broadcast status update via WebSocket
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'STATUS_UPDATE',
                appointment_id: appointmentId,
                new_status: newStatus,
                timestamp: new Date().toISOString()
            }));
        }
    }

    /**
     * Update artist status
     */
    updateArtistStatus(status) {
        // This would typically update the database via API
        console.log('Updating artist status to:', status);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .session-timer {
        font-family: 'Courier New', monospace;
    }
    
    .command-buttons {
        border-top: 1px solid #e9ecef;
        padding-top: 1rem;
    }
    
    .sanitation-timer .progress {
        background-color: #e9ecef;
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CommandCenter();
});

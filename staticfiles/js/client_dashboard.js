/**
 * Client Dashboard - Real-time Session Status Updates
 * Handles WebSocket connections and progress stepper updates
 */

class ClientDashboard {
    constructor() {
        this.websocket = null;
        this.appointments = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.init();
    }

    init() {
        this.initializeWebSocket();
        this.initializeAppointmentTracking();
        this.initializeRescheduleLocks();
        this.startPeriodicUpdates();
    }

    /**
     * Initialize WebSocket connection for real-time updates
     */
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/client/`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('Client WebSocket connected');
                this.reconnectAttempts = 0;
                
                // Send initial subscription message
                this.websocket.send(JSON.stringify({
                    type: 'SUBSCRIBE',
                    client_id: this.getClientId()
                }));
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
                this.attemptReconnect();
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
            case 'STATUS_UPDATE':
                this.handleStatusUpdate(data);
                break;
            case 'SESSION_STARTED':
                this.handleSessionStarted(data);
                break;
            case 'SESSION_COMPLETED':
                this.handleSessionCompleted(data);
                break;
            case 'ARTIST_NOTIFICATION':
                this.handleArtistNotification(data);
                break;
            default:
                console.log('Unknown WebSocket message:', data);
        }
    }

    /**
     * Handle appointment status updates
     */
    handleStatusUpdate(data) {
        const appointmentId = data.appointment_id;
        const newStatus = data.new_status;
        
        // Update progress stepper
        this.updateProgressStepper(appointmentId, newStatus);
        
        // Update status bar
        this.updateStatusBar(appointmentId, newStatus, data.message);
        
        // Show notification
        this.showNotification(data.message, 'info');
        
        // Play notification sound (if available)
        this.playNotificationSound();
    }

    /**
     * Handle session started event
     */
    handleSessionStarted(data) {
        const appointmentId = data.appointment_id;
        const startTime = data.start_time;
        
        // Update progress stepper to "In Progress"
        this.updateProgressStepper(appointmentId, 'On-going');
        
        // Update status bar with session info
        this.updateSessionStartTime(appointmentId, startTime);
        
        // Show prominent notification
        this.showNotification('Your session has started! Please head inside.', 'success');
        
        // Play notification sound
        this.playNotificationSound();
        
        // Redirect to session view if on appointments page
        if (window.location.pathname.includes('appointments')) {
            this.highlightActiveAppointment(appointmentId);
        }
    }

    /**
     * Handle session completed event
     */
    handleSessionCompleted(data) {
        const appointmentId = data.appointment_id;
        const ratingUrl = data.rating_url;
        
        // Update progress stepper to "Completed"
        this.updateProgressStepper(appointmentId, 'Finished');
        
        // Show completion notification
        this.showNotification('Session completed! Please leave a review.', 'success');
        
        // Redirect to rating page after delay
        setTimeout(() => {
            if (ratingUrl) {
                window.location.href = ratingUrl;
            }
        }, 3000);
    }

    /**
     * Update progress stepper UI
     */
    updateProgressStepper(appointmentId, status) {
        const stepperElements = document.querySelectorAll(`[data-appointment-id="${appointmentId}"] .progress-stepper`);
        
        stepperElements.forEach(stepper => {
            const items = stepper.querySelectorAll('.stepper-item');
            
            // Reset all items
            items.forEach(item => {
                item.classList.remove('active', 'completed');
                item.classList.add('pending');
            });
            
            // Update based on status
            if (status === 'Approved') {
                items[0].classList.add('completed');
                items[1].classList.add('active');
            } else if (status === 'On-going') {
                items[0].classList.add('completed');
                items[1].classList.add('active');
            } else if (status === 'Finished') {
                items[0].classList.add('completed');
                items[1].classList.add('completed');
                items[2].classList.add('active');
            }
        });
    }

    /**
     * Update status bar
     */
    updateStatusBar(appointmentId, status, message) {
        const statusBar = document.getElementById(`status-bar-${appointmentId}`);
        if (!statusBar) return;
        
        let alertHtml = '';
        
        if (status === 'On-going') {
            alertHtml = `
                <div class="alert alert-info py-2">
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <i class="bi bi-play-circle me-2"></i>
                            <strong>Your session is in progress!</strong>
                            <div class="small mt-1">${message}</div>
                        </div>
                        <div class="spinner-border spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                </div>
            `;
        } else if (status === 'Approved') {
            alertHtml = `
                <div class="alert alert-success py-2">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-calendar-check me-2"></i>
                        <div>
                            <strong>Appointment Confirmed</strong>
                            <div class="small">${message}</div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        statusBar.innerHTML = alertHtml;
    }

    /**
     * Update session start time display
     */
    updateSessionStartTime(appointmentId, startTime) {
        const startTimeEl = document.getElementById(`session-start-${appointmentId}`);
        if (startTimeEl && startTime) {
            const date = new Date(startTime);
            startTimeEl.textContent = date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    /**
     * Highlight active appointment
     */
    highlightActiveAppointment(appointmentId) {
        // Remove existing highlights
        document.querySelectorAll('.highlight-card').forEach(card => {
            card.style.border = '';
        });
        
        // Add highlight to active appointment
        const activeCard = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
        if (activeCard) {
            activeCard.style.border = '3px solid var(--olive-beige)';
            activeCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Initialize 48-hour reschedule lock logic
     */
    initializeRescheduleLocks() {
        document.querySelectorAll('.reschedule-btn').forEach(button => {
            const appointmentDateTime = button.dataset.appointmentDatetime;
            if (appointmentDateTime) {
                this.updateRescheduleLock(button, appointmentDateTime);
            }
        });
    }

    /**
     * Update reschedule button based on 48-hour lock
     */
    updateRescheduleLock(button, appointmentDateTime) {
        const now = new Date();
        const appointmentDate = new Date(appointmentDateTime);
        
        // Calculate days difference
        const timeDiff = appointmentDate - now;
        const diffInDays = timeDiff / (1000 * 3600 * 24);
        
        const rescheduleText = button.querySelector('.reschedule-text');
        const originalText = rescheduleText ? rescheduleText.textContent : 'Reschedule';
        
        if (diffInDays >= 2) {
            // More than 48 hours: Allow rescheduling
            button.disabled = false;
            button.style.opacity = '1';
            button.style.cursor = 'pointer';
            if (rescheduleText) rescheduleText.textContent = originalText;
            button.title = 'Click to reschedule this appointment';
            
        } else if (diffInDays >= 0) {
            // Within 48 hours: Locked with explanation
            button.disabled = true;
            button.style.opacity = '0.6';
            button.style.cursor = 'not-allowed';
            if (rescheduleText) rescheduleText.textContent = 'Locked';
            button.title = `Rescheduling is only available up to 48 hours before your appointment (${Math.ceil(diffInDays * 24)} hours remaining)`;
            
            // Add contact artist option
            this.addContactArtistOption(button);
            
        } else {
            // Past appointment: Cannot reschedule
            button.disabled = true;
            button.style.opacity = '0.5';
            button.style.cursor = 'not-allowed';
            if (rescheduleText) rescheduleText.textContent = 'Expired';
            button.title = 'Cannot reschedule past appointments';
        }
    }

    /**
     * Add contact artist option for locked reschedule buttons
     */
    addContactArtistOption(rescheduleButton) {
        const parent = rescheduleButton.parentElement;
        
        // Check if contact option already exists
        if (parent.querySelector('.contact-artist-btn')) {
            return;
        }
        
        // Remove reschedule button from DOM (not just disable)
        rescheduleButton.style.display = 'none';
        
        // Create contact artist button that opens modal
        const contactBtn = document.createElement('button');
        contactBtn.className = 'appointment-btn contact-artist-btn';
        contactBtn.style.background = 'var(--olive-beige)';
        contactBtn.style.color = 'white';
        contactBtn.innerHTML = '<i class="bi bi-telephone"></i> Contact Artist';
        contactBtn.setAttribute('data-bs-toggle', 'modal');
        contactBtn.setAttribute('data-bs-target', '#contactArtistModal');
        
        // Copy data attributes from reschedule button
        contactBtn.setAttribute('data-id', rescheduleButton.dataset.id);
        contactBtn.setAttribute('data-service', rescheduleButton.dataset.service);
        contactBtn.setAttribute('data-artist', rescheduleButton.dataset.artist);
        contactBtn.setAttribute('data-date', rescheduleButton.dataset.date);
        contactBtn.setAttribute('data-time', rescheduleButton.dataset.time);
        
        // Insert after reschedule button
        parent.insertBefore(contactBtn, rescheduleButton.nextSibling);
    }

    /**
     * Initialize appointment tracking
     */
    initializeAppointmentTracking() {
        // Find all appointment cards and store their data
        document.querySelectorAll('.highlight-card').forEach(card => {
            const appointmentId = card.dataset.appointmentId;
            if (appointmentId) {
                this.appointments.set(appointmentId, {
                    element: card,
                    status: this.getAppointmentStatus(card)
                });
            }
        });
    }

    /**
     * Get appointment status from DOM
     */
    getAppointmentStatus(card) {
        const statusBadge = card.querySelector('.status-badge');
        return statusBadge ? statusBadge.textContent.trim() : 'Unknown';
    }

    /**
     * Start periodic updates for checking appointment status
     */
    startPeriodicUpdates() {
        // Check for late appointments every 2 minutes
        setInterval(() => {
            this.checkForLateAppointments();
        }, 120000);
        
        // Update session timers every 30 seconds
        setInterval(() => {
            this.updateSessionTimers();
        }, 30000);
        
        // Update reschedule locks every 5 minutes
        setInterval(() => {
            this.updateRescheduleLocks();
        }, 300000);
    }

    /**
     * Update reschedule locks periodically
     */
    updateRescheduleLocks() {
        document.querySelectorAll('.reschedule-btn').forEach(button => {
            const appointmentDateTime = button.dataset.appointmentDatetime;
            if (appointmentDateTime) {
                this.updateRescheduleLock(button, appointmentDateTime);
            }
        });
    }

    /**
     * Check for appointments that should have started but haven't
     */
    checkForLateAppointments() {
        const now = new Date();
        
        this.appointments.forEach((appointment, appointmentId) => {
            if (appointment.status === 'Approved') {
                // Check if appointment is more than 10 minutes late
                const appointmentTime = this.getAppointmentTime(appointment.element);
                if (appointmentTime) {
                    const timeDiff = now - appointmentTime;
                    const minutesLate = Math.floor(timeDiff / (1000 * 60));
                    
                    if (minutesLate > 10) {
                        this.showLateAppointmentWarning(appointmentId, minutesLate);
                    }
                }
            }
        });
    }

    /**
     * Get appointment time from DOM
     */
    getAppointmentTime(card) {
        const timeEl = card.querySelector('.appointment-time');
        if (timeEl) {
            const timeText = timeEl.textContent.trim();
            const today = new Date();
            const [time, period] = timeText.split(' ');
            const [hours, minutes] = time.split(':').map(Number);
            
            let hour24 = hours;
            if (period === 'PM' && hours !== 12) hour24 += 12;
            if (period === 'AM' && hours === 12) hour24 = 0;
            
            return new Date(today.getFullYear(), today.getMonth(), today.getDate(), hour24, minutes);
        }
        return null;
    }

    /**
     * Show warning for late appointments
     */
    showLateAppointmentWarning(appointmentId, minutesLate) {
        const statusBar = document.getElementById(`status-bar-${appointmentId}`);
        if (statusBar && !statusBar.querySelector('.late-warning')) {
            const warningHtml = `
                <div class="alert alert-warning py-2 late-warning">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <div>
                            <strong>Appointment is ${minutesLate} minutes late</strong>
                            <div class="small">You can contact the artist if needed.</div>
                            <button class="btn btn-sm btn-outline-warning mt-1" onclick="clientDashboard.contactArtist('${appointmentId}')">
                                <i class="bi bi-telephone me-1"></i> Contact Artist
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            statusBar.insertAdjacentHTML('beforeend', warningHtml);
        }
    }

    /**
     * Update session timers
     */
    updateSessionTimers() {
        document.querySelectorAll('[id^="session-start-"]').forEach(el => {
            const appointmentId = el.id.replace('session-start-', '');
            if (el.textContent !== '--:--') {
                // Could add elapsed time calculation here
                console.log(`Session ${appointmentId} is active`);
            }
        });
    }

    /**
     * Attempt to reconnect WebSocket
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, 5000 * this.reconnectAttempts); // Exponential backoff
        } else {
            console.log('Max reconnection attempts reached');
            this.showNotification('Connection lost. Please refresh the page.', 'warning');
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
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
     * Play notification sound
     */
    playNotificationSound() {
        try {
            // Create a simple beep sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800; // 800Hz beep
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (error) {
            console.log('Could not play notification sound:', error);
        }
    }

    /**
     * Get client ID (simplified version)
     */
    getClientId() {
        // In a real implementation, this would get the actual client ID
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Contact artist (placeholder function)
     */
    contactArtist(appointmentId) {
        // This would open a contact modal or redirect to contact page
        this.showNotification('Contact feature coming soon!', 'info');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.clientDashboard = new ClientDashboard();
});

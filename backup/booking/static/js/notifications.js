// Notification Management System - Prevent re-display on refresh
class NotificationManager {
    constructor() {
        this.storageKey = 'pp_notifications_shown';
        this.init();
    }

    init() {
        // Clear any existing notifications from storage on page load
        this.clearShownNotifications();
        
        // Process current messages
        this.processCurrentMessages();
        
        // Set up auto-cleanup
        this.setupAutoCleanup();
    }

    // Get current page identifier
    getPageIdentifier() {
        return window.location.pathname + window.location.search;
    }

    // Clear shown notifications for current page
    clearShownNotifications() {
        const shown = this.getShownNotifications();
        const currentPage = this.getPageIdentifier();
        if (shown[currentPage]) {
            delete shown[currentPage];
            localStorage.setItem(this.storageKey, JSON.stringify(shown));
        }
    }

    // Get shown notifications from storage
    getShownNotifications() {
        try {
            return JSON.parse(localStorage.getItem(this.storageKey) || '{}');
        } catch {
            return {};
        }
    }

    // Mark notification as shown
    markAsShown(message, tags, page) {
        const shown = this.getShownNotifications();
        if (!shown[page]) {
            shown[page] = [];
        }
        
        // Create unique identifier for this message
        const messageId = this.createMessageId(message, tags);
        if (!shown[page].includes(messageId)) {
            shown[page].push(messageId);
            localStorage.setItem(this.storageKey, JSON.stringify(shown));
        }
    }

    // Create unique message ID
    createMessageId(message, tags) {
        return btoa(message + tags).substring(0, 20);
    }

    // Check if notification was already shown
    wasAlreadyShown(message, tags, page) {
        const shown = this.getShownNotifications();
        const messageId = this.createMessageId(message, tags);
        return shown[page] && shown[page].includes(messageId);
    }

    // Process current Django messages
    processCurrentMessages() {
        const toasts = document.querySelectorAll('.pp-toast');
        const alerts = document.querySelectorAll('.alert');
        const currentPage = this.getPageIdentifier();

        // Process toasts
        toasts.forEach(toast => {
            const message = toast.querySelector('.pp-toast-body')?.textContent?.trim();
            const tags = this.getToastTags(toast);
            
            if (message && !this.wasAlreadyShown(message, tags, currentPage)) {
                this.markAsShown(message, tags, currentPage);
                this.showNotification(toast);
            } else {
                // Hide if already shown
                toast.style.display = 'none';
            }
        });

        // Process alerts
        alerts.forEach(alert => {
            const message = alert.textContent?.trim();
            const tags = this.getAlertTags(alert);
            
            if (message && !this.wasAlreadyShown(message, tags, currentPage)) {
                this.markAsShown(message, tags, currentPage);
                this.showAlert(alert);
            } else {
                // Hide if already shown
                alert.style.display = 'none';
            }
        });
    }

    // Get toast tags
    getToastTags(toast) {
        const classes = toast.className.split(' ');
        const tagClass = classes.find(cls => cls.startsWith('pp-toast-'));
        return tagClass ? tagClass.replace('pp-toast-', '') : 'info';
    }

    // Get alert tags
    getAlertTags(alert) {
        const classes = alert.className.split(' ');
        const tagClass = classes.find(cls => cls.startsWith('alert-'));
        return tagClass ? tagClass.replace('alert-', '') : 'info';
    }

    // Show notification with animation
    showNotification(toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 100);
    }

    // Show alert with animation
    showAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        alert.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            alert.style.opacity = '1';
            alert.style.transform = 'translateY(0)';
        }, 100);
    }

    // Setup auto-cleanup
    setupAutoCleanup() {
        // Clean up old notifications (older than 1 hour)
        const shown = this.getShownNotifications();
        const now = Date.now();
        const oneHour = 60 * 60 * 1000;
        
        Object.keys(shown).forEach(page => {
            if (shown[page].timestamp && (now - shown[page].timestamp) > oneHour) {
                delete shown[page];
            }
        });
        
        localStorage.setItem(this.storageKey, JSON.stringify(shown));
    }

    // Manual clear all notifications
    clearAll() {
        localStorage.removeItem(this.storageKey);
    }
}

// Initialize notification manager
document.addEventListener('DOMContentLoaded', function() {
    window.notificationManager = new NotificationManager();
    
    // Add global function to clear notifications if needed
    window.clearNotifications = function() {
        window.notificationManager.clearAll();
        console.log('All notifications cleared from storage');
    };
});

// Handle page visibility changes (tab switching, etc.)
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // When page becomes visible again, ensure notifications are processed correctly
        setTimeout(() => {
            if (window.notificationManager) {
                window.notificationManager.processCurrentMessages();
            }
        }, 100);
    }
});

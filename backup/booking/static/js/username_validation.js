/**
 * Username Validation and Formatting
 * Real-time username validation with security checks
 */

class UsernameValidator {
    constructor() {
        this.touchedFields = new WeakSet();
        this.init();
    }

    init() {
        // Find all username inputs
        const usernameInputs = document.querySelectorAll('input[name="username"]');
        
        usernameInputs.forEach(input => {
            // Add event listeners
            input.addEventListener('input', this.formatUsername.bind(this));
            input.addEventListener('blur', this.validateUsername.bind(this));
            input.addEventListener('focus', this.onFocus.bind(this));
        });
    }

    /**
     * Format username as user types (convert to lowercase)
     */
    formatUsername(event) {
        const input = event.target;
        
        // Convert to lowercase for consistency
        input.value = input.value.toLowerCase();
        
        // Remove invalid characters (only allow alphanumeric, dots, underscores)
        const cleanValue = input.value.replace(/[^a-z0-9._]/g, '');
        input.value = cleanValue;
        
        // Store clean value for validation
        input.dataset.cleanValue = cleanValue;

        // Only do real-time validation if touched (exactly like First Name)
        if (!this.touchedFields.has(input)) return;

        // Re-validate to show real-time feedback (exactly like First Name)
        this.validateUsername(input);
    }

    /**
     * Validate username on blur
     */
    validateUsername(event) {
        const input = event.target;
        const username = input.dataset.cleanValue || input.value.trim();
        
        // Only validate if field has been touched
        if (!this.touchedFields.has(input)) return;

        // Remove previous validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        // Remove submit-required error if field now has content
        if (username.length > 0) {
            const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
            if (submitReqFeedback) {
                submitReqFeedback.remove();
            }
        }
        
        if (!username) {
            this.showValidation(input, 'Username is required', false);
            return;
        }
        
        // Check length constraints
        if (username.length < 3) {
            this.showValidation(input, 'Username must be at least 3 characters long', false);
            return;
        }
        
        if (username.length > 15) {
            this.showValidation(input, 'Username must be no more than 15 characters long', false);
            return;
        }
        
        // Check allowed characters
        if (!/^[a-z0-9._]+$/.test(username)) {
            return;
        }
        
        // Check for invalid patterns
        if (username.startsWith('.') || username.startsWith('_')) {
            this.showValidation(input, 'Username cannot start with a dot or underscore', false);
            return;
        }
        
        if (username.endsWith('.') || username.endsWith('_')) {
            this.showValidation(input, 'Username cannot end with a dot or underscore', false);
            return;
        }
        
        if (username.includes('..') || username.includes('__')) {
            this.showValidation(input, 'Username cannot contain consecutive dots or underscores', false);
            return;
        }
        
        // Check for reserved usernames
        if (this.isReservedUsername(username)) {
            this.showValidation(input, 'This username is reserved and cannot be used', false);
            return;
        }
        
        // Check for suspicious patterns
        if (this.isSuspiciousUsername(username)) {
            this.showValidation(input, 'This username is not allowed', false);
            return;
        }
        
        // Valid username - remove success message and submit-required error
        this.showValidation(input, '', true);
        
        // Remove submit-required error when field becomes valid
        const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
        if (submitReqFeedback) {
            submitReqFeedback.remove();
        }
    }

    /**
     * Check if username is reserved
     */
    isReservedUsername(username) {
        const reservedUsernames = [
            'admin', 'administrator', 'root', 'staff', 'moderator', 'support', 'help',
            'system', 'api', 'www', 'mail', 'email', 'info', 'contact', 'about',
            'terms', 'privacy', 'policy', 'legal', 'copyright', 'trademark',
            'login', 'logout', 'register', 'signup', 'signin', 'signout',
            'profile', 'account', 'settings', 'dashboard', 'home', 'index',
            'search', 'browse', 'explore', 'discover', 'trending', 'popular',
            'new', 'latest', 'recent', 'featured', 'recommended', 'suggested',
            'nailtech', 'appointment', 'booking', 'service', 'artist', 'client',
            'user', 'users', 'member', 'members', 'guest', 'anonymous',
            'null', 'undefined', 'test', 'demo', 'sample', 'example', 'placeholder',
            'bot', 'robot', 'crawler', 'spider', 'scraper', 'automated',
            'security', 'verify', 'confirm', 'activate', 'validate', 'authenticate',
            'forgot', 'reset', 'recover', 'change', 'update', 'edit', 'delete',
            'create', 'add', 'remove', 'upload', 'download', 'export', 'import',
            'backup', 'restore', 'archive', 'delete', 'remove', 'clear', 'clean',
            'debug', 'dev', 'development', 'staging', 'production', 'live',
            'beta', 'alpha', 'preview', 'demo', 'trial', 'free', 'premium',
            'pro', 'plus', 'gold', 'silver', 'bronze', 'basic', 'advanced',
            'webmaster', 'owner', 'founder', 'creator', 'author', 'editor',
            'manager', 'director', 'executive', 'president', 'ceo', 'cfo', 'cto',
            'sales', 'marketing', 'advertising', 'promotion', 'campaign', 'offer',
            'discount', 'coupon', 'deal', 'special', 'limited', 'exclusive',
            'news', 'blog', 'forum', 'community', 'social', 'network', 'group',
            'chat', 'message', 'notification', 'alert', 'warning', 'error',
            'success', 'failure', 'pending', 'processing', 'completed', 'cancelled',
            'active', 'inactive', 'online', 'offline', 'available', 'busy',
            'open', 'closed', 'public', 'private', 'hidden', 'visible', 'secret',
            'temporary', 'permanent', 'fixed', 'mobile', 'desktop', 'tablet',
            'phone', 'email', 'sms', 'call', 'voice', 'video', 'audio',
            'image', 'photo', 'picture', 'video', 'document', 'file', 'download',
            'upload', 'share', 'like', 'follow', 'subscribe', 'unsubscribe',
            'comment', 'review', 'rating', 'feedback', 'report', 'flag',
            'spam', 'abuse', 'harassment', 'bullying', 'inappropriate',
            'illegal', 'fraud', 'scam', 'phishing', 'malware', 'virus',
            'hack', 'crack', 'exploit', 'vulnerability', 'security', 'breach',
            'data', 'information', 'content', 'media', 'assets', 'resources',
            'tools', 'utilities', 'features', 'functions', 'options', 'preferences',
            'configuration', 'setup', 'installation', 'maintenance', 'upgrade', 'update',
            'version', 'release', 'patch', 'hotfix', 'bug', 'issue', 'problem',
            'solution', 'fix', 'repair', 'restore', 'recover', 'backup', 'sync'
        ];
        
        return reservedUsernames.includes(username);
    }

    /**
     * Check for suspicious username patterns
     */
    isSuspiciousUsername(username) {
        // Check for patterns that might indicate automated accounts
        const suspiciousPatterns = [
            /^[0-9]+$/,           // All numbers
            /^[._]+$/,               // Only special characters
            /admin.*/,                // Starts with admin
            /.*admin$/,                // Ends with admin
            /.*admin.*/,                // Contains admin
            /test.*/,                 // Starts with test
            /.*test$/,                 // Ends with test
            /.*test.*/,                 // Contains test
            /demo.*/,                 // Starts with demo
            /.*demo$/,                 // Ends with demo
            /.*demo.*/,                 // Contains demo
            /bot.*/,                  // Starts with bot
            /.*bot$/,                  // Ends with bot
            /.*bot.*/,                  // Contains bot
            /spam.*/,                 // Starts with spam
            /.*spam$/,                 // Ends with spam
            /.*spam.*/                  // Contains spam
        ];
        
        for (const pattern of suspiciousPatterns) {
            if (pattern.test(username)) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Show validation feedback
     */
    showValidation(input, message, isValid) {
        // Remove existing feedback
        const existingFeedback = input.parentNode.querySelector('.username-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Add validation class
        if (isValid) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
            // Don't show success message - just remove feedback
            return;
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        }
        
        // Create feedback element only for errors
        const feedback = document.createElement('div');
        feedback.className = `username-feedback invalid-feedback`;
        feedback.textContent = message;
        
        // Insert feedback after input
        input.parentNode.insertBefore(feedback, input.nextSibling);
    }

    /**
     * Handle focus event
     */
    onFocus(event) {
        const input = event.target;
        // Mark field as touched on focus (exactly like First Name)
        this.touchedFields.add(input);
    }

    /**
     * Get clean username for form submission
     */
    static getCleanUsername(input) {
        return input.dataset.cleanValue || input.value.trim().toLowerCase();
    }

    /**
     * Generate username suggestions
     */
    static generateSuggestions(baseUsername) {
        if (!baseUsername) {
            return [];
        }
        
        const base = baseUsername.toLowerCase().replace(/[^a-z0-9._]/g, '').substring(0, 10);
        const suggestions = [];
        
        // Generate variations
        suggestions.push(`${base}01`);
        suggestions.push(`${base}_2024`);
        suggestions.push(`${base}.user`);
        suggestions.push(`user_${base}`);
        suggestions.push(`${base}_official`);
        
        // Add numbers if no special chars
        if (!base.includes('.') && !base.includes('_')) {
            suggestions.push(`${base}_${2024}`);
            suggestions.push(`${base}${123}`);
        }
        
        // Filter out reserved names and duplicates
        const filteredSuggestions = [];
        for (const suggestion of suggestions) {
            if (!this.isReservedUsername(suggestion) && 
                suggestion.length >= 3 && 
                suggestion.length <= 15 &&
                !filteredSuggestions.includes(suggestion)) {
                filteredSuggestions.push(suggestion);
            }
        }
        
        return filteredSuggestions.slice(0, 5);  // Return top 5 suggestions
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new UsernameValidator();
});

// Export for use in other scripts
window.UsernameValidator = UsernameValidator;

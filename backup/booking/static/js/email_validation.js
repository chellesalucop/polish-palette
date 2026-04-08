/**
 * Email Validation and Formatting
 * Real-time email validation with security checks
 */

class EmailValidator {
    constructor() {
        this.touchedFields = new WeakSet();
        this.init();
    }

    init() {
        // Find all email inputs
        const emailInputs = document.querySelectorAll('input[type="email"]');
        
        emailInputs.forEach(input => {
            // Add event listeners
            input.addEventListener('input', this.formatEmail.bind(this));
            input.addEventListener('blur', this.validateEmail.bind(this));
            input.addEventListener('focus', this.onFocus.bind(this));
        });
    }

    /**
     * Format email as user types (convert to lowercase)
     */
    formatEmail(event) {
        const input = event.target;
        
        // Convert to lowercase for consistency
        input.value = input.value.toLowerCase();
        
        // Store clean value for validation
        input.dataset.cleanValue = input.value.trim();

        // Only do real-time validation if touched (exactly like First Name)
        if (!this.touchedFields.has(input)) return;

        // Re-validate to show real-time feedback (exactly like First Name)
        this.validateEmail(input);
    }

    /**
     * Validate email on blur
     */
    validateEmail(event) {
        const input = event.target;
        const email = input.dataset.cleanValue || input.value.trim();
        
        // Only validate if field has been touched
        if (!this.touchedFields.has(input)) return;

        // Remove previous validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        // Remove submit-required error if field now has content
        if (email.length > 0) {
            const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
            if (submitReqFeedback) {
                submitReqFeedback.remove();
            }
        }
        
        if (!email) {
            this.showValidation(input, 'Email address is required', false);
            return;
        }
        
        // Basic email format check
        const emailRegex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/;
        if (!emailRegex.test(email)) {
            this.showValidation(input, 'Please enter a valid email address (e.g., user@domain.com)', false);
            return;
        }
        
        // Check for common email structure issues
        const validation = this.validateEmailStructure(email);
        if (!validation.isValid) {
            this.showValidation(input, validation.message, false);
            return;
        }
        
        // Check for disposable email domains
        if (this.isDisposableEmail(email)) {
            this.showValidation(input, 'Disposable email addresses are not allowed. Please use a permanent email address.', false);
            return;
        }
        
        // Valid email - remove success message and submit-required error
        this.showValidation(input, '', true);
        
        // Remove submit-required error when field becomes valid
        const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
        if (submitReqFeedback) {
            submitReqFeedback.remove();
        }
    }

    /**
     * Validate email structure
     */
    validateEmailStructure(email) {
        // Split into local and domain parts
        const parts = email.split('@');
        if (parts.length !== 2) {
            return { isValid: false, message: 'Email must contain exactly one @ symbol' };
        }
        
        const [localPart, domain] = parts;
        
        // Check local part
        if (!localPart) {
            return { isValid: false, message: 'Email local part cannot be empty' };
        }
        
        if (localPart.length > 64) {
            return { isValid: false, message: 'Email local part is too long (max 64 characters)' };
        }
        
        if (localPart.startsWith('.') || localPart.endsWith('.')) {
            return { isValid: false, message: 'Email local part cannot start or end with a dot' };
        }
        
        if (localPart.includes('..')) {
            return { isValid: false, message: 'Email local part cannot contain consecutive dots' };
        }
        
        // Check domain part
        if (!domain) {
            return { isValid: false, message: 'Email domain part cannot be empty' };
        }
        
        if (domain.length > 253) {
            return { isValid: false, message: 'Email domain is too long (max 253 characters)' };
        }
        
        if (!domain.includes('.')) {
            return { isValid: false, message: 'Email domain must contain at least one dot' };
        }
        
        // Check top-level domain
        const tld = domain.split('.').pop();
        if (tld.length < 2) {
            return { isValid: false, message: 'Top-level domain must be at least 2 characters long' };
        }
        
        return { isValid: true, message: 'Valid email address' };
    }

    /**
     * Check if email is from a disposable service
     */
    isDisposableEmail(email) {
        const disposableDomains = [
            '10minutemail.com', '20minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'temp-mail.org', 'throwaway.email', 'yopmail.com', 'maildrop.cc',
            'tempmail.org', '10mail.org', 'mailcatch.com', 'zippymail.info',
            'sharklasers.com', 'grr.la', 'spamgourmet.com', 'mailnesia.com',
            'tempmail.de', 'deadaddress.com', 'mailnull.com', 'jetable.org',
            'nospam.ze.tc', 'nospam4.us', 'trashmail.io', 'tempmail.org',
            'mail2rss.com', 'spambox.me', 'tempmail.info', 'yopmail.net',
            'coolmail.com', 'mailtemp.org', 'throwaway.email', 'tempmail.dev',
            'temp-email.info', 'tempmail.plus', 'fakemail.fr', 'tempmail.app',
            'temp-email.org', 'tempmail.io', 'emailtemp.org', 'tempemail.net',
            'tempmail.co', 'tempmail.us', 'tempmail.email', 'tempmail.link',
            'tempmail.site', 'tempmail.space', 'tempmail.world', 'tempmail.online',
            'tempmail.app', 'tempmail.live', 'tempmail.store', 'tempmail.tech',
            'tempmail.cloud', 'tempmail.solutions', 'tempmail.services', 'tempmail.systems',
            'tempmail.platform', 'tempmail.tools', 'tempmail.works', 'tempmail.zone',
            'tempmail.network', 'tempmail.center', 'tempmail.space', 'tempmail.host',
            'tempmail.server', 'tempmail.site', 'tempmail.web', 'tempmail.tech',
            'tempmail.pro', 'tempmail.xyz', 'tempmail.club', 'tempmail.fun',
            'tempmail.life', 'tempmail.co', 'tempmail.io', 'tempmail.email',
            'tempmail.online', 'tempmail.website', 'tempmail.app', 'tempmail.dev',
            'tempmail.test', 'tempmail.demo', 'tempmail.sample', 'tempmail.example',
            'tempmail.fake', 'tempmail.dummy', 'tempmail.mock', 'tempmail.virtual',
            'tempmail.temporary', 'tempmail.short', 'tempmail.quick', 'tempmail.fast',
            'tempmail.easy', 'tempmail.simple', 'tempmail.basic', 'tempmail.free',
            'tempmail.premium', 'tempmail.pro', 'tempmail.plus', 'tempmail.gold',
            'tempmail.silver', 'tempmail.bronze', 'tempmail.platinum', 'tempmail.diamond',
            'tempmail.vip', 'tempmail.special', 'tempmail.exclusive', 'tempmail.limited',
            'tempmail.unlimited', 'tempmail.infinity', 'tempmail.eternal', 'tempmail.forever',
            'tempmail.always', 'tempmail.never', 'tempmail.constant', 'tempmail.permanent',
            'tempmail.temporary', 'tempmail.moment', 'tempmail.instant', 'tempmail.now',
            'tempmail.today', 'tempmail.tomorrow', 'tempmail.week', 'tempmail.month',
            'tempmail.year', 'tempmail.decade', 'tempmail.century', 'tempmail.millennium'
        ];
        
        const domain = email.split('@').pop().toLowerCase();
        return disposableDomains.includes(domain);
    }

    /**
     * Show validation feedback
     */
    showValidation(input, message, isValid) {
        // Remove existing feedback
        const existingFeedback = input.parentNode.querySelector('.email-feedback');
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
        feedback.className = 'email-feedback invalid-feedback';
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
     * Get clean email for form submission
     */
    static getCleanEmail(input) {
        return input.dataset.cleanValue || input.value.trim().toLowerCase();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new EmailValidator();
});

// Export for use in other scripts
window.EmailValidator = EmailValidator;

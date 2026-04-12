// Form Resubmission Prevention
class FormResubmissionPrevention {
    constructor() {
        this.init();
    }

    init() {
        // Handle form submissions on artist dashboard
        this.preventFormResubmission();
        this.handleBrowserBackButton();
        this.setupUnloadProtection();
    }

    // Prevent form resubmission
    preventFormResubmission() {
        const forms = document.querySelectorAll('form[method="post"]');
        
        forms.forEach(form => {
            // Track if form has been submitted
            let isSubmitted = false;
            
            form.addEventListener('submit', function(e) {
                if (isSubmitted) {
                    e.preventDefault();
                    console.warn('Form resubmission prevented');
                    return false;
                }
                
                // Mark form as submitted
                isSubmitted = true;
                
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.style.opacity = '0.7';
                    
                    // Add loading spinner if not present
                    if (!submitBtn.querySelector('.spinner-border')) {
                        const spinner = document.createElement('span');
                        spinner.className = 'spinner-border spinner-border-sm ms-2';
                        spinner.setAttribute('role', 'status');
                        submitBtn.appendChild(spinner);
                    }
                }
            });

            // Reset submission flag when navigating away
            window.addEventListener('beforeunload', () => {
                isSubmitted = false;
            });
        });
    }

    // Handle browser back button
    handleBrowserBackButton() {
        // Clear form submission history when using back button
        window.addEventListener('pageshow', function(event) {
            // Check if page is loaded from cache (back button)
            if (event.persisted) {
                // Reset all forms
                const forms = document.querySelectorAll('form[method="post"]');
                forms.forEach(form => {
                    form.reset();
                    
                    // Re-enable submit buttons
                    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.style.opacity = '1';
                        
                        // Remove loading spinner
                        const spinner = submitBtn.querySelector('.spinner-border');
                        if (spinner) {
                            spinner.remove();
                        }
                    }
                });
                
                console.log('Page restored from cache - forms reset');
            }
        });
    }

    // Setup unload protection
    setupUnloadProtection() {
        let isSubmitting = false;
        
        // Track form submissions
        document.addEventListener('submit', function(e) {
            if (e.target.tagName === 'FORM' && e.target.method === 'post') {
                isSubmitting = true;
            }
        });

        // Warn before leaving if form is being submitted
        window.addEventListener('beforeunload', function(e) {
            if (isSubmitting) {
                // Allow navigation to complete
                setTimeout(() => {
                    isSubmitting = false;
                }, 1000);
            }
        });
    }

    // Reset form submission state after successful operations
    static resetFormState() {
        const forms = document.querySelectorAll('form[method="post"]');
        forms.forEach(form => {
            // Re-enable submit buttons
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
                
                // Remove loading spinner
                const spinner = submitBtn.querySelector('.spinner-border');
                if (spinner) {
                    spinner.remove();
                }
            }
        });
    }

    // Check for form resubmission warning
    static checkForResubmissionWarning() {
        // Look for browser's form resubmission warning
        const warningText = 'Confirm Form Resubmission';
        const bodyText = document.body.textContent || document.body.innerText;
        
        if (bodyText.includes(warningText)) {
            console.warn('Form resubmission warning detected');
            
            // Auto-click to refresh the page properly
            if (confirm('Form resubmission detected. Refresh the page to clear this?')) {
                window.location.reload();
            }
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.formResubmissionPrevention = new FormResubmissionPrevention();
    
    // Make reset function globally available
    window.resetFormState = FormResubmissionPrevention.resetFormState;
    
    // Check for existing warnings
    setTimeout(() => {
        FormResubmissionPrevention.checkForResubmissionWarning();
    }, 1000);
});

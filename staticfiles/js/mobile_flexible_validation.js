/**
 * Flexible Mobile Number Input - Clean-on-Entry Strategy
 * Allows any format (09, 9, +639) and normalizes to 10-digit format
 */

document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('contact_number');
    if (!phoneInput) return;

    // Simply override any existing event listeners by adding ours with capture
    // This ensures our handler runs first and can stop propagation
    
    const input = phoneInput; // Use the original element

    // Track whether the user has interacted with the field
    let touched = false;

    // Valid Philippine mobile prefixes (first 3 digits of 10-digit number, all start with 9)
    const validPrefixes = [
        '917', '918', '919', '905', '906', '915', '916', '926', '927',
        '920', '921', '928', '929', '939', '948', '949',
        '951', '952', '953', '954', '955', '956',
        '907', '908', '909', '910', '911', '912', '913', '914',
        '990', '991', '992', '993', '994',
        '934', '935', '936', '937', '938',
        '940', '941', '942', '943', '944', '945', '946', '947',
        '977', '978', '979', '980', '981', '982', '983', '984', '985', '986', '987', '988', '989',
        '995', '996', '997', '998', '999'
    ];

    /**
     * Clean and normalize phone number input
     * Handles the "0" or "63" prefixes and limits to 10 digits
     */
    function sanitizePhoneInput(value) {
        // Remove all non-numeric characters
        let clean = value.replace(/\D/g, '');
        
        // Remove ANY starting 0 immediately
        if (clean.startsWith('0')) {
            clean = clean.substring(1);
        }
        
        // Handle the "63" prefixes
        if (clean.startsWith('639')) {
            clean = clean.substring(2); // Strip 63
        }
        
        // Don't limit for now - let the HTML maxlength handle it
        return clean;
    }

    /**
     * Format phone number for display (XXX XXX XXXX)
     */
    function formatPhoneNumber(value) {
        // Remove non-digits for formatting
        let clean = value.replace(/\D/g, '');
        
        // Format as XXX XXX XXXX
        if (clean.length > 6) {
            return clean.substring(0, 3) + ' ' + clean.substring(3, 6) + ' ' + clean.substring(6);
        } else if (clean.length > 3) {
            return clean.substring(0, 3) + ' ' + clean.substring(3);
        }
        
        return clean;
    }

    /**
     * Validate phone number with proper priority order
     */
    function validatePhoneNumber() {
        const value = sanitizePhoneInput(input.value);
        let isValid = true;
        let message = '';

        // Check if empty - don't show error for empty, just remove validation
        if (value.length === 0) {
            hideValidation();
            return false;
        }
        // Priority 1: Check length first (must be exactly 10 digits)
        else if (value.length < 10) {
            isValid = false;
            message = 'Must be 10 digits after 0';
        }
        else if (value.length > 10) {
            isValid = false;
            message = 'Must be 10 digits after 0';
        }
        // Priority 2: Must start with 9
        else if (!value.startsWith('9')) {
            isValid = false;
            message = 'Please enter a valid mobile number.';
        }
        // Priority 3: Only check prefix if length is exactly 10 and starts with 9
        else if (value.length === 10) {
            const prefix = value.substring(0, 3); // First 3 digits (e.g., 917, 905)
            if (!validPrefixes.includes(prefix)) {
                isValid = false;
                message = 'Invalid Philippine mobile prefix';
            }
        }

        showValidation(input, message, isValid);
        return isValid;
    }

    function hideValidation() {
        // Remove existing feedback with unique ID
        let existingFeedback = document.getElementById('phone-validation-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Remove any submit-required feedback on this field
        const fieldContainer = input.closest('.mb-3') || input.parentNode;
        fieldContainer.querySelectorAll('.submit-required-feedback').forEach(el => el.remove());
        input.classList.remove('submit-required-invalid');
        
        // Remove validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        // Clear validation styles from input field
        input.style.borderColor = '';
        input.style.boxShadow = '';
    }

    function showValidation(inputField, message, isValid) {
        // Remove existing phone feedback
        let existingFeedback = document.getElementById('phone-validation-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Remove any submit-required feedback on this field to prevent duplicates
        const fieldContainer = inputField.closest('.mb-3') || inputField.parentNode;
        fieldContainer.querySelectorAll('.submit-required-feedback').forEach(el => el.remove());
        inputField.classList.remove('submit-required-invalid');

        // Remove validation classes
        inputField.classList.remove('is-valid', 'is-invalid');

        if (isValid && inputField.value.replace(/\D/g, '').length === 10) {
            inputField.classList.add('is-valid');
            
            // Let CSS handle the green glow
        } else if (message) {
            inputField.classList.add('is-invalid');
            
            // Let CSS handle the red glow
            
            // Error feedback
            const feedback = document.createElement('div');
            feedback.id = 'phone-validation-feedback';
            feedback.className = 'phone-feedback';
            feedback.style.fontSize = '0.875rem';
            feedback.style.marginTop = '0.25rem';
            feedback.style.color = '#dc3545';
            feedback.textContent = message;

            // Insert feedback after input
            inputField.parentNode.insertBefore(feedback, inputField.nextSibling);
        } else {
            // Clear validation styles
            inputField.classList.remove('is-valid', 'is-invalid');
        }
    }

    // Real-time validation on input - exactly like First Name
    input.addEventListener('input', function(e) {
        let currentValue = e.target.value;
        
        // Stop propagation to prevent global script interference
        e.stopPropagation();
        
        // Restrict to numbers only - remove all non-numeric characters
        currentValue = currentValue.replace(/[^0-9]/g, '');
        e.target.value = currentValue;
        
        // Prefix Blocker: Check for +, 6, or 0 at start
        if (currentValue.startsWith('+') || currentValue.startsWith('6') || currentValue.startsWith('0')) {
            showZeroBlockerError();
            flashInputBorder();
            
            // Remove the problematic prefix
            if (currentValue.startsWith('+63')) {
                currentValue = currentValue.substring(3);
            } else if (currentValue.startsWith('+')) {
                currentValue = currentValue.substring(1);
            } else if (currentValue.startsWith('63')) {
                currentValue = currentValue.substring(2);
            } else if (currentValue.startsWith('6')) {
                currentValue = currentValue.substring(1);
            } else if (currentValue.startsWith('0')) {
                currentValue = currentValue.substring(1);
            }
            
            e.target.value = currentValue;
            return;
        } else {
            hideZeroBlockerError();
        }
        
        // Re-validate to show real-time feedback (exactly like First Name)
        validatePhoneNumber();
    });

    function showZeroBlockerError() {
        showValidation(input, 'Please start after +63 or 0', false);
    }

    function hideZeroBlockerError() {
        hideValidation();
    }

    function validatePhoneNumber() {
        const currentValue = input.value.replace(/[^0-9]/g, '');
        
        // Only validate if field has been touched
        if (!touched) {
            return true;
        }
        
        // Remove previous validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        // Remove existing feedback
        const existingFeedback = input.parentNode.querySelector('.phone-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Remove submit-required error if field now has content
        if (currentValue.length > 0) {
            const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
            if (submitReqFeedback) {
                submitReqFeedback.remove();
            }
        }
        
        // Check for Empty (like Last Name)
        if (currentValue === "") {
            input.classList.add('is-invalid');
            showValidation(input, 'Contact Number is required', false);
            return false;
        }
        
        // Simple validation: must start with 9 and be 10 digits
        if (currentValue.length < 10) {
            if (!currentValue.startsWith('9')) {
                showValidation(input, 'Please enter a valid mobile number.', false);
            } else {
                showValidation(input, '', true);
                // Remove submit-required error when field becomes valid
                const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
                if (submitReqFeedback) {
                    submitReqFeedback.remove();
                }
            }
        } else if (currentValue.length === 10) {
            if (currentValue.startsWith('9')) {
                showValidation(input, '', true);
                // Remove submit-required error when field becomes valid
                const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
                if (submitReqFeedback) {
                    submitReqFeedback.remove();
                }
            } else {
                showValidation(input, 'Please enter a valid mobile number.', false);
            }
        } else {
            if (!currentValue.startsWith('9')) {
                showValidation(input, 'Please enter a valid mobile number.', false);
            } else {
                showValidation(input, 'Must be exactly 10 digits', false);
            }
        }
    }

    function updateHelperText(value) {
        const helperText = document.getElementById('phone-helper-text');
        const remaining = 10 - value.length;
        
        if (value.length === 0) {
            helperText.textContent = 'Enter your 10-digit mobile number (e.g., 917 123 4567)';
            helperText.style.color = '#6c757d';
        } else if (value.length < 10) {
            helperText.textContent = `${remaining} more digit${remaining !== 1 ? 's' : ''} to go...`;
            helperText.style.color = '#6c757d';
        } else {
            helperText.textContent = '';
            helperText.style.color = '#6c757d';
        }
    }

    function updateBorderColor(value) {
        if (value.length === 10) {
            input.style.borderColor = '#28a745';
            input.style.boxShadow = '0 0 0 0.2rem rgba(40, 167, 69, 0.25)';
        } else {
            input.style.borderColor = '';
            input.style.boxShadow = '';
        }
    }

    function flashInputBorder() {
        input.style.transition = 'border-color 0.3s ease';
        input.style.borderColor = '#dc3545';
        input.style.boxShadow = '0 0 0 0.2rem rgba(220, 53, 69, 0.25)';
        
        setTimeout(() => {
            input.style.borderColor = '';
            input.style.boxShadow = '';
        }, 300);
    }

    // Handle paste events with numeric restriction
    input.addEventListener('paste', function(e) {
        e.preventDefault();
        let pastedData = (e.clipboardData || window.clipboardData).getData('text');
        
        // Remove all non-numeric characters from pasted data
        pastedData = pastedData.replace(/[^0-9]/g, '');
        
        // Check if pasted data starts with 6 or 0 for prefix-blocker
        if (pastedData.startsWith('6') || pastedData.startsWith('0')) {
            showZeroBlockerError();
            flashInputBorder();
            // Hide error after 2 seconds for paste events
            setTimeout(() => hideZeroBlockerError(), 2000);
        } else {
            hideZeroBlockerError();
        }
        
        // Apply clean-on-entry to pasted data
        let sanitized = sanitizePhoneInput(pastedData);
        e.target.value = formatPhoneNumber(sanitized);
        
        // Update helper text and border color
        updateHelperText(sanitized);
        updateBorderColor(sanitized);
    });

    // Handle focus state - exactly like First Name
    input.addEventListener('focus', function(e) {
        touched = true; // Mark as touched when focused (like First Name)
    }, true);

    // Handle blur state - exactly like First Name
    input.addEventListener('blur', function(e) {
        // Validate the phone number (like First Name)
        validatePhoneNumber();
    });

    // Make the sanitize function globally available for form submission
    window.sanitizePhoneInput = sanitizePhoneInput;
});

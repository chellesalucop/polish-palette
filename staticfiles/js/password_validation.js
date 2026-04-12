/**
 * Password Complexity Validation & Real-time Match Check
 * Developer's Implementation for High-Entropy Password Policy
 */

document.addEventListener('DOMContentLoaded', function() {
    const password = document.querySelector('input[name="password"]');
    const confirmPassword = document.querySelector('input[name="confirm_password"]');
    
    // Track if fields have been touched (clicked into)
    let passwordTouched = false;
    let confirmPasswordTouched = false;

    // Get other form fields for validation
    const usernameInput = document.querySelector('input[name="username"]');
    const emailInput = document.querySelector('input[name="email"]');

    // Password criteria in priority order for real-time feedback.
    const criteria = {
        length: /.{10,}/,                   // Length: ≥ 10 characters (modern standard)
        uppercase: /[A-Z]/,                 // Casing: At least one uppercase letter
        numeric: /[0-9]/,                   // Numeric: At least one digit
        special: /[!@#$%^&*(),.?":{}|<>_\-\[\]\\/~`+=;']/ // At least one special character
    };

    // Common keyboard patterns and sequences to reject
    const keyboardPatterns = [
        'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
        'qwerty', 'asdfgh', 'zxcvb',
        '1234567890', '0987654321',
        'abcdefgh', 'password', 'pass1234'
    ];

    /**
     * Check if password contains keyboard smashes or simple sequences
     */
    function hasKeyboardPattern(password) {
        const lowerPass = password.toLowerCase();
        
        // Check against known keyboard patterns
        for (const pattern of keyboardPatterns) {
            if (lowerPass.includes(pattern)) {
                return true;
            }
        }
        
        // Check for simple number sequences (5+ consecutive)
        if (/(?:0123456789|1234567890|9876543210|0987654321)/.test(password)) {
            return true;
        }
        
        // Check for repeated characters (4+ same character)
        if (/(.)\1{3,}/.test(password)) {
            return true;
        }
        
        return false;
    }

    /**
     * Check if password contains username or email
     */
    function containsUserInfo(password) {
        const lowerPass = password.toLowerCase();
        
        // Check against username
        if (usernameInput && usernameInput.value.length >= 3) {
            const username = usernameInput.value.toLowerCase();
            if (lowerPass.includes(username)) {
                return 'username';
            }
        }
        
        // Check against email (local part before @)
        if (emailInput && emailInput.value.includes('@')) {
            const emailLocal = emailInput.value.split('@')[0].toLowerCase();
            if (emailLocal.length >= 3 && lowerPass.includes(emailLocal)) {
                return 'email';
            }
        }
        
        return false;
    }

    function validatePasswordComplexity() {
        const val = password.value;
        let allMet = true;
        let message = '';

        const requirementsContainer = document.getElementById('password-requirements');
        if (requirementsContainer) {
            requirementsContainer.style.display = val.length > 0 ? 'block' : 'none';
        }

        // Only show errors if user has started typing (field not empty)
        if (val.length === 0) {
            hidePasswordValidation();
            return false; // Not valid yet, but don't show errors
        }
        
        // Remove submit-required error if field now has content
        const submitReqFeedback = password.parentNode.querySelector('.submit-required-feedback');
        if (submitReqFeedback) {
            submitReqFeedback.remove();
        }

        // Helper to update requirement UI
        function updateReqUI(id, met) {
            const el = document.getElementById(id);
            if (!el) return;
            const icon = el.querySelector('i');
            
            if (met) {
                el.classList.remove('text-muted');
                el.classList.add('text-success');
                if (icon) {
                    icon.className = 'bi bi-check-circle-fill me-1';
                }
            } else {
                el.classList.add('text-muted');
                el.classList.remove('text-success');
                if (icon) {
                    icon.className = 'bi bi-circle me-1';
                }
            }
        }

        // Update checklist items
        const isLenMet = criteria.length.test(val);
        const isUpperMet = criteria.uppercase.test(val);
        const isNumMet = criteria.numeric.test(val);
        const isSpecialMet = criteria.special.test(val);
        const isUniqueMet = !hasKeyboardPattern(val) && !containsUserInfo(val);

        updateReqUI('req-length', isLenMet);
        updateReqUI('req-upper', isUpperMet);
        updateReqUI('req-number', isNumMet);
        updateReqUI('req-special', isSpecialMet);
        updateReqUI('req-unique', isUniqueMet);

        // Calculate overall validity
        allMet = isLenMet && isUpperMet && isNumMet && isSpecialMet && isUniqueMet;
        
        // Casing and priority messages for general feedback
        if (!isLenMet) {
            message = 'Minimum length of 10 characters';
        } else if (!isUpperMet) {
            message = 'Include at least 1 uppercase letter';
        } else if (!isNumMet) {
            message = 'Include at least 1 number';
        } else if (!isSpecialMet) {
            message = 'Include at least 1 special character';
        } else if (hasKeyboardPattern(val)) {
            message = 'Avoid simple patterns and sequences';
        } else {
            const userInfoCheck = containsUserInfo(val);
            if (userInfoCheck === 'username') {
                message = 'Password cannot contain your username';
            } else if (userInfoCheck === 'email') {
                message = 'Password cannot contain your email';
            }
        }

        // Update password field border and show validation
        if (allMet && val.length > 0) {
            password.classList.add('is-valid');
            password.classList.remove('is-invalid');
            hidePasswordValidation();
            
            // Remove submit-required error when field becomes valid
            const submitReqFeedback = password.parentNode.querySelector('.submit-required-feedback');
            if (submitReqFeedback) {
                submitReqFeedback.remove();
            }
        } else if (val.length > 0) {
            password.classList.add('is-invalid');
            password.classList.remove('is-valid');
            // We can still show the specific error message as a fallback, 
            // but the checklist is the primary visual.
            showPasswordValidation(password, message, false);
        } else {
            password.classList.remove('is-valid', 'is-invalid');
            hidePasswordValidation();
        }

        return allMet;
    }

    function getValidationContainer(input) {
        return input.closest('.mb-3') || input.parentNode;
    }

    function insertFeedbackOutsidePasswordField(input, feedback) {
        const container = input.closest('.mb-3');
        if (container) {
            container.insertAdjacentElement('beforeend', feedback);
            return;
        }
        
        input.parentNode.insertBefore(feedback, input.nextSibling);
    }

    function showPasswordValidation(input, message, isValid) {
        // Remove existing password feedback only
        hidePasswordValidation();
        
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
        feedback.className = 'password-feedback invalid-feedback';
        feedback.textContent = message;
        feedback.style.color = '#dc3545';
        feedback.style.fontSize = '0.875rem';
        feedback.style.marginTop = '0.25rem';
        feedback.style.display = 'block';
        
        // Keep feedback outside password wrapper so eye icon remains aligned.
        insertFeedbackOutsidePasswordField(input, feedback);
    }

    function hidePasswordValidation() {
        const container = getValidationContainer(password);
        const existingFeedback = container.querySelector('.password-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    }

    function hideConfirmPasswordValidation() {
        const container = getValidationContainer(confirmPassword);
        const existingFeedback = container.querySelector('.confirm-password-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    }

    function validatePasswordRequired() {
        // Only validate if field has been touched
        if (!passwordTouched) return true;
        
        if (password.value.trim() === '') {
            // Show "Password is required" message
            showPasswordValidation(password, "Password is required", false);
            return false;
        } else {
            // Clear required message
            return true;
        }
    }

    function validateConfirmPasswordRequired() {
        // Only validate if field has been touched
        if (!confirmPasswordTouched) return true;
        
        if (confirmPassword.value.trim() === '') {
            // Show "Confirm Password is required" message
            showConfirmPasswordValidation(confirmPassword, "Confirm Password is required", false);
            return false;
        } else {
            // Clear required message
            return true;
        }
    }

    function showConfirmPasswordValidation(input, message, isValid) {
        // Remove existing confirm password feedback only
        hideConfirmPasswordValidation();
        
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
        feedback.className = 'confirm-password-feedback invalid-feedback';
        feedback.textContent = message;
        feedback.style.color = '#dc3545';
        feedback.style.fontSize = '0.875rem';
        feedback.style.marginTop = '0.25rem';
        feedback.style.display = 'block';
        
        // Keep feedback outside password wrapper so eye icon remains aligned.
        insertFeedbackOutsidePasswordField(input, feedback);
    }

    function validateMatch() {
        const val1 = password.value;
        const val2 = confirmPassword.value;

        // Clear any existing confirm password messages first
        hideConfirmPasswordValidation();

        if (val2.length > 0) {
            if (val1.length === 0) {
                // Password field is empty - show error
                confirmPassword.classList.add('is-invalid');
                confirmPassword.classList.remove('is-valid');
                
                // Show "Enter password first" message
                showConfirmPasswordValidation(confirmPassword, "Enter password first", false);
            } else if (val1 === val2) {
                const passwordIsValid = validatePasswordComplexity();

                if (passwordIsValid) {
                    // Passwords match and password is valid
                    confirmPassword.classList.add('is-valid');
                    confirmPassword.classList.remove('is-invalid');
                } else {
                    // Confirm matches, but primary password is still invalid
                    confirmPassword.classList.add('is-invalid');
                    confirmPassword.classList.remove('is-valid');
                    showConfirmPasswordValidation(confirmPassword, "Password not valid.", false);
                }
            } else {
                // Passwords do not match
                confirmPassword.classList.add('is-invalid');
                confirmPassword.classList.remove('is-valid');
                
                // Show "Passwords do not match" message
                showConfirmPasswordValidation(confirmPassword, "Passwords do not match", false);
            }
        } else {
            // Reset if empty
            confirmPassword.classList.remove('is-valid', 'is-invalid');
        }

        // Update submit button state
        updateSubmitButton();
    }

    function updateSubmitButton() {
        const passwordComplex = validatePasswordComplexity();
        const passwordsMatch = password.value === confirmPassword.value && confirmPassword.value.length > 0;

        // Keep validation checks active but never disable the submit button.
        return passwordComplex && passwordsMatch;
    }

    // Event listeners for real-time validation - exactly like First Name
    password.addEventListener('input', function() {
        validatePasswordComplexity();
        validateMatch();
    });
    
    password.addEventListener('focus', function() {
        passwordTouched = true; // Mark as touched when focused (exactly like First Name)
    });
    
    password.addEventListener('blur', validatePasswordRequired);
    
    confirmPassword.addEventListener('input', function() {
        validateMatch();
    });
    
    confirmPassword.addEventListener('focus', function() {
        confirmPasswordTouched = true; // Mark as touched when focused (exactly like First Name)
    });
    
    confirmPassword.addEventListener('blur', validateConfirmPasswordRequired);
    
    // Re-validate password when username or email changes (to check if password contains them)
    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            if (password.value.length > 0) {
                validatePasswordComplexity();
            }
        });
    }
    
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            if (password.value.length > 0) {
                validatePasswordComplexity();
            }
        });
    }
    
    // Initial validation - hide all messages initially
    validatePasswordComplexity();
    updateSubmitButton();
});

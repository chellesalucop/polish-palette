/**
 * Name Identity Validation (First & Last)
 * Real-time validation for name fields with XSS prevention
 */

document.addEventListener('DOMContentLoaded', function() {
    const nameFields = ['first_name', 'last_name'];
    
    // Track touched state for each field
    const touchedFields = {
        first_name: false,
        last_name: false
    };

    nameFields.forEach(fieldName => {
        const input = document.querySelector(`input[name="${fieldName}"]`);
        
        if (!input) return; // Skip if field doesn't exist
        
        // Create error message div
        const errorMsg = document.createElement('div');
        errorMsg.className = 'name-feedback text-danger small mt-1 d-none';
        input.parentNode.appendChild(errorMsg);

        // Name validation regex: Only letters, spaces, hyphens, and periods allowed
        const nameRegex = /^[a-zA-Z\s\-\.]+$/;

        // Input filtering - only allow letters A-Z, a-z, and spaces
        input.addEventListener('input', function(e) {
            const value = e.target.value;
            
            // Allow only letters A-Z, a-z, and spaces
            const filteredValue = value.replace(/[^a-zA-Z\s]/g, '');
            
            if (filteredValue !== value) {
                e.target.value = filteredValue;
                // Re-validate after filtering
                validateName();
            } else {
                // Re-validate on valid input
                validateName();
            }
        });

        // Paste event filtering
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            let pastedData = (e.clipboardData || window.clipboardData).getData('text');
            
            // Filter pasted data to allow only letters A-Z, a-z, and spaces
            const sanitizedData = pastedData.replace(/[^a-zA-Z\s]/g, '');
            
            // Insert sanitized data at cursor position
            const start = input.selectionStart;
            const end = input.selectionEnd;
            const currentValue = input.value;
            
            // Insert sanitized data
            const newValue = currentValue.substring(0, start) + sanitizedData + currentValue.substring(end);
            input.value = newValue;
            
            // Set cursor position after inserted text
            const newCursorPos = start + sanitizedData.length;
            input.setSelectionRange(newCursorPos, newCursorPos);
            
            // Re-validate
            validateName();
        });

        // Track if validation is from blur (not real-time input)
        let isBlurValidation = false;

        function validateName() {
            // Validate against trimmed/collapsed value, but don't modify input while typing
            const val = input.value.trim().replace(/\s{2,}/g, ' ');
            
            // Only validate if field has been touched
            if (!touchedFields[fieldName]) {
                return true;
            }

            // Clear previous validation classes
            input.classList.remove('is-valid', 'is-invalid');
            
            // Remove existing feedback
            const existingFeedback = input.parentNode.querySelector('.name-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }

            // During real-time typing, skip empty/length checks so leading spaces don't trigger errors.
            // These are enforced on blur and submit instead.
            if (!isBlurValidation && val.length < 2) {
                // Remove submit-required error if field now has content
                if (val.length > 0) {
                    const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
                    if (submitReqFeedback) {
                        submitReqFeedback.remove();
                    }
                }
                return true;
            }

            // Name validation with specific field rules
            if (val === "") {
                // Check for Empty (also catches spaces-only input after trim)
                const label = input.closest('.mb-3')?.querySelector('.form-label')?.textContent?.trim() || 'This field';
                input.classList.add('is-invalid');
                showValidation(input, `${label} is required`, false);
                return false;
            } 
            // Length Guard: Minimum 2, Maximum 50 characters
            else if (val.length < 2 || val.length > 50) {
                input.classList.add('is-invalid');
                showValidation(input, 'Please enter a valid name.', false);
                return false;
            }
            // Stage 2: Pattern Match - Only alphabetic characters A-Z, a-z, and spaces
            else if (!/^[a-zA-Z\s]+$/.test(val)) {
                input.classList.add('is-invalid');
                showValidation(input, 'Please enter a valid name.', false);
                return false;
            }
            else if (/^[A-Za-z]\s+[A-Za-z]$/.test(val)) {
                // Single letter + space + single letter (too short)
                input.classList.add('is-invalid');
                showValidation(input, 'Name must be at least 2 characters long.', false);
                return false;
            }
            else {
                // Rule 1: Consecutive Limit - No character more than 2 times consecutively
                // e.g., "aa" is PASS, "aaa" is FAIL
                if (/(.)\1{2,}/i.test(val)) {
                    input.classList.add('is-invalid');
                    showValidation(input, 'A letter cannot appear more than 2 times in a row.', false);
                    return false;
                }
                
                // Rule 2: Global Frequency - For strings > 10 chars, no character > 40% of length
                const lettersOnly = val.replace(/\s/g, '').toLowerCase();
                if (lettersOnly.length > 10) {
                    const letterCounts = {};
                    for (const char of lettersOnly) {
                        letterCounts[char] = (letterCounts[char] || 0) + 1;
                    }
                    for (const [letter, count] of Object.entries(letterCounts)) {
                        if (count / lettersOnly.length > 0.4) {
                            input.classList.add('is-invalid');
                            showValidation(input, 'A single letter appears too frequently in this name.', false);
                            return false;
                        }
                    }
                }
                
                // Rule 3: Consonant Cluster Limit - Max 4 consecutive consonants
                // Supports names like "Schwarz" but blocks "Sshhnn"
                if (/[^aeiou\s]{5,}/i.test(val)) {
                    input.classList.add('is-invalid');
                    showValidation(input, 'Too many consecutive consonants.', false);
                    return false;
                }
                
                // Valid - remove success message and submit-required error
                input.classList.add('is-valid');
                showValidation(input, '', true);
                
                // Remove submit-required error when field becomes valid
                const submitReqFeedback = input.parentNode.querySelector('.submit-required-feedback');
                if (submitReqFeedback) {
                    submitReqFeedback.remove();
                }
                
                return true;
            }
        }

        function showValidation(input, message, isValid) {
            // Remove existing feedback
            const existingFeedback = input.parentNode.querySelector('.name-feedback');
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
            feedback.className = 'name-feedback invalid-feedback';
            feedback.textContent = message;
            feedback.style.color = '#dc3545';
            feedback.style.fontSize = '0.875rem';
            feedback.style.marginTop = '0.25rem';
            
            // Insert feedback after input
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }

        // Event listeners
        input.addEventListener('focus', function() {
            touchedFields[fieldName] = true; // Mark as touched when focused
        });

        input.addEventListener('blur', function() {
            // Sanitize whitespace when user leaves the field: trim + collapse double spaces
            const sanitized = input.value.trim().replace(/\s{2,}/g, ' ');
            if (input.value !== sanitized) {
                input.value = sanitized;
            }
            isBlurValidation = true;
            validateName();
            isBlurValidation = false;
        });

        input.addEventListener('input', function() {
            // Don't clear error messages - keep them visible (persistent errors)
            // Re-validate to show real-time feedback
            validateName();
        });
    });

    // Function to check if all name fields are valid
    function validateAllNames() {
        let allValid = true;
        nameFields.forEach(fieldName => {
            const input = document.querySelector(`input[name="${fieldName}"]`);
            if (input && touchedFields[fieldName]) {
                const val = input.value.trim();
                
                if (val === '' || val.length < 2 || !/^[a-zA-Z\s]+$/.test(val)) {
                    allValid = false;
                }
            }
        });
        return allValid;
    }

    // Export validation function for use in other scripts
    window.validateNameFields = validateAllNames;
});

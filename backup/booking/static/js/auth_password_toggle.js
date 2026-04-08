document.addEventListener('DOMContentLoaded', function () {
    const toggles = document.querySelectorAll('.toggle-password');

    toggles.forEach(function (toggle) {
        // Ensure proper accessibility attributes
        toggle.setAttribute('role', 'button');
        toggle.setAttribute('tabindex', '0');
        toggle.setAttribute('aria-label', 'Show password');
        
        // Add cursor pointer for better UX
        toggle.style.cursor = 'pointer';

        const toggleVisibility = function () {
            // Find the parent wrapper or use parent element
            const wrapper = toggle.closest('.password-field') || toggle.closest('.position-relative') || toggle.parentElement;
            if (!wrapper) {
                console.warn('Password toggle wrapper not found');
                return;
            }

            // Find the password input within the wrapper
            const passwordInput = wrapper.querySelector('input[type="password"], input[type="text"]');
            if (!passwordInput) {
                console.warn('Password input not found in wrapper');
                return;
            }

            const showing = passwordInput.type === 'text';
            passwordInput.type = showing ? 'password' : 'text';

            // SVG Path Definitions
            const eyeIconPaths = '<path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/><path d="M0 8s3-5.5 8-5.5s8 5.5 8 5.5s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 1 0 0-7a3.5 3.5 0 0 0 0 7z"/>';
            const eyeSlashIconPaths = '<path d="m10.79 12.912-1.614-1.615a3.5 3.5 0 0 1-4.474-4.474l-2.06-2.06C.938 6.278 0 8 0 8s3 5.5 8 5.5a7 7 0 0 0 2.79-.588M5.21 3.088A7 7 0 0 1 8 2.5c5 0 8 5.5 8 5.5s-.939 1.721-2.641 3.238l-2.047-2.047a3.5 3.5 0 0 0-4.474-4.474z"/><path d="M5.525 7.646a2.5 2.5 0 0 0 2.829 2.829zm4.95.708-2.829-2.83a2.5 2.5 0 0 1 2.829 2.829zm3.171 6-12-12 .708-.708 12 12z"/>';

            // Toggle icon content/classes
            if (toggle.tagName.toLowerCase() === 'svg') {
                toggle.innerHTML = showing ? eyeSlashIconPaths : eyeIconPaths;
                toggle.classList.toggle('bi-eye', !showing);
                toggle.classList.toggle('bi-eye-slash', showing);
            } else {
                toggle.classList.toggle('bi-eye', !showing);
                toggle.classList.toggle('bi-eye-slash', showing);
            }
            
            // Update aria label
            toggle.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
            
            console.log('Password toggle clicked:', showing ? 'Hiding password' : 'Showing password');
        };

        toggle.addEventListener('click', function (event) {
            event.preventDefault();
            toggleVisibility();
        });

        toggle.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                toggleVisibility();
            }
        });
    });
});

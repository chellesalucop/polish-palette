/* =========================
   BASE PAGE
========================= */

/* BURGER BUTTON CLOSING FOR NAVBAR MOBILE VIEW */
document.addEventListener("click", function (event) {
    // Handle main navbar mobile menu
    const menu = document.getElementById("mobileMenu");
    const button = document.querySelector(".burger-btn");

    if (menu && button) {
        if (!menu.contains(event.target) && !button.contains(event.target)) {
            const bsCollapse = bootstrap.Collapse.getInstance(menu);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        }
    }
    
    // Handle artist sidebar mobile menu
    const artistSidebar = document.getElementById("artistSidebar");
    const artistButton = document.getElementById("mobileToggle");
    const sidebarOverlay = document.getElementById("sidebarOverlay");
    
    if (artistSidebar && artistButton) {
        if (!artistSidebar.contains(event.target) && !artistButton.contains(event.target) && !sidebarOverlay.contains(event.target)) {
            if (artistSidebar.classList.contains('collapsed') === false) {
                artistSidebar.classList.add('collapsed');
                document.getElementById('mainContent').classList.add('sidebar-collapsed');
                sidebarOverlay.classList.remove('show');
            }
        }
    }
});

// Mobile menu toggle function for client pages
function toggleMobileMenu() {
    const menu = document.getElementById("mobileMenu");
    if (menu) {
        const bsCollapse = bootstrap.Collapse.getInstance(menu);
        if (bsCollapse) {
            bsCollapse.toggle();
        }
    }
}

/* =========================
   LANDING PAGE
========================= */

/* NEXT / PREVIOUS LOGIC FOR GALLERY SECTION */
document.addEventListener("DOMContentLoaded", function () {
    // Only run the landing page gallery pagination when the landing gallery controls exist
    const nextBtn = document.getElementById("nextBtn");
    const prevBtn = document.getElementById("prevBtn");
    const galleryGridEl = document.getElementById("galleryGrid");

    // Check if we're on the landing page by looking for landing-specific elements
    // This prevents the pagination from running on the booking form gallery
    const isLandingPage = document.querySelector('.landing-gallery') || 
                         document.querySelector('.hero-section') ||
                         (nextBtn && prevBtn && galleryGridEl && galleryGridEl.closest('.landing-gallery')) ||
                         (galleryGridEl && !galleryGridEl.closest('.booking-container') && !galleryGridEl.closest('.reference-section'));

    if (!isLandingPage) {
        return; // Not the landing gallery page — skip pagination logic
    }

    const items = document.querySelectorAll(".gallery-item");
    const itemsPerPage = 3;
    let currentPage = 0;
    const totalPages = Math.max(1, Math.ceil(items.length / itemsPerPage));

    function showPage(page) {
        const grid = galleryGridEl;

        grid.style.opacity = 0;
        grid.style.transform = "translateX(40px)";

        setTimeout(() => {
            items.forEach((item, index) => {
                item.style.display =
                    index >= page * itemsPerPage && index < (page + 1) * itemsPerPage
                    ? "block"
                    : "none";
            });

            grid.style.transform = "translateX(0)";
            grid.style.opacity = 1;

        }, 250);
    }

    nextBtn.addEventListener("click", () => {
        currentPage = (currentPage + 1) % totalPages;
        showPage(currentPage);
    });

    prevBtn.addEventListener("click", () => {
        currentPage = (currentPage - 1 + totalPages) % totalPages;
        showPage(currentPage);
    });

    showPage(currentPage);
});

/* INDICATOR AND MODAL FOR GALLERY SECTION */
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize landing gallery modal/indicators if we're on the landing gallery (wrapper present)
    if (!document.querySelector('.gallery-wrapper')) {
        return;
    }

    const galleryGrid = document.getElementById('galleryGrid');
    const galleryItems = document.querySelectorAll('.gallery-item');
    const galleryPrevBtn = document.querySelector('.gallery-btn.prev-btn');
    const galleryNextBtn = document.querySelector('.gallery-btn.next-btn');
    const galleryIndicators = document.getElementById('galleryIndicators');
    let currentGalleryIndex = 0;
    const itemsPerPage = 3;
    
    const modal = document.getElementById('galleryModal');
    const modalImage = document.getElementById('modalImage');
    const modalClose = document.querySelector('.modal-close');
    const modalPrev = document.querySelector('.modal-prev');
    const modalNext = document.querySelector('.modal-next');
    const currentImageNum = document.getElementById('currentImageNum');
    const totalImages = document.getElementById('totalImages');
    let currentModalIndex = 0;
    
    const galleryImages = Array.from(galleryItems).map(item => ({
        src: item.querySelector('img').src,
        caption: item.querySelector('.gallery-caption').textContent
    }));
    
/* INDICATOR LOGIC */
function initializeIndicators() {
    galleryIndicators.innerHTML = '';

    const totalPages = Math.ceil(galleryImages.length / itemsPerPage);

    for (let i = 0; i < totalPages; i++) {
        const dot = document.createElement('div');
        dot.className = 'gallery-dot';
        if (i === 0) dot.classList.add('active');

        dot.addEventListener('click', () => {
            showGalleryPage(i * itemsPerPage);
        });

        galleryIndicators.appendChild(dot);
    }
}
    
function updateIndicators() {
    const dots = document.querySelectorAll('.gallery-dot');
    const currentPage = Math.floor(currentGalleryIndex / itemsPerPage);

    dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentPage);
    });
}
    
    function showGalleryPage(index) {
        const totalItems = galleryItems.length;
        const maxIndex = Math.max(0, totalItems - itemsPerPage);
        
        if (index < 0) currentGalleryIndex = maxIndex;
        else if (index > maxIndex) currentGalleryIndex = 0;
        else currentGalleryIndex = index;
        
        galleryItems.forEach((item, i) => {
            if (i >= currentGalleryIndex && i < currentGalleryIndex + itemsPerPage) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });

        updateIndicators();
    }
    
    function showNextGallery() {
        showGalleryPage(currentGalleryIndex + itemsPerPage);
    }
    
    function showPrevGallery() {
        showGalleryPage(currentGalleryIndex - itemsPerPage);
    }
    
    /* MODAL LOGIC */
    function openModal(index) {
        currentModalIndex = index;
        modalImage.src = galleryImages[index].src;
        currentImageNum.textContent = index + 1;
        updateIndicators();
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    function showNextModal() {
        currentModalIndex = (currentModalIndex + 1) % galleryImages.length;
        openModal(currentModalIndex);
    }
    
    function showPrevModal() {
        currentModalIndex = (currentModalIndex - 1 + galleryImages.length) % galleryImages.length;
        openModal(currentModalIndex);
    }
    
    galleryItems.forEach((item, index) => {
        item.addEventListener('click', () => openModal(index));
        item.style.cursor = 'pointer';
    });
    
    if (galleryNextBtn) {
        galleryNextBtn.addEventListener('click', showNextGallery);
    }
    if (galleryPrevBtn) {
        galleryPrevBtn.addEventListener('click', showPrevGallery);
    }
    
    modalClose.addEventListener('click', closeModal);
    modalPrev.addEventListener('click', showPrevModal);
    modalNext.addEventListener('click', showNextModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
        if (modal.style.display === 'block') {
            if (e.key === 'ArrowLeft') showPrevModal();
            if (e.key === 'ArrowRight') showNextModal();
        }
    });
    
    initializeIndicators();
    showGalleryPage(0);
});

/* ARROW NEXT / PREVIOUS LOGIC FOR RATING SECTION */
document.addEventListener('DOMContentLoaded', function() {
    const avatars = document.querySelectorAll('.avatar');
    const testimonialText = document.getElementById('testimonialText');
    const customerName = document.getElementById('customerName');
    const customerTitle = document.getElementById('customerTitle');
    const prevBtn = document.querySelector('.rating-nav-btn.prev-btn');
    const nextBtn = document.querySelector('.rating-nav-btn.next-btn');
    let currentIndex = 0;
    
    const testimonials = [
        {
            text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vitae nulla diam in ac diam cum diam. Facilisi morbi tempus ullamcorper.",
            name: "Jihyo",
            title: "Happy Customer"
        },
        {
            text: "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
            name: "Sana",
            title: "Regular Client"
        },
        {
            text: "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat.",
            name: "Chaeyoung",
            title: "Satisfied Customer"
        },
        {
            text: "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione.",
            name: "Tzuyu",
            title: "Loyal Customer"
        },
        {
            text: "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores.",
            name: "Nayeon",
            title: "Happy Client"
        }
    ];
    
    function showTestimonial(index) {
        avatars.forEach(avatar => avatar.classList.remove('active'));

        avatars.forEach(avatar => {
            for (let i = 0; i < 5; i++) {
                avatar.classList.remove(`position-${i}`);
            }
        });

        avatars[index].classList.add('active');

        testimonialText.textContent = `"${testimonials[index].text}"`;
        customerName.textContent = testimonials[index].name;
        customerTitle.textContent = testimonials[index].title;

        updateAvatarPositions(index);
        
        currentIndex = index;
    }
    
    function updateAvatarPositions(activeIndex) {
        avatars.forEach((avatar, index) => {
            let relativePosition = (activeIndex - index + 5) % 5;
            avatar.classList.add(`position-${relativePosition}`);
        });
    }
    
    function showNext() {
        const nextIndex = (currentIndex + 1) % avatars.length;
        showTestimonial(nextIndex);
    }
    
    function showPrev() {
        const prevIndex = (currentIndex - 1 + avatars.length) % avatars.length;
        showTestimonial(prevIndex);
    }

    nextBtn.addEventListener('click', showNext);
    prevBtn.addEventListener('click', showPrev);
    
    avatars.forEach((avatar, index) => {
        avatar.addEventListener('click', () => showTestimonial(index));
    });
    
    showTestimonial(0);
});

/* MODAL DESCRIPTION FOR SERVICE SECTION */
document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".view-more-link");
    const overlay = document.getElementById("serviceModalOverlay");
    const modals = document.querySelectorAll(".service-modal");
    const closes = document.querySelectorAll(".service-modal-close");

    links.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const modalId = this.getAttribute("data-modal");
            const modal = document.getElementById(modalId);

            overlay.classList.add("active");
            modal.classList.add("active");
        });
    });

    function closeModal() {
        overlay.classList.remove("active");
        modals.forEach(m => m.classList.remove("active"));
    }

    closes.forEach(close => {
        close.addEventListener("click", closeModal);
    });

    overlay.addEventListener("click", closeModal);
});

/* =========================
   LOG IN / SIGN UP PAGE
========================= */

/* TOGGLE EYE ICON PASSWORD VISIBILITY LOGIC FOR LOGIN / SIGNUP SECTIONS */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".toggle-password").forEach(toggle => {
        toggle.addEventListener("click", function () {
            const input = this.previousElementSibling;
            const type = input.getAttribute("type") === "password" ? "text" : "password";
            input.setAttribute("type", type);
            this.classList.toggle("bi-eye");
            this.classList.toggle("bi-eye-slash");
        });
    });
});

/* =========================
   BASE PAGE & NAVIGATION
========================= */

document.addEventListener("click", function (event) {
    const menu = document.getElementById("mobileMenu");
    const button = document.querySelector(".burger-btn");

    if (menu && button) {
        if (!menu.contains(event.target) && !button.contains(event.target)) {
            const bsCollapse = bootstrap.Collapse.getInstance(menu);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        }
    }
    
    const artistSidebar = document.getElementById("artistSidebar");
    const artistButton = document.getElementById("mobileToggle");
    const sidebarOverlay = document.getElementById("sidebarOverlay");
    
    if (artistSidebar && artistButton) {
        if (!artistSidebar.contains(event.target) && !artistButton.contains(event.target) && !sidebarOverlay.contains(event.target)) {
            if (artistSidebar.classList.contains('collapsed') === false) {
                artistSidebar.classList.add('collapsed');
                document.getElementById('mainContent').classList.add('sidebar-collapsed');
                sidebarOverlay.classList.remove('show');
            }
        }
    }
});

/* =========================
   LANDING PAGE COMPONENTS
========================= */

document.addEventListener("DOMContentLoaded", function () {
    // Gallery Indicators & Pagination
    const galleryItems = document.querySelectorAll('.gallery-item');
    if (galleryItems.length > 0) {
        const galleryNextBtn = document.querySelector('.gallery-btn.next-btn');
        const galleryPrevBtn = document.querySelector('.gallery-btn.prev-btn');
        const galleryIndicators = document.getElementById('galleryIndicators');
        let currentGalleryIndex = 0;
        const itemsPerPage = 3;

        function showGalleryPage(index) {
            const totalItems = galleryItems.length;
            const maxIndex = Math.max(0, totalItems - itemsPerPage);
            if (index < 0) currentGalleryIndex = maxIndex;
            else if (index > maxIndex) currentGalleryIndex = 0;
            else currentGalleryIndex = index;
            
            galleryItems.forEach((item, i) => {
                item.style.display = (i >= currentGalleryIndex && i < currentGalleryIndex + itemsPerPage) ? 'block' : 'none';
            });
            updateIndicators();
        }

        function updateIndicators() {
            if (!galleryIndicators) return;
            const dots = galleryIndicators.querySelectorAll('.gallery-dot');
            const currentPage = Math.floor(currentGalleryIndex / itemsPerPage);
            dots.forEach((dot, index) => dot.classList.toggle('active', index === currentPage));
        }

        if (galleryNextBtn) galleryNextBtn.addEventListener('click', () => showGalleryPage(currentGalleryIndex + itemsPerPage));
        if (galleryPrevBtn) galleryPrevBtn.addEventListener('click', () => showGalleryPage(currentGalleryIndex - itemsPerPage));
        
        showGalleryPage(0);
    }

    // Service Modal Logic
    const serviceLinks = document.querySelectorAll(".view-more-link");
    const serviceOverlay = document.getElementById("serviceModalOverlay");
    if (serviceLinks.length > 0) {
        serviceLinks.forEach(link => {
            link.addEventListener("click", function (e) {
                e.preventDefault();
                const modalId = this.getAttribute("data-modal");
                const modal = document.getElementById(modalId);
                serviceOverlay.classList.add("active");
                modal.classList.add("active");
            });
        });
        serviceOverlay.addEventListener("click", () => {
            serviceOverlay.classList.remove("active");
            document.querySelectorAll(".service-modal").forEach(m => m.classList.remove("active"));
        });
    }
});

/* =====================================
   AUTH PAGES (LOG IN / SIGN UP) 
===================================== */
let formChanged = false;
let initialFormValues = {};

document.addEventListener('DOMContentLoaded', function() {
    // 1. Auto-dismiss Django Alerts (2 Seconds)
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 2000);
    });

    const form = document.querySelector('form[method="POST"]');
    if (!form) return; 

    const inputs = form.querySelectorAll('input:not([type="checkbox"])');
    
    // 2. Capture initial state
    inputs.forEach(input => {
        initialFormValues[input.name || input.id] = input.value;
    });
    
    // 3. Setup Validation & Change Tracking
    inputs.forEach(input => {
        let msg = input.parentNode.querySelector('.validation-msg');
        if (!msg) {
            msg = document.createElement('div');
            msg.className = 'validation-msg small mt-1';
            msg.style.display = 'none';
            input.parentNode.appendChild(msg);
        }

        input.addEventListener('input', function(e) {
            // STRICT 10-DIGIT LIMIT FOR CONTACT
            if (field.id === 'contact_number') {
                field.value = field.value.replace(/[^0-9]/g, '').substring(0, 10);
            }
            
            validateField(e.target);
            
            // Update formChanged status
            let isDirty = false;
            inputs.forEach(i => {
                if (i.value !== initialFormValues[i.name || i.id]) {
                    isDirty = true;
                }
            });
            formChanged = isDirty;
        });
    });

    function validateField(field) {
        let isValid = true;
        let message = "";
        const value = field.value.trim();
        const msgElement = field.parentNode.querySelector('.validation-msg');

        if (field.id === 'first_name' || field.id === 'last_name') {
            field.value = field.value.replace(/[^A-Za-z\s]/g, '');
            if (value.length < 2) { isValid = false; message = "Min 2 characters."; }
        } 
        else if (field.id === 'contact_number') {
            // Valid only if exactly 10 digits
            if (value.length !== 10) { 
                isValid = false; 
                message = "Must be exactly 10 digits."; 
            }
        } 
        else if (field.type === 'email') {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (value.length > 0 && !emailRegex.test(value)) { isValid = false; message = "Invalid email format."; }
        } 
        else if (field.id === 'password') {
            const hasNumber = /\d/.test(value);
            const hasChar = /[A-Za-z]/.test(value);
            if (value.length < 8 || !hasNumber || !hasChar) { isValid = false; message = "Need 8+ chars, letter & number."; }
        }

        // Visual Feedback
        if (value === "") {
            field.style.borderColor = "var(--red-violet)";
            if (msgElement) msgElement.style.display = 'none';
        } else if (isValid) {
            field.style.borderColor = "#28a745";
            if (msgElement) msgElement.style.display = 'none';
        } else {
            field.style.borderColor = "#dc3545";
            if (msgElement) {
                msgElement.textContent = message;
                msgElement.style.color = "#dc3545";
                msgElement.style.display = 'block';
            }
        }
    }
    
    // 4. EYE TOGGLE LOGIC (FIXED for SVGs)
    const eyeIcon = '<path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/><path d="M0 8s3-5.5 8-5.5s8 5.5 8 5.5s-3 5.5-8 5.5S0 8 0 8zm8 3.5a3.5 3.5 0 1 0 0-7a3.5 3.5 0 0 0 0 7z"/>';
    const eyeSlashIcon = '<path d="m10.79 12.912-1.614-1.615a3.5 3.5 0 0 1-4.474-4.474l-2.06-2.06C.938 6.278 0 8 0 8s3 5.5 8 5.5a7 7 0 0 0 2.79-.588M5.21 3.088A7 7 0 0 1 8 2.5c5 0 8 5.5 8 5.5s-.939 1.721-2.641 3.238l-2.047-2.047a3.5 3.5 0 0 0-4.474-4.474z"/><path d="M5.525 7.646a2.5 2.5 0 0 0 2.829 2.829zm4.95.708-2.829-2.83a2.5 2.5 0 0 1 2.829 2.829zm3.171 6-12-12 .708-.708 12 12z"/>';

    document.querySelectorAll(".toggle-password").forEach(toggle => {
        toggle.addEventListener("click", function () {
            // Find the input within the same container
            const input = this.parentElement.querySelector('input');
            if (input) {
                const isPassword = input.getAttribute("type") === "password";
                input.setAttribute("type", isPassword ? "text" : "password");
                
                // Toggle the SVG paths
                if (this.tagName.toLowerCase() === 'svg') {
                    this.innerHTML = isPassword ? eyeIcon : eyeSlashIcon;
                    this.classList.toggle("bi-eye", isPassword);
                    this.classList.toggle("bi-eye-slash", !isPassword);
                } else {
                    // Fallback for font-based icons if any exist
                    this.classList.toggle("bi-eye");
                    this.classList.toggle("bi-eye-slash");
                }
            }
        });
    });

    form.addEventListener('submit', function(e) {
        let formIsValid = true;
        inputs.forEach(input => {
            if (input.hasAttribute('required') && !input.value.trim()) formIsValid = false;
            const borderColor = window.getComputedStyle(input).borderColor;
            if (borderColor === "rgb(220, 53, 69)") formIsValid = false;
        });

        if (!formIsValid) {
            e.preventDefault();
            alert("Please ensure all fields are valid (10 digits for contact).");
        } else {
            formChanged = false; 
        }
    });
});

/* =====================================
   THE EXIT WARNING
===================================== */
window.addEventListener('beforeunload', function(e) {
    if (formChanged) {
        e.preventDefault();
        e.returnValue = ''; 
    }
});
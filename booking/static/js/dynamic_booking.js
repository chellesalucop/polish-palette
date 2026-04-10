// Dynamic Booking Logic & Customization System
class DynamicBookingSystem {
    constructor() {
        this.bookingState = {
            serviceCategory: null,
            complexityLevel: null,
            complexityPrice: 0,
            tipCode: null,
            referenceType: null,
            referenceFile: null,
            galleryImageId: null,
            galleryImageTitle: null, // Tracks the beautiful name of the design
            appointmentDate: null,
            appointmentTime: null,
            artistId: null,
            basePrice: 0,
            totalPrice: 0
        };

        // Service pricing structure
        this.servicePricing = {
            'gel_polish': {
                base_price: 350,
                name: 'Gel Polish (Natural Nail Overlay)'
            },
            'soft_gel_extensions': {
                base_price: 800,
                name: 'Soft-Gel Extensions (Tip Application + Overlay)'
            },
            'removal': {
                base_price: 0,
                name: 'Removal (Safe and gentle enhancement removal)'
            }
        };

        // Tip data mapping
        this.tipData = {
            'PGT01': { shape: 'Long Coffin', length: 'Long' },
            'PGT02': { shape: 'Medium Square', length: 'Medium' },
            'PGT03': { shape: 'Medium Coffin', length: 'Medium' },
            'PGT04': { shape: 'Medium Stiletto', length: 'Medium' },
            'PGT05': { shape: 'Medium Almond', length: 'Medium' },
            'PGT06': { shape: 'Short Square', length: 'Short' },
            'PGT07': { shape: 'Short Coffin', length: 'Short' },
            'PGT08': { shape: 'Short Stiletto', length: 'Short' },
            'PGT09': { shape: 'Short Almond', length: 'Short' }
        };

        this.init();
    }

    init() {
        this.bindEvents();
        this.setMinDate();
        this.handleAutoFillFromURL(); 

        // Intercept the original booking_form.js summary update
        setTimeout(() => {
            if (window.bookingStepNavigation && typeof window.bookingStepNavigation.updateSelectionSummary === 'function') {
                const originalUpdate = window.bookingStepNavigation.updateSelectionSummary.bind(window.bookingStepNavigation);
                window.bookingStepNavigation.updateSelectionSummary = () => {
                    originalUpdate(); 
                    this.updateSummary(); 
                };
            }
        }, 500);
    }

    bindEvents() {
        // Service category selection
        document.querySelectorAll('.service-category').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectServiceCategory(e);
            });
        });

        // Complexity selection
        document.querySelectorAll('.complexity-option').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectComplexity(e);
            });
        });

        // Tip selection
        document.querySelectorAll('.tip-option').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectTip(e);
            });
        });

        // Reference selection
        document.querySelectorAll('.reference-option').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectReferenceType(e);
            });
        });

        // Gallery image selection
        document.querySelectorAll('.gallery-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectGalleryImage(e);
            });
        });

        // File upload
        const fileInput = document.getElementById('referenceFile');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }

        // Date/time/artist change events
        ['appointment_date', 'appointment_time', 'artist'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', (e) => {
                    if (id === 'appointment_date') {
                        this.bookingState.appointmentDate = e.target.value;
                    } else if (id === 'appointment_time') {
                        this.bookingState.appointmentTime = e.target.value;
                    } else if (id === 'artist') {
                        this.bookingState.artistId = e.target.value;
                    }
                    this.updateSummary();
                    this.validateForm();
                });
            }
        });

        // Acknowledgment checkbox
        const acknowledgeCheckbox = document.getElementById('acknowledge48Hour');
        if (acknowledgeCheckbox) {
            acknowledgeCheckbox.addEventListener('change', () => this.validateForm());
        }

        // Form submission
        const form = document.getElementById('bookingForm');
        if (form) {
            form.addEventListener('submit', (e) => this.submitBooking(e));
        }

        // NEW: Phase Transition Enforcer
        // This guarantees our script overwrites the older script every time you navigate phases
        document.querySelectorAll('.nav-btn, .step').forEach(btn => {
            btn.addEventListener('click', () => {
                setTimeout(() => {
                    this.updateSummary();
                }, 50); // 50ms delay lets the old script run first, then we crush its output
            });
        });
    }

    // --- AI AUTOMATION & PHASE 3 REDIRECT FUNCTION ---
    handleAutoFillFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        
        const category = urlParams.get('category');
        let complexity = urlParams.get('complexity');
        const tip = urlParams.get('tip');
        const refId = urlParams.get('ref');

        if (category) {
            const categoryElement = document.querySelector(`.service-category[data-category="${category}"]`);
            if (categoryElement) categoryElement.click();
        }

        if (complexity) {
            complexity = complexity.toLowerCase().replace(' set', '').trim();
            setTimeout(() => {
                const complexityOption = document.querySelector(`.complexity-option[data-complexity="${complexity}"]`);
                if (complexityOption) complexityOption.click();
            }, 100);
        }

        if (tip && category === 'soft_gel_extensions') {
            setTimeout(() => {
                const tipElement = document.querySelector(`.tip-option[data-tip="${tip}"]`);
                if (tipElement) tipElement.click();
            }, 200);
        }

        // FAST-FORWARD TO PHASE 3 FOR AI RECOMMENDATIONS
        if (refId) {
            setTimeout(() => {
                // 1. Virtually click "Next" to pass Step 1 safely
                if (window.bookingStepNavigation) window.bookingStepNavigation.nextStep();
                
                setTimeout(() => {
                    // 2. Virtually click "Next" to pass Step 2 safely
                    if (window.bookingStepNavigation) window.bookingStepNavigation.nextStep();
                    
                    setTimeout(() => {
                        // 3. Now on Phase 3: Auto-select gallery and click the specific image
                        const galleryOption = document.querySelector('.reference-option[data-reference="gallery"]');
                        if (galleryOption) galleryOption.click();
                        
                        setTimeout(() => {
                            const galleryItem = document.querySelector(`.gallery-item[data-image-id="${refId}"]`);
                            if (galleryItem) {
                                galleryItem.click();
                                // Scroll gracefully to the grid so they see their design is picked
                                try {
                                    galleryItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                } catch(e) {}
                            }
                        }, 150);
                    }, 200); // Wait for Step 2 animation
                }, 200); // Wait for Step 1 animation
            }, 300); // Wait for initial auto-fill
        }
    }

    selectServiceCategory(e) {
        const category = e.target.closest('.service-category') || e.currentTarget;
        const selectedCategory = category.dataset.category;

        document.querySelectorAll('.service-category').forEach(c => c.classList.remove('selected'));
        category.classList.add('selected');

        this.bookingState.serviceCategory = selectedCategory;
        this.bookingState.basePrice = this.servicePricing[selectedCategory].base_price;
        this.bookingState.complexityLevel = null;
        this.bookingState.complexityPrice = 0;
        this.bookingState.tipCode = null;

        this.resetDependentFields('service');
        this.validateForm();
        
        if (window.bookingStepNavigation) {
            window.bookingStepNavigation.updateSelectionSummary();
        }

        const defaultGrid = document.getElementById('complexity-grid-default');
        const removalGrid = document.getElementById('complexity-grid-removal');
        
        if (selectedCategory === 'removal') {
            if (defaultGrid) defaultGrid.classList.add('hidden');
            if (removalGrid) removalGrid.classList.remove('hidden');
        } else {
            if (defaultGrid) defaultGrid.classList.remove('hidden');
            if (removalGrid) removalGrid.classList.add('hidden');
        }
    }

    selectComplexity(e) {
        const option = e.target.closest('.complexity-option') || e.currentTarget;
        const complexity = option.dataset.complexity;
        const price = parseInt(option.dataset.price) || 0;

        document.querySelectorAll('.complexity-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');

        this.bookingState.complexityLevel = complexity;
        this.bookingState.complexityPrice = price;

        this.resetDependentFields('complexity');

        const referenceSection = document.getElementById('referenceSection');
        if (referenceSection) {
            referenceSection.classList.remove('hidden');
        }

        this.validateForm();
        
        if (window.bookingStepNavigation) {
            window.bookingStepNavigation.updateSelectionSummary();
        }
    }

    selectTip(e) {
        const option = e.target.closest('.tip-option') || e.currentTarget;
        const tipCode = option.dataset.tip;

        document.querySelectorAll('.tip-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');

        this.bookingState.tipCode = tipCode;

        this.validateForm();
        if (window.bookingStepNavigation) {
            window.bookingStepNavigation.updateSelectionSummary();
        }
    }

    selectReferenceType(e) {
        const option = e.target.closest('.reference-option') || e.currentTarget;
        const referenceType = option.dataset.reference;
        
        const radio = option.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;

        document.querySelectorAll('.reference-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');

        this.bookingState.referenceType = referenceType;
        this.bookingState.referenceFile = null;
        this.bookingState.galleryImageId = null;
        this.bookingState.galleryImageTitle = null;

        const uploadSection = document.getElementById('uploadSection');
        const gallerySection = document.getElementById('gallerySection');
        const designNoteSection = document.getElementById('designNoteSection');
        
        if (uploadSection) uploadSection.classList.add('hidden');
        if (gallerySection) gallerySection.classList.add('hidden');
        if (designNoteSection) designNoteSection.classList.add('hidden');

        if (referenceType === 'upload') {
            if (uploadSection) uploadSection.classList.remove('hidden');
            if (designNoteSection) designNoteSection.classList.remove('hidden');
        } else if (referenceType === 'gallery') {
            if (gallerySection) gallerySection.classList.remove('hidden');
            if (designNoteSection) designNoteSection.classList.remove('hidden');
        }

        this.resetDependentFields('reference');

        const placeholder = document.getElementById('uploadPlaceholder');
        const successIndicator = document.getElementById('uploadSuccessIndicator');
        if (placeholder && successIndicator) {
            placeholder.classList.remove('hidden');
            successIndicator.classList.add('hidden');
        }

        this.validateForm();
        if (window.bookingStepNavigation) {
            window.bookingStepNavigation.updateSelectionSummary();
        }
    }

    selectGalleryImage(e) {
        const item = e.target.closest('.gallery-item') || e.currentTarget;
        
        document.querySelectorAll('.gallery-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');

        // FORCE EXACT NAME CAPTURE
        const id = item.dataset.imageId;
        const imgElement = item.querySelector('img');
        const title = item.dataset.designTitle || (imgElement ? imgElement.alt : `Design #${id}`);

        this.bookingState.galleryImageId = id;
        this.bookingState.galleryImageTitle = title; // Storing the exact beautiful name

        this.validateForm();
        
        if (window.bookingStepNavigation) {
            window.bookingStepNavigation.updateSelectionSummary();
        }
        
        // Ensure our summary override runs immediately after setting this
        this.updateSummary();
    }

    handleFileUpload(e) {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 2 * 1024 * 1024) {
                alert('File size must be less than 2MB');
                e.target.value = '';
                return;
            }
            if (!file.type.startsWith('image/')) {
                alert('Only image files are allowed');
                e.target.value = '';
                return;
            }

            this.bookingState.referenceFile = file;
            
            this.showUploadSuccess(file.name);
            
            if (window.bookingStepNavigation) {
                window.bookingStepNavigation.updateSelectionSummary();
            }
            this.updateSummary();
            this.validateForm();
        }
    }

    showUploadSuccess(filename) {
        const placeholder = document.getElementById('uploadPlaceholder');
        const successIndicator = document.getElementById('uploadSuccessIndicator');
        const fileNameDisplay = document.getElementById('fileNameDisplay');
        
        if (placeholder) placeholder.classList.add('hidden');
        if (successIndicator) successIndicator.classList.remove('hidden');
        if (fileNameDisplay) fileNameDisplay.innerText = filename;
    }

    selectDate(e) {
        this.bookingState.appointmentDate = e.target.value;
        this.validateForm();
        if (window.bookingStepNavigation) window.bookingStepNavigation.updateSelectionSummary();
        this.updateSummary();
    }

    selectTime(e) {
        this.bookingState.appointmentTime = e.target.value;
        this.validateForm();
        if (window.bookingStepNavigation) window.bookingStepNavigation.updateSelectionSummary();
        this.updateSummary();
    }

    selectArtist(e) {
        this.bookingState.artistId = e.target.value;
        this.validateForm();
        if (window.bookingStepNavigation) window.bookingStepNavigation.updateSelectionSummary();
        this.updateSummary();
    }

    resetDependentFields(fromField) {
        switch(fromField) {
            case 'service':
                this.bookingState.complexityLevel = null;
                this.bookingState.complexityPrice = 0;
                this.bookingState.tipCode = null;
                this.bookingState.referenceType = null;
                this.bookingState.referenceFile = null;
                this.bookingState.galleryImageId = null;
                this.bookingState.galleryImageTitle = null;
                this.bookingState.appointmentDate = null;
                this.bookingState.appointmentTime = null;
                this.bookingState.artistId = null;
                break;
            case 'complexity':
                this.bookingState.tipCode = null;
                this.bookingState.referenceType = null;
                this.bookingState.referenceFile = null;
                this.bookingState.galleryImageId = null;
                this.bookingState.galleryImageTitle = null;
                this.bookingState.appointmentDate = null;
                this.bookingState.appointmentTime = null;
                this.bookingState.artistId = null;
                break;
            case 'reference':
                this.bookingState.appointmentDate = null;
                this.bookingState.appointmentTime = null;
                this.bookingState.artistId = null;
                break;
        }

        if (fromField === 'service') {
            document.querySelectorAll('.complexity-option').forEach(o => o.classList.remove('selected'));
        }
        
        if (fromField === 'service' || fromField === 'complexity') {
            document.querySelectorAll('.tip-option').forEach(o => o.classList.remove('selected'));
            document.querySelectorAll('.reference-option').forEach(o => {
                o.style.borderColor = '#e9ecef';
                o.style.background = '#fff';
                const radio = o.querySelector('input[type="radio"]');
                if (radio) radio.checked = false;
            });
            document.querySelectorAll('.gallery-item').forEach(i => i.classList.remove('selected'));
            
            if (document.getElementById('referenceFile')) {
                document.getElementById('referenceFile').value = '';
            }
        }
        
        if (document.getElementById('appointment_date')) document.getElementById('appointment_date').value = '';
        if (document.getElementById('appointment_time')) document.getElementById('appointment_time').value = '';
        if (document.getElementById('artist')) document.getElementById('artist').value = '';

        if (fromField === 'service') {
            document.getElementById('complexitySection')?.classList.add('hidden');
            document.getElementById('tipSection')?.classList.add('hidden');
            document.getElementById('referenceSection')?.classList.add('hidden');
            document.getElementById('datetimeSection')?.classList.add('hidden');
            document.getElementById('artistSection')?.classList.add('hidden');
            document.getElementById('summarySection')?.classList.add('hidden');
            document.getElementById('formActions')?.classList.add('hidden');
        } else if (fromField === 'complexity') {
            document.getElementById('referenceSection')?.classList.add('hidden');
            document.getElementById('datetimeSection')?.classList.add('hidden');
            document.getElementById('artistSection')?.classList.add('hidden');
            document.getElementById('summarySection')?.classList.add('hidden');
            document.getElementById('formActions')?.classList.add('hidden');
        } else if (fromField === 'reference') {
            document.getElementById('datetimeSection')?.classList.add('hidden');
            document.getElementById('artistSection')?.classList.add('hidden');
            document.getElementById('summarySection')?.classList.add('hidden');
            document.getElementById('formActions')?.classList.add('hidden');
        }
    }

    updateSummary() {
        this.bookingState.totalPrice = (this.bookingState.basePrice || 0) + (this.bookingState.complexityPrice || 0);
        this.updateHiddenFields();

        if (document.getElementById('selectedService')) {
            document.getElementById('selectedService').textContent = this.bookingState.serviceCategory ? this.servicePricing[this.bookingState.serviceCategory].name : '-';
        }
        if (document.getElementById('selectedComplexity')) {
            document.getElementById('selectedComplexity').textContent = this.bookingState.complexityLevel ? this.formatComplexity(this.bookingState.complexityLevel) : '-';
        }
        if (document.getElementById('selectedArtist')) {
            document.getElementById('selectedArtist').textContent = this.bookingState.artistId ? this.getArtistName(this.bookingState.artistId) : '-';
        }
        if (document.getElementById('selectedDateDisplay')) {
            document.getElementById('selectedDateDisplay').textContent = this.bookingState.appointmentDate ? this.formatDate(this.bookingState.appointmentDate) : '-';
        }
        if (document.getElementById('selectedTimeDisplay')) {
            document.getElementById('selectedTimeDisplay').textContent = this.bookingState.appointmentTime ? this.formatTime(this.bookingState.appointmentTime) : '-';
        }
        if (document.getElementById('selectedPrice')) {
            document.getElementById('selectedPrice').textContent = `₱${this.bookingState.totalPrice}`;
        }

        if (document.getElementById('summary-service')) {
            document.getElementById('summary-service').textContent = this.bookingState.serviceCategory ? this.servicePricing[this.bookingState.serviceCategory].name : '-';
        }
        if (document.getElementById('summary-complexity')) {
            document.getElementById('summary-complexity').textContent = this.bookingState.complexityLevel ? this.formatComplexity(this.bookingState.complexityLevel) : '-';
        }
        if (document.getElementById('summary-artist')) {
            document.getElementById('summary-artist').textContent = this.bookingState.artistId ? this.getArtistName(this.bookingState.artistId) : '-';
        }
        if (document.getElementById('summary-date')) {
            document.getElementById('summary-date').textContent = this.bookingState.appointmentDate ? this.formatDate(this.bookingState.appointmentDate) : '-';
        }
        if (document.getElementById('summary-time')) {
            document.getElementById('summary-time').textContent = this.bookingState.appointmentTime ? this.formatTime(this.bookingState.appointmentTime) : '-';
        }
        if (document.getElementById('summary-price')) {
            document.getElementById('summary-price').textContent = `₱${this.bookingState.totalPrice}`;
        }

        // PERFECT DESIGN TEXT FORMATTING
        let designText = '-';
        if (this.bookingState.serviceCategory === 'removal') {
            designText = 'N.A. (Removal)';
        } else if (this.bookingState.referenceType === 'upload' && this.bookingState.referenceFile) {
            designText = this.bookingState.referenceFile.name; // Just the filename
        } else if (this.bookingState.referenceType === 'gallery' && this.bookingState.galleryImageTitle) {
            designText = this.bookingState.galleryImageTitle; // Exact name: "Sunset Bloom French"
        }

        // Target both summaries directly to overwrite older scripts
        if (document.getElementById('selectedDesign')) document.getElementById('selectedDesign').textContent = designText;
        if (document.getElementById('summary-design')) document.getElementById('summary-design').textContent = designText;

        this.validateForm();
    }

    updateHiddenFields() {
        if(document.getElementById('serviceCategory')) document.getElementById('serviceCategory').value = this.bookingState.serviceCategory || '';
        if(document.getElementById('complexityLevel')) document.getElementById('complexityLevel').value = this.bookingState.complexityLevel || '';
        if(document.getElementById('tipCode')) document.getElementById('tipCode').value = this.bookingState.tipCode || '';
        if(document.getElementById('referenceType')) document.getElementById('referenceType').value = this.bookingState.serviceCategory === 'removal' ? 'none' : (this.bookingState.referenceType || '');
        if(document.getElementById('galleryImageId')) document.getElementById('galleryImageId').value = this.bookingState.galleryImageId || '';
        if(document.getElementById('totalPrice')) document.getElementById('totalPrice').value = this.bookingState.totalPrice;
    }

    validateForm() {
        const submitBtn = document.getElementById('submitBtn');
        if (!submitBtn) return false;
        
        const acknowledgeCheckbox = document.getElementById('acknowledge48Hour');
        
        const checks = {
            serviceCategory: this.bookingState.serviceCategory || document.querySelector('.service-category.selected'),
            complexityLevel: this.bookingState.complexityLevel || document.querySelector('.complexity-option.selected'),
            referenceType: this.bookingState.serviceCategory === 'removal' ? true : (this.bookingState.referenceType || document.querySelector('.reference-option.selected')),
            referenceValue: this.bookingState.serviceCategory === 'removal' ? true : (this.bookingState.referenceType === 'gallery' ? 
                (this.bookingState.galleryImageId || document.querySelector('.gallery-item.selected')?.dataset.imageId) : 
                (this.bookingState.referenceFile || document.getElementById('referenceFile')?.files.length)),
            appointmentDate: this.bookingState.appointmentDate || document.getElementById('appointment_date')?.value,
            appointmentTime: this.bookingState.appointmentTime || document.getElementById('appointment_time')?.value,
            artistId: this.bookingState.artistId || document.getElementById('artist')?.value,
            acknowledgment: acknowledgeCheckbox && acknowledgeCheckbox.checked
        };
        
        const isValid = Object.values(checks).every(Boolean);
        
        submitBtn.disabled = !isValid;
        
        if (isValid) {
            submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Confirm Booking';
            submitBtn.classList.remove('disabled');
        } else {
            submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Complete All Steps to Book';
            submitBtn.classList.add('disabled');
        }
        
        return isValid;
    }

    submitBooking(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const submitBtn = document.getElementById('submitBtn');
        
        this.updateHiddenFields();
        
        formData.set('service_category', this.bookingState.serviceCategory || '');
        formData.set('complexity_level', this.bookingState.complexityLevel || '');
        formData.set('tip_code', this.bookingState.tipCode || '');
        formData.set('reference_type', this.bookingState.serviceCategory === 'removal' ? 'none' : (this.bookingState.referenceType || ''));
        formData.set('gallery_image_id', this.bookingState.galleryImageId || '');
        formData.set('total_price', this.bookingState.totalPrice || '0');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Booking...';
        }

        const submitUrl = e.target.action || window.location.pathname;

        fetch(submitUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { 
                    throw new Error(`HTTP ${response.status}: ${text}`); 
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url || '/dashboard/';
            } else {
                alert(data.message || 'Booking failed. Please try again.');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Book Appointment';
                }
            }
        })
        .catch(error => {
            console.error('Booking error details:', error);
            alert(`An error occurred: ${error.message}. Please try again.`);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Book Appointment';
            }
        });
    }

    setMinDate() {
        const dateInput = document.getElementById('appointment_date');
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.setAttribute('min', today);
        }
    }

    formatComplexity(complexity) {
        const complexityMap = {
            'plain': 'Plain Gel Polish',
            'minimal': 'Minimal Set',
            'full': 'Full Set',
            'advanced': 'Advanced Set',
            'gel_polish_removal': 'Gel Polish Removal',
            'extensions_removal': 'Extensions Removal'
        };
        return complexityMap[complexity] || complexity;
    }

    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' 
        });
    }

    formatTime(timeStr) {
        if (!timeStr) return '';
        const [hours, minutes] = timeStr.split(':');
        const hour = parseInt(hours);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour > 12 ? hour - 12 : hour;
        return `${displayHour}:${minutes} ${ampm}`;
    }

    getArtistName(artistId) {
        const artistSelect = document.getElementById('artist');
        if (artistSelect) {
            const option = artistSelect.querySelector(`option[value="${artistId}"]`);
            return option ? option.textContent : '-';
        }
        return '-';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dynamicBookingSystem = new DynamicBookingSystem();
});
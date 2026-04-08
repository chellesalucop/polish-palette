// Complete Booking Form JavaScript with all step navigation functionality
console.log('Booking form script loaded');

document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded - initializing booking form');

    // Enhanced step navigation system
    let currentStep = 1;
    const totalSteps = 6;
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');

    // BookingStepNavigation class functionality
    class BookingStepNavigation {
        constructor() {
            this.currentStep = 1;
            this.totalSteps = 6;
            this.init();
        }

        init() {
            this.updateStepDisplay();
        }

        nextStep() {
            if (this.currentStep === 2) {
                const selectedService = document.querySelector('.service-category.selected');
                if (selectedService && selectedService.dataset.category === 'removal') {
                    this.currentStep = 4; // Skip Step 3 (Design)
                    this.updateStepDisplay();
                    return;
                }
            }
            if (this.currentStep < this.totalSteps) {
                this.currentStep++;
                this.updateStepDisplay();
            }
        }

        previousStep() {
            if (this.currentStep === 4) {
                const selectedService = document.querySelector('.service-category.selected');
                if (selectedService && selectedService.dataset.category === 'removal') {
                    this.currentStep = 2; // Jump back to Step 2
                    this.updateStepDisplay();
                    return;
                }
            }
            if (this.currentStep > 1) {
                this.currentStep--;
                this.updateStepDisplay();
            }
        }

        goToStep(stepNumber) {
            if (stepNumber >= 1 && stepNumber <= this.totalSteps) {
                this.currentStep = stepNumber;
                this.updateStepDisplay();
            }
        }

        validateCurrentStep() {
            switch (this.currentStep) {
                case 1:
                    // Service category validation
                    const selectedService = document.querySelector('.service-category.selected');
                    if (!selectedService) {
                        this.showNotification('Please select a service type');
                        return false;
                    }
                    return true;

                case 2:
                    // Complexity validation
                    const selectedComplexity = document.querySelector('.complexity-option.selected');
                    if (!selectedComplexity) {
                        this.showNotification('Please select a complexity level');
                        return false;
                    }
                    return true;

                case 3:
                    // Design reference validation
                    const selectedReference = document.querySelector('.reference-option.selected');
                    if (!selectedReference) {
                        this.showNotification('Please select a design reference option');
                        return false;
                    }

                    // If gallery selected, ensure an image is chosen
                    if (selectedReference.dataset.reference === 'gallery') {
                        const selectedImage = document.querySelector('.gallery-item.selected');
                        if (!selectedImage) {
                            this.showNotification('Please select a design from gallery');
                            return false;
                        }
                    }

                    // If upload selected, ensure file is uploaded
                    if (selectedReference.dataset.reference === 'upload') {
                        const fileInput = document.getElementById('referenceFile');
                        if (!fileInput.files.length) {
                            this.showNotification('Please upload a design image');
                            return false;
                        }
                    }

                    return true;

                case 4:
                    // Artist validation
                    const artistSelect = document.getElementById('artist');
                    const selectedArtistValue = artistSelect ? artistSelect.value : '';
                    if (!selectedArtistValue) {
                        this.showNotification('Please select an artist');
                        return false;
                    }
                    return true;

                case 5:
                    // Date and time validation
                    const date = document.getElementById('appointment_date').value;
                    const time = document.getElementById('appointment_time').value;
                    if (!date || !time) {
                        this.showNotification('Please select appointment date and time');
                        return false;
                    }
                    return true;

                case 6:
                    // Confirmation validation - check acknowledgment and all previous steps
                    const acknowledgeCheckbox = document.getElementById('acknowledge48Hour');
                    const isAcknowledged = acknowledgeCheckbox && acknowledgeCheckbox.checked;
                    if (!isAcknowledged) {
                        this.showNotification('Please acknowledge 48-hour cancellation policy');
                        return false;
                    }

                    // Let DynamicBookingSystem handle the full validation and submit button state
                    if (window.dynamicBookingSystem) {
                        return window.dynamicBookingSystem.validateForm();
                    }
                    
                    // Fallback validation if DynamicBookingSystem is not available
                    const serviceSelected = document.querySelector('.service-category.selected');
                    const complexitySelected = document.querySelector('.complexity-option.selected');
                    const referenceSelected = document.querySelector('.reference-option.selected');
                    const confirmArtistSelect = document.getElementById('artist');
                    const confirmArtistValue = confirmArtistSelect ? confirmArtistSelect.value : '';
                    const dateValue = document.getElementById('appointment_date')?.value;
                    const timeValue = document.getElementById('appointment_time')?.value;

                    if (!serviceSelected || !complexitySelected || !referenceSelected || 
                        !confirmArtistValue || !dateValue || !timeValue) {
                        return false;
                    }
                    return true;

                default:
                    return true;
            }
        }

        updateStepDisplay() {
            const isRemoval = document.querySelector('.service-category.selected')?.dataset.category === 'removal';
            
            // Update step indicators
            document.querySelectorAll('.step').forEach((step, index) => {
                const stepNumber = index + 1;
                step.classList.toggle('active', stepNumber === this.currentStep);
                step.classList.toggle('completed', stepNumber < this.currentStep);
                
                // Dim Step 3 for removal since it's skipped
                if (stepNumber === 3) {
                    step.style.opacity = isRemoval ? '0.4' : '1';
                    step.style.pointerEvents = isRemoval ? 'none' : 'auto';
                }
            });

            // Update step content
            document.querySelectorAll('.booking-step').forEach((step, index) => {
                const stepNumber = index + 1;
                step.classList.toggle('active', stepNumber === this.currentStep);
            });

            // Update selection summary visibility
            const selectionSummary = document.getElementById('selectionSummary');
            if (this.currentStep > 1 && this.currentStep < 6) {
                selectionSummary.style.display = 'block';
                this.updateSelectionSummary();
            } else {
                selectionSummary.style.display = 'none';
            }

            // Update confirmation step summary
            if (this.currentStep === 6) {
                this.updateConfirmationSummary();
                // Let DynamicBookingSystem handle submit button state
                if (window.dynamicBookingSystem) {
                    window.dynamicBookingSystem.validateForm();
                }
            }
        }

        updateSelectionSummary() {
            // Service
            const selectedService = document.querySelector('.service-category.selected');
            document.getElementById('selectedService').textContent =
                selectedService ? selectedService.querySelector('h3').textContent : '-';

            // Complexity
            const selectedComplexity = document.querySelector('.complexity-option.selected');
            document.getElementById('selectedComplexity').textContent =
                selectedComplexity ? selectedComplexity.querySelector('.complexity-name').textContent : '-';

            // Artist
            const artist = document.getElementById('artist');
            const artistName = artist ? artist.options[artist.selectedIndex].text : '-';
            document.getElementById('selectedArtist').textContent = artistName;

            // Price
            const selectedPrice = selectedComplexity ? selectedComplexity.dataset.price : 0;
            document.getElementById('selectedPrice').textContent = `₱${selectedPrice}`;
            
            // Date
            const dateInput = document.getElementById('appointment_date');
            const dateDisplay = document.getElementById('selectedDateDisplay');
            if (dateInput && dateInput.value && dateDisplay) {
                // T00:00:00 prevents timezone shift on local parse
                dateDisplay.textContent = new Date(dateInput.value + 'T00:00:00').toLocaleDateString();
            } else if (dateDisplay) {
                dateDisplay.textContent = '-';
            }

            // Time
            const timeInput = document.getElementById('appointment_time');
            const timeDisplay = document.getElementById('selectedTimeDisplay');
            if (timeInput && timeInput.value && timeDisplay) {
                timeDisplay.textContent = this.formatTime(timeInput.value);
            } else if (timeDisplay) {
                timeDisplay.textContent = '-';
            }

            // Design
            const selectedDesign = document.getElementById('selectedDesign');
            if (selectedDesign) {
                if (selectedService && selectedService.dataset.category === 'removal') {
                    selectedDesign.textContent = 'Nail Removal';
                } else {
                    const selectedReference = document.querySelector('.reference-option.selected');
                    if (selectedReference) {
                        const type = selectedReference.dataset.reference;
                        if (type === 'upload') {
                            const fileName = document.getElementById('selectedFileName')?.textContent || 'Uploaded Image';
                            selectedDesign.textContent = `Custom (${fileName})`;
                        } else {
                            const galleryId = document.querySelector('.gallery-item.selected')?.dataset.imageId;
                            selectedDesign.textContent = `Gallery (ID: ${galleryId || '-'})`;
                        }
                    } else {
                        selectedDesign.textContent = '-';
                    }
                }
            }
        }

        updateConfirmationSummary() {
            // Service
            const selectedService = document.querySelector('.service-category.selected');
            const serviceName = selectedService ? selectedService.querySelector('h3').textContent : '-';
            document.getElementById('summary-service').textContent = serviceName;

            // Complexity
            const selectedComplexity = document.querySelector('.complexity-option.selected');
            const complexityName = selectedComplexity ? selectedComplexity.querySelector('.complexity-name').textContent : '-';
            document.getElementById('summary-complexity').textContent = complexityName;

            // Artist
            const artist = document.getElementById('artist');
            const artistName = artist ? artist.options[artist.selectedIndex].text : '-';
            document.getElementById('summary-artist').textContent = artistName;

            // Date
            const date = document.getElementById('appointment_date').value;
            document.getElementById('summary-date').textContent = date ? new Date(date).toLocaleDateString() : '-';

            // Time
            const time = document.getElementById('appointment_time').value;
            document.getElementById('summary-time').textContent = time ? this.formatTime(time) : '-';

            // Price
            const basePrice = selectedService ?
                (selectedService.dataset.category === 'soft_gel_extensions' ? 800 : (selectedService.dataset.category === 'removal' ? 0 : 350)) : 0;
            const complexityPrice = selectedComplexity ? parseInt(selectedComplexity.dataset.price) : 0;
            const totalPrice = basePrice + complexityPrice;
            document.getElementById('summary-price').textContent = `₱${totalPrice}`;

            // Design
            const summaryDesign = document.getElementById('summary-design');
            if (summaryDesign) {
                if (selectedService && selectedService.dataset.category === 'removal') {
                    summaryDesign.textContent = 'Nail Removal';
                } else {
                    const selectedReference = document.querySelector('.reference-option.selected');
                    if (selectedReference) {
                        summaryDesign.textContent = selectedReference.dataset.reference === 'upload' ? 'Custom Design' : 'Gallery Inspiration';
                    } else {
                        summaryDesign.textContent = '-';
                    }
                }
            }
        }

        formatTime(time) {
            const [hours, minutes] = time.split(':');
            const hour = parseInt(hours);
            const minute = parseInt(minutes);
            const period = hour >= 12 ? 'PM' : 'AM';
            const displayHour = hour > 12 ? hour - 12 : (hour === 0 ? 12 : hour);
            return `${displayHour}:${minute.toString().padStart(2, '0')} ${period}`;
        }

        showNotification(message) {
            // Create notification element if it doesn't exist
            let notification = document.getElementById('bookingNotification');
            if (!notification) {
                notification = document.createElement('div');
                notification.id = 'bookingNotification';
                notification.className = 'alert alert-warning alert-dismissible fade show';
                notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
                notification.innerHTML = `
                    <button type="button" class="btn-close" data-dismiss="alert">&times;</button>
                    ${message}
                `;
                document.body.appendChild(notification);

                // Auto-remove after 3 seconds
                setTimeout(() => {
                    if (notification && notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 3000);
            }
        }
    }

    // Initialize the navigation system
    window.bookingStepNavigation = new BookingStepNavigation();

    // Fix navigation buttons to work with the actual HTML structure
    document.addEventListener('DOMContentLoaded', function () {
        // Add event listeners to all navigation buttons
        document.querySelectorAll('.prev-btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                if (window.bookingStepNavigation.validateCurrentStep()) {
                    window.bookingStepNavigation.previousStep();
                }
            });
        });

        document.querySelectorAll('.next-btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                if (window.bookingStepNavigation.validateCurrentStep()) {
                    window.bookingStepNavigation.nextStep();
                }
            });
        });

        // Add click handlers for service categories
        document.querySelectorAll('.service-category').forEach(card => {
            card.addEventListener('click', function () {
                // Remove selected class from all cards
                document.querySelectorAll('.service-category').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');

                // Update hidden input
                const serviceCategory = card.dataset.category;
                const hiddenInput = document.getElementById('serviceCategory');
                if (hiddenInput) {
                    hiddenInput.value = serviceCategory;
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        });

        // Add click handlers for complexity options
        document.querySelectorAll('.complexity-option').forEach(card => {
            card.addEventListener('click', function () {
                // Remove selected class from all cards
                document.querySelectorAll('.complexity-option').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');

                // Update hidden input
                const complexityLevel = card.dataset.complexity;
                const hiddenInput = document.getElementById('complexityLevel');
                if (hiddenInput) {
                    hiddenInput.value = complexityLevel;
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        });

        // Add click handlers for gallery items
        document.querySelectorAll('.gallery-item').forEach(item => {
            item.addEventListener('click', function () {
                // Remove selected class from all items
                document.querySelectorAll('.gallery-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');

                // Update hidden input
                const hiddenInput = document.getElementById('galleryImageId');
                if (hiddenInput) {
                    hiddenInput.value = this.dataset.imageId;
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        });

        // Add change handlers for file upload
        const fileInput = document.getElementById('referenceFile');
        if (fileInput) {
            fileInput.addEventListener('change', function () {
                const file = this.files[0];
                if (file) {
                    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
                    
                    if (!validTypes.includes(file.type)) {
                        window.bookingStepNavigation.showNotification('Only JPG and PNG formats are allowed.');
                        this.value = ''; // clears invalid file
                        return;
                    }
                    if (file.size > 2 * 1024 * 1024) { // 2MB limit
                        window.bookingStepNavigation.showNotification('Maximum file size is 2MB.');
                        this.value = ''; // clears invalid file
                        return;
                    }
                    
                    const displayElement = document.getElementById('selectedFileName');
                    if (displayElement) {
                        displayElement.textContent = file.name;
                    }
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        }

        // Add click handlers for reference options
        document.querySelectorAll('.reference-option').forEach(option => {
            option.addEventListener('click', function () {
                // Handle radio button selection
                const radio = option.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                }

                // Remove selected class from all options
                document.querySelectorAll('.reference-option').forEach(o => o.classList.remove('selected'));
                option.classList.add('selected');

                // Show/hide appropriate sections
                const uploadSection = document.getElementById('uploadSection');
                const gallerySection = document.getElementById('gallerySection');
                const designNoteSection = document.getElementById('designNoteSection');
                
                if (uploadSection) uploadSection.classList.add('hidden');
                if (gallerySection) gallerySection.classList.add('hidden');
                if (designNoteSection) designNoteSection.classList.add('hidden');

                const referenceType = option.dataset.reference;
                if (referenceType === 'upload') {
                    if (uploadSection) uploadSection.classList.remove('hidden');
                    if (designNoteSection) designNoteSection.classList.remove('hidden');
                } else if (referenceType === 'gallery') {
                    if (gallerySection) gallerySection.classList.remove('hidden');
                    if (designNoteSection) designNoteSection.classList.remove('hidden');
                }

                // Update hidden input
                const hiddenInput = document.getElementById('referenceType');
                if (hiddenInput) {
                    hiddenInput.value = referenceType;
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        });

        // Add change handlers for artist selection
        const artistSelect = document.getElementById('artist');
        if (artistSelect) {
            artistSelect.addEventListener('change', function () {
                // Update summary
                const selectedOption = this.options[this.selectedIndex];
                const artistNameElement = document.getElementById('selectedArtist');
                const artistInfo = document.getElementById('selectedArtistInfo');
                const selectedArtistName = document.getElementById('selectedArtistName');
                const selectedArtistStatus = document.getElementById('selectedArtistStatus');
                
                if (artistNameElement) {
                    artistNameElement.textContent = selectedOption ? selectedOption.text.split(' - ')[0] : '-';
                }
                
                // Show/hide artist info section
                if (artistInfo && selectedArtistName && selectedArtistStatus) {
                    if (this.value && selectedOption) {
                        artistInfo.style.display = 'block';
                        const artistText = selectedOption.textContent.trim();
                        const artistName = artistText.split(' - ')[0]; // Get name before status
                        
                        selectedArtistName.textContent = artistName;
                        selectedArtistStatus.textContent = selectedOption.getAttribute('data-status') || 'Available';
                    } else {
                        artistInfo.style.display = 'none';
                        selectedArtistName.textContent = '-';
                        selectedArtistStatus.textContent = '-';
                    }
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        }

        // Add change handlers for date/time
        const dateInput = document.getElementById('appointment_date');
        const timeInput = document.getElementById('appointment_time');

        if (dateInput) {
            dateInput.addEventListener('change', function () {
                const dateDisplay = document.getElementById('selectedDateDisplay');
                if (dateDisplay) {
                    dateDisplay.textContent = this.value ? new Date(this.value).toLocaleDateString() : '-';
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        }

        if (timeInput) {
            timeInput.addEventListener('change', function () {
                const timeDisplay = document.getElementById('selectedTimeDisplay');
                if (timeDisplay) {
                    timeDisplay.textContent = this.value || '-';
                }

                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        }

        // Initialize first step
        window.bookingStepNavigation.updateStepDisplay();

        // Add acknowledgment checkbox handler
        const acknowledgeCheckbox = document.getElementById('acknowledge48Hour');
        if (acknowledgeCheckbox) {
            acknowledgeCheckbox.addEventListener('change', function () {
                // Update step navigation validation
                if (window.bookingStepNavigation) {
                    window.bookingStepNavigation.validateCurrentStep();
                }
            });
        }
    });

    // Legacy functions for backward compatibility
    function updateNextButton() {
        let canProceed = false;

        if (currentStep === 1) {
            // Service step - check if service is selected
            const serviceSelected = document.querySelector('input[name="core_category"]:checked');
            canProceed = serviceSelected !== null;
            console.log('Step 1 validation:', canProceed ? 'Service selected' : 'No service selected');
        } else if (currentStep === 2) {
            // Artist step - check if artist is selected
            const artistSelected = document.querySelector('input[name="artist"]:checked');
            canProceed = artistSelected !== null;
            console.log('Step 2 validation:', canProceed ? 'Artist selected' : 'No artist selected');
        } else if (currentStep === 3) {
            // Date step - check if date is selected
            const dateSelected = document.getElementById('selected-date').value;
            canProceed = dateSelected !== '';
            console.log('Step 3 validation:', canProceed ? 'Date selected' : 'No date selected');
        } else if (currentStep === 4) {
            // Time step - check if time is selected
            const timeSelected = document.querySelector('input[name="time"]:checked');
            canProceed = timeSelected !== null;
            console.log('Step 4 validation:', canProceed ? 'Time selected' : 'No time selected');
        } else if (currentStep === 5) {
            // Final step - always allow submission
            canProceed = true;
        }

        if (nextBtn) {
            nextBtn.disabled = !canProceed;
            nextBtn.style.opacity = canProceed ? '1' : '0.5';
            nextBtn.style.cursor = canProceed ? 'pointer' : 'not-allowed';
        }
    }

    function showStep(step) {
        document.querySelectorAll('.booking-step').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));

        document.getElementById(`step-${step}`).classList.add('active');
        document.querySelector(`.step[data-step="${step}"]`).classList.add('active');

        if (prevBtn) prevBtn.disabled = step === 1;
        if (nextBtn) nextBtn.style.display = step === totalSteps ? 'none' : 'flex';

        // Update step number indicators
        document.querySelectorAll('.step-number').forEach((num, index) => {
            if (index + 1 <= step) {
                num.classList.add('completed');
            }
            if (index + 1 === step) {
                num.classList.add('active');
            }
        });

        // Update Next button state when changing steps
        updateNextButton();
    }

    // Navigation buttons
    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            if (currentStep < totalSteps && !nextBtn.disabled) {
                currentStep++;
                showStep(currentStep);
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
            }
        });
    }

    // Service selection
    document.querySelectorAll('input[name="core_category"]').forEach(input => {
        input.addEventListener('change', function () {
            console.log('Service selected:', this.value);
            const builderChecklists = document.getElementById('builder-checklists');
            const builderEstimate = document.getElementById('builder-estimate');
            const tipCustomizationBlock = document.getElementById('checklist-tip-customization');

            if (this.value) {
                if (builderChecklists) builderChecklists.style.display = 'block';
                if (builderEstimate) builderEstimate.style.display = 'block';
                if (tipCustomizationBlock) {
                    tipCustomizationBlock.style.display = this.value === 'soft_gel_extensions' ? 'block' : 'none';
                }
            }

            // Update Next button state
            updateNextButton();
        });
    });

    // Artist selection
    document.querySelectorAll('.artist-card').forEach(card => {
        card.addEventListener('click', function () {
            const radioInput = card.querySelector('input[name="artist"]');
            if (radioInput) {
                document.querySelectorAll('.artist-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                radioInput.checked = true;

                // Update Next button state
                updateNextButton();
            }
        });
    });

    // Advanced Interactive Calendar functionality
    const calContainer = document.querySelector('.calendar-container');
    if (calContainer) {
        let currentDate = new Date();
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const minBookingDate = new Date(today);
        minBookingDate.setDate(minBookingDate.getDate() + 1); // Earliest allowable is tomorrow

        let currentMonth = currentDate.getMonth();
        let currentYear = currentDate.getFullYear();

        const monthDisplay = document.getElementById('calendarMonthDisplay');
        const grid = document.getElementById('calendarDaysGrid');
        const timeSlotsContainer = document.getElementById('timeSlotsContainer');
        const timeSlotsGrid = document.getElementById('timeSlotsGrid');
        const hiddenDate = document.getElementById('appointment_date');
        const hiddenTime = document.getElementById('appointment_time');

        const availableHours = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00'];

        function formatTimeDisplay(timeStr) {
            let [h, m] = timeStr.split(':');
            h = parseInt(h);
            let ampm = h >= 12 ? 'PM' : 'AM';
            let formattedH = h % 12 || 12;
            return `${formattedH}:${m} ${ampm}`;
        }

        function renderCalendar() {
            if (!grid) return;
            grid.innerHTML = '';

            const firstDay = new Date(currentYear, currentMonth, 1).getDay();
            const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
            const dateStr = new Date(currentYear, currentMonth, 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

            if (monthDisplay) monthDisplay.textContent = dateStr;

            for (let i = 0; i < firstDay; i++) {
                grid.innerHTML += `<div class="calendar-day empty"></div>`;
            }

            for (let i = 1; i <= daysInMonth; i++) {
                const dayDate = new Date(currentYear, currentMonth, i);
                dayDate.setHours(0, 0, 0, 0);

                const isoDateStr = `${currentYear}-${(currentMonth + 1).toString().padStart(2, '0')}-${i.toString().padStart(2, '0')}`;

                let extraClasses = '';
                if (dayDate < minBookingDate) extraClasses += ' disabled';
                if (dayDate.getDay() === 0) extraClasses += ' disabled'; // Disable Sundays (day 0)
                if (hiddenDate && hiddenDate.value === isoDateStr) extraClasses += ' selected';

                grid.innerHTML += `<div class="calendar-day${extraClasses}" data-date="${isoDateStr}">${i}</div>`;
            }
        }

        function renderTimeSlots(dateString) {
            if (!timeSlotsContainer || !timeSlotsGrid) return;
            timeSlotsContainer.classList.remove('hidden');
            timeSlotsGrid.innerHTML = '';

            const bookedTimes = window.bookedSlotsData && window.bookedSlotsData[dateString] ? window.bookedSlotsData[dateString] : [];

            availableHours.forEach(time => {
                // Backend might send "14:00:00" or just "14:00"
                const isBooked = bookedTimes.includes(time) || bookedTimes.includes(time + ":00");
                const isSelected = hiddenTime && hiddenTime.value === time;

                const slotDiv = document.createElement('div');
                slotDiv.className = `time-slot ${isBooked ? 'booked' : ''} ${isSelected ? 'selected' : ''}`;

                const label = document.createElement('label');
                if (isBooked) {
                    label.innerHTML = `
                        <div class="time-text">${formatTimeDisplay(time)}</div>
                        <div class="booked-text" style="font-size: 0.75rem; color: #dc3545; margin-top: 2px;">Booked</div>
                    `;
                } else {
                    label.innerHTML = `<div class="time-text">${formatTimeDisplay(time)}</div>`;
                }
                slotDiv.appendChild(label);

                if (!isBooked) {
                    slotDiv.addEventListener('click', function () {
                        document.querySelectorAll('.time-slot.selected').forEach(d => d.classList.remove('selected'));
                        slotDiv.classList.add('selected');
                        if (hiddenTime) {
                            hiddenTime.value = time;
                            hiddenTime.dispatchEvent(new Event('change'));
                            updateNextButton();
                        }
                    });
                }

                timeSlotsGrid.appendChild(slotDiv);
            });
        }

        const prevBtnNav = document.getElementById('prevMonth');
        if (prevBtnNav) {
            prevBtnNav.addEventListener('click', () => {
                const tempDate = new Date(currentYear, currentMonth - 1, 1);
                if (tempDate >= new Date(today.getFullYear(), today.getMonth(), 1)) {
                    currentMonth--;
                    if (currentMonth < 0) { currentMonth = 11; currentYear--; }
                    renderCalendar();
                }
            });
        }

        const nextMBtnNav = document.getElementById('nextMonth');
        if (nextMBtnNav) {
            nextMBtnNav.addEventListener('click', () => {
                currentMonth++;
                if (currentMonth > 11) { currentMonth = 0; currentYear++; }
                renderCalendar();
            });
        }

        if (grid) {
            grid.addEventListener('click', (e) => {
                const dayEl = e.target.closest('.calendar-day');
                if (dayEl && !dayEl.classList.contains('disabled') && !dayEl.classList.contains('empty') && !dayEl.classList.contains('booked')) {
                    document.querySelectorAll('.calendar-day.selected').forEach(d => d.classList.remove('selected'));
                    dayEl.classList.add('selected');

                    const dateVal = dayEl.dataset.date;
                    if (hiddenDate) {
                        hiddenDate.value = dateVal;
                        hiddenDate.dispatchEvent(new Event('change'));
                    }
                    if (hiddenTime) {
                        hiddenTime.value = '';
                        hiddenTime.dispatchEvent(new Event('change'));
                    }
                    updateNextButton();
                    renderTimeSlots(dateVal);
                }
            });
        }

        renderCalendar();
        if (hiddenDate && hiddenDate.value) {
            renderTimeSlots(hiddenDate.value);
        }
    }

    // Initialize
    showStep(currentStep);
    updateNextButton();
    console.log('Booking form initialized with validation');
});

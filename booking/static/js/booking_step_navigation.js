// Simplified step-based booking form navigation
// Works with dynamic_booking.js for form functionality

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
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateStepDisplay();
        }
    }

    previousStep() {
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
                const artist = document.getElementById('artist').value;
                if (!artist) {
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
                return true;
            
            default:
                return true;
        }
    }

    updateStepDisplay() {
        // Update step indicators
        document.querySelectorAll('.step').forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.toggle('active', stepNumber === this.currentStep);
            step.classList.toggle('completed', stepNumber < this.currentStep);
        });

        // Update step content
        document.querySelectorAll('.booking-step').forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.toggle('active', stepNumber === this.currentStep);
        });

        // Update selection summary visibility
        const selectionSummary = document.getElementById('selectionSummary');
        if (this.currentStep > 1) {
            selectionSummary.style.display = 'block';
            this.updateSelectionSummary();
        } else {
            selectionSummary.style.display = 'none';
        }

        // Update confirmation step summary
        if (this.currentStep === 6) {
            this.updateConfirmationSummary();
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
            (selectedService.dataset.category === 'soft_gel_extensions' ? 800 : 350) : 0;
        const complexityPrice = selectedComplexity ? parseInt(selectedComplexity.dataset.price) : 0;
        const totalPrice = basePrice + complexityPrice;
        document.getElementById('summary-price').textContent = `₱${totalPrice}`;
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

document.addEventListener('DOMContentLoaded', () => {
    window.bookingStepNavigation = new BookingStepNavigation();
});

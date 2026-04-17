class PayMongoPayment {
    constructor() {
        this.checkoutSession = null;
        this.bookingData = null;
        this.init();
    }
    
    init() {
        // Enable payment button when acknowledgment checkbox is checked
        const acknowledgeCheckbox = document.getElementById('acknowledge48Hour');
        const payBtn = document.getElementById('payBtn');
        
        if (acknowledgeCheckbox && payBtn) {
            acknowledgeCheckbox.addEventListener('change', () => {
                payBtn.disabled = !acknowledgeCheckbox.checked;
            });
        }
    }
    
    async processPayment() {
        try {
            // Validate that all required data is available
            if (!this.validateBookingData()) {
                return;
            }
            
            // Show loading state
            this.showProcessing(true);
            
            // Create checkout session
            const response = await fetch('/api/create-checkout-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    amount: this.getTotalPrice(),
                    description: 'Nail Appointment Booking',
                    booking_data: this.getBookingData()
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Redirect to PayMongo checkout
                window.location.href = data.checkout_url;
            } else {
                this.showError(data.error || 'Failed to create payment session');
            }
            
        } catch (error) {
            console.error('Payment processing error:', error);
            this.showError('Payment processing failed. Please try again.');
        } finally {
            this.showProcessing(false);
        }
    }
    
    validateBookingData() {
        // Check if all booking steps are completed
        const selectedService = document.querySelector('.service-category.selected');
        const selectedComplexity = document.querySelector('.complexity-option.selected');
        const artist = document.getElementById('artist').value;
        const date = document.getElementById('appointment_date').value;
        const time = document.getElementById('appointment_time').value;
        const acknowledgeCheckbox = document.getElementById('acknowledge48Hour');
        
        if (!selectedService) {
            this.showError('Please select a service type');
            return false;
        }
        
        if (!selectedComplexity) {
            this.showError('Please select a complexity level');
            return false;
        }
        
        if (!artist) {
            this.showError('Please select an artist');
            return false;
        }
        
        if (!date || !time) {
            this.showError('Please select appointment date and time');
            return false;
        }
        
        if (!acknowledgeCheckbox.checked) {
            this.showError('Please acknowledge the cancellation policy');
            return false;
        }
        
        return true;
    }
    
    getBookingData() {
        const selectedService = document.querySelector('.service-category.selected');
        const selectedComplexity = document.querySelector('.complexity-option.selected');
        const artist = document.getElementById('artist');
        const referenceOption = document.querySelector('.reference-option.selected');
        const referenceFile = document.getElementById('referenceFile');
        
        return {
            service_category: selectedService ? selectedService.dataset.category : '',
            complexity_level: selectedComplexity ? selectedComplexity.dataset.complexity : '',
            artist_id: artist ? artist.value : '',
            appointment_date: document.getElementById('appointment_date').value,
            appointment_time: document.getElementById('appointment_time').value,
            reference_type: referenceOption ? referenceOption.dataset.reference : '',
            gallery_image_id: document.getElementById('galleryImageId').value,
            custom_art_description: document.getElementById('designNote').value,
            reference_file: referenceFile && referenceFile.files.length > 0 ? referenceFile.files[0].name : null
        };
    }
    
    getTotalPrice() {
        const priceText = document.getElementById('summary-price').textContent;
        return parseInt(priceText.replace('₱', '').replace(',', ''));
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    showProcessing(show) {
        const payBtn = document.getElementById('payBtn');
        if (show) {
            payBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Processing...';
            payBtn.disabled = true;
        } else {
            payBtn.innerHTML = '<i class="bi bi-lock"></i> Confirm Payment';
            const acknowledgeCheckbox = document.getElementById('acknowledge48Hour');
            payBtn.disabled = !acknowledgeCheckbox.checked;
        }
    }
    
    showError(message) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.payment-notification');
        existingNotifications.forEach(notification => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
        
        // Create new notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger alert-dismissible fade show payment-notification';
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        notification.innerHTML = `
            <button type="button" class="btn-close" data-dismiss="alert">&times;</button>
            <i class="bi bi-exclamation-triangle"></i> ${message}
        `;
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    showSuccess(message) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.payment-notification');
        existingNotifications.forEach(notification => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
        
        // Create new notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show payment-notification';
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        notification.innerHTML = `
            <button type="button" class="btn-close" data-dismiss="alert">&times;</button>
            <i class="bi bi-check-circle"></i> ${message}
        `;
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// Initialize payment handler
document.addEventListener('DOMContentLoaded', () => {
    window.payMongoPayment = new PayMongoPayment();
});

// Global function for template
function processPayment() {
    window.payMongoPayment.processPayment();
}

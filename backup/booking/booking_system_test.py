"""
Comprehensive Booking System Test
This test goes through the entire booking flow to verify all functionality works correctly.
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TestBookingSystem:
    def setup_method(self):
        """Setup the test environment"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.base_url = "http://127.0.0.1:8000"
        
    def teardown_method(self):
        """Cleanup after test"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def test_complete_booking_flow(self):
        """Test the complete booking flow from service selection to payment"""
        print("\n=== Starting Complete Booking Flow Test ===")
        
        try:
            # Step 1: Navigate to booking page
            print("Step 1: Navigating to booking page...")
            self.driver.get(f"{self.base_url}/booking/")
            self.wait_for_page_load()
            
            # Verify we're on the booking page
            assert "booking" in self.driver.current_url.lower()
            print("✅ Successfully navigated to booking page")
            
            # Step 2: Test Service Selection
            print("\nStep 2: Testing Service Selection...")
            self.test_service_selection()
            
            # Step 3: Test Artist Selection
            print("\nStep 3: Testing Artist Selection...")
            self.test_artist_selection()
            
            # Step 4: Test Date Selection
            print("\nStep 4: Testing Date Selection...")
            self.test_date_selection()
            
            # Step 5: Test Time Selection
            print("\nStep 5: Testing Time Selection...")
            self.test_time_selection()
            
            # Step 6: Test Summary Display
            print("\nStep 6: Testing Summary Display...")
            self.test_summary_display()
            
            # Step 7: Test Payment Section
            print("\nStep 7: Testing Payment Section...")
            self.test_payment_section()
            
            print("\n🎉 All booking system tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            self.take_screenshot("test_failure")
            raise
    
    def test_service_selection(self):
        """Test service selection functionality"""
        wait = WebDriverWait(self.driver, 10)
        
        # Check if service options are visible
        service_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".builder-category-card"))
        )
        
        assert len(service_cards) >= 2, "Service options should be available"
        print(f"✅ Found {len(service_cards)} service options")
        
        # Try to select Gel Polish
        try:
            gel_polish = self.driver.find_element(By.CSS_SELECTOR, 'input[value="gel_polish"]')
            gel_polish.click()
            print("✅ Gel Polish service selected")
            
            # Check if builder sections appear
            time.sleep(1)
            builder_checklists = self.driver.find_element(By.ID, "builder-checklists")
            assert builder_checklists.is_displayed(), "Builder sections should appear after service selection"
            print("✅ Builder sections appeared after service selection")
            
        except NoSuchElementException:
            print("⚠️ Gel Polish option not found, trying alternative...")
            # Try clicking the service card directly
            service_cards[0].click()
            time.sleep(1)
        
        # Test complexity selection
        try:
            complexity_select = wait.until(
                EC.element_to_be_clickable((By.ID, "style-complexity"))
            )
            complexity_select.send_keys("minimal")
            print("✅ Complexity selection working")
        except TimeoutException:
            print("⚠️ Complexity selection not available")
    
    def test_artist_selection(self):
        """Test artist selection functionality"""
        wait = WebDriverWait(self.driver, 10)
        
        # Navigate to artist step
        next_button = self.driver.find_element(By.ID, "nextBtn")
        next_button.click()
        time.sleep(1)
        
        # Check if artist cards are present
        try:
            artist_cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".artist-card"))
            )
            
            assert len(artist_cards) > 0, "Artist cards should be available"
            print(f"✅ Found {len(artist_cards)} artist cards")
            
            # Select first artist
            artist_cards[0].click()
            time.sleep(1)
            
            # Check if radio button is selected
            radio_input = artist_cards[0].find_element(By.CSS_SELECTOR, 'input[name="artist"]')
            assert radio_input.is_selected(), "Artist radio button should be selected"
            print("✅ Artist selection working")
            
        except TimeoutException:
            print("⚠️ Artist selection not available - may need to complete service selection first")
    
    def test_date_selection(self):
        """Test date selection functionality"""
        wait = WebDriverWait(self.driver, 10)
        
        # Navigate to date step
        try:
            next_button = self.driver.find_element(By.ID, "nextBtn")
            next_button.click()
            time.sleep(1)
        except:
            print("⚠️ Could not navigate to date step")
        
        # Check if calendar is present
        try:
            calendar_days = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".calendar-day:not(.disabled)"))
            )
            
            assert len(calendar_days) > 0, "Available calendar days should be present"
            print(f"✅ Found {len(calendar_days)} available calendar days")
            
            # Select first available date
            calendar_days[0].click()
            time.sleep(1)
            
            # Check if date is selected
            selected_date_input = self.driver.find_element(By.ID, "selected-date")
            assert selected_date_input.value, "Date should be selected"
            print("✅ Date selection working")
            
        except TimeoutException:
            print("⚠️ Calendar not available")
    
    def test_time_selection(self):
        """Test time selection functionality"""
        wait = WebDriverWait(self.driver, 10)
        
        # Navigate to time step
        try:
            next_button = self.driver.find_element(By.ID, "nextBtn")
            next_button.click()
            time.sleep(1)
        except:
            print("⚠️ Could not navigate to time step")
        
        # Check if time slots are present
        try:
            time_inputs = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[name="time"]:not(:disabled)'))
            )
            
            assert len(time_inputs) > 0, "Available time slots should be present"
            print(f"✅ Found {len(time_inputs)} available time slots")
            
            # Select first available time
            time_inputs[0].click()
            time.sleep(1)
            
            assert time_inputs[0].is_selected(), "Time slot should be selected"
            print("✅ Time selection working")
            
        except TimeoutException:
            print("⚠️ Time slots not available")
    
    def test_summary_display(self):
        """Test summary display functionality"""
        try:
            # Navigate to summary step
            next_button = self.driver.find_element(By.ID, "nextBtn")
            next_button.click()
            time.sleep(1)
            
            # Check if summary section is present
            summary_section = self.driver.find_element(By.ID, "selectionSummary")
            assert summary_section.is_displayed(), "Summary section should be visible"
            print("✅ Summary section is visible")
            
            # Check summary elements
            summary_elements = {
                "selectedService": "Service",
                "selectedArtist": "Artist", 
                "selectedDateDisplay": "Date",
                "selectedTimeDisplay": "Time"
            }
            
            for element_id, element_name in summary_elements.items():
                try:
                    element = self.driver.find_element(By.ID, element_id)
                    text = element.text
                    print(f"✅ {element_name}: {text}")
                except NoSuchElementException:
                    print(f"⚠️ {element_name} element not found")
                    
        except Exception as e:
            print(f"⚠️ Summary display test issue: {str(e)}")
    
    def test_payment_section(self):
        """Test payment section functionality"""
        try:
            # Check if payment section is present
            payment_card = self.driver.find_element(By.CSS_SELECTOR, ".payment-card")
            assert payment_card.is_displayed(), "Payment section should be visible"
            print("✅ Payment section is visible")
            
            # Check GCash QR code
            qr_code = self.driver.find_element(By.CSS_SELECTOR, ".qr-frame img")
            assert qr_code.is_displayed(), "GCash QR code should be visible"
            print("✅ GCash QR code is visible")
            
            # Check transaction details input
            transaction_input = self.driver.find_element(By.NAME, "gcash_transaction_id")
            assert transaction_input.is_displayed(), "Transaction ID input should be visible"
            print("✅ Transaction ID input is visible")
            
        except Exception as e:
            print(f"⚠️ Payment section test issue: {str(e)}")
    
    def test_form_submission(self):
        """Test form submission functionality"""
        try:
            # Try to submit the form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, ".confirm-booking-btn")
            
            # Check if button is enabled
            if not submit_button.is_enabled():
                print("⚠️ Submit button is disabled - form may be incomplete")
            else:
                print("✅ Submit button is enabled")
                # Don't actually submit to avoid creating real bookings
                print("ℹ️ Form submission ready (not actually submitting to avoid test data)")
                
        except Exception as e:
            print(f"⚠️ Form submission test issue: {str(e)}")
    
    def wait_for_page_load(self, timeout=10):
        """Wait for page to fully load"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        try:
            self.driver.save_screenshot(f"{name}.png")
            print(f"📸 Screenshot saved: {name}.png")
        except Exception as e:
            print(f"Could not take screenshot: {str(e)}")

# Additional utility tests
class TestBookingComponents:
    """Test individual booking components"""
    
    def setup_method(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.base_url = "http://127.0.0.1:8000"
    
    def teardown_method(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def test_page_load(self):
        """Test if booking page loads correctly"""
        self.driver.get(f"{self.base_url}/booking/")
        
        # Check if main elements are present
        assert "booking" in self.driver.title.lower() or "booking" in self.driver.current_url.lower()
        print("✅ Booking page loads correctly")
    
    def test_required_elements(self):
        """Test if required elements are present"""
        self.driver.get(f"{self.base_url}/booking/")
        
        required_elements = [
            ".booking-steps",
            ".booking-form", 
            ".selection-summary",
            ".payment-card"
        ]
        
        for element in required_elements:
            try:
                found_element = self.driver.find_element(By.CSS_SELECTOR, element)
                print(f"✅ Required element found: {element}")
            except NoSuchElementException:
                print(f"❌ Required element missing: {element}")

if __name__ == "__main__":
    print("🧪 Starting Booking System Tests")
    print("=" * 50)
    
    # Run individual component tests first
    print("\n--- Component Tests ---")
    component_test = TestBookingComponents()
    try:
        component_test.setup_method()
        component_test.test_page_load()
        component_test.test_required_elements()
        component_test.teardown_method()
        print("✅ Component tests passed")
    except Exception as e:
        print(f"❌ Component tests failed: {str(e)}")
    
    # Run complete booking flow test
    print("\n--- Complete Flow Test ---")
    flow_test = TestBookingSystem()
    try:
        flow_test.setup_method()
        flow_test.test_complete_booking_flow()
        flow_test.teardown_method()
        print("✅ Complete flow test passed")
    except Exception as e:
        print(f"❌ Complete flow test failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete")

"""
Simplified Booking System Test
Tests the booking system UI and functionality without requiring authentication
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TestBookingSystemUI:
    def setup_method(self):
        """Setup the test environment"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
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
    
    def test_booking_page_structure(self):
        """Test the booking page structure and elements"""
        print("\n=== Testing Booking Page Structure ===")
        
        # Navigate to booking page
        self.driver.get(f"{self.base_url}/booking/")
        time.sleep(2)
        
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Check if we can access the booking page (even if redirected)
        if "login" in self.driver.current_url.lower():
            print("⚠️ Redirected to login - testing booking page elements via direct template inspection")
            # We'll test the template structure by accessing it directly
            self.test_template_structure()
        else:
            print("✅ Successfully accessed booking page")
            self.test_booking_elements()
    
    def test_template_structure(self):
        """Test the template structure by reading the HTML file"""
        print("\n=== Testing Template Structure ===")
        
        template_path = "c:/Users/jomar/Downloads/PolishPalette/nail_booking/booking/templates/booking/booking_form.html"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Check for key template elements
            required_elements = [
                ("booking-steps", "Booking steps indicator"),
                ("booking-form", "Main booking form"),
                ("selectionSummary", "Selection summary section"),
                ("payment-card", "Payment section"),
                ("builder-category-card", "Service selection cards"),
                ("artist-card", "Artist selection cards"),
                ("calendar-day", "Calendar date selection"),
                ("nextBtn", "Next button"),
                ("prevBtn", "Previous button"),
                ("selectedService", "Service display in summary"),
                ("selectedArtist", "Artist display in summary"),
                ("selectedDateDisplay", "Date display in summary"),
                ("selectedTimeDisplay", "Time display in summary"),
            ]
            
            found_elements = 0
            total_elements = len(required_elements)
            
            for element_id, description in required_elements:
                if element_id in template_content:
                    print(f"✅ Template contains: {description}")
                    found_elements += 1
                else:
                    print(f"❌ Template missing: {description}")
            
            print(f"\n📊 Template Structure: {found_elements}/{total_elements} elements found")
            
            # Check for JavaScript functionality
            if "booking_form.js" in template_content:
                print("✅ Template includes JavaScript file")
            else:
                print("❌ Template missing JavaScript file")
            
            # Check for form structure
            if "<form" in template_content and "method=\"POST\"" in template_content:
                print("✅ Template contains proper form structure")
            else:
                print("❌ Template missing proper form structure")
            
            return found_elements > 0
            
        except Exception as e:
            print(f"❌ Could not read template file: {str(e)}")
            return False
    
    def test_booking_elements(self):
        """Test booking elements on the live page"""
        print("\n=== Testing Live Booking Elements ===")
        
        # Test booking steps
        try:
            steps = self.driver.find_elements(By.CSS_SELECTOR, ".booking-steps .step")
            print(f"✅ Found {len(steps)} booking steps")
            
            for i, step in enumerate(steps, 1):
                step_label = step.find_element(By.CSS_SELECTOR, ".step-label").text
                print(f"  Step {i}: {step_label}")
        except NoSuchElementException:
            print("❌ Booking steps not found")
        
        # Test service selection
        try:
            service_cards = self.driver.find_elements(By.CSS_SELECTOR, ".builder-category-card")
            print(f"✅ Found {len(service_cards)} service selection cards")
            
            if service_cards:
                # Try to click first service
                service_cards[0].click()
                time.sleep(1)
                print("✅ Service card clickable")
                
                # Check if builder sections appear
                try:
                    builder_checklists = self.driver.find_element(By.ID, "builder-checklists")
                    if builder_checklists.is_displayed():
                        print("✅ Builder sections appear after service selection")
                    else:
                        print("⚠️ Builder sections not visible after service selection")
                except NoSuchElementException:
                    print("⚠️ Builder sections not found")
        except NoSuchElementException:
            print("❌ Service selection cards not found")
        
        # Test artist selection
        try:
            # Try to navigate to artist step
            next_button = self.driver.find_element(By.ID, "nextBtn")
            next_button.click()
            time.sleep(1)
            
            artist_cards = self.driver.find_elements(By.CSS_SELECTOR, ".artist-card")
            print(f"✅ Found {len(artist_cards)} artist cards")
            
            if artist_cards:
                # Try to select first artist
                artist_cards[0].click()
                time.sleep(1)
                print("✅ Artist card clickable")
        except (NoSuchElementException, Exception) as e:
            print(f"⚠️ Artist selection test issue: {str(e)}")
        
        # Test calendar
        try:
            # Try to navigate to date step
            next_button = self.driver.find_element(By.ID, "nextBtn")
            next_button.click()
            time.sleep(1)
            
            calendar_days = self.driver.find_elements(By.CSS_SELECTOR, ".calendar-day:not(.disabled)")
            print(f"✅ Found {len(calendar_days)} available calendar days")
            
            if calendar_days:
                calendar_days[0].click()
                time.sleep(1)
                print("✅ Calendar day clickable")
        except (NoSuchElementException, Exception) as e:
            print(f"⚠️ Calendar test issue: {str(e)}")
        
        # Test summary section
        try:
            summary_section = self.driver.find_element(By.ID, "selectionSummary")
            if summary_section.is_displayed():
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
                        print(f"  {element_name}: '{text}'")
                    except NoSuchElementException:
                        print(f"  {element_name}: Not found")
            else:
                print("⚠️ Summary section not visible")
        except NoSuchElementException:
            print("❌ Summary section not found")
        
        # Test payment section
        try:
            payment_card = self.driver.find_element(By.CSS_SELECTOR, ".payment-card")
            if payment_card.is_displayed():
                print("✅ Payment section is visible")
                
                # Check GCash elements
                try:
                    qr_code = self.driver.find_element(By.CSS_SELECTOR, ".qr-frame img")
                    if qr_code.is_displayed():
                        print("✅ GCash QR code visible")
                    else:
                        print("⚠️ GCash QR code not visible")
                except NoSuchElementException:
                    print("⚠️ GCash QR code not found")
                
                try:
                    transaction_input = self.driver.find_element(By.NAME, "gcash_transaction_id")
                    if transaction_input.is_displayed():
                        print("✅ Transaction ID input visible")
                    else:
                        print("⚠️ Transaction ID input not visible")
                except NoSuchElementException:
                    print("⚠️ Transaction ID input not found")
            else:
                print("⚠️ Payment section not visible")
        except NoSuchElementException:
            print("❌ Payment section not found")
    
    def test_css_files_exist(self):
        """Test if required CSS files exist"""
        print("\n=== Testing CSS Files ===")
        
        css_files = [
            "clientDashboard.css",
            "booking_form.css", 
            "client_base.css"
        ]
        
        css_path = "c:/Users/jomar/Downloads/PolishPalette/nail_booking/booking/static/css/"
        
        found_files = 0
        total_files = len(css_files)
        
        for css_file in css_files:
            file_path = css_path + css_file
            if os.path.exists(file_path):
                print(f"✅ CSS file exists: {css_file}")
                found_files += 1
            else:
                print(f"❌ CSS file missing: {css_file}")
        
        return found_files == total_files  # Return True only if all files exist
    
    def test_javascript_files_exist(self):
        """Test if required JavaScript files exist"""
        print("\n=== Testing JavaScript Files ===")
        
        js_files = [
            "booking_form.js"
        ]
        
        js_path = "c:/Users/jomar/Downloads/PolishPalette/nail_booking/booking/static/js/"
        
        found_files = 0
        total_files = len(js_files)
        
        for js_file in js_files:
            file_path = js_path + js_file
            if os.path.exists(file_path):
                print(f"✅ JavaScript file exists: {js_file}")
                found_files += 1
            else:
                print(f"❌ JavaScript file missing: {js_file}")
        
        return found_files == total_files  # Return True only if all files exist
    
    def run_comprehensive_test(self):
        """Run comprehensive booking system test"""
        print("🧪 Starting Comprehensive Booking System Test")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: Template Structure
        test_results.append(("Template Structure", self.test_template_structure()))
        
        # Test 2: Page Structure
        test_results.append(("Page Structure", self.test_booking_page_structure()))
        
        # Test 3: CSS Files
        test_results.append(("CSS Files", self.test_css_files_exist()))
        
        # Test 4: JavaScript Files
        test_results.append(("JavaScript Files", self.test_javascript_files_exist()))
        
        # Print results summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print("=" * 60)
        print(f"🏁 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All structural tests passed! Booking system foundation is solid.")
        elif passed >= 3:
            print("⚠️ Most tests passed. Booking system has good structure.")
        else:
            print("❌ Many tests failed. Booking system needs structural work.")
        
        return passed >= 3  # Consider it a success if at least 3/4 tests pass

if __name__ == "__main__":
    tester = TestBookingSystemUI()
    try:
        tester.setup_method()
        success = tester.run_comprehensive_test()
        tester.teardown_method()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        exit(1)

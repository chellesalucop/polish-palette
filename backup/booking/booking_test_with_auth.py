"""
Booking System Test with Authentication
This test handles login first, then tests the booking system.
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TestBookingSystemWithAuth:
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
    
    def login_as_client(self):
        """Login as a client user"""
        print("🔐 Logging in as client...")
        
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login/")
        
        try:
            # Fill login form
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            username_input.send_keys("testclient@example.com")  # Test user email
            password_input.send_keys("testpass123")  # Test user password
            
            # Submit form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                lambda driver: "login" not in driver.current_url.lower()
            )
            
            print("✅ Successfully logged in")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def test_booking_page_access(self):
        """Test if we can access the booking page after login"""
        print("\n=== Testing Booking Page Access ===")
        
        # Try to login first
        if not self.login_as_client():
            print("⚠️ Could not login, testing booking page directly...")
        
        # Navigate to booking page
        self.driver.get(f"{self.base_url}/booking/")
        time.sleep(2)
        
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Check if we're on booking page or redirected to login
        if "login" in self.driver.current_url.lower():
            print("❌ Redirected to login - authentication required")
            return False
        elif "booking" in self.driver.current_url.lower():
            print("✅ Successfully accessed booking page")
            return True
        else:
            print("⚠️ Unexpected page")
            return False
    
    def test_booking_elements_present(self):
        """Test if booking elements are present on the page"""
        print("\n=== Testing Booking Elements ===")
        
        if not self.test_booking_page_access():
            print("❌ Cannot test elements - cannot access booking page")
            return False
        
        # Check for key booking elements
        elements_to_check = [
            (".booking-steps", "Booking steps indicator"),
            (".booking-form", "Main booking form"),
            (".selection-summary", "Selection summary section"),
            (".payment-card", "Payment section"),
            (".builder-category-card", "Service selection cards"),
            ("#step-1", "Step 1 section"),
            ("#nextBtn", "Next button"),
            ("#prevBtn", "Previous button")
        ]
        
        found_elements = 0
        total_elements = len(elements_to_check)
        
        for selector, description in elements_to_check:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found: {description}")
                found_elements += 1
            except NoSuchElementException:
                print(f"❌ Missing: {description}")
        
        print(f"\n📊 Element Summary: {found_elements}/{total_elements} elements found")
        return found_elements > 0
    
    def test_service_selection(self):
        """Test service selection functionality"""
        print("\n=== Testing Service Selection ===")
        
        if not self.test_booking_page_access():
            return False
        
        try:
            # Look for service selection options
            service_selectors = [
                ".builder-category-card",
                'input[name="core_category"]',
                'input[value="gel_polish"]',
                'input[value="soft_gel_extensions"]'
            ]
            
            for selector in service_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found service elements: {selector} ({len(elements)} found)")
                        
                        # Try to click first service
                        if selector == ".builder-category-card":
                            elements[0].click()
                            time.sleep(1)
                            print("✅ Clicked service card")
                        elif selector.startswith('input'):
                            elements[0].click()
                            time.sleep(1)
                            print("✅ Clicked service radio button")
                        
                        return True
                except:
                    continue
            
            print("❌ No service selection elements found")
            return False
            
        except Exception as e:
            print(f"❌ Service selection test failed: {str(e)}")
            return False
    
    def test_artist_selection(self):
        """Test artist selection functionality"""
        print("\n=== Testing Artist Selection ===")
        
        try:
            # Try to navigate to artist step
            next_button = self.driver.find_element(By.ID, "nextBtn")
            next_button.click()
            time.sleep(1)
            
            # Look for artist cards
            artist_cards = self.driver.find_elements(By.CSS_SELECTOR, ".artist-card")
            if artist_cards:
                print(f"✅ Found {len(artist_cards)} artist cards")
                
                # Try to select first artist
                artist_cards[0].click()
                time.sleep(1)
                print("✅ Selected artist")
                return True
            else:
                print("❌ No artist cards found")
                return False
                
        except Exception as e:
            print(f"❌ Artist selection test failed: {str(e)}")
            return False
    
    def test_summary_functionality(self):
        """Test summary section functionality"""
        print("\n=== Testing Summary Functionality ===")
        
        try:
            # Look for summary elements
            summary_elements = [
                ("#selectedService", "Service display"),
                ("#selectedArtist", "Artist display"),
                ("#selectedDateDisplay", "Date display"),
                ("#selectedTimeDisplay", "Time display"),
                ("#selectedPrice", "Price display")
            ]
            
            found_summary = False
            for element_id, description in summary_elements:
                try:
                    element = self.driver.find_element(By.ID, element_id)
                    text = element.text
                    print(f"✅ {description}: '{text}'")
                    found_summary = True
                except NoSuchElementException:
                    print(f"⚠️ {description}: Not found")
            
            return found_summary
            
        except Exception as e:
            print(f"❌ Summary test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all booking system tests"""
        print("🧪 Starting Comprehensive Booking System Tests")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: Page Access
        test_results.append(("Page Access", self.test_booking_page_access()))
        
        # Test 2: Elements Present
        test_results.append(("Elements Present", self.test_booking_elements_present()))
        
        # Test 3: Service Selection
        test_results.append(("Service Selection", self.test_service_selection()))
        
        # Test 4: Artist Selection
        test_results.append(("Artist Selection", self.test_artist_selection()))
        
        # Test 5: Summary Functionality
        test_results.append(("Summary Functionality", self.test_summary_functionality()))
        
        # Print results summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
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
            print("🎉 All tests passed! Booking system is working correctly.")
        elif passed > 0:
            print("⚠️ Some tests passed. Booking system has partial functionality.")
        else:
            print("❌ All tests failed. Booking system needs significant work.")
        
        return passed == total

if __name__ == "__main__":
    tester = TestBookingSystemWithAuth()
    try:
        tester.setup_method()
        success = tester.run_all_tests()
        tester.teardown_method()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        exit(1)

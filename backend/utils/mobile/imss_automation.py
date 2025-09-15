#!/usr/bin/env python3
"""
SIMPLIFIED IMSS Digital App Automation
Connects to manually started Appium server on localhost:4723
"""

import time
import random
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class IMSSDigitalAutomation:
    def __init__(self):
        """Simplified IMSS automation - connects to existing Appium server"""
        self.app_package = 'st.android.imsspublico'
        self.app_activity = 'crc642176304cdb761b92.Splash'
        self.driver = None
        self.wait = None

    def connect_to_app(self):
        """Connect to IMSS app via existing Appium server"""
        print("🔧 Connecting to IMSS app via Appium server...")
        
        options = UiAutomator2Options()
        options.platform_name = 'Android'
        options.device_name = 'Android'  # Generic name, Appium will auto-detect
        options.app_package = self.app_package
        options.app_activity = self.app_activity
        options.automation_name = 'UiAutomator2'
        
        # Optimized settings
        options.no_reset = True
        options.auto_launch = True
        options.auto_grant_permissions = True
        options.new_command_timeout = 300

        try:
            # Connect to manually started Appium server
            self.driver = webdriver.Remote("http://localhost:4723", options=options)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Connected to IMSS app successfully")
            
            # Wait for app to load
            time.sleep(8)
            return True
            
        except WebDriverException as e:
            print(f"❌ Failed to connect to IMSS app: {e}")
            print("💡 Make sure:")
            print("   1. Appium server is running (http://localhost:4723)")
            print("   2. Android device is connected with USB debugging")
            print("   3. IMSS Digital app is installed on device")
            return False

    def find_element_safely(self, by, value, timeout=15):
        """Find element with timeout"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None

    def tap_element(self, element, description=""):
        """Tap element with logging"""
        if element:
            try:
                element.click()
                print(f"✅ Tapped: {description}")
                time.sleep(random.uniform(1.5, 2.5))
                return True
            except Exception as e:
                print(f"❌ Failed to tap {description}: {e}")
                return False
        return False

    def input_text(self, element, text, description=""):
        """Input text with logging"""
        if element:
            try:
                element.click()
                time.sleep(0.5)
                element.clear()
                time.sleep(0.3)
                element.send_keys(text)
                print(f"✅ Filled: {description}")
                time.sleep(1.0)
                return True
            except Exception as e:
                print(f"❌ Failed to fill {description}: {e}")
                return False
        return False

    def navigate_to_constancia(self) -> bool:
        """Find and tap Constancia option"""
        print("🔍 Looking for Constancia option...")
        
        # Wait for app to fully load
        time.sleep(5)
        
        # Try different selectors for Constancia
        selectors = [
            (AppiumBy.XPATH, "//*[contains(@text, 'Constancia de semanas cotizadas')]"),
            (AppiumBy.XPATH, "//*[contains(@text, 'semanas cotizadas')]"),
            (AppiumBy.XPATH, "//*[contains(@text, 'Constancia')]"),
            (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Constancia')]"),
        ]
        
        # Try with scrolling
        for attempt in range(3):
            for by, selector in selectors:
                element = self.find_element_safely(by, selector, timeout=5)
                if element:
                    if self.tap_element(element, "Constancia option"):
                        time.sleep(3)
                        return True
            
            # Scroll down for next attempt
            if attempt < 2:
                try:
                    size = self.driver.get_window_size()
                    self.driver.swipe(size['width']//2, int(size['height']*0.7),
                                    size['width']//2, int(size['height']*0.3), 1000)
                    time.sleep(2)
                    print(f"📜 Scrolled down (attempt {attempt + 1})")
                except:
                    pass

        print("❌ Could not find Constancia option")
        return False

    def fill_form(self, curp_id: str, email: str) -> bool:
        """Fill CURP and email form"""
        print("📝 Filling CURP and email form...")
        time.sleep(3)
        
        # Fill CURP field
        print("🆔 Looking for CURP input field...")
        curp_selectors = [
            (AppiumBy.XPATH, "//*[contains(@hint, 'CURP')]"),
            (AppiumBy.XPATH, "//android.widget.EditText[1]"),
            (AppiumBy.CLASS_NAME, "android.widget.EditText"),
        ]
        
        curp_filled = False
        for by, selector in curp_selectors:
            curp_field = self.find_element_safely(by, selector, timeout=8)
            if curp_field:
                if self.input_text(curp_field, curp_id, f"CURP: {curp_id}"):
                    curp_filled = True
                    break
        
        if not curp_filled:
            print("❌ Could not find or fill CURP field")
            return False
        
        # Fill Email field
        print("📧 Looking for email input field...")
        email_selectors = [
            (AppiumBy.XPATH, "//*[contains(@hint, 'Correo')]"),
            (AppiumBy.XPATH, "//*[contains(@hint, 'electrónico')]"),
            (AppiumBy.XPATH, "//*[contains(@hint, 'email')]"),
            (AppiumBy.XPATH, "//android.widget.EditText[2]"),
        ]
        
        email_filled = False
        for by, selector in email_selectors:
            email_field = self.find_element_safely(by, selector, timeout=8)
            if email_field:
                if self.input_text(email_field, email, f"Email: {email}"):
                    email_filled = True
                    break
        
        if not email_filled:
            print("❌ Could not find or fill email field")
            return False
        
        return True

    def submit_form(self) -> bool:
        """Submit the form"""
        print("🚀 Looking for submit button...")
        
        submit_selectors = [
            (AppiumBy.XPATH, "//*[contains(@text, 'INICIAR SESIÓN')]"),
            (AppiumBy.XPATH, "//*[contains(@text, 'INICIAR SESION')]"),
            (AppiumBy.XPATH, "//*[contains(@text, 'ENVIAR')]"),
            (AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'INICIAR')]"),
            (AppiumBy.XPATH, "//android.widget.Button"),
        ]
        
        for by, selector in submit_selectors:
            submit_button = self.find_element_safely(by, selector, timeout=10)
            if submit_button:
                if self.tap_element(submit_button, "Submit button"):
                    time.sleep(5)
                    return True
        
        print("❌ Could not find submit button")
        return False

    def handle_response(self) -> bool:
        """Handle response dialog/confirmation"""
        print("📋 Handling response...")
        
        # Look for ACEPTAR button or confirmation
        accept_selectors = [
            (AppiumBy.XPATH, "//*[contains(@text, 'ACEPTAR')]"),
            (AppiumBy.XPATH, "//*[contains(@text, 'Aceptar')]"),
            (AppiumBy.XPATH, "//*[contains(@text, 'OK')]"),
        ]
        
        # Wait and look for dialog
        time.sleep(5)
        
        for by, selector in accept_selectors:
            accept_button = self.find_element_safely(by, selector, timeout=8)
            if accept_button:
                if self.tap_element(accept_button, "Accept/OK button"):
                    time.sleep(3)
                    print("✅ Response handled")
                    return True
        
        print("⚠️ No response dialog found - assuming request was processed")
        return True

    def run_automation(self, curp_id: str, email: str) -> bool:
        """Run complete IMSS automation workflow"""
        print("\n🏥 STARTING IMSS DIGITAL AUTOMATION")
        print("=" * 50)
        print(f"🆔 CURP: {curp_id}")
        print(f"📧 Email: {email}")
        print("=" * 50)

        try:
            # Step 1: Connect to app
            if not self.connect_to_app():
                return False

            # Step 2: Navigate to Constancia
            if not self.navigate_to_constancia():
                return False

            # Step 3: Fill form
            if not self.fill_form(curp_id, email):
                return False

            # Step 4: Submit form
            if not self.submit_form():
                return False

            # Step 5: Handle response
            if not self.handle_response():
                return False

            print("\n🎉 IMSS AUTOMATION COMPLETED!")
            print("✅ CURP request submitted to IMSS")
            print("📧 Check the email for PDF link")
            
            return True

        except Exception as e:
            print(f"❌ IMSS automation error: {e}")
            return False

        finally:
            # Always close the session
            if self.driver:
                try:
                    self.driver.quit()
                    print("🧹 Mobile session closed")
                except:
                    pass

def run_imss_automation(curp_id: str, email: str, debug: bool = False) -> bool:
    """
    Main function to run IMSS automation (for integration)
    
    Args:
        curp_id (str): CURP ID to process
        email (str): Email address for PDF delivery
        debug (bool): Debug mode (not used in simplified version)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"🎯 Starting IMSS automation for {curp_id}")
    automator = IMSSDigitalAutomation()
    
    result = automator.run_automation(curp_id, email)
    
    if result:
        print(f"✅ IMSS automation completed for {curp_id}")
    else:
        print(f"❌ IMSS automation failed for {curp_id}")
    
    return result

def main():
    """Test function"""
    print("🧪 IMSS AUTOMATION TEST")
    print("=" * 40)
    print("⚠️ Make sure Appium server is running:")
    print("   1. Open terminal: conda deactivate")
    print("   2. cd backend")
    print("   3. .\\venv\\Scripts\\activate")
    print("   4. appium")
    print("=" * 40)
    
    # Test with sample data
    test_curp = "ABCD123456HEFGHI01"
    test_email = "test@outlook.com"
    
    result = run_imss_automation(test_curp, test_email)
    
    if result:
        print("\n🎊 TEST SUCCESS!")
    else:
        print("\n❌ TEST FAILED!")

if __name__ == "__main__":
    main()
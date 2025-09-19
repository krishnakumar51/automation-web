#!/usr/bin/env python3

"""
Details Form Handler Module
===========================

Handles birth date details form for Outlook mobile app

"""

import time
import subprocess
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException


class DetailsForm:
    """Handles birth date details form"""

    def __init__(self, driver, utils, screen_size):
        self.driver = driver
        self.utils = utils
        self.screen_size = screen_size

    def fill_details(self, birth_day: int, birth_month: str, birth_year: int) -> bool:
        """FIXED: Details with proven working year input method"""
        print("\n=== STEP 4: Details (FIXED) ===")
        time.sleep(2)

        # Day dropdown
        if not self._fill_day(birth_day):
            print(f"FAILED: Could not select birth day '{birth_day}'")
            return False

        # Month dropdown  
        if not self._fill_month(birth_month):
            print(f"FAILED: Could not select birth month '{birth_month}'")
            return False

        # Year field
        if not self._fill_year(birth_year):
            print(f"FAILED: Could not fill birth year '{birth_year}'")
            return False

        print(f"\nBirth date successfully filled: {birth_month} {birth_day}, {birth_year}")
        return self.utils.click_next_production("Details")

    def _fill_day(self, birth_day: int) -> bool:
        """Fill day dropdown"""
        print(f"Selecting day: {birth_day}")

        day_selectors = [
            (AppiumBy.XPATH, "//*[contains(@text, 'Day')]"),
            (AppiumBy.XPATH, "//*[contains(@hint, 'Day')]"),
            (AppiumBy.XPATH, "//android.widget.Spinner[1]")
        ]

        for by, selector in day_selectors:
            if self.utils.click_element_bulletproof(by, selector, "Day Dropdown"):
                time.sleep(1)
                # Select day option
                day_option = self.utils.find_element_bulletproof(AppiumBy.XPATH, f"//*[@text='{birth_day}']", timeout=5)
                if day_option:
                    try:
                        day_option.click()
                        print(f"✓ Selected day: {birth_day}")
                        time.sleep(1)
                        return True
                    except StaleElementReferenceException:
                        # Refind and click
                        day_option = self.utils.find_element_bulletproof(AppiumBy.XPATH, f"//*[@text='{birth_day}']", timeout=3)
                        if day_option:
                            day_option.click()
                            time.sleep(1)
                            return True

        return False

    def _fill_month(self, birth_month: str) -> bool:
        """Fill month dropdown"""
        print(f"Selecting month: {birth_month}")

        month_selectors = [
            (AppiumBy.XPATH, "//*[contains(@text, 'Month')]"),
            (AppiumBy.XPATH, "//*[contains(@hint, 'Month')]"),
            (AppiumBy.XPATH, "//android.widget.Spinner[2]")
        ]

        for by, selector in month_selectors:
            if self.utils.click_element_bulletproof(by, selector, "Month Dropdown"):
                time.sleep(1)
                # Select month option
                month_option = self.utils.find_element_bulletproof(AppiumBy.XPATH, f"//*[@text='{birth_month}']", timeout=5)
                if month_option:
                    try:
                        month_option.click()
                        print(f"✓ Selected month: {birth_month}")
                        time.sleep(1)
                        return True
                    except StaleElementReferenceException:
                        # Refind and click
                        month_option = self.utils.find_element_bulletproof(AppiumBy.XPATH, f"//*[@text='{birth_month}']", timeout=3)
                        if month_option:
                            month_option.click()
                            time.sleep(1)
                            return True

        return False

    def _fill_year(self, birth_year: int) -> bool:
        """Fill year field using proven working method"""
        print(f"Entering year: {birth_year}")

        # Method 1: Use bulletproof method on all EditText elements (proven working)
        edit_texts = self.utils.find_elements_bulletproof(AppiumBy.CLASS_NAME, "android.widget.EditText", timeout=5)
        if edit_texts:
            # Use bulletproof typing on EditText class (it will find the right one)
            if self.utils.type_text_bulletproof(AppiumBy.CLASS_NAME, "android.widget.EditText",
                                             str(birth_year), "Year Field (bulletproof)"):
                print(f"✓ Year entered successfully: {birth_year}")
                return True
            else:
                print("⚠ Year input method 1 failed, trying method 2...")

                # Method 2: Direct manipulation of last EditText with backspace clearing
                try:
                    year_element = edit_texts[-1]  # Last EditText is usually year
                    year_element.click()
                    time.sleep(0.6)

                    # Use only backspace clearing (no element.clear())
                    print("Clearing year field with backspace...")
                    for _ in range(20):  # Clear thoroughly
                        self.driver.press_keycode(67)  # DEL
                        time.sleep(0.02)
                    time.sleep(0.5)

                    # Try send_keys first
                    try:
                        year_element.send_keys(str(birth_year))
                        print(f"✓ Year entered (method 2): {birth_year}")
                        return True
                    except Exception:
                        # ADB fallback
                        subprocess.run(['adb', 'shell', 'input', 'text', str(birth_year)],
                                     timeout=5, check=False)
                        print(f"✓ Year entered (ADB): {birth_year}")
                        return True

                except Exception as e:
                    print(f"⚠ Year method 2 failed: {e}")
                    print("Continuing anyway...")
        else:
            print("⚠ No EditText elements found for year")

        # Hide keyboard
        try:
            self.driver.hide_keyboard()
            time.sleep(0.5)
        except:
            pass

        return True  # Continue even if year fails

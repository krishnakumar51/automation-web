#!/usr/bin/env python3

"""
Names Form Handler Module
=========================

Handles name input form for Outlook mobile app

"""

import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException


class NamesForm:
    """Handles name input form"""

    def __init__(self, driver, utils, screen_size):
        self.driver = driver
        self.utils = utils
        self.screen_size = screen_size

    def fill_names(self, first_name: str, last_name: str) -> bool:
        """Name input"""
        print("\n=== STEP 5: Name ===")
        time.sleep(2)

        # Get all EditText elements
        edit_texts = self.utils.find_elements_bulletproof(AppiumBy.CLASS_NAME, "android.widget.EditText", timeout=5)

        if len(edit_texts) >= 2:
            try:
                # First name
                first_elem = edit_texts[0]
                first_elem.click()
                time.sleep(0.5)

                try:
                    first_elem.clear()
                except:
                    # Backspace clear
                    for _ in range(10):
                        self.driver.press_keycode(67)
                        time.sleep(0.02)

                time.sleep(0.3)
                first_elem.send_keys(first_name)
                print(f"✓ First name: {first_name}")

                # Last name
                last_elem = edit_texts[1]
                last_elem.click()
                time.sleep(0.5)

                try:
                    last_elem.clear()
                except:
                    # Backspace clear
                    for _ in range(10):
                        self.driver.press_keycode(67)
                        time.sleep(0.02)

                time.sleep(0.3)
                last_elem.send_keys(last_name)
                print(f"✓ Last name: {last_name}")

            except StaleElementReferenceException:
                # Fallback with bulletproof typing
                print("Using bulletproof method for names...")
                self.utils.type_text_bulletproof(AppiumBy.CLASS_NAME, "android.widget.EditText",
                                               first_name, "First Name")

                # Second field with instance selector
                try:
                    second_field = self.driver.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().className("android.widget.EditText").instance(1)'
                    )
                    second_field.click()
                    time.sleep(0.5)

                    for _ in range(10):
                        self.driver.press_keycode(67)
                        time.sleep(0.02)

                    second_field.send_keys(last_name)
                    print(f"✓ Last name (instance): {last_name}")
                except:
                    print("⚠ Last name input may have failed")

        try:
            self.driver.hide_keyboard()
            time.sleep(0.8)
        except:
            pass

        return self.utils.click_next_production("Name")

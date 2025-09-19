#!/usr/bin/env python3

"""
Mobile Utilities Module
=======================

Shared utilities and helper functions for mobile automation

"""

import time
import subprocess
from typing import Optional, List, Any
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


class MobileUtils:
    """Shared mobile automation utilities"""

    def __init__(self, driver, screen_size):
        self.driver = driver
        self.screen_size = screen_size

    def find_elements_bulletproof(self, by: str, value: str, timeout: int = 10, retry_attempts: int = 3) -> List[Any]:
        """Bulletproof element finding that always refreshes"""
        for attempt in range(retry_attempts):
            try:
                elements = WebDriverWait(self.driver, timeout).until(
                    lambda d: d.find_elements(by, value)
                )

                if elements:
                    # Filter for displayed elements
                    visible_elements = []
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                visible_elements.append(elem)
                        except StaleElementReferenceException:
                            continue
                        except Exception:
                            visible_elements.append(elem)

                    if visible_elements:
                        return visible_elements

                time.sleep(0.5)

            except TimeoutException:
                if attempt < retry_attempts - 1:
                    time.sleep(0.5)
            except Exception as e:
                if attempt < retry_attempts - 1:
                    time.sleep(0.5)

        return []

    def find_element_bulletproof(self, by: str, value: str, timeout: int = 10, retry_attempts: int = 3) -> Optional[Any]:
        """Bulletproof single element finding"""
        elements = self.find_elements_bulletproof(by, value, timeout, retry_attempts)
        return elements[0] if elements else None

    def click_element_bulletproof(self, by: str, value: str, description: str = "") -> bool:
        """Bulletproof element clicking that always refreshes element"""
        for _ in range(3):  # Max 3 attempts
            try:
                element = self.find_element_bulletproof(by, value, timeout=8)
                if not element:
                    return False

                # Try to click
                element.click()
                print(f"✓ Clicked: {description}")
                time.sleep(1)
                return True

            except StaleElementReferenceException:
                time.sleep(0.5)
                continue
            except Exception as e:
                print(f"✗ Click failed: {description} - {e}")
                time.sleep(0.5)
                continue

        return False

    def type_text_bulletproof(self, by: str, value: str, text: str, description: str = "") -> bool:
        """FIXED: Bulletproof text input using proven working method"""
        for attempt in range(3):
            try:
                # Always find fresh element
                element = self.find_element_bulletproof(by, value, timeout=8)
                if not element:
                    return False

                # Focus on element
                element.click()
                time.sleep(0.5)

                # FIXED: Use backspace clearing instead of element.clear() for year fields
                if "year" in description.lower() or "Year" in description:
                    print(f"Using backspace clearing for: {description}")
                    # Backspace clearing for year field
                    for _ in range(15):  # Clear existing content
                        self.driver.press_keycode(67)  # DEL key
                        time.sleep(0.02)
                    time.sleep(0.3)
                else:
                    # Standard clearing for other fields
                    try:
                        element.clear()
                        time.sleep(0.3)
                    except:
                        # Fallback to backspace
                        current_text = element.get_attribute("text") or ""
                        for _ in range(len(current_text) + 5):
                            self.driver.press_keycode(67)
                            time.sleep(0.02)
                        time.sleep(0.3)

                # Input text
                try:
                    element.send_keys(str(text))
                    print(f"✓ Typed: {description} = '{text}'")
                    time.sleep(0.5)
                    return True
                except Exception:
                    # ADB fallback
                    subprocess.run(['adb', 'shell', 'input', 'text', str(text)],
                                 timeout=8, check=False)
                    print(f"✓ Typed (ADB): {description} = '{text}'")
                    time.sleep(0.5)
                    return True

            except StaleElementReferenceException:
                if attempt < 2:
                    time.sleep(1)
                    continue
            except Exception as e:
                print(f"✗ Type failed: {description} - {e}")
                if attempt < 2:
                    time.sleep(1)
                    continue

        return False

    def click_next_production(self, context: str = "") -> bool:
        """Production Next button clicking"""
        strategies = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Next").clickable(true).enabled(true)'),
            (AppiumBy.XPATH, "//*[contains(@text, 'Next')]"),
            (AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'Next')]")
        ]

        for by, selector in strategies:
            if self.click_element_bulletproof(by, selector, f"Next ({context})"):
                return True

        # ENTER fallback
        try:
            self.driver.press_keycode(66)
            time.sleep(1)
            print("✓ ENTER key pressed")
            return True
        except:
            pass

        return False

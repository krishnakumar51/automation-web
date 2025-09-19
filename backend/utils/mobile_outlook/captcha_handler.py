#!/usr/bin/env python3

"""
CAPTCHA Handler Module
======================

Handles CAPTCHA challenges for Outlook mobile app

"""

import time
import subprocess
from appium.webdriver.common.appiumby import AppiumBy


class CaptchaHandler:
    """Handles CAPTCHA challenges"""

    def __init__(self, driver, utils, screen_size):
        self.driver = driver
        self.utils = utils
        self.screen_size = screen_size

    def handle_captcha(self) -> bool:
        """CAPTCHA handling"""
        print("\n=== STEP 6: CAPTCHA ===")
        time.sleep(3)

        # Find CAPTCHA button
        selectors = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.Button").textContains("Press").clickable(true).enabled(true)'),
            (AppiumBy.XPATH, "//android.widget.Button[contains(@text,'Press')]")
        ]

        button = None
        for by, selector in selectors:
            button = self.utils.find_element_bulletproof(by, selector, timeout=8)
            if button:
                break

        if button:
            try:
                location = button.location
                size = button.size
                x = location['x'] + size['width'] // 2
                y = location['y'] + size['height'] // 2

                # Native long press
                try:
                    self.driver.execute_script("mobile: longClickGesture", {
                        "elementId": button.id,
                        "duration": 15000
                    })
                    print("✓ Native long press (15s)")
                    time.sleep(4)
                    return True
                except:
                    pass

                # ADB fallback
                subprocess.run([
                    "adb", "shell", "input", "touchscreen", "swipe",
                    str(x), str(y), str(x), str(y), "15000"
                ], check=False)
                print("✓ ADB long press (15s)")
                time.sleep(4)
                return True

            except Exception as e:
                print(f"Button press failed: {e}")

        # Coordinate fallback
        x = self.screen_size['width'] // 2
        y = int(self.screen_size['height'] * 0.6)
        subprocess.run([
            "adb", "shell", "input", "touchscreen", "swipe",
            str(x), str(y), str(x), str(y), "15000"
        ], check=False)
        print("✓ Coordinate long press (15s)")
        time.sleep(4)
        return True

    def wait_authentication(self) -> bool:
        """Wait for authentication"""
        print("Waiting for authentication...")

        for _ in range(45):  # 90 seconds max
            try:
                progress_bars = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.ProgressBar")
                visible = []

                for bar in progress_bars:
                    try:
                        if bar.is_displayed():
                            visible.append(bar)
                    except:
                        continue

                if not visible:
                    print("✓ Authentication complete")
                    time.sleep(3)
                    return True
            except:
                pass

            time.sleep(2)

        print("✓ Auth timeout, continuing")
        return True

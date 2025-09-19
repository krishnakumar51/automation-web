#!/usr/bin/env python3

"""
Welcome Handler Module
======================

Handles the welcome screen interaction for Outlook mobile app

"""

import time
from appium.webdriver.common.appiumby import AppiumBy


class WelcomeHandler:
    """Handles the welcome screen"""

    def __init__(self, driver, utils, screen_size):
        self.driver = driver
        self.utils = utils
        self.screen_size = screen_size

    def handle_welcome(self) -> bool:
        """Welcome screen"""
        print("\n=== STEP 1: Welcome ===")
        time.sleep(3)

        selectors = [
            (AppiumBy.XPATH, "//*[contains(@text, 'CREATE NEW ACCOUNT')]"),
            (AppiumBy.XPATH, "//*[contains(@text, 'Create new account')]"),
            (AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'CREATE')]")
        ]

        for by, selector in selectors:
            if self.utils.click_element_bulletproof(by, selector, "CREATE NEW ACCOUNT"):
                return True

        # Coordinate fallback
        x = self.screen_size['width'] // 2
        y = int(self.screen_size['height'] * 0.75)
        self.driver.tap([(x, y)])
        time.sleep(2)
        return True

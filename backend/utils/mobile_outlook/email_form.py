#!/usr/bin/env python3

"""
Email Form Handler Module
=========================

Handles email input form for Outlook mobile app

"""

import time
from appium.webdriver.common.appiumby import AppiumBy


class EmailForm:
    """Handles email input form"""

    def __init__(self, driver, utils, screen_size):
        self.driver = driver
        self.utils = utils
        self.screen_size = screen_size

    def fill_email(self, username: str) -> bool:
        """Email creation"""
        print("\n=== STEP 2: Email ===")
        time.sleep(2)

        selectors = [
            (AppiumBy.XPATH, "//*[contains(@hint, 'email')]"),
            (AppiumBy.CLASS_NAME, "android.widget.EditText")
        ]

        for by, selector in selectors:
            if self.utils.type_text_bulletproof(by, selector, username, "Email"):
                return self.utils.click_next_production("Email")

        return False

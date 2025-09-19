#!/usr/bin/env python3

"""
Password Form Handler Module
============================

Handles password input form for Outlook mobile app

"""

import time
from appium.webdriver.common.appiumby import AppiumBy


class PasswordForm:
    """Handles password input form"""

    def __init__(self, driver, utils, screen_size):
        self.driver = driver
        self.utils = utils
        self.screen_size = screen_size

    def fill_password(self, password: str) -> bool:
        """Password creation"""
        print("\n=== STEP 3: Password ===")
        time.sleep(2)

        selectors = [
            (AppiumBy.XPATH, "//*[contains(@hint, 'Password')]"),
            (AppiumBy.CLASS_NAME, "android.widget.EditText")
        ]

        for by, selector in selectors:
            if self.utils.type_text_bulletproof(by, selector, password, "Password"):
                return self.utils.click_next_production("Password")

        return False

#!/usr/bin/env python3

"""
Mobile Setup Module for Outlook Automation
==========================================

Handles Appium driver setup and configuration for mobile automation

"""

import time
import subprocess
from typing import Optional
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MobileSetup:
    """Mobile driver setup and configuration"""

    def __init__(self, app_package: str = 'com.microsoft.office.outlook'):
        self.app_package = app_package
        self.driver = None
        self.screen_size = None

    def setup_driver(self) -> bool:
        """Production driver setup"""
        try:
            print("Setting up mobile driver...")
            options = UiAutomator2Options()
            options.platform_name = 'Android'
            options.device_name = 'Android'
            options.app_package = self.app_package
            options.app_activity = '.MainActivity'
            options.automation_name = 'UiAutomator2'
            options.no_reset = False
            options.full_reset = False
            options.new_command_timeout = 300
            options.unicode_keyboard = True
            options.reset_keyboard = True
            options.auto_grant_permissions = True

            self.driver = webdriver.Remote("http://localhost:4723", options=options)
            self.driver.update_settings({"enforceXPath1": True})
            self.screen_size = self.driver.get_window_size()

            print("✓ Mobile driver ready")
            return True

        except Exception as e:
            print(f"✗ Mobile setup failed: {e}")
            return False

    def cleanup_driver(self):
        """Clean up driver resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("✓ Mobile driver cleaned up")
            except:
                pass

    def get_driver(self):
        """Get the current driver instance"""
        return self.driver

    def get_screen_size(self):
        """Get the screen size"""
        return self.screen_size

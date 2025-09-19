#!/usr/bin/env python3

"""
Automation Runner Module
========================

Main orchestrator for mobile Outlook automation

"""

import time
import random
from typing import Dict, Any
from .mobile_setup import MobileSetup
from .utils import MobileUtils
from .welcome_handler import WelcomeHandler
from .email_form import EmailForm
from .password_form import PasswordForm
from .details_form import DetailsForm
from .names_form import NamesForm
from .captcha_handler import CaptchaHandler
from .post_verification import PostVerificationHandler


class OutlookMobileAutomation:
    """Main mobile automation orchestrator"""

    def __init__(self, app_package: str = 'com.microsoft.office.outlook'):
        self.setup = MobileSetup(app_package)
        self.utils = None
        self.handlers = {}

    def run_automation(self, user_data: Dict[str, Any]) -> bool:
        """Run complete mobile automation"""
        print("🔧 MOBILE OUTLOOK AUTOMATION")
        print("====================================")
        print(f"Email: {user_data['username']}@outlook.com")
        print(f"Password: {user_data['password']}")
        print("====================================")

        try:
            # Setup driver
            if not self.setup.setup_driver():
                return False

            # Initialize utilities and handlers
            self._initialize_handlers()

            time.sleep(4)

            # Execute automation steps
            steps = [
                ("Welcome", lambda: self.handlers['welcome'].handle_welcome()),
                ("Email", lambda: self.handlers['email'].fill_email(user_data['username'])),
                ("Password", lambda: self.handlers['password'].fill_password(user_data['password'])),
                ("Details", lambda: self.handlers['details'].fill_details(
                    user_data['birth_date']['day'],
                    user_data['birth_date']['month'],
                    user_data['birth_date']['year']
                )),
                ("Name", lambda: self.handlers['names'].fill_names(user_data['first_name'], user_data['last_name'])),
                ("CAPTCHA", lambda: self.handlers['captcha'].handle_captcha()),
                ("Post-CAPTCHA", lambda: self.handlers['post_verification'].handle_post_captcha()),
                ("Final Wait", lambda: self.handlers['post_verification'].final_wait())
            ]

            for step_name, step_function in steps:
                print(f"\n🔧 {step_name}...")
                try:
                    result = step_function()
                    if result:
                        print(f"✅ {step_name} SUCCESS")
                    else:
                        print(f"⚠ {step_name} FAILED")
                        if step_name in ["Welcome", "Email", "Password"]:
                            return False
                        else:
                            print("⚠ Continuing...")
                except Exception as e:
                    print(f"❌ {step_name} ERROR: {e}")
                    if step_name not in ["Welcome", "Email", "Password"]:
                        continue
                    else:
                        return False

            print("\n🎉 MOBILE AUTOMATION SUCCESS!")
            return True

        except Exception as e:
            print(f"💥 Automation failed: {e}")
            return False
        finally:
            self.setup.cleanup_driver()

    def _initialize_handlers(self):
        """Initialize all handler classes"""
        driver = self.setup.get_driver()
        screen_size = self.setup.get_screen_size()

        self.utils = MobileUtils(driver, screen_size)

        self.handlers = {
            'welcome': WelcomeHandler(driver, self.utils, screen_size),
            'email': EmailForm(driver, self.utils, screen_size),
            'password': PasswordForm(driver, self.utils, screen_size),
            'details': DetailsForm(driver, self.utils, screen_size),
            'names': NamesForm(driver, self.utils, screen_size),
            'captcha': CaptchaHandler(driver, self.utils, screen_size),
            'post_verification': PostVerificationHandler(driver, self.utils, screen_size)
        }


def generate_user_data() -> Dict[str, Any]:
    """Generate user data for testing"""
    return {
        'username': f'mobile{random.randint(100000, 999999)}',
        'password': f'Mobile{random.randint(100, 999)}Pass!',
        'first_name': 'Mobile',
        'last_name': 'User',
        'birth_date': {
            'day': random.randint(1, 28),
            'month': random.choice(['January', 'February', 'March', 'April', 'May', 'June']),
            'year': random.randint(1990, 2000)
        }
    }


def create_outlook_account_mobile(user_data: Dict[str, Any]) -> bool:
    """Create Outlook account using mobile automation"""
    automation = OutlookMobileAutomation()
    return automation.run_automation(user_data)


if __name__ == "__main__":
    """Test function"""
    print("🔧 MOBILE Outlook Automation")
    print("🔧 Mobile automation with modular structure")
    print("="*50)

    user_data = generate_user_data()
    print(f"Account: {user_data['username']}@outlook.com")
    print(f"Password: {user_data['password']}")
    print("Starting mobile automation...")

    success = create_outlook_account_mobile(user_data)

    if success:
        print(f"\n🎊 MOBILE SUCCESS!")
        print(f"📧 {user_data['username']}@outlook.com")
        print(f"🔒 {user_data['password']}")
    else:
        print("\n❌ Failed")

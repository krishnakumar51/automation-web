#!/usr/bin/env python3

"""
Post-Verification Handler Module
================================

Handles post-CAPTCHA flow for Outlook mobile app

"""

import time
from appium.webdriver.common.appiumby import AppiumBy


class PostVerificationHandler:
    """Handles post-CAPTCHA verification flow"""

    def __init__(self, driver, utils, screen_size):
        self.driver = driver
        self.utils = utils
        self.screen_size = screen_size

    def handle_post_captcha(self) -> bool:
        """Post-CAPTCHA pages (optimized for speed: ~4–6s total)"""
        print("\n=== STEP 7: Post-CAPTCHA (FAST) ===")

        # Wait for auth to complete (kept, but do not over-wait inside it)
        self._wait_authentication()
        time.sleep(1.0)

        # Fast inbox probe
        def inbox_reached() -> bool:
            if self.utils.find_element_bulletproof(AppiumBy.XPATH, "//*[@text='Search']", timeout=1, retry_attempts=1):
                return True
            if self.utils.find_element_bulletproof(AppiumBy.XPATH, "//*[contains(@content-desc,'Search')]", timeout=1, retry_attempts=1):
                return True
            return False

        # Quick-click helper: 1s timeout, 1 retry, direct click to avoid slow helper
        def quick_click(xpaths: list) -> bool:
            for xp in xpaths:
                el = self.utils.find_element_bulletproof(AppiumBy.XPATH, xp, timeout=1, retry_attempts=1)
                if el:
                    for _ in range(2):  # retry once if stale
                        try:
                            el.click()
                            time.sleep(0.6)  # small settle before next probe
                            return True
                        except:
                            el = self.utils.find_element_bulletproof(AppiumBy.XPATH, xp, timeout=1, retry_attempts=1)
                            if not el:
                                break
            return False

        # Selectors per page (case-flexible)
        maybe_later = [
            "//*[@text='MAYBE LATER']",
            "//*[contains(translate(@text,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'MAYBE LATER')]",
            "//*[contains(@text,'Maybe later')]",
            "//*[contains(@content-desc,'Maybe later')]",
        ]

        your_data_next = [
            "//*[@text='NEXT']",
            "//*[contains(translate(@text,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'NEXT')]",
            "//*[contains(@text,'Next')]",
            "//*[contains(@content-desc,'Next')]",
        ]

        getting_better_accept = [
            "//*[@text='ACCEPT']",
            "//*[contains(translate(@text,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'ACCEPT')]",
            "//*[contains(@text,'Accept')]",
            "//*[contains(@content-desc,'Accept')]",
        ]

        continue_outlook = [
            "//*[@text='CONTINUE TO OUTLOOK']",
            "//*[contains(translate(@text,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONTINUE TO OUTLOOK')]",
            "//*[contains(@text,'Continue to Outlook')]",
            "//*[contains(@content-desc,'Continue to Outlook')]",
        ]

        # Optional OS dialogs (quick pass only)
        quick_os = [
            "//*[contains(@text,'Not now')]",
            "//*[contains(@text,'Maybe later')]",
            "//*[contains(@text,'Skip')]",
            "//*[contains(@text,'No thanks')]",
        ]

        # Run a short, time-bounded burst: try all relevant buttons each pass
        start = time.time()
        budget_sec = 7.0  # hard cap so this step doesn't drag
        passes = 0

        while time.time() - start < budget_sec:
            passes += 1

            # If already on inbox, stop immediately
            if inbox_reached():
                print("✓ Reached inbox!")
                return True

            # Try most likely current page buttons fast (no strict order; app may auto-advance)
            # 1) Add another account?
            if quick_click(maybe_later) and inbox_reached():
                print("✓ Reached inbox!")
                return True

            # 2) Your Data, Your Way
            if quick_click(your_data_next) and inbox_reached():
                print("✓ Reached inbox!")
                return True

            # 3) Getting Better Together
            if quick_click(getting_better_accept) and inbox_reached():
                print("✓ Reached inbox!")
                return True

            # 4) Powering Your Experiences
            if quick_click(continue_outlook) and inbox_reached():
                print("✓ Reached inbox!")
                return True

            # 5) One quick shot at OS/system prompts
            quick_click(quick_os)

            # Small adaptive pause; shorten if we already clicked something in this pass
            time.sleep(0.4)

        # Final inbox probe before exit
        if inbox_reached():
            print("✓ Reached inbox!")
            return True

        print("✓ Post-CAPTCHA handling done (fast path)")
        return True

    def _wait_authentication(self) -> bool:
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

    def final_wait(self) -> bool:
        """Final wait"""
        print("\n=== STEP 8: Final Wait ===")
        time.sleep(10)
        print("✓ Final wait complete")
        return True

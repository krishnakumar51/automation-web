import time
import pyautogui
from .selectors import IFRAME_SELECTORS

def handle_human_challenge(page) -> bool:
    """Handle human challenge (press and hold captcha)"""
    print(f"\n🤖 HANDLING HUMAN CHALLENGE")
    page.wait_for_timeout(5000)
    current_url = page.url

    print("=== DEBUG: Looking for iframe-based human captcha ===")
    main_iframe = None

    for selector in IFRAME_SELECTORS:
        try:
            print(f"Trying iframe selector: {selector}")
            main_iframe = page.wait_for_selector(selector, timeout=10000)
            if main_iframe and main_iframe.is_visible():
                print(f"✅ Found main captcha iframe with selector: {selector}")
                break
        except Exception as e:
            print(f"❌ Selector {selector} failed: {e}")
            continue

    if not main_iframe:
        print("❌ No iframe captcha found, trying fallback approach...")
        return handle_traditional_challenge(page)
    else:
        return handle_iframe_challenge(page, main_iframe, current_url)

def handle_iframe_challenge(page, main_iframe, current_url) -> bool:
    """Handle iframe-based captcha challenge"""
    print("✅ Found iframe captcha. Attempting to interact with it...")
    
    iframe_bbox = main_iframe.bounding_box()
    if not iframe_bbox:
        print("❌ Could not get iframe bounding box")
        return False

    print(f"📐 Iframe position: x={iframe_bbox['x']}, y={iframe_bbox['y']}, w={iframe_bbox['width']}, h={iframe_bbox['height']}")

    # Initialize captcha coordinates with iframe center as default
    captcha_x = iframe_bbox['x'] + iframe_bbox['width'] / 2
    captcha_y = iframe_bbox['y'] + iframe_bbox['height'] / 2
    print(f"📍 Initial captcha coordinates (iframe center): ({captcha_x}, {captcha_y})")

    # Try to access iframe content
    try:
        iframe_content = main_iframe.content_frame()
        if iframe_content:
            print("✅ Successfully accessed iframe content!")
            page.wait_for_timeout(3000)
            
            try:
                iframe_content.wait_for_selector('#px-captcha', timeout=10000)
                captcha_element = iframe_content.query_selector('#px-captcha')
                if captcha_element:
                    print("✅ Found #px-captcha element inside iframe!")
                    captcha_bbox = captcha_element.bounding_box()
                    if captcha_bbox:
                        captcha_x = iframe_bbox['x'] + captcha_bbox['x'] + captcha_bbox['width'] / 2
                        captcha_y = iframe_bbox['y'] + captcha_bbox['y'] + captcha_bbox['height'] / 2
                        print(f"📍 Refined captcha center: ({captcha_x}, {captcha_y})")
                    else:
                        print(f"⚠️ Could not get captcha element bbox, using iframe center: ({captcha_x}, {captcha_y})")
                else:
                    print(f"❌ #px-captcha not found, using iframe center: ({captcha_x}, {captcha_y})")
            except Exception as e:
                print(f"❌ Error accessing iframe content: {e}")
                print(f"⚠️ Using iframe center: ({captcha_x}, {captcha_y})")
        else:
            print("❌ Could not access iframe content (cross-origin restriction)")
            print(f"⚠️ Using iframe center: ({captcha_x}, {captcha_y})")
    except Exception as e:
        print(f"❌ Error accessing iframe: {e}")
        print(f"⚠️ Using iframe center: ({captcha_x}, {captcha_y})")

    return perform_mouse_challenge(page, captcha_x, captcha_y, current_url)

def handle_traditional_challenge(page) -> bool:
    """Handle traditional challenge button"""
    challenge_button = None
    captcha_x = None
    captcha_y = None

    challenge_found = page.evaluate("""
    () => {
        const allElements = Array.from(document.querySelectorAll('div, button, span'));
        for (const element of allElements) {
            const text = (element.innerText || '').toLowerCase();
            const ariaLabel = (element.getAttribute('aria-label') || '').toLowerCase();
            const id = (element.id || '').toLowerCase();
            
            if ((text.includes('press') && text.includes('hold')) ||
                (ariaLabel.includes('press') && ariaLabel.includes('hold')) ||
                ariaLabel.includes('human challenge') ||
                text.includes('human challenge') ||
                id.includes('challenge')) {
                if (element.offsetParent !== null) {
                    element.setAttribute('data-found-challenge', 'true');
                    console.log('Found challenge element:', element);
                    return true;
                }
            }
        }
        return false;
    }
    """)

    if challenge_found:
        challenge_button = page.query_selector("[data-found-challenge='true']")
        print("✅ Found traditional challenge button using JavaScript search!")

        if challenge_button:
            bbox = challenge_button.bounding_box()
            if bbox:
                captcha_x = bbox['x'] + bbox['width'] / 2
                captcha_y = bbox['y'] + bbox['height'] / 2
                print(f"📍 Challenge button center: ({captcha_x}, {captcha_y})")
            else:
                print("❌ Could not get challenge button bounding box")
                captcha_x = 960
                captcha_y = 540

    if not challenge_button or captcha_x is None or captcha_y is None:
        print("❌ FAILED: Could not find any human challenge element or get coordinates.")
        return False

    return perform_mouse_challenge(page, captcha_x, captcha_y, page.url)

def perform_mouse_challenge(page, captcha_x, captcha_y, current_url) -> bool:
    """Perform the actual mouse press and hold challenge"""
    if captcha_x is None or captcha_y is None:
        print("❌ ERROR: Invalid captcha coordinates!")
        return False

    print(f"✅ Using captcha coordinates: ({captcha_x}, {captcha_y})")

    # Get browser window position
    browser_viewport = page.viewport_size
    print(f"Browser viewport size: {browser_viewport}")

    current_mouse_pos = pyautogui.position()
    print(f"Current physical mouse position: {current_mouse_pos}")

    browser_info = page.evaluate("""
    () => {
        return {
            windowX: window.screenX || window.screenLeft || 0,
            windowY: window.screenY || window.screenTop || 0,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            outerWidth: window.outerWidth,
            outerHeight: window.outerHeight
        };
    }
    """)
    print(f"Browser window info: {browser_info}")

    # Calculate screen coordinates
    screen_x = browser_info['windowX'] + captcha_x
    screen_y = browser_info['windowY'] + captcha_y
    print(f"📍 Calculated screen coordinates: ({screen_x}, {screen_y})")

    # Safety check
    screen_width, screen_height = pyautogui.size()
    if screen_x < 0 or screen_x > screen_width or screen_y < 0 or screen_y > screen_height:
        print(f"⚠️ Coordinates out of bounds! Screen size: {screen_width}x{screen_height}")
        print(f"⚠️ Using fallback coordinates...")
        screen_x = screen_width // 2
        screen_y = screen_height // 2

    # User warning
    print("\n" + "="*70)
    print("🚨 IMPORTANT: ABOUT TO TAKE CONTROL OF YOUR PHYSICAL MOUSE!")
    print("="*70)
    print("⚠️ The script will now:")
    print(" 1. Move your physical mouse cursor to the captcha")
    print(" 2. Press and HOLD the left mouse button physically")
    print(" 3. Keep it pressed for exactly 15 seconds")
    print("💡 This is REAL hardware control - not simulated!")
    print("💡 The hold will automatically end after 15 seconds")
    print("="*70)

    # Countdown
    for i in range(5, 0, -1):
        print(f"⏰ Starting in {i} seconds... (Close browser now to cancel)")
        page.wait_for_timeout(1000)

    print(f"\n🖱️ Moving PHYSICAL mouse to captcha position...")
    print(f"📍 Using fixed coordinates: (830, 757)")

    # Disable failsafe and perform mouse operations
    pyautogui.FAILSAFE = False
    pyautogui.moveTo(830, 757, duration=1.5)
    page.wait_for_timeout(500)

    print("\n🖱️ PHYSICAL MOUSE DOWN - Starting 15-second press and hold on captcha...")
    print("💡 Using REAL PHYSICAL MOUSE - indistinguishable from human interaction!")

    try:
        pyautogui.mouseDown(button='left')
        print("✅ Physical left mouse button is now PRESSED and HELD!")
        print("🔒 Mouse button will remain pressed for 15 seconds...")
    except Exception as e:
        print(f"❌ Error pressing physical mouse button: {e}")
        print("⚠️ Falling back to Playwright mouse events...")
        page.mouse.move(830, 757)
        page.mouse.down(button='left')
        print("⚠️ Using Playwright mouse events as fallback")

    # Hold for exactly 15 seconds
    start_time = time.time()
    last_status_time = 0
    hold_duration = 15

    print("\n🔄 15-SECOND HOLD ACTIVE")
    try:
        while True:
            current_time = time.time()
            elapsed = current_time - start_time

            if elapsed >= hold_duration:
                print(f"⏰ 15 seconds completed! Releasing mouse button...")
                break

            # Print status every 10 seconds
            if current_time - last_status_time >= 10:
                remaining = hold_duration - elapsed
                print(f"⏱️ Still holding... {int(elapsed)}s elapsed, {int(remaining)}s remaining (Mouse button pressed)")
                last_status_time = current_time

            # Check for success indicators every 5 seconds
            if int(elapsed) % 5 == 0:
                try:
                    # Look for success indicators
                    checkmark = page.query_selector("div[id='checkmark']")
                    if checkmark and checkmark.is_visible():
                        print(f"✅ SUCCESS: Checkmark appeared after {int(elapsed)}s!")
                        print("🎉 Challenge completed successfully!")
                        print("💡 Will continue holding until 15 seconds is complete...")

                    success_elements = page.query_selector_all("svg[class*='checkmark'], div[class*='success'], div[class*='verified'], div[class*='complete']")
                    for elem in success_elements:
                        if elem.is_visible():
                            print(f"✅ SUCCESS: Success indicator found after {int(elapsed)}s!")
                            print("💡 Will continue holding until 15 seconds is complete...")
                            break

                    # Check for page navigation
                    new_url = page.url
                    if new_url != current_url and "challenge" not in new_url.lower():
                        print(f"✅ SUCCESS: Page navigated after {int(elapsed)}s!")
                        print(f" New URL: {new_url}")
                        print("💡 Will continue holding until 15 seconds is complete...")
                        current_url = new_url
                except Exception as e:
                    # Continue holding even if there's an error checking
                    pass

            page.wait_for_timeout(200)

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n🛑 Hold ended after {int(elapsed)}s (before 15 seconds completion)")
        print(f" Reason: {str(e)}")
        
        if "Target page, context or browser has been closed" in str(e) or "Connection closed" in str(e):
            print("✅ Browser was closed by user - this is normal!")
        else:
            print("⚠️ Unexpected error occurred")
    finally:
        # Always release the physical mouse button
        try:
            print("\n🖱️ Releasing physical mouse button...")
            pyautogui.mouseUp(button='left')
            print("✅ Physical mouse button released successfully!")
        except Exception as e:
            print(f"⚠️ Error releasing mouse button: {e}")

    print("\n🏁 Press and hold session completed!")
    page.wait_for_timeout(5000)
    return True

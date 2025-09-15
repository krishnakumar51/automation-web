import playwright.sync_api as pw
import time
from .browser_setup import setup_browser_and_page
from .form_filling import fill_email_form, fill_password_form, fill_birth_date_form, fill_names_form
from .captcha_handler import handle_human_challenge
from .post_verification import handle_post_verification

def create_outlook_account(playwright: pw.Playwright, username: str, password: str, birth_month: str, birth_day: str, birth_year: str, first_name: str, last_name: str) -> bool:
    """
    Navigates to the Outlook account creation page, fills in the email username, password, birth date, first name, last name, and clicks next

    Args:
        playwright (pw.Playwright): The Playwright instance
        username (str): The desired username part of the email (e.g., 'pranav910' for 'pranav910@outlook.com')
        password (str): The password for the new account
        birth_month (str): The birth month (e.g., 'January', 'February', etc.)
        birth_day (str): The birth day (e.g., '1', '15', '31')
        birth_year (str): The birth year (e.g., '1990', '1995')
        first_name (str): The first name for the account
        last_name (str): The last name for the account

    Returns:
        bool: True if successful, raises exception on failure
    """
    browser = None
    context = None
    page = None

    try:
        print("🚀 Starting Outlook account creation process...")

        # Phase 1: Browser Setup
        browser, context, page = setup_browser_and_page(playwright)
        print("✅ Browser setup completed")

        # Phase 2: Fill Email Form
        if not fill_email_form(page, username):
            raise Exception("Failed to fill email form")
        print("✅ Email form completed")

        # Phase 3: Fill Password Form
        if not fill_password_form(page, password):
            raise Exception("Failed to fill password form")
        print("✅ Password form completed")

        # Phase 4: Fill Birth Date Form
        if not fill_birth_date_form(page, birth_month, birth_day, birth_year):
            raise Exception("Failed to fill birth date form")
        print("✅ Birth date form completed")

        # Phase 5: Fill Names Form
        if not fill_names_form(page, first_name, last_name):
            raise Exception("Failed to fill names form")
        print("✅ Names form completed")

        # Phase 6: Handle Human Challenge
        if not handle_human_challenge(page):
            raise Exception("Failed to handle human challenge")
        print("✅ Human challenge completed")

        # Phase 7: Post-verification flow
        if not handle_post_verification(page):
            raise Exception("Failed post-verification flow")
        print("✅ Post-verification completed")

        # Final success message
        print("\n🎉 OUTLOOK ACCOUNT CREATION SUCCESSFUL!")
        print(f"📧 Email: {username}@outlook.com")
        print(f"🔑 Password: {'*' * len(password)}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"📅 Birth Date: {birth_month} {birth_day}, {birth_year}")
        print(f"✅ Signed in using {username}@outlook.com")

        return True

    except Exception as e:
        print(f"❌ Error during automation: {e}")
        raise

    finally:
        # IMPORTANT: Always cleanup resources (your original code)
        try:
            if page:
                page.close()
        except:
            pass
        try:
            if context:
                context.close()
        except:
            pass
        try:
            if browser:
                browser.close()
        except:
            pass
        print("🧹 Browser cleanup completed")

def trigger_mobile_automation_if_available(process_id: str, curp_id: str, email: str, first_name: str, last_name: str) -> dict:
    """
    UPDATED: Trigger mobile automation that connects to manually started Appium server

    Returns:
        dict: {"success": bool, "status": str, "message": str}
    """
    try:
        print("📱 Checking mobile IMSS automation...")

        # Step 1: Check if mobile module exists
        try:
            from utils.mobile import start_mobile_automation
            print("✅ Mobile automation module found")
        except ImportError as import_error:
            print(f"⚠️ Mobile automation module not available: {import_error}")
            return {
                "success": False,
                "status": "module_not_available",
                "message": "Mobile automation module not set up"
            }

        # Step 2: Check if Appium server is running
        try:
            import requests
            response = requests.get("http://localhost:4723/status", timeout=5)
            if response.status_code != 200:
                raise Exception("Server not responding properly")
            print("✅ Found running Appium server")
        except Exception as server_error:
            print(f"❌ No Appium server running: {server_error}")
            print("\n" + "="*60)
            print("🚨 APPIUM SERVER NOT RUNNING")
            print("="*60)
            print("Please start Appium server manually:")
            print()
            print("1. Open NEW terminal")
            print("2. conda deactivate")
            print("3. cd backend")
            print("4. .\\venv\\Scripts\\activate")
            print("5. appium")
            print()
            print("Keep that terminal running, then retry CURP automation.")
            print("="*60)

            return {
                "success": False,
                "status": "appium_server_not_running",
                "message": "Appium server not running on http://localhost:4723"
            }

        # Step 3: Run mobile automation
        print(f"🎯 Starting mobile automation for {curp_id}")

        mobile_result = start_mobile_automation(
            process_id=process_id,
            curp_id=curp_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        if mobile_result:
            print("✅ Mobile IMSS automation completed successfully!")
            return {
                "success": True,
                "status": "completed",
                "message": "Mobile automation completed successfully"
            }
        else:
            print("❌ Mobile automation failed")
            return {
                "success": False,
                "status": "automation_failed",
                "message": "Mobile automation workflow failed"
            }

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error in mobile automation trigger: {error_msg}")
        return {
            "success": False,
            "status": "trigger_error",
            "message": f"Mobile automation trigger error: {error_msg}"
        }

def check_appium_server_running() -> bool:
    """Simple check if Appium server is running"""
    try:
        import requests
        response = requests.get("http://localhost:4723/status", timeout=3)
        return response.status_code == 200
    except:
        return False

def print_appium_start_instructions():
    """Print simple instructions to start Appium server"""
    print("\n" + "="*70)
    print("📋 HOW TO START APPIUM SERVER")
    print("="*70)
    print("Open a NEW terminal and run these commands:")
    print()
    print("  conda deactivate")
    print("  cd backend")
    print("  .\\venv\\Scripts\\activate")
    print("  appium")
    print()
    print("Keep that terminal running while using CURP automation.")
    print("="*70)

def test_mobile_integration_from_outlook():
    """Test mobile integration - simplified version"""
    print("🧪 Testing Mobile Integration")
    print("-" * 50)

    # Check mobile module
    try:
        from utils.mobile import start_mobile_automation
        print("✅ Mobile automation module available")
    except ImportError as e:
        print(f"❌ Mobile automation module missing: {e}")
        print("📋 Create utils/mobile/ folder with __init__.py and imss_automation.py")
        return False

    # Check Appium server
    if check_appium_server_running():
        print("✅ Appium server is running")
        server_ok = True
    else:
        print("❌ Appium server not running")
        print_appium_start_instructions()
        server_ok = False

    # Check Android device
    try:
        import subprocess
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True, timeout=5)
        if "device" in result.stdout and len([l for l in result.stdout.split('\n') if '\tdevice' in l]) > 0:
            print("✅ Android device connected")
        else:
            print("⚠️ No Android devices connected")
    except:
        print("⚠️ Cannot check Android devices")

    return server_ok

def test_complete_integration():
    """Test complete integration including email polling"""
    print("🧪 Testing COMPLETE Integration (Outlook + Mobile + Email)")
    print("="*70)
    
    # Test mobile integration
    mobile_ok = test_mobile_integration_from_outlook()
    
    # Test email polling module
    try:
        from .email_polling import poll_and_download_pdf, test_email_polling
        print("✅ Email polling module available")
        email_ok = True
        
        # Run email polling test
        test_email_polling()
        
    except ImportError as e:
        print(f"❌ Email polling module missing: {e}")
        print("📋 Create utils/outlook/email_polling.py")
        email_ok = False
    
    print("\n" + "="*70)
    print("📊 INTEGRATION STATUS SUMMARY")
    print("="*70)
    print(f"✅ Outlook Creation: Working (existing)")
    print(f"{'✅' if mobile_ok else '❌'} Mobile Automation: {'Working' if mobile_ok else 'Needs setup'}")
    print(f"{'✅' if email_ok else '❌'} Email Polling: {'Working' if email_ok else 'Needs setup'}")
    
    if mobile_ok and email_ok:
        print("\n🎉 COMPLETE INTEGRATION READY!")
        print("Your CURP-to-PDF automation can now run end-to-end!")
    else:
        print("\n⚠️ Some components need setup - see instructions above")
    
    return mobile_ok and email_ok

if __name__ == "__main__":
    # Test complete integration
    test_complete_integration()
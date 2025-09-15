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
        print(f"📅 Signed in using{username}@outlook.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        raise
    
    finally:
        # Cleanup resources
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

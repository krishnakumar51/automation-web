"""
Email Polling and PDF Download Module - IMPROVED VERSION
Handles signing into Outlook web, monitoring for IMSS emails, and downloading PDFs
"""

import playwright.sync_api as pw
import time
import os
import hashlib
import sqlite3
from datetime import datetime, timedelta
from .selectors import EMAIL_SELECTORS, PASSWORD_SELECTORS, NEXT_BUTTON_SELECTORS
from .captcha_handler import handle_human_challenge

def poll_and_download_pdf(process_id: str, email: str, password: str, timeout_minutes: int = 10) -> dict:
    """
    Complete email polling and PDF download workflow
    
    Args:
        process_id: Process UUID from database
        email: Outlook email address
        password: Outlook password
        timeout_minutes: How long to wait for email
    
    Returns:
        dict: {"success": bool, "link_found": bool, "file_path": str, "file_name": str, "file_size": int, "error": str}
    """
    browser = None
    context = None
    page = None
    
    try:
        print(f"📧 Starting email polling for {email}")
        update_email_pdf_status(process_id, "monitoring", "Starting email monitoring")
        
        # Create downloads directory
        downloads_dir = create_downloads_directory(process_id)
        
        with pw.sync_playwright() as playwright:
            print("🚀 Starting browser for email monitoring...")
            
            # Launch browser with download support
            browser = playwright.chromium.launch(
                headless=False,  # Show browser for debugging
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security'
                ]
            )
            
            context = browser.new_context(
                accept_downloads=True,
                download_path=downloads_dir,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            # Step 1: Sign into Outlook
            print("🔑 Signing into Outlook...")
            if not sign_in_to_outlook(page, email, password):
                raise Exception("Failed to sign into Outlook")
            
            print("✅ Successfully signed into Outlook")
            
            # Step 2: Monitor for IMSS email
            print(f"👀 Monitoring inbox for IMSS email (timeout: {timeout_minutes} minutes)...")
            update_email_pdf_status(process_id, "monitoring", f"Monitoring inbox for IMSS email")
            
            pdf_link = wait_for_imss_email(page, timeout_minutes * 60)
            
            if not pdf_link:
                raise Exception(f"No IMSS email received within {timeout_minutes} minutes")
            
            print(f"✅ Found IMSS email with PDF link: {pdf_link[:50]}...")
            update_email_pdf_status(process_id, "link_found", f"Found PDF link in email")
            
            # Step 3: Download PDF
            print("📥 Downloading PDF...")
            download_result = download_pdf_from_link(page, pdf_link, downloads_dir)
            
            if not download_result["success"]:
                raise Exception(f"Failed to download PDF: {download_result['error']}")
            
            # Step 4: Update database with file details
            file_path = download_result["file_path"]
            file_name = download_result["file_name"]
            file_size = download_result["file_size"]
            file_hash = download_result["file_hash"]
            
            update_email_pdf_status(
                process_id, 
                "completed", 
                "PDF downloaded successfully",
                pdf_filename=file_name,
                pdf_file_path=file_path,
                file_size=file_size,
                file_hash=file_hash
            )
            
            print(f"✅ PDF downloaded successfully: {file_name} ({file_size} bytes)")
            
            # Step 5: Logout
            print("🚪 Logging out of Outlook...")
            logout_outlook(page)
            
            return {
                "success": True,
                "link_found": True,
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "file_hash": file_hash,
                "error": None
            }
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email polling failed: {error_msg}")
        update_email_pdf_status(process_id, "failed", error_msg)
        
        return {
            "success": False,
            "link_found": False,
            "file_path": None,
            "file_name": None,
            "file_size": 0,
            "file_hash": None,
            "error": error_msg
        }
        
    finally:
        # Cleanup browser resources
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
        print("🧹 Email polling browser cleanup completed")

def sign_in_to_outlook(page: pw.Page, email: str, password: str) -> bool:
    """Sign into Outlook web interface - IMPROVED VERSION"""
    try:
        # Navigate to Outlook
        print("🌐 Navigating to Outlook...")
        page.goto("https://outlook.live.com/mail/", wait_until="networkidle")
        
        # Handle sign-in if not already signed in
        time.sleep(3)
        
        # IMPROVED: Better check for already signed in state
        already_signed_in_selectors = [
            "div[data-testid='app-switcher']",
            "[aria-label*='Inbox']",
            "div[role='main']",
            ".o365cs-nav-topMenuLink",
            "[data-testid='message-list']"
        ]
        
        for selector in already_signed_in_selectors:
            if page.locator(selector).count() > 0:
                print("✅ Already signed in")
                return True
        
        # Look for sign-in button or email input
        signin_buttons = [
            "a:has-text('Sign in')",
            "button:has-text('Sign in')",
            "[data-task='signin']",
            ".signin-button"
        ]
        
        for button_selector in signin_buttons:
            try:
                if page.locator(button_selector).count() > 0:
                    print("🔑 Clicking sign in...")
                    page.click(button_selector)
                    page.wait_for_load_state("networkidle")
                    break
            except:
                continue
        
        time.sleep(2)
        
        # IMPROVED: Fill email with better error handling
        print(f"📧 Entering email: {email}")
        email_filled = False
        for selector in EMAIL_SELECTORS:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, email)
                    email_filled = True
                    print(f"✅ Email filled using selector: {selector}")
                    break
            except Exception as e:
                print(f"⚠️ Failed to fill email with selector {selector}: {e}")
                continue
        
        if not email_filled:
            # Fallback email selectors
            fallback_email_selectors = [
                "input[type='email']",
                "input[name='loginfmt']",
                "input[placeholder*='email']",
                "input[id*='email']"
            ]
            for selector in fallback_email_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.fill(selector, email)
                        email_filled = True
                        print(f"✅ Email filled using fallback selector: {selector}")
                        break
                except:
                    continue
        
        if not email_filled:
            raise Exception("Could not find email input field")
        
        # Click Next
        next_clicked = False
        for selector in NEXT_BUTTON_SELECTORS:
            try:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    next_clicked = True
                    print(f"✅ Next clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not next_clicked:
            # Fallback next button selectors
            fallback_next_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value='Next']",
                "button:has-text('Next')"
            ]
            for selector in fallback_next_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        next_clicked = True
                        print(f"✅ Next clicked using fallback selector: {selector}")
                        break
                except:
                    continue
        
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # IMPROVED: Fill password with better error handling
        print("🔑 Entering password...")
        password_filled = False
        for selector in PASSWORD_SELECTORS:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, password)
                    password_filled = True
                    print(f"✅ Password filled using selector: {selector}")
                    break
            except Exception as e:
                print(f"⚠️ Failed to fill password with selector {selector}: {e}")
                continue
        
        if not password_filled:
            # Fallback password selectors
            fallback_password_selectors = [
                "input[type='password']",
                "input[name='passwd']",
                "input[placeholder*='password']",
                "input[id*='password']"
            ]
            for selector in fallback_password_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.fill(selector, password)
                        password_filled = True
                        print(f"✅ Password filled using fallback selector: {selector}")
                        break
                except:
                    continue
        
        if not password_filled:
            raise Exception("Could not find password input field")
        
        # Click Sign in
        signin_clicked = False
        for selector in NEXT_BUTTON_SELECTORS:
            try:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    signin_clicked = True
                    print(f"✅ Sign in clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not signin_clicked:
            # Fallback signin button selectors
            fallback_signin_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='Sign in']",
                "button:has-text('Sign in')"
            ]
            for selector in fallback_signin_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        signin_clicked = True
                        print(f"✅ Sign in clicked using fallback selector: {selector}")
                        break
                except:
                    continue
        
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # Handle human challenge if present
        if handle_human_challenge(page):
            print("✅ Human challenge handled")
        
        # Handle "Stay signed in?" prompt
        try:
            stay_signed_in_selectors = [
                "button:has-text('No')",
                "button:has-text('Don\\'t show this again')",
                "input[value='No']"
            ]
            for selector in stay_signed_in_selectors:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    page.wait_for_load_state("networkidle")
                    break
        except:
            pass
        
        # IMPROVED: Wait for inbox to load with multiple selectors
        inbox_selectors = [
            "[data-testid='message-list']",
            ".o365cs-nav-topMenuLink", 
            "div[role='main']",
            "[aria-label*='Inbox']",
            ".ms-FocusZone"
        ]
        
        inbox_loaded = False
        for selector in inbox_selectors:
            try:
                page.wait_for_selector(selector, timeout=30000)
                inbox_loaded = True
                print(f"✅ Inbox loaded (detected with: {selector})")
                break
            except:
                continue
        
        if not inbox_loaded:
            print("⚠️ Could not confirm inbox loaded, but continuing...")
        
        print("✅ Successfully signed into Outlook")
        return True
        
    except Exception as e:
        print(f"❌ Failed to sign into Outlook: {e}")
        return False

def wait_for_imss_email(page: pw.Page, timeout_seconds: int) -> str:
    """
    Wait for IMSS email and extract PDF link - IMPROVED VERSION
    
    Returns:
        str: PDF link URL or None if not found
    """
    try:
        print(f"👀 Waiting for IMSS email (timeout: {timeout_seconds} seconds)...")
        
        start_time = time.time()
        check_interval = 15  # Check every 15 seconds
        
        while time.time() - start_time < timeout_seconds:
            try:
                # IMPROVED: Refresh inbox with better error handling
                print("🔄 Refreshing inbox...")
                page.reload()
                
                # Wait for page to load with multiple fallback selectors
                inbox_loaded = False
                inbox_selectors = [
                    "[data-testid='message-list']",
                    ".ms-List",
                    "[role='listbox']",
                    ".ms-FocusZone",
                    "div[role='main']"
                ]
                
                for selector in inbox_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=10000)
                        inbox_loaded = True
                        break
                    except:
                        continue
                
                if not inbox_loaded:
                    print("⚠️ Could not detect inbox loading, continuing anyway...")
                
                time.sleep(3)
                
                # IMPROVED: Look for IMSS emails with better keywords
                imss_keywords = [
                    "IMSS", "Constancia", "semanas cotizadas", "Instituto Mexicano", 
                    "seguro social", "Digital", "CURP", "documento", "PDF",
                    "descarga", "trámite", "solicitud"
                ]
                
                for keyword in imss_keywords:
                    # IMPROVED: Multiple message selectors
                    message_selectors = [
                        f"[role='listitem']:has-text('{keyword}')",
                        f"div[data-testid='message-list'] div:has-text('{keyword}')",
                        f"[aria-label*='{keyword}']",
                        f"span:has-text('{keyword}')",
                        f".ms-List-cell:has-text('{keyword}')",
                        f"[role='option']:has-text('{keyword}')"
                    ]
                    
                    for selector in message_selectors:
                        try:
                            messages = page.locator(selector).all()
                            
                            if messages:
                                print(f"✅ Found potential IMSS email with keyword: {keyword} (selector: {selector})")
                                
                                # Click on the first matching message
                                try:
                                    messages[0].click()
                                    page.wait_for_load_state("networkidle")
                                    time.sleep(4)
                                    
                                    # Look for PDF link in message body
                                    pdf_link = extract_pdf_link_from_message(page)
                                    
                                    if pdf_link:
                                        return pdf_link
                                    else:
                                        print("⚠️ Message found but no PDF link detected")
                                        # Go back to inbox and continue searching
                                        page.go_back()
                                        page.wait_for_load_state("networkidle")
                                        break
                                except Exception as click_error:
                                    print(f"⚠️ Error clicking message: {click_error}")
                                    continue
                        except Exception as selector_error:
                            print(f"⚠️ Error with selector {selector}: {selector_error}")
                            continue
                
            except Exception as check_error:
                print(f"⚠️ Error during email check: {check_error}")
            
            # Show progress
            elapsed = time.time() - start_time
            remaining = timeout_seconds - elapsed
            if int(elapsed) % 60 == 0 and elapsed > 0:  # Show progress every minute
                print(f"⏰ Still waiting for IMSS email... {remaining/60:.1f} minutes remaining")
            
            time.sleep(check_interval)
        
        print("⏰ Timeout waiting for IMSS email")
        return None
        
    except Exception as e:
        print(f"❌ Error waiting for IMSS email: {e}")
        return None

def extract_pdf_link_from_message(page: pw.Page) -> str:
    """Extract PDF download link from email message - IMPROVED VERSION"""
    try:
        print("🔍 Extracting PDF link from message...")
        
        # IMPROVED: More comprehensive link selectors
        link_selectors = [
            "a[href*='.pdf']",
            "a[href*='descargar']",
            "a[href*='download']",
            "a[href*='documento']",
            "a[href*='constancia']",
            "a:has-text('Descargar')",
            "a:has-text('Ver documento')",
            "a:has-text('Constancia')",
            "a:has-text('PDF')",
            "a:has-text('Aquí')",
            "a:has-text('Link')",
            "a:has-text('Enlace')",
            "a:has-text('Documento')",
            "a:has-text('Archivo')",
            "a[href*='gob.mx']",
            "a[href*='imss']"
        ]
        
        for selector in link_selectors:
            try:
                links = page.locator(selector).all()
                if links:
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            text = link.inner_text().lower()
                            
                            if href and (
                                'pdf' in href.lower() or 
                                'descargar' in href.lower() or 
                                'download' in href.lower() or 
                                'documento' in href.lower() or
                                'constancia' in href.lower() or
                                'archivo' in href.lower()
                            ):
                                print(f"✅ Found direct PDF link: {href[:100]}...")
                                return href
                            
                            if href and text and (
                                'descargar' in text or 
                                'documento' in text or 
                                'constancia' in text or 
                                'aquí' in text or 
                                'link' in text or
                                'archivo' in text
                            ):
                                print(f"✅ Found text-based PDF link: {href[:100]}...")
                                return href
                                
                        except Exception as link_error:
                            print(f"⚠️ Error processing link: {link_error}")
                            continue
            except Exception as selector_error:
                print(f"⚠️ Error with link selector {selector}: {selector_error}")
                continue
        
        # IMPROVED: Look for any external government links
        all_links = page.locator("a[href^='http']").all()
        for link in all_links:
            try:
                href = link.get_attribute('href')
                text = link.inner_text().lower()
                
                if href and (
                    'imss' in href.lower() or 
                    'gob.mx' in href.lower() or 
                    'seguro' in href.lower() or
                    'gobierno' in href.lower()
                ) and (
                    'descargar' in text or 
                    'documento' in text or 
                    'constancia' in text or 
                    'aquí' in text or 
                    'link' in text or
                    'pdf' in text
                ):
                    print(f"✅ Found government PDF link: {href[:100]}...")
                    return href
            except:
                continue
        
        print("❌ No PDF link found in message")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting PDF link: {e}")
        return None

def download_pdf_from_link(page: pw.Page, pdf_link: str, downloads_dir: str) -> dict:
    """Download PDF from link and return file details - IMPROVED VERSION"""
    try:
        print(f"📥 Downloading PDF from: {pdf_link[:100]}...")
        
        # IMPROVED: Better download handling
        try:
            # Set up download expectation
            with page.expect_download(timeout=60000) as download_info:
                # Navigate to PDF link
                page.goto(pdf_link, wait_until="networkidle", timeout=30000)
                
            download = download_info.value
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"CURP_Constancia_{timestamp}.pdf"
            file_path = os.path.join(downloads_dir, file_name)
            
            # Save the download
            download.save_as(file_path)
            
            # Verify file was downloaded
            if not os.path.exists(file_path):
                raise Exception("File was not saved properly")
            
            # Get file info
            file_size = os.path.getsize(file_path)
            
            # Verify it's actually a PDF (check file size and basic structure)
            if file_size < 100:  # PDF files should be at least 100 bytes
                raise Exception(f"Downloaded file too small ({file_size} bytes)")
            
            file_hash = calculate_file_hash(file_path)
            
            print(f"✅ PDF downloaded: {file_name} ({file_size} bytes)")
            
            return {
                "success": True,
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "file_hash": file_hash,
                "error": None
            }
            
        except Exception as download_error:
            # Fallback: Try direct download without expect_download
            print(f"⚠️ Download expectation failed, trying direct approach: {download_error}")
            
            response = page.goto(pdf_link, wait_until="networkidle", timeout=30000)
            
            if response and response.status == 200:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"CURP_Constancia_{timestamp}.pdf"
                file_path = os.path.join(downloads_dir, file_name)
                
                # Save response body as file
                with open(file_path, 'wb') as f:
                    f.write(response.body())
                
                # Get file info
                file_size = os.path.getsize(file_path)
                file_hash = calculate_file_hash(file_path)
                
                print(f"✅ PDF downloaded (fallback method): {file_name} ({file_size} bytes)")
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "file_name": file_name,
                    "file_size": file_size,
                    "file_hash": file_hash,
                    "error": None
                }
            else:
                raise Exception(f"Failed to download PDF - HTTP {response.status if response else 'no response'}")
        
    except Exception as e:
        error_msg = f"Failed to download PDF: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "file_path": None,
            "file_name": None,
            "file_size": 0,
            "file_hash": None,
            "error": error_msg
        }

def logout_outlook(page: pw.Page):
    """Logout from Outlook - IMPROVED VERSION"""
    try:
        print("🚪 Logging out of Outlook...")
        
        # IMPROVED: Better profile menu detection
        profile_selectors = [
            "[data-testid='app-switcher']",
            "[aria-label='Account manager']",
            "button[title*='account']",
            "div[data-testid='account-manager']",
            "button[aria-label*='Account']",
            ".ms-Persona-primaryText",
            "[data-automationid='PersonaMenuTrigger']"
        ]
        
        profile_clicked = False
        for selector in profile_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    time.sleep(2)
                    profile_clicked = True
                    print(f"✅ Profile menu clicked: {selector}")
                    break
            except:
                continue
        
        if not profile_clicked:
            print("⚠️ Could not find profile menu, skipping logout")
            return
        
        # IMPROVED: Better sign out detection
        signout_selectors = [
            "a:has-text('Sign out')",
            "button:has-text('Sign out')",
            "[data-testid='sign-out']",
            "a:has-text('Cerrar sesión')",
            "button:has-text('Logout')",
            "[aria-label*='Sign out']"
        ]
        
        signout_clicked = False
        for selector in signout_selectors:
            try:
                if page.locator(selector).count() > 0:
                    page.click(selector)
                    signout_clicked = True
                    print(f"✅ Sign out clicked: {selector}")
                    break
            except:
                continue
        
        if signout_clicked:
            page.wait_for_load_state("networkidle")
            print("✅ Successfully logged out")
        else:
            print("⚠️ Could not find sign out button")
        
    except Exception as e:
        print(f"⚠️ Error during logout: {e}")

def create_downloads_directory(process_id: str) -> str:
    """Create downloads directory for process"""
    downloads_dir = os.path.join("downloads", process_id)
    os.makedirs(downloads_dir, exist_ok=True)
    return downloads_dir

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file"""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except:
        return ""

def update_email_pdf_status(process_id: str, status: str, message: str = "", **kwargs):
    """Update email PDF processing status in database"""
    try:
        conn = sqlite3.connect('curp_automation.db')
        cursor = conn.cursor()
        
        if status == "completed":
            cursor.execute('''
            UPDATE email_pdf_processing 
            SET status = ?, pdf_downloaded_at = CURRENT_TIMESTAMP,
                pdf_filename = ?, pdf_file_path = ?, file_size = ?, file_hash = ?
            WHERE process_id = ?
            ''', (status, kwargs.get('pdf_filename'), kwargs.get('pdf_file_path'), 
                  kwargs.get('file_size'), kwargs.get('file_hash'), process_id))
        elif status == "link_found":
            cursor.execute('''
            UPDATE email_pdf_processing 
            SET status = ?, pdf_link_found_at = CURRENT_TIMESTAMP
            WHERE process_id = ?
            ''', (status, process_id))
        elif status == "failed":
            cursor.execute('''
            UPDATE email_pdf_processing 
            SET status = ?, error_message = ?
            WHERE process_id = ?
            ''', (status, message, process_id))
        else:
            cursor.execute('''
            UPDATE email_pdf_processing 
            SET status = ?
            WHERE process_id = ?
            ''', (status, process_id))
        
        conn.commit()
        conn.close()
        print(f"📊 Updated email PDF status to: {status}")
        
    except Exception as e:
        print(f"⚠️ Failed to update email PDF status: {e}")

def test_email_polling():
    """Test email polling functionality"""
    print("🧪 Testing Email Polling Module")
    print("="*50)
    
    # This would be called with real credentials in actual usage
    test_email = "test@outlook.com"
    test_password = "testpassword"
    test_process_id = "test-process-123"
    
    print("⚠️ This is a test function - replace with real credentials")
    print(f"Would test polling for: {test_email}")
    
    # In real usage:
    # result = poll_and_download_pdf(test_process_id, test_email, test_password, timeout_minutes=5)
    # print(f"Result: {result}")

if __name__ == "__main__":
    test_email_polling()
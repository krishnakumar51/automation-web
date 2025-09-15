import time
from .selectors import STAY_SIGNED_IN_NO_SELECTORS

def handle_post_verification(page) -> bool:
    """Handle post-verification flow (Stay signed in?, navigate to Outlook)"""
    print(f"\n✅ HANDLING POST-VERIFICATION FLOW")
    
    try:
        # Handle "Stay signed in?" dialog
        if not handle_stay_signed_in(page):
            print("⚠️ Could not handle 'Stay signed in?' dialog")
            # Continue anyway as this might not always appear
        
        # Navigate to Outlook Mail
        # if not navigate_to_outlook_mail(page):
        #     print("⚠️ Could not navigate to Outlook Mail")
        #     # Continue anyway - user can manually navigate
        
        print("✅ Post-verification flow completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in post-verification flow: {e}")
        # Don't fail the entire process for post-verification issues
        return True

def handle_stay_signed_in(page) -> bool:
    """Handle 'Stay signed in?' dialog by clicking 'No'"""
    page.wait_for_timeout(2000)
    print("⏭️ Handling 'Stay signed in?'...")
    no_clicked = False

    for selector in STAY_SIGNED_IN_NO_SELECTORS:
        try:
            no_btn = page.wait_for_selector(selector, timeout=8000, state="visible")
            if no_btn:
                no_btn.scroll_into_view_if_needed()
                no_btn.click()
                no_clicked = True
                print("✅ Clicked 'No' on 'Stay signed in?'")
                break
        except Exception as e:
            print(f"No selector {selector} failed: {e}")

    # Fallback approach
    if not no_clicked:
        print("⚠️ Couldn't find 'No' button. Trying text content fallback...")
        buttons = page.query_selector_all("button")
        for btn in buttons:
            try:
                if btn.is_visible() and btn.inner_text().strip().lower() == "no":
                    btn.click()
                    no_clicked = True
                    print("✅ Clicked 'No' (fallback)")
                    break
            except:
                continue

    page.wait_for_timeout(15000)
    return no_clicked

# def navigate_to_outlook_mail(page) -> bool:
#     """Navigate to Outlook Mail"""
#     print("⏭️ Navigate to Outlook Mail from account dashboard...")
    
#     try:
#         # Try direct navigation first
#         page.goto('https://outlook.live.com/mail/', wait_until="domcontentloaded")
#         print("✅ Navigated to Outlook Mail!")
#         page.wait_for_timeout(5000)
#         return True
        
#     except Exception as e:
#         print(f"⚠️ Failed to navigate to Outlook Mail directly: {e}")
        
#         # Fallback: look for Mail link
#         try:
#             mail_links = ["a[aria-label='Mail']", "a:has-text('Outlook')", "a:has-text('Mail')"]
#             mail_clicked = False
            
#             for sel in mail_links:
#                 link = page.query_selector(sel)
#                 if link and link.is_visible():
#                     link.scroll_into_view_if_needed()
#                     link.click()
#                     mail_clicked = True
#                     print("✅ Clicked Mail/Outlook link on account dashboard.")
#                     page.wait_for_timeout(5000)
#                     break
                    
#             if not mail_clicked:
#                 print("⚠️ Couldn't find Mail link. User may need to manually navigate.")
#                 return False
                
#             return True
            
#         except Exception as le:
#             print(f"⚠️ Fallback Mail link failed: {le}")
#             return False

import playwright.sync_api as pw
import time
import os
import argparse
import pyautogui
from utils.outlook import create_outlook_account
import threading


def open_link(url: str, headless: bool = False) -> None:
    """
    Opens a given URL in Chrome browser using Playwright
    
    Args:
        url (str): The URL to navigate to
        headless (bool): Whether to run browser in headless mode (default: False)
    """
    with pw.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to the provided URL
        page.goto(url)
        
        # Keep browser open - uncomment the line below if you want to auto-close after 5 seconds
        # page.wait_for_timeout(5000)
        # browser.close()




# Example usage:
# open_link("https://www.google.com")
# open_link("https://github.com", headless=True)

# def run(playwright: pw.Playwright) -> None:
#     """
#     Legacy function maintained for backward compatibility
#     """
#     create_outlook_account(playwright, "pranav2602", "DefaultPassword123!", "January", "15", "1995", "Pranav", "Sharma")

if __name__ == "__main__":
    import argparse
    import sys
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Automate Outlook account creation")
    parser.add_argument("--username", "-u", type=str, 
                        help="Username for the new account (without @outlook.com)")
    parser.add_argument("--password", "-p", type=str, 
                        help="Password for the new account")
    parser.add_argument("--birth-month", "-m", type=str, 
                        help="Birth month (e.g., 'January', 'February', etc.)")
    parser.add_argument("--birth-day", "-d", type=str, 
                        help="Birth day (e.g., '1', '15', '31')")
    parser.add_argument("--birth-year", "-y", type=str, 
                        help="Birth year (e.g., '1990', '1995')")
    parser.add_argument("--first-name", "-f", type=str, 
                        help="First name for the account")
    parser.add_argument("--last-name", "-l", type=str, 
                        help="Last name for the account")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get parameters from command line or use defaults
    username = args.username if args.username else "p8288fvgh"
    password = args.password if args.password else "Pranavsurya@123"
    birth_month = getattr(args, 'birth_month') if getattr(args, 'birth_month') else "January"
    birth_day = getattr(args, 'birth_day') if getattr(args, 'birth_day') else "15" 
    birth_year = getattr(args, 'birth_year') if getattr(args, 'birth_year') else "1995"
    first_name = getattr(args, 'first_name') if getattr(args, 'first_name') else "Pranav"
    last_name = getattr(args, 'last_name') if getattr(args, 'last_name') else "Sharma"
    
    print(f"Starting account creation with username: {username}")
    print(f"Password length: {len(password)} characters")
    print(f"Birth date: {birth_month} {birth_day}, {birth_year}")
    print(f"Name: {first_name} {last_name}")
    
    # Use the with statement to ensure proper cleanup
    with pw.sync_playwright() as playwright:
        # Call create_outlook_account with all parameters
        create_outlook_account(playwright, username, password, birth_month, birth_day, birth_year, first_name, last_name)
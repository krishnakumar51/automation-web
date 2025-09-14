import time
from .selectors import (
    EMAIL_SELECTORS, PASSWORD_SELECTORS, NEXT_BUTTON_SELECTORS,
    BIRTH_MONTH_SELECTORS, BIRTH_DAY_SELECTORS, BIRTH_YEAR_SELECTORS,
    FIRST_NAME_SELECTORS, LAST_NAME_SELECTORS,
    get_month_option_selectors, get_day_option_selectors
)

def fill_email_form(page, username: str) -> bool:
    """Fill email form and click Next"""
    print(f"\n📧 FILLING EMAIL FORM: {username}")
    page.wait_for_timeout(5000)
    
    # Debug: Print all input elements found on the page
    print("=== DEBUG: Finding all input elements on page ===")
    inputs = page.query_selector_all("input")
    for i, input_elem in enumerate(inputs):
        try:
            input_type = input_elem.get_attribute("type") or "unknown"
            input_name = input_elem.get_attribute("name") or "unknown"
            input_id = input_elem.get_attribute("id") or "unknown"
            aria_label = input_elem.get_attribute("aria-label") or "unknown"
            placeholder = input_elem.get_attribute("placeholder") or "unknown"
            visible = input_elem.is_visible()
            print(f"Input {i}: type='{input_type}', name='{input_name}', id='{input_id}', aria-label='{aria_label}', placeholder='{placeholder}', visible={visible}")
        except:
            print(f"Input {i}: Could not get attributes")
    print("=== END DEBUG ===")

    page.wait_for_load_state("domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    print(f"Attempting to fill email username: {username}")
    email_filled = False

    # Try each selector
    for selector in EMAIL_SELECTORS:
        if email_filled:
            break
        try:
            print(f"Trying selector: {selector}")
            email_input = page.wait_for_selector(selector, timeout=5000, state="visible")
            if email_input:
                print(f"Found email input with selector: {selector}")
                email_input.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                email_input.click()
                page.wait_for_timeout(500)
                email_input.fill("")
                page.wait_for_timeout(500)
                email_input.type(username, delay=150)
                page.wait_for_timeout(1000)
                
                filled_value = email_input.input_value()
                if filled_value == username:
                    print(f"Successfully filled email field with: {username}")
                    email_filled = True
                    break
                else:
                    print(f"Fill verification failed. Expected: {username}, Got: {filled_value}")
        except Exception as e:
            print(f"Selector {selector} failed: {str(e)}")
            continue

    # JavaScript fallback
    if not email_filled:
        print("\nTrying JavaScript approach to find and fill email field...")
        filled = page.evaluate(f"""
        () => {{
            console.log('Starting JavaScript email field search...');
            const allInputs = Array.from(document.querySelectorAll('input'));
            console.log('Found', allInputs.length, 'input elements');
            
            const emailInputs = allInputs.filter(input => {{
                const type = (input.type || '').toLowerCase();
                const name = (input.name || '').toLowerCase();
                const ariaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
                const placeholder = (input.placeholder || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                
                const isEmailType = type === 'email';
                const hasEmailInName = name.includes('email') || name.includes('member');
                const hasEmailInLabel = ariaLabel.includes('email') || ariaLabel.includes('new email');
                const hasEmailInPlaceholder = placeholder.includes('email');
                const hasEmailInId = id.includes('email') || id.includes('floating');
                const isVisible = input.offsetParent !== null;
                
                return isVisible && (isEmailType || hasEmailInName || hasEmailInLabel ||
                    hasEmailInPlaceholder || hasEmailInId);
            }});
            
            console.log('Found', emailInputs.length, 'potential email inputs');
            if (emailInputs.length > 0) {{
                const targetInput = emailInputs[0];
                console.log('Trying to fill first email input');
                targetInput.focus();
                targetInput.value = '';
                targetInput.value = '{username}';
                targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                targetInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                console.log('Filled with:', targetInput.value);
                return targetInput.value === '{username}';
            }}
            console.log('No suitable email input found');
            return false;
        }}
        """)
        
        if filled:
            print("Successfully filled email field using JavaScript!")
            email_filled = True
            page.wait_for_timeout(1000)

    if not email_filled:
        print("FAILED: Could not find or fill the email input field")
        return False

    # Click Next button
    return click_next_button(page, "email")

def fill_password_form(page, password: str) -> bool:
    """Fill password form and click Next"""
    print(f"\n🔐 FILLING PASSWORD FORM")
    page.wait_for_timeout(5000)

    print("=== DEBUG: Finding password input elements ===")
    password_inputs = page.query_selector_all("input")
    for i, input_elem in enumerate(password_inputs):
        try:
            input_type = input_elem.get_attribute("type") or "unknown"
            input_name = input_elem.get_attribute("name") or "unknown"
            input_id = input_elem.get_attribute("id") or "unknown"
            aria_label = input_elem.get_attribute("aria-label") or "unknown"
            placeholder = input_elem.get_attribute("placeholder") or "unknown"
            visible = input_elem.is_visible()
            print(f"Password Input {i}: type='{input_type}', name='{input_name}', id='{input_id}', aria-label='{aria_label}', placeholder='{placeholder}', visible={visible}")
        except:
            print(f"Password Input {i}: Could not get attributes")
    print("=== END PASSWORD DEBUG ===")

    print(f"Attempting to fill password: {'*' * len(password)}")
    password_filled = False

    # Try each password selector
    for selector in PASSWORD_SELECTORS:
        if password_filled:
            break
        try:
            print(f"Trying password selector: {selector}")
            password_input = page.wait_for_selector(selector, timeout=5000, state="visible")
            if password_input:
                print(f"Found password input with selector: {selector}")
                password_input.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                password_input.click()
                page.wait_for_timeout(500)
                password_input.fill("")
                page.wait_for_timeout(500)
                password_input.type(password, delay=150)
                page.wait_for_timeout(1000)
                
                filled_value = password_input.input_value()
                if len(filled_value) == len(password):
                    print(f"Successfully filled password field (length: {len(password)} characters)")
                    password_filled = True
                    break
                else:
                    print(f"Password fill verification failed. Expected length: {len(password)}, Got length: {len(filled_value)}")
        except Exception as e:
            print(f"Password selector {selector} failed: {str(e)}")
            continue

    # JavaScript fallback for password
    if not password_filled:
        print("\nTrying JavaScript approach to find and fill password field...")
        filled = page.evaluate(f"""
        () => {{
            console.log('Starting JavaScript password field search...');
            const allInputs = Array.from(document.querySelectorAll('input'));
            console.log('Found', allInputs.length, 'input elements');
            
            const passwordInputs = allInputs.filter(input => {{
                const type = (input.type || '').toLowerCase();
                const name = (input.name || '').toLowerCase();
                const ariaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
                const placeholder = (input.placeholder || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                
                const isPasswordType = type === 'password';
                const hasPasswordInName = name.includes('password') || name.includes('passwd') || name.includes('pwd');
                const hasPasswordInLabel = ariaLabel.includes('password');
                const hasPasswordInPlaceholder = placeholder.includes('password');
                const hasPasswordInId = id.includes('password') || id.includes('pwd');
                const isVisible = input.offsetParent !== null;
                
                return isVisible && (isPasswordType || hasPasswordInName || hasPasswordInLabel ||
                    hasPasswordInPlaceholder || hasPasswordInId);
            }});
            
            console.log('Found', passwordInputs.length, 'potential password inputs');
            if (passwordInputs.length > 0) {{
                const targetInput = passwordInputs[0];
                console.log('Trying to fill first password input');
                targetInput.focus();
                targetInput.value = '';
                targetInput.value = '{password}';
                targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                targetInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                console.log('Filled password with length:', targetInput.value.length);
                return targetInput.value.length === {len(password)};
            }}
            console.log('No suitable password input found');
            return false;
        }}
        """)
        
        if filled:
            print("Successfully filled password field using JavaScript!")
            password_filled = True
            page.wait_for_timeout(1000)

    if not password_filled:
        print("FAILED: Could not find or fill the password input field")
        return False

    return click_next_button(page, "password")

def fill_birth_date_form(page, birth_month: str, birth_day: str, birth_year: str) -> bool:
    """Fill birth date form and click Next"""
    print(f"\n📅 FILLING BIRTH DATE FORM: {birth_month} {birth_day}, {birth_year}")
    page.wait_for_timeout(5000)

    print("=== DEBUG: Finding all form elements on birth date page ===")
    all_elements = page.query_selector_all("button, input, select")
    for i, element in enumerate(all_elements):
        try:
            tag_name = element.evaluate("el => el.tagName")
            element_type = element.get_attribute("type") or "unknown"
            element_name = element.get_attribute("name") or "unknown"
            element_id = element.get_attribute("id") or "unknown"
            aria_label = element.get_attribute("aria-label") or "unknown"
            role = element.get_attribute("role") or "unknown"
            visible = element.is_visible()
            inner_text = element.inner_text()[:50] if element.inner_text() else "no text"
            print(f"Element {i}: {tag_name}, type='{element_type}', name='{element_name}', id='{element_id}', aria-label='{aria_label}', role='{role}', visible={visible}, text='{inner_text}'")
        except:
            print(f"Element {i}: Could not get attributes")
    print("=== END BIRTH DATE DEBUG ===")

    # Fill birth month
    month_filled = fill_birth_month(page, birth_month)
    if not month_filled:
        print(f"FAILED: Could not select birth month '{birth_month}'")
        return False

    # Fill birth day
    day_filled = fill_birth_day(page, birth_day)
    if not day_filled:
        print(f"FAILED: Could not select birth day '{birth_day}'")
        return False

    # Fill birth year
    year_filled = fill_birth_year(page, birth_year)
    if not year_filled:
        print(f"FAILED: Could not fill birth year '{birth_year}'")
        return False

    print(f"\nBirth date successfully filled: {birth_month} {birth_day}, {birth_year}")
    return click_next_button(page, "birth_date")

def fill_birth_month(page, birth_month: str) -> bool:
    """Fill birth month dropdown"""
    print("\n--- FILLING BIRTH MONTH ---")
    month_filled = False
    month_button = None

    for selector in BIRTH_MONTH_SELECTORS:
        try:
            print(f"Trying month button selector: {selector}")
            found_button = page.query_selector(selector)
            if found_button and found_button.is_visible():
                month_button = found_button
                print(f"Found month button with selector: {selector}")
                break
        except Exception as e:
            print(f"Month button selector {selector} failed: {str(e)}")
            continue

    if month_button:
        try:
            month_button.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            print("Clicking month dropdown button...")
            month_button.click(force=True)
            page.wait_for_timeout(2000)

            print(f"Looking for month option: {birth_month}")
            month_option = None
            month_option_selectors = get_month_option_selectors(birth_month)

            for option_selector in month_option_selectors:
                try:
                    print(f"Trying month option selector: {option_selector}")
                    found_option = page.wait_for_selector(option_selector, timeout=3000, state="visible")
                    if found_option:
                        month_option = found_option
                        print(f"Found month option with selector: {option_selector}")
                        break
                except Exception as e:
                    print(f"Month option selector {option_selector} failed: {str(e)}")
                    continue

            if month_option:
                print(f"Clicking on month option: {birth_month}")
                month_option.click(force=True)
                month_filled = True
                page.wait_for_timeout(1000)
            else:
                # JavaScript approach
                print("Using JavaScript to find and click month option...")
                month_selected = page.evaluate(f"""
                () => {{
                    console.log('Starting JavaScript month selection for: {birth_month}');
                    const allElements = Array.from(document.querySelectorAll('*')).filter(el => {{
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
                    }});
                    
                    const monthElements = allElements.filter(el => {{
                        const text = el.textContent || el.innerText || '';
                        const exactMatch = text.trim().toLowerCase() === '{birth_month.lower()}';
                        const containsMatch = text.toLowerCase().includes('{birth_month.lower()}') && text.length < 50;
                        return exactMatch || containsMatch;
                    }});
                    
                    for (const element of monthElements) {{
                        try {{
                            const isClickable = element.tagName === 'BUTTON' ||
                                element.tagName === 'A' || element.tagName === 'DIV' ||
                                element.tagName === 'LI' || element.tagName === 'SPAN' ||
                                element.onclick || element.getAttribute('role') === 'option' ||
                                element.getAttribute('role') === 'button';
                            if (isClickable) {{
                                element.click();
                                console.log('Successfully clicked month element');
                                return true;
                            }}
                        }} catch (e) {{
                            console.log('Click failed for element:', e);
                        }}
                    }}
                    return false;
                }}
                """)
                
                if month_selected:
                    print(f"Successfully selected month '{birth_month}' using JavaScript")
                    month_filled = True
                    page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Error handling month dropdown: {str(e)}")

    return month_filled

def fill_birth_day(page, birth_day: str) -> bool:
    """Fill birth day dropdown"""
    print("\n--- FILLING BIRTH DAY ---")
    day_filled = False
    day_button = None

    for selector in BIRTH_DAY_SELECTORS:
        try:
            print(f"Trying day button selector: {selector}")
            found_button = page.query_selector(selector)
            if found_button and found_button.is_visible():
                day_button = found_button
                print(f"Found day button with selector: {selector}")
                break
        except Exception as e:
            print(f"Day button selector {selector} failed: {str(e)}")
            continue

    if day_button:
        try:
            day_button.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            print("Clicking day dropdown button...")
            day_button.click(force=True)
            page.wait_for_timeout(2000)

            print(f"Looking for day option: {birth_day}")
            day_option = None
            day_option_selectors = get_day_option_selectors(birth_day)

            for option_selector in day_option_selectors:
                try:
                    print(f"Trying day option selector: {option_selector}")
                    found_option = page.wait_for_selector(option_selector, timeout=3000, state="visible")
                    if found_option:
                        day_option = found_option
                        print(f"Found day option with selector: {option_selector}")
                        break
                except Exception as e:
                    print(f"Day option selector {option_selector} failed: {str(e)}")
                    continue

            if day_option:
                print(f"Clicking on day option: {birth_day}")
                day_option.click(force=True)
                day_filled = True
                page.wait_for_timeout(1000)
            else:
                # JavaScript approach
                print("Using JavaScript to find and click day option...")
                day_selected = page.evaluate(f"""
                () => {{
                    console.log('Starting JavaScript day selection for: {birth_day}');
                    const allElements = Array.from(document.querySelectorAll('*')).filter(el => {{
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
                    }});
                    
                    const dayElements = allElements.filter(el => {{
                        const text = (el.textContent || el.innerText || '').trim();
                        return text === '{birth_day}' || text === '{birth_day.zfill(2)}';
                    }});
                    
                    for (const element of dayElements) {{
                        try {{
                            const isClickable = element.tagName === 'BUTTON' ||
                                element.tagName === 'A' || element.tagName === 'DIV' ||
                                element.tagName === 'LI' || element.tagName === 'SPAN' ||
                                element.onclick || element.getAttribute('role') === 'option' ||
                                element.getAttribute('role') === 'button';
                            if (isClickable) {{
                                element.click();
                                console.log('Successfully clicked day element');
                                return true;
                            }}
                        }} catch (e) {{
                            console.log('Click failed for element:', e);
                        }}
                    }}
                    return false;
                }}
                """)
                
                if day_selected:
                    print(f"Successfully selected day '{birth_day}' using JavaScript")
                    day_filled = True
                    page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Error handling day dropdown: {str(e)}")

    return day_filled

def fill_birth_year(page, birth_year: str) -> bool:
    """Fill birth year input"""
    print("\n--- FILLING BIRTH YEAR ---")
    year_filled = False
    year_input = None

    for selector in BIRTH_YEAR_SELECTORS:
        try:
            print(f"Trying year input selector: {selector}")
            found_input = page.query_selector(selector)
            if found_input and found_input.is_visible():
                year_input = found_input
                print(f"Found year input with selector: {selector}")
                break
        except Exception as e:
            print(f"Year input selector {selector} failed: {str(e)}")
            continue

    if year_input:
        try:
            year_input.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            print(f"Filling year input with: {birth_year}")
            
            year_input.click()
            page.wait_for_timeout(500)
            year_input.press("Control+a")
            page.wait_for_timeout(200)
            year_input.press("Delete")
            page.wait_for_timeout(500)
            year_input.type(birth_year, delay=150)
            page.wait_for_timeout(1000)

            filled_value = year_input.input_value()
            if filled_value == birth_year:
                print(f"Successfully filled year: {birth_year}")
                year_filled = True
            else:
                print(f"Year verification failed. Expected: {birth_year}, Got: {filled_value}")
                print("Trying alternative fill method...")
                year_input.fill("")
                page.wait_for_timeout(500)
                year_input.fill(birth_year)
                page.wait_for_timeout(1000)
                filled_value = year_input.input_value()
                if filled_value == birth_year:
                    print(f"Successfully filled year with alternative method: {birth_year}")
                    year_filled = True
        except Exception as e:
            print(f"Error filling year input: {str(e)}")

    # JavaScript fallback
    if not year_filled:
        print("Trying JavaScript approach for year input...")
        filled = page.evaluate(f"""
        () => {{
            console.log('Starting JavaScript year filling for: {birth_year}');
            const allInputs = Array.from(document.querySelectorAll('input'));
            const yearInputs = allInputs.filter(input => {{
                const type = (input.type || '').toLowerCase();
                const name = (input.name || '').toLowerCase();
                const ariaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
                const id = (input.id || '').toLowerCase();
                const placeholder = (input.placeholder || '').toLowerCase();
                
                const isNumberType = type === 'number';
                const hasYearInName = name.includes('year');
                const hasYearInLabel = ariaLabel.includes('year');
                const hasYearInId = id.includes('year');
                const hasYearInPlaceholder = placeholder.includes('year');
                const isVisible = input.offsetParent !== null;
                
                return isVisible && (hasYearInName || hasYearInLabel || hasYearInId || hasYearInPlaceholder ||
                    (isNumberType && (name.includes('birth') || ariaLabel.includes('birth'))));
            }});
            
            if (yearInputs.length > 0) {{
                const yearInput = yearInputs[0];
                try {{
                    yearInput.focus();
                    yearInput.select();
                    yearInput.value = '';
                    yearInput.value = '{birth_year}';
                    yearInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    yearInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    yearInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                    console.log('Filled year with value:', yearInput.value);
                    return yearInput.value === '{birth_year}';
                }} catch (e) {{
                    console.log('Error filling year:', e);
                }}
            }}
            return false;
        }}
        """)
        
        if filled:
            print(f"Successfully filled year '{birth_year}' using JavaScript!")
            year_filled = True
            page.wait_for_timeout(1000)

    return year_filled

def fill_names_form(page, first_name: str, last_name: str) -> bool:
    """Fill first and last name form and click Next"""
    print(f"\n👤 FILLING NAMES FORM: First='{first_name}', Last='{last_name}'")
    page.wait_for_timeout(5000)

    print("=== DEBUG: Finding all input elements on name page ===")
    name_inputs = page.query_selector_all("input")
    for i, input_elem in enumerate(name_inputs):
        try:
            input_type = input_elem.get_attribute("type") or "unknown"
            input_name = input_elem.get_attribute("name") or "unknown"
            input_id = input_elem.get_attribute("id") or "unknown"
            aria_label = input_elem.get_attribute("aria-label") or "unknown"
            placeholder = input_elem.get_attribute("placeholder") or "unknown"
            visible = input_elem.is_visible()
            print(f"Name Input {i}: type='{input_type}', name='{input_name}', id='{input_id}', aria-label='{aria_label}', placeholder='{placeholder}', visible={visible}")
        except:
            print(f"Name Input {i}: Could not get attributes")
    print("=== END NAME DEBUG ===")

    # Fill first name
    first_name_filled = fill_first_name(page, first_name)
    if not first_name_filled:
        print(f"FAILED: Could not fill first name '{first_name}'")
        return False

    # Fill last name
    last_name_filled = fill_last_name(page, last_name)
    if not last_name_filled:
        print(f"FAILED: Could not fill last name '{last_name}'")
        return False

    print(f"\nNames successfully filled: First='{first_name}', Last='{last_name}'")
    return click_next_button(page, "names")

def fill_first_name(page, first_name: str) -> bool:
    """Fill first name input"""
    print("\n--- FILLING FIRST NAME ---")
    first_name_filled = False

    for selector in FIRST_NAME_SELECTORS:
        if first_name_filled:
            break
        try:
            print(f"Trying first name selector: {selector}")
            first_name_input = page.wait_for_selector(selector, timeout=5000, state="visible")
            if first_name_input:
                print(f"Found first name input with selector: {selector}")
                first_name_input.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                first_name_input.click()
                page.wait_for_timeout(500)
                first_name_input.fill("")
                page.wait_for_timeout(500)
                first_name_input.type(first_name, delay=150)
                page.wait_for_timeout(1000)
                
                filled_value = first_name_input.input_value()
                if filled_value == first_name:
                    print(f"Successfully filled first name: {first_name}")
                    first_name_filled = True
                    break
                else:
                    print(f"First name verification failed. Expected: {first_name}, Got: {filled_value}")
        except Exception as e:
            print(f"First name selector {selector} failed: {str(e)}")
            continue

    # JavaScript fallback
    if not first_name_filled:
        print("Trying JavaScript approach for first name...")
        filled = page.evaluate(f"""
        () => {{
            console.log('Starting JavaScript first name search for: {first_name}');
            const firstNameInput = document.querySelector('input[id="firstNameInput"]') ||
                document.querySelector('input[name="firstNameInput"]') ||
                Array.from(document.querySelectorAll('input')).find(input => {{
                    const id = (input.id || '').toLowerCase();
                    const name = (input.name || '').toLowerCase();
                    const ariaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
                    return id.includes('firstname') || name.includes('firstname') ||
                        ariaLabel.includes('first name') || id.includes('first');
                }});
            
            if (firstNameInput && firstNameInput.offsetParent !== null) {{
                console.log('Found first name input, filling...');
                firstNameInput.focus();
                firstNameInput.value = '';
                firstNameInput.value = '{first_name}';
                firstNameInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                firstNameInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                firstNameInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                console.log('First name filled with:', firstNameInput.value);
                return firstNameInput.value === '{first_name}';
            }}
            return false;
        }}
        """)
        
        if filled:
            print(f"Successfully filled first name '{first_name}' using JavaScript!")
            first_name_filled = True
            page.wait_for_timeout(1000)

    return first_name_filled

def fill_last_name(page, last_name: str) -> bool:
    """Fill last name input"""
    print("\n--- FILLING LAST NAME ---")
    last_name_filled = False

    for selector in LAST_NAME_SELECTORS:
        if last_name_filled:
            break
        try:
            print(f"Trying last name selector: {selector}")
            last_name_input = page.wait_for_selector(selector, timeout=5000, state="visible")
            if last_name_input:
                print(f"Found last name input with selector: {selector}")
                last_name_input.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                last_name_input.click()
                page.wait_for_timeout(500)
                last_name_input.fill("")
                page.wait_for_timeout(500)
                last_name_input.type(last_name, delay=150)
                page.wait_for_timeout(1000)
                
                filled_value = last_name_input.input_value()
                if filled_value == last_name:
                    print(f"Successfully filled last name: {last_name}")
                    last_name_filled = True
                    break
                else:
                    print(f"Last name verification failed. Expected: {last_name}, Got: {last_name}")
        except Exception as e:
            print(f"Last name selector {selector} failed: {str(e)}")
            continue

    # JavaScript fallback
    if not last_name_filled:
        print("Trying JavaScript approach for last name...")
        filled = page.evaluate(f"""
        () => {{
            console.log('Starting JavaScript last name search for: {last_name}');
            const lastNameInput = document.querySelector('input[id="lastNameInput"]') ||
                document.querySelector('input[name="lastNameInput"]') ||
                Array.from(document.querySelectorAll('input')).find(input => {{
                    const id = (input.id || '').toLowerCase();
                    const name = (input.name || '').toLowerCase();
                    const ariaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
                    return id.includes('lastname') || name.includes('lastname') ||
                        ariaLabel.includes('last name') || id.includes('last');
                }});
            
            if (lastNameInput && lastNameInput.offsetParent !== null) {{
                console.log('Found last name input, filling...');
                lastNameInput.focus();
                lastNameInput.value = '';
                lastNameInput.value = '{last_name}';
                lastNameInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                lastNameInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                lastNameInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                console.log('Last name filled with:', lastNameInput.value);
                return lastNameInput.value === '{last_name}';
            }}
            return false;
        }}
        """)
        
        if filled:
            print(f"Successfully filled last name '{last_name}' using JavaScript!")
            last_name_filled = True
            page.wait_for_timeout(1000)

    return last_name_filled

def click_next_button(page, form_type: str) -> bool:
    """Generic Next button clicking function"""
    print(f"\nLooking for Next button on {form_type} page...")
    next_clicked = False

    for selector in NEXT_BUTTON_SELECTORS:
        if next_clicked:
            break
        try:
            print(f"Trying {form_type} Next button selector: {selector}")
            next_button = page.wait_for_selector(selector, timeout=5000, state="visible")
            if next_button:
                print(f"Found {form_type} Next button with selector: {selector}")
                next_button.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                next_button.click(force=True)
                print(f"Clicked {form_type} Next button!")
                next_clicked = True
                page.wait_for_timeout(3000)
                break
        except Exception as e:
            print(f"{form_type} Next button selector {selector} failed: {str(e)}")
            continue

    # JavaScript fallback
    if not next_clicked:
        print(f"Trying JavaScript approach for {form_type} Next button...")
        clicked = page.evaluate("""
        () => {
            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"]'));
            const nextButton = buttons.find(btn => {
                const text = (btn.innerText || '').toLowerCase();
                const value = (btn.value || '').toLowerCase();
                const id = (btn.id || '').toLowerCase();
                return text.includes('next') || value.includes('next') ||
                    text.includes('create') || value.includes('create') ||
                    text.includes('continue') || value.includes('continue') ||
                    id.includes('signup') || id.includes('next') ||
                    btn.type === 'submit';
            });
            
            if (nextButton) {
                nextButton.click();
                return true;
            }
            return false;
        }
        """)
        
        if clicked:
            print(f"Clicked {form_type} Next button using JavaScript!")
            next_clicked = True
            page.wait_for_timeout(3000)

    if not next_clicked:
        print(f"Could not find or click {form_type} Next button")
        return False

    return True

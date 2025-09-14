"""
CSS selectors for Outlook account creation automation
"""

# Email input selectors
EMAIL_SELECTORS = [
    "input[aria-label='New email'][type='email']",
    "input[name='New email'][type='email']",
    "input[id='floatingLabelInput5']",
    "input[name='MemberName']",
    "input[name='NewMemberName']",
    "input[name='LiveEmailAddress']",
    "input[type='email']",
    "input[aria-label*='email' i]",
    "input[placeholder*='email' i]",
    "input[name*='email' i]",
    "input[type='text'][aria-label*='email' i]",
    "input[type='text'][name*='email' i]"
]

# Next button selectors
NEXT_BUTTON_SELECTORS = [
    "input[type='submit']",
    "button[type='submit']",
    "input[value*='Next' i]",
    "button:has-text('Next')",
    "input[id*='signup' i]",
    "button[id*='signup' i]",
    "#idSIButton9",
    "input[data-report-event='Signup_Submit']",
    "button[data-report-event='Signup_Submit']"
]

# Password input selectors
PASSWORD_SELECTORS = [
    "input[type='password']",
    "input[name='Password']",
    "input[name='passwd']",
    "input[name='password']",
    "input[aria-label*='password' i]",
    "input[placeholder*='password' i]",
    "input[id*='password' i]",
    "input[id*='pwd' i]",
    "input[aria-label='Password']",
    "input[name='NewPassword']"
]

# Birth date selectors
BIRTH_MONTH_SELECTORS = [
    "button[name='BirthMonth']",
    "button[id='BirthMonthDropdown']",
    "button[aria-label='Birth month']",
    "button[role='combobox'][name='BirthMonth']",
    "button[role='combobox'][aria-label*='month' i]",
    "button[class*='Dropdown'][name='BirthMonth']"
]

BIRTH_DAY_SELECTORS = [
    "button[name='BirthDay']",
    "button[id='BirthDayDropdown']",
    "button[aria-label='Birth day']",
    "button[role='combobox'][name='BirthDay']",
    "button[role='combobox'][aria-label*='day' i]",
    "button[class*='Dropdown'][name='BirthDay']"
]

BIRTH_YEAR_SELECTORS = [
    "input[name='BirthYear']",
    "input[id='floatingLabelInput21']",
    "input[aria-label='Birth year']",
    "input[type='number'][name='BirthYear']",
    "input[type='number'][aria-label*='year' i]",
    "input[placeholder*='year' i]"
]

# Name input selectors
FIRST_NAME_SELECTORS = [
    "input[id='firstNameInput']",
    "input[name='firstNameInput']",
    "input[id*='firstName' i]",
    "input[name*='firstName' i]",
    "input[aria-label*='first name' i]",
    "input[placeholder*='first name' i]"
]

LAST_NAME_SELECTORS = [
    "input[id='lastNameInput']",
    "input[name='lastNameInput']",
    "input[id*='lastName' i]",
    "input[name*='lastName' i]",
    "input[aria-label*='last name' i]",
    "input[placeholder*='last name' i]"
]

# Captcha and challenge selectors
IFRAME_SELECTORS = [
    'iframe[data-testid="humanCaptchaIframe"]',
    'iframe[title="Verification challenge"]',
    'iframe[src*="hsprotect.net"]',
    'iframe[src*="iframe.hsprotect.net"]'
]

# Post-verification selectors
STAY_SIGNED_IN_NO_SELECTORS = [
    "button:has-text('No')",
    "input[value='No']",
    "button[aria-label='No']"
]

def get_month_option_selectors(birth_month: str):
    """Generate month option selectors"""
    return [
        f"*[role='option']:has-text('{birth_month}')",
        f"div:has-text('{birth_month}')",
        f"li:has-text('{birth_month}')",
        f"span:has-text('{birth_month}')",
        f"button:has-text('{birth_month}')"
    ]

def get_day_option_selectors(birth_day: str):
    """Generate day option selectors"""
    return [
        f"*[role='option']:has-text('{birth_day}')",
        f"div:has-text('{birth_day}')",
        f"li:has-text('{birth_day}')",
        f"span:has-text('{birth_day}')",
        f"button:has-text('{birth_day}')"
    ]

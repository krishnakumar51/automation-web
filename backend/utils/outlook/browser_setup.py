import playwright.sync_api as pw
import time

def setup_browser_and_page(playwright: pw.Playwright):
    """
    Setup browser with stealth configuration and navigate to signup page
    
    Returns:
        tuple: (browser, context, page)
    """
    # Launch browser with stealth settings
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            '--no-first-run',
            '--no-service-autorun',
            '--no-default-browser-check',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--metrics-recording-only',
            '--no-report-upload',
            '--safebrowsing-disable-auto-update',
            '--enable-automation=false',
            '--disable-client-side-phishing-detection'
        ]
    )
    
    # Create context with stealth headers
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
        permissions=['geolocation', 'notifications'],
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        }
    )
    
    # Create page with stealth scripts
    page = context.new_page()
    page.set_default_timeout(60000)
    
    # Add stealth JavaScript
    page.add_init_script(get_stealth_script())
    
    # Navigate to signup page
    print("🌐 Navigating to Microsoft account signup page...")
    page.goto("https://signup.live.com/signup?wa=wsignin1.0&rpsnv=13&ct=1632423730&rver=7.0&wp=MBI_SSL&wreply=https%3A%2F%2Foutlook.live.com%2Fowa%2F&id=292841&CBCXT=out&lw=1&fl=dob%2Cflname%2Cwld", wait_until="domcontentloaded")
    
    # Wait for page to load
    page.wait_for_timeout(5000)
    
    # Test shadow DOM prevention
    shadow_test_result = test_shadow_dom_prevention(page)
    print(f"📊 Shadow DOM Test: {shadow_test_result['status']}")
    
    return browser, context, page

def get_stealth_script():
    """Return the stealth JavaScript injection script"""
    return """
    // Remove webdriver property completely
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        set: () => {},
        configurable: true,
        enumerable: false
    });

    // Override the chrome property with realistic values
    window.chrome = {
        runtime: {
            onConnect: undefined,
            onMessage: undefined
        },
        loadTimes: function() {
            return {
                requestTime: Date.now() / 1000 - Math.random() * 1000,
                startLoadTime: Date.now() / 1000 - Math.random() * 1000,
                commitLoadTime: Date.now() / 1000 - Math.random() * 1000,
                finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 1000,
                finishLoadTime: Date.now() / 1000 - Math.random() * 1000,
                firstPaintTime: Date.now() / 1000 - Math.random() * 1000,
                firstPaintAfterLoadTime: 0,
                navigationType: 'Other',
                wasFetchedViaSpdy: false,
                wasNpnNegotiated: false,
                npnNegotiatedProtocol: 'unknown',
                wasAlternateProtocolAvailable: false,
                connectionInfo: 'unknown'
            };
        }
    };

    // Mock realistic plugins array
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", __proto__: MimeType.prototype},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf", description: "", __proto__: MimeType.prototype},
                description: "",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            }
        ],
        configurable: true,
        enumerable: false
    });

    // Mock other navigator properties
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
        configurable: true,
        enumerable: false
    });

    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 4,
        configurable: true,
        enumerable: false
    });

    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8,
        configurable: true,
        enumerable: false
    });
    """

def test_shadow_dom_prevention(page):
    """Test if shadow DOM prevention is working"""
    return page.evaluate("""
    () => {
        const captcha = document.querySelector('#px-captcha');
        if (!captcha) {
            return {status: 'NO_CAPTCHA_FOUND', message: 'Captcha element not present - good!'};
        }
        
        const hasShadowRoot = captcha.shadowRoot !== null;
        return {
            status: hasShadowRoot ? 'SHADOW_ROOT_EXISTS' : 'SHADOW_ROOT_PREVENTED',
            hasShadowRoot: hasShadowRoot,
            message: hasShadowRoot ? 'Shadow DOM detected - automation may fail' : 'Shadow DOM prevented - automation should work'
        };
    }
    """)

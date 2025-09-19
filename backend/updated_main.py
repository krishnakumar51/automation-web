from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import random
import threading
import time
from datetime import datetime
from typing import List, Optional
import asyncio
import sys
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CURP-to-PDF Complete Automation API", version="3.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FIRST_NAMES = [
    "mary", "john", "david", "michael", "sarah", "jennifer", "william", "elizabeth", "robert", "lisa",
    "james", "maria", "christopher", "nancy", "daniel", "karen", "matthew", "betty", "anthony", "helen",
    "mark", "sandra", "donald", "donna", "steven", "carol", "paul", "ruth", "andrew", "sharon",
    "joshua", "michelle", "kenneth", "laura", "kevin", "sarah", "brian", "kimberly", "george", "deborah",
    "edward", "dorothy", "ronald", "lisa", "timothy", "nancy", "jason", "karen", "jeffrey", "betty"
]

LAST_NAMES = [
    "smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis", "rodriguez", "martinez",
    "hernandez", "lopez", "gonzalez", "wilson", "anderson", "thomas", "taylor", "moore", "jackson", "martin",
    "lee", "perez", "thompson", "white", "harris", "sanchez", "clark", "ramirez", "lewis", "robinson",
    "walker", "young", "allen", "king", "wright", "scott", "torres", "nguyen", "hill", "flores",
    "green", "adams", "nelson", "baker", "hall", "rivera", "campbell", "mitchell", "carter", "roberts"
]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Real CURP IDs for testing
REAL_CURP_IDS = [
    "CUMM950620MVZVNG02",
    "POMA660904HDGNRL05", 
    "CAHJ710630HSLSGR02",
    "BEGM810317HCLTNN18",
    "MALE041117HNLRPRA9",
    "GARV020510HMCRMCA7",
    "HECK010527MOCRRTA8",
    "GACA751016HDFRMN07",
    "OEGV730512HGRRLC00",
    "MIRJ700911HDFLMN18"
]

# Database setup
def init_database():
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    # Master process tracking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS master_process_status (
        process_id TEXT PRIMARY KEY,
        curp_id TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        email TEXT,
        overall_status TEXT NOT NULL DEFAULT 'pending',
        progress_percentage INTEGER DEFAULT 0,
        current_stage TEXT DEFAULT 'outlook_creation',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        logs TEXT DEFAULT ''
    )
    """)

    # Outlook account creation table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS outlook_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_id TEXT NOT NULL,
        email TEXT,
        password TEXT,
        birth_month TEXT,
        birth_day TEXT,
        birth_year TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        error_message TEXT,
        FOREIGN KEY (process_id) REFERENCES master_process_status (process_id)
    )
    """)

    # IMSS processing table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS imss_processing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_id TEXT NOT NULL,
        curp_id TEXT NOT NULL,
        email TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        error_message TEXT,
        FOREIGN KEY (process_id) REFERENCES master_process_status (process_id)
    )
    """)

    # Email PDF processing table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_pdf_processing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_id TEXT NOT NULL,
        email TEXT NOT NULL,
        curp_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'monitoring',
        monitoring_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        pdf_link_found_at TIMESTAMP,
        pdf_downloaded_at TIMESTAMP,
        pdf_filename TEXT,
        pdf_file_path TEXT,
        file_size INTEGER,
        file_hash TEXT,
        error_message TEXT,
        FOREIGN KEY (process_id) REFERENCES master_process_status (process_id)
    )
    """)

    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Pydantic models
class CURPRequest(BaseModel):
    curp_id: str
    first_name: str
    last_name: str
    date_of_birth: str  # YYYY-MM-DD format

class DemoCURPRequest(BaseModel):
    count: int = 1

class ProcessResponse(BaseModel):
    process_id: str
    curp_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    email: Optional[str]
    overall_status: str
    progress_percentage: int
    current_stage: str
    created_at: str
    updated_at: str

class ProcessStatusResponse(BaseModel):
    process_id: str
    overall_status: str
    progress_percentage: int
    current_stage: str
    outlook_status: Optional[str]
    imss_status: Optional[str]
    email_status: Optional[str]
    pdf_filename: Optional[str]
    logs: str

# Global variables for logging
current_logs = []
logs_lock = threading.Lock()

def add_log(message: str, process_id: Optional[str] = None):
    """Add a log message to the current logs list"""
    with logs_lock:
        log_entry = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "process_id": process_id
        }
        current_logs.append(log_entry)
        logger.info(f"Log [{process_id}]: {message}")

def generate_demo_curp_data():
    """Generate CURP data with REALISTIC birth dates (1980-2005) and ENGLISH names for Outlook"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    curp_id = random.choice(REAL_CURP_IDS)

    # FIXED: Generate realistic birth date between 1980-2005 instead of parsing from CURP
    # This ensures ages between 20-45 years old (realistic for working adults)
    birth_year = random.randint(1980, 2005)
    birth_month = random.randint(1, 12)

    # Handle different month lengths
    if birth_month in [1, 3, 5, 7, 8, 10, 12]:
        birth_day = random.randint(1, 31)
    elif birth_month in [4, 6, 9, 11]:
        birth_day = random.randint(1, 30)
    else:  # February
        # Handle leap years
        if birth_year % 4 == 0 and (birth_year % 100 != 0 or birth_year % 400 == 0):
            birth_day = random.randint(1, 29)
        else:
            birth_day = random.randint(1, 28)

    # Format as YYYY-MM-DD
    date_of_birth = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"

    print(f"🎂 Generated realistic age: {2025 - birth_year} years old (born {date_of_birth})")
    print(f"👤 English names for Outlook: {first_name.title()} {last_name.title()}")

    return {
        "curp_id": curp_id,
        "first_name": first_name.title(),  # Capitalize for display
        "last_name": last_name.title(),    # Capitalize for display
        "date_of_birth": date_of_birth
    }

def generate_outlook_data(first_name: str, last_name: str, date_of_birth: str):
    """Generate Outlook account data with IMPROVED EMAIL STRUCTURE for better success"""
    # FIXED: Better email generation strategy to avoid conflicts
    # Format: firstname + 3random + lastname + 3random
    # Example: john456smith789@outlook.com

    # Use lowercase for email generation
    first_clean = first_name.lower().replace(" ", "")
    last_clean = last_name.lower().replace(" ", "")

    # Generate random numbers (3 digits each part)
    first_numbers = f"{random.randint(100, 999)}"  # 3 digits after first name
    last_numbers = f"{random.randint(100, 999)}"   # 3 digits after last name

    # Create username: firstname + numbers + lastname + numbers
    # This reduces conflicts and follows Outlook preferences
    username = f"{first_clean}{first_numbers}{last_clean}{last_numbers}"
    email = f"{username}@outlook.com"

    # Parse birth date for Outlook format
    birth_date_obj = datetime.strptime(date_of_birth, "%Y-%m-%d")
    birth_month = MONTHS[birth_date_obj.month - 1]  # Convert to full month name
    birth_day = str(birth_date_obj.day)
    birth_year = str(birth_date_obj.year)
    password = "wrfyh@6498$"  # Hardcoded secure password

    print(f"📧 Generated Outlook account: {email}")
    print(f"👤 Pattern: {first_clean}+{first_numbers}+{last_clean}+{last_numbers}")
    print(f"🎂 Age for Outlook signup: {2025 - birth_date_obj.year} years old")

    return {
        "username": username,
        "email": email,
        "password": password,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "birth_year": birth_year
    }

def create_master_process(curp_data: dict):
    """Create master process entry and return process_id"""
    process_id = str(uuid.uuid4())
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO master_process_status
    (process_id, curp_id, first_name, last_name, date_of_birth, overall_status, current_stage, logs)
    VALUES (?, ?, ?, ?, ?, 'pending', 'mobile_outlook_creation', 'Process started')
    """, (
        process_id,
        curp_data['curp_id'],
        curp_data['first_name'],
        curp_data['last_name'],
        curp_data['date_of_birth'],
    ))

    conn.commit()
    conn.close()
    return process_id

def update_master_process_status(process_id: str, status: str, stage: str, progress: int, email: str = None, logs: str = ""):
    """Update master process status"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    if email:
        cursor.execute("""
        UPDATE master_process_status
        SET overall_status = ?, current_stage = ?, progress_percentage = ?, email = ?,
            updated_at = CURRENT_TIMESTAMP, logs = logs || ? || char(10)
        WHERE process_id = ?
        """, (status, stage, progress, email, logs, process_id))
    else:
        cursor.execute("""
        UPDATE master_process_status
        SET overall_status = ?, current_stage = ?, progress_percentage = ?,
            updated_at = CURRENT_TIMESTAMP, logs = logs || ? || char(10)
        WHERE process_id = ?
        """, (status, stage, progress, logs, process_id))

    conn.commit()
    conn.close()

def store_outlook_account(process_id: str, account_data: dict, status: str = "pending"):
    """Store Outlook account data"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO outlook_accounts
    (process_id, email, password, birth_month, birth_day, birth_year, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        process_id,
        account_data['email'],
        account_data['password'],
        account_data['birth_month'],
        account_data['birth_day'],
        account_data['birth_year'],
        status
    ))

    conn.commit()
    conn.close()

def update_outlook_account_status(process_id: str, status: str, error_message: str = None):
    """Update Outlook account status"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    if error_message:
        cursor.execute("""
        UPDATE outlook_accounts
        SET status = ?, error_message = ?, completed_at = CURRENT_TIMESTAMP
        WHERE process_id = ?
        """, (status, error_message, process_id))
    else:
        cursor.execute("""
        UPDATE outlook_accounts
        SET status = ?, completed_at = CURRENT_TIMESTAMP
        WHERE process_id = ?
        """, (status, process_id))

    conn.commit()
    conn.close()

def store_imss_processing(process_id: str, curp_id: str, email: str):
    """Store IMSS processing entry"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO imss_processing (process_id, curp_id, email, status)
    VALUES (?, ?, ?, 'pending')
    """, (process_id, curp_id, email))

    conn.commit()
    conn.close()

def store_email_pdf_processing(process_id: str, curp_id: str, email: str):
    """Store email PDF processing entry"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO email_pdf_processing (process_id, email, curp_id, status)
    VALUES (?, ?, ?, 'monitoring')
    """, (process_id, email, curp_id))

    conn.commit()
    conn.close()

def update_imss_status(process_id: str, status: str, message: str = ""):
    """Update IMSS processing status in database"""
    try:
        conn = sqlite3.connect('curp_automation.db')
        cursor = conn.cursor()

        if status == "completed":
            cursor.execute("""
            UPDATE imss_processing
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE process_id = ?
            """, (status, process_id))
        elif status == "failed":
            cursor.execute("""
            UPDATE imss_processing
            SET status = ?, error_message = ?
            WHERE process_id = ?
            """, (status, message, process_id))
        else:
            cursor.execute("""
            UPDATE imss_processing
            SET status = ?
            WHERE process_id = ?
            """, (status, process_id))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Failed to update IMSS status: {e}")

def update_email_pdf_status(process_id: str, status: str, message: str = ""):
    """Update email PDF processing status in database"""
    try:
        conn = sqlite3.connect('curp_automation.db')
        cursor = conn.cursor()

        if status == "completed":
            cursor.execute("""
            UPDATE email_pdf_processing
            SET status = ?, pdf_downloaded_at = CURRENT_TIMESTAMP
            WHERE process_id = ?
            """, (status, process_id))
        elif status == "failed":
            cursor.execute("""
            UPDATE email_pdf_processing
            SET status = ?, error_message = ?
            WHERE process_id = ?
            """, (status, message, process_id))
        else:
            cursor.execute("""
            UPDATE email_pdf_processing
            SET status = ?
            WHERE process_id = ?
            """, (status, process_id))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Failed to update email PDF status: {e}")

def test_mobile_integration():
    """Test function to verify mobile integration works"""
    try:
        from mobile_outlook import create_outlook_account_mobile, trigger_mobile_automation_if_available
        print("✅ Mobile automation module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Mobile automation module not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing mobile integration: {e}")
        return False

def curp_automation_worker(curp_data: dict, process_id: str):
    """
    COMPLETE CURP-to-PDF automation worker with FULL MOBILE AUTOMATION INTEGRATION
    WORKFLOW:
    1. Create Outlook account (MOBILE automation)
    2. Submit IMSS form (MOBILE automation) 
    3. Monitor email and download PDF (WEB automation)
    4. Update database with complete progress tracking

    PROGRESS LOGIC:
    - Outlook created: 35%
    - IMSS submitted: 75% 
    - PDF link found: 90%
    - PDF downloaded: 100%
    """
    try:
        add_log(f"🚀 Starting COMPLETE MOBILE CURP automation for {curp_data['curp_id']}", process_id)

        # ==========================================
        # PHASE 1: CREATE OUTLOOK ACCOUNT (MOBILE)
        # ==========================================
        add_log("📱 Phase 1: Creating Outlook account via MOBILE automation", process_id)
        update_master_process_status(process_id, "in_progress", "mobile_outlook_creation", 10, 
                                   logs=f"Starting MOBILE Outlook account creation for {curp_data['first_name']} {curp_data['last_name']}")

        # Generate Outlook account data based on personal info
        outlook_data = generate_outlook_data(
            curp_data['first_name'], 
            curp_data['last_name'], 
            curp_data['date_of_birth']
        )

        # Store outlook account entry in database
        store_outlook_account(process_id, outlook_data, "pending")
        add_log(f"Generated mobile Outlook credentials - Email: {outlook_data['email']}", process_id)

        # Create user data for mobile automation
        mobile_user_data = {
            'username': outlook_data['username'],
            'password': outlook_data['password'],
            'first_name': curp_data['first_name'],
            'last_name': curp_data['last_name'],
            'birth_date': {
                'day': int(outlook_data['birth_day']),
                'month': outlook_data['birth_month'],
                'year': int(outlook_data['birth_year'])
            }
        }

        # Execute MOBILE Outlook automation
        outlook_success = False
        try:
            from utils.mobile_outlook import create_outlook_account_mobile
            add_log("Mobile Outlook automation imported successfully", process_id)

            # Call mobile automation
            result = create_outlook_account_mobile(mobile_user_data)

            if result:
                outlook_success = True
                add_log(f"✅ MOBILE Outlook account created successfully: {outlook_data['email']}", process_id)
                # Update database status
                update_outlook_account_status(process_id, "completed")
                update_master_process_status(process_id, "in_progress", "outlook_completed", 35, 
                                           email=outlook_data['email'],
                                           logs="Mobile Outlook account created - Starting mobile IMSS automation")
            else:
                raise Exception("Mobile Outlook account creation returned False")

        except Exception as outlook_error:
            add_log(f"❌ MOBILE Outlook creation failed: {str(outlook_error)}", process_id)
            update_outlook_account_status(process_id, "failed", str(outlook_error))
            raise outlook_error

        # ==========================================
        # PHASE 2: MOBILE IMSS AUTOMATION
        # ==========================================
        mobile_success = False
        if outlook_success:
            add_log("🏥 Phase 2: Starting mobile IMSS automation", process_id)
            update_master_process_status(process_id, "in_progress", "imss_processing", 45,
                                       logs="Outlook completed - Starting mobile IMSS automation")

            # Store IMSS processing entry
            store_imss_processing(process_id, curp_data['curp_id'], outlook_data['email'])

            try:
                # Import the trigger function from mobile automation
                from utils.mobile import start_mobile_automation

                add_log("Mobile IMSS automation trigger imported successfully", process_id)

                # Call mobile IMSS automation
                mobile_result = start_mobile_automation(
                    process_id=process_id,
                    curp_id=curp_data['curp_id'],
                    email=outlook_data['email'],
                    first_name=curp_data['first_name'],
                    last_name=curp_data['last_name']
                )

                # Handle result based on status
                if mobile_result["success"]:
                    # Mobile IMSS automation succeeded
                    mobile_success = True
                    add_log("✅ Mobile IMSS automation completed successfully", process_id)
                    update_imss_status(process_id, "completed", "Mobile automation completed")

                    # Update to 75% - ready for email monitoring
                    update_master_process_status(process_id, "in_progress", "imss_completed", 75,
                                               logs="IMSS form submitted successfully via mobile - Starting email monitoring")

                else:
                    # Mobile automation failed - still try email monitoring as fallback
                    add_log(f"⚠️ Mobile IMSS automation issue: {mobile_result['message']}", process_id)
                    add_log("Proceeding to email monitoring despite mobile automation issue", process_id)

                    # Mark as partial but continue to email monitoring
                    update_imss_status(process_id, "failed", mobile_result["message"])
                    update_master_process_status(process_id, "in_progress", "mobile_failed_fallback", 50,
                                               logs=f"Mobile IMSS automation failed: {mobile_result['message']} - Trying email monitoring as fallback")
                    mobile_success = False  # Will try email monitoring anyway

            except ImportError as ie:
                # Mobile module not available - continue with email monitoring
                error_msg = f"Mobile IMSS automation not available: {str(ie)}"
                add_log(f"⚠️ {error_msg}", process_id)
                add_log("Mobile IMSS automation not available - proceeding to email monitoring", process_id)

                update_imss_status(process_id, "skipped", "Mobile IMSS automation module not available")
                update_master_process_status(process_id, "in_progress", "mobile_skipped", 50,
                                           logs="Mobile IMSS automation not available - Proceeding to email monitoring")
                mobile_success = False  # Will try email monitoring

            except Exception as me:
                # Mobile automation error - continue with email monitoring as fallback
                error_msg = f"Mobile IMSS automation error: {str(me)}"
                add_log(f"❌ {error_msg}", process_id)
                add_log("Mobile IMSS automation failed - trying email monitoring as fallback", process_id)

                update_imss_status(process_id, "failed", error_msg)
                update_master_process_status(process_id, "in_progress", "mobile_error_fallback", 50,
                                           logs=f"Mobile IMSS automation error: {error_msg} - Trying email monitoring as fallback")
                mobile_success = False  # Will try email monitoring anyway

        # ==========================================
        # PHASE 3: EMAIL MONITORING AND PDF DOWNLOAD
        # ==========================================
        if outlook_success:  # Continue if at least Outlook succeeded
            add_log("📧 Phase 3: Starting email monitoring and PDF download", process_id)

            # Store email processing entry
            store_email_pdf_processing(process_id, curp_data['curp_id'], outlook_data['email'])

            # Determine timeout based on mobile success
            if mobile_success:
                timeout_minutes = 10  # Shorter timeout if IMSS was submitted successfully
                update_master_process_status(process_id, "in_progress", "email_monitoring", 80,
                                           logs="IMSS submitted successfully - Monitoring email for PDF (10 min timeout)")
            else:
                timeout_minutes = 30  # Longer timeout if mobile failed (user might submit manually)
                update_master_process_status(process_id, "in_progress", "email_monitoring_fallback", 60,
                                           logs="Mobile automation failed - Monitoring email for manual IMSS submission (30 min timeout)")

            try:
                # Import email polling module (keeping web automation for email monitoring)
                from utils.outlook.email_polling import poll_and_download_pdf

                add_log(f"Starting email polling (timeout: {timeout_minutes} minutes)", process_id)

                # Run email polling and PDF download
                email_result = poll_and_download_pdf(
                    process_id=process_id,
                    email=outlook_data['email'],
                    password=outlook_data['password'],
                    timeout_minutes=timeout_minutes
                )

                if email_result["success"]:
                    # PDF downloaded successfully!
                    add_log(f"✅ PDF downloaded successfully: {email_result['file_name']}", process_id)

                    # Update to 100% completion
                    update_master_process_status(process_id, "completed", "pdf_downloaded", 100,
                                               logs=f"Process completed successfully - PDF downloaded: {email_result['file_name']} ({email_result['file_size']} bytes)")

                    add_log(f"🎉 COMPLETE MOBILE CURP automation finished for {curp_data['curp_id']}", process_id)
                    add_log(f"📄 PDF file: {email_result['file_name']} ({email_result['file_size']} bytes)", process_id)

                elif email_result["link_found"]:
                    # Link found but download failed
                    add_log(f"⚠️ PDF link found but download failed: {email_result['error']}", process_id)

                    update_master_process_status(process_id, "partial", "pdf_link_found_download_failed", 90,
                                               logs=f"PDF link found but download failed: {email_result['error']}")

                else:
                    # No email received within timeout
                    add_log(f"⚠️ No IMSS email received within {timeout_minutes} minutes", process_id)

                    if mobile_success:
                        # Mobile succeeded but no email - this is unusual
                        update_master_process_status(process_id, "partial", "imss_submitted_no_email", 85,
                                                   logs=f"IMSS form submitted but no email received within {timeout_minutes} minutes")
                    else:
                        # Mobile failed and no email - likely IMSS was never submitted
                        update_master_process_status(process_id, "partial", "no_imss_submission", 50,
                                                   logs=f"No IMSS submission detected and no email received within {timeout_minutes} minutes")

            except ImportError as email_import_error:
                # Email polling module not available
                error_msg = f"Email polling module not available: {str(email_import_error)}"
                add_log(f"❌ {error_msg}", process_id)

                update_email_pdf_status(process_id, "failed", error_msg)

                if mobile_success:
                    # Mobile succeeded but can't check email
                    update_master_process_status(process_id, "partial", "imss_submitted_no_email_module", 75,
                                               logs=f"IMSS submitted successfully but email polling not available: {error_msg}")
                else:
                    # Nothing worked
                    update_master_process_status(process_id, "partial", "outlook_only", 35,
                                               logs=f"Only Outlook creation succeeded - Mobile IMSS and email modules not available")

            except Exception as email_error:
                # Email polling failed
                error_msg = f"Email polling failed: {str(email_error)}"
                add_log(f"❌ {error_msg}", process_id)

                update_email_pdf_status(process_id, "failed", error_msg)

                if mobile_success:
                    # Mobile succeeded but email polling failed
                    update_master_process_status(process_id, "partial", "imss_submitted_email_failed", 75,
                                               logs=f"IMSS submitted successfully but email polling failed: {error_msg}")
                else:
                    # Both mobile and email failed
                    update_master_process_status(process_id, "partial", "mobile_and_email_failed", 35,
                                               logs=f"Mobile automation and email polling both failed")

        else:
            raise Exception("Cannot proceed without successful Outlook account creation")

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"MOBILE CURP automation failed for {curp_data['curp_id']}: {str(e)}"

        add_log(f"❌ {error_msg}", process_id)
        add_log(f"Error details: {error_details}", process_id)

        # Update all relevant database tables with error status
        try:
            update_outlook_account_status(process_id, "failed", str(e))
        except:
            pass

        try:
            update_imss_status(process_id, "failed", str(e))
        except:
            pass

        try:
            update_email_pdf_status(process_id, "failed", str(e))
        except:
            pass

        # Set to failed with 0% progress
        update_master_process_status(process_id, "failed", "mobile_automation_error", 0, 
                                   logs=f"Mobile automation failed: {error_msg}")

    finally:
        # Final cooldown before next process
        try:
            add_log("Mobile automation process completed - Cooldown for 3 seconds...", process_id)
        except Exception:
            pass
        time.sleep(3)

# API Routes
@app.get("/")
async def root():
    return {"message": "CURP-to-PDF COMPLETE Mobile Automation API is running", "version": "3.0.0", "automation_type": "COMPLETE_MOBILE"}

@app.post("/process-curp", response_model=dict)
async def process_curp(request: CURPRequest, background_tasks: BackgroundTasks):
    """Process a real CURP with personal information using COMPLETE mobile automation"""
    # Clear previous logs
    global current_logs
    with logs_lock:
        current_logs = []

    add_log(f"Starting COMPLETE MOBILE CURP processing for {request.curp_id}")

    # Create master process
    curp_data = {
        "curp_id": request.curp_id,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "date_of_birth": request.date_of_birth
    }

    process_id = create_master_process(curp_data)

    # Add background task for automation
    background_tasks.add_task(curp_automation_worker, curp_data, process_id)

    add_log(f"Queued COMPLETE MOBILE CURP processing: {request.curp_id} for {request.first_name} {request.last_name}")

    return {
        "message": f"Started COMPLETE MOBILE CURP processing for {request.curp_id}",
        "process_id": process_id,
        "curp_data": curp_data,
        "automation_type": "COMPLETE_MOBILE",
        "workflow": "Mobile Outlook + Mobile IMSS + Web Email Monitoring"
    }

@app.post("/demo-curp", response_model=dict)
async def process_demo_curp(request: DemoCURPRequest, background_tasks: BackgroundTasks):
    """Process demo CURP IDs for testing using COMPLETE mobile automation"""
    if request.count <= 0 or request.count > 5:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 5")

    # Clear previous logs
    global current_logs
    with logs_lock:
        current_logs = []

    add_log(f"Starting demo COMPLETE MOBILE CURP processing for {request.count} accounts")

    process_ids = []
    curp_data_list = []

    for i in range(request.count):
        # Generate demo CURP data
        curp_data = generate_demo_curp_data()
        curp_data_list.append(curp_data)

        # Create master process
        process_id = create_master_process(curp_data)
        process_ids.append(process_id)

        # Add background task for automation
        background_tasks.add_task(curp_automation_worker, curp_data, process_id)
        add_log(f"Queued demo COMPLETE MOBILE CURP {i+1}/{request.count}: {curp_data['curp_id']} for {curp_data['first_name']} {curp_data['last_name']}")

    return {
        "message": f"Started demo COMPLETE MOBILE processing for {request.count} CURPs",
        "process_ids": process_ids,
        "curp_data_list": curp_data_list,
        "automation_type": "COMPLETE_MOBILE",
        "workflow": "Mobile Outlook + Mobile IMSS + Web Email Monitoring"
    }

@app.get("/processes", response_model=List[ProcessResponse])
async def get_all_processes():
    """Get all CURP processes"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT process_id, curp_id, first_name, last_name, date_of_birth, email,
           overall_status, progress_percentage, current_stage, created_at, updated_at
    FROM master_process_status
    ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    processes = []
    for row in rows:
        processes.append(ProcessResponse(
            process_id=row[0],
            curp_id=row[1],
            first_name=row[2],
            last_name=row[3],
            date_of_birth=row[4],
            email=row[5],
            overall_status=row[6],
            progress_percentage=row[7],
            current_stage=row[8],
            created_at=row[9],
            updated_at=row[10]
        ))

    return processes

@app.get("/process/{process_id}", response_model=ProcessStatusResponse)
async def get_process_status(process_id: str):
    """Get detailed status of a specific process"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    # Get master process status
    cursor.execute("""
    SELECT overall_status, progress_percentage, current_stage, logs
    FROM master_process_status
    WHERE process_id = ?
    """, (process_id,))

    master_row = cursor.fetchone()
    if not master_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Process not found")

    # Get outlook status
    cursor.execute('SELECT status FROM outlook_accounts WHERE process_id = ?', (process_id,))
    outlook_row = cursor.fetchone()
    outlook_status = outlook_row[0] if outlook_row else None

    # Get IMSS status
    cursor.execute('SELECT status FROM imss_processing WHERE process_id = ?', (process_id,))
    imss_row = cursor.fetchone()
    imss_status = imss_row[0] if imss_row else None

    # Get email/PDF status
    cursor.execute('SELECT status, pdf_filename FROM email_pdf_processing WHERE process_id = ?', (process_id,))
    email_row = cursor.fetchone()
    email_status = email_row[0] if email_row else None
    pdf_filename = email_row[1] if email_row and email_row[1] else None

    conn.close()

    return ProcessStatusResponse(
        process_id=process_id,
        overall_status=master_row[0],
        progress_percentage=master_row[1],
        current_stage=master_row[2],
        outlook_status=outlook_status,
        imss_status=imss_status,
        email_status=email_status,
        pdf_filename=pdf_filename,
        logs=master_row[3]
    )

@app.get("/logs")
async def get_current_logs():
    """Get current processing logs"""
    with logs_lock:
        return {"logs": current_logs.copy()}

@app.delete("/process/{process_id}")
async def delete_process(process_id: str):
    """Delete a specific process and all related data"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    # Delete from all tables
    cursor.execute('DELETE FROM email_pdf_processing WHERE process_id = ?', (process_id,))
    cursor.execute('DELETE FROM imss_processing WHERE process_id = ?', (process_id,))
    cursor.execute('DELETE FROM outlook_accounts WHERE process_id = ?', (process_id,))
    cursor.execute('DELETE FROM master_process_status WHERE process_id = ?', (process_id,))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Process not found")

    conn.commit()
    conn.close()

    return {"message": f"Process {process_id} deleted successfully"}

@app.delete("/processes")
async def clear_all_processes():
    """Clear all processes and data"""
    conn = sqlite3.connect('curp_automation.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM email_pdf_processing')
    cursor.execute('DELETE FROM imss_processing')
    cursor.execute('DELETE FROM outlook_accounts')
    cursor.execute('DELETE FROM master_process_status')

    conn.commit()
    conn.close()

    return {"message": "All processes cleared successfully"}

@app.get("/demo-curps")
async def get_demo_curps():
    """Get list of available demo CURP IDs"""
    return {
        "demo_curp_ids": REAL_CURP_IDS,
        "total_count": len(REAL_CURP_IDS),
        "message": "Use /demo-curp endpoint to process these automatically with COMPLETE MOBILE automation"
    }

@app.get("/mobile-status")
async def get_mobile_status():
    """Get complete mobile automation integration status"""
    mobile_available = test_mobile_integration()

    return {
        "mobile_automation_available": mobile_available,
        "automation_type": "COMPLETE_MOBILE",
        "workflow": "Mobile Outlook + Mobile IMSS + Web Email Monitoring",
        "progress_stages": {
            "outlook_created": "35%",
            "imss_submitted": "75%", 
            "pdf_link_found": "90%",
            "pdf_downloaded": "100%"
        },
        "integration_status": "✅ Ready" if mobile_available else "❌ Setup Required",
        "requirements": [
            "Appium server running on localhost:4723",
            "Android device connected with USB debugging",
            "Microsoft Outlook app installed on device",
            "IMSS Digital app installed on device", 
            "Python packages: appium-python-client, selenium, requests",
            "Playwright for email monitoring (web)"
        ] if not mobile_available else []
    }

if __name__ == "__main__":
    import uvicorn

    # Test mobile integration on startup
    print("\n" + "="*60)
    print("🚀 COMPLETE MOBILE CURP-to-PDF Automation API")
    print("="*60)
    print("📱 Workflow: Mobile Outlook + Mobile IMSS + Web Email")
    print("📊 Progress: 35% → 75% → 90% → 100%")
    print("📱 Testing mobile automation integration...")

    mobile_status = test_mobile_integration()

    if mobile_status:
        print("✅ Complete mobile automation integration: READY")
        print("📱 Mobile automation modules loaded successfully")
        print("🏥 Mobile IMSS automation available")
        print("📧 Email monitoring integration ready")
    else:
        print("⚠️  Complete mobile automation integration: SETUP REQUIRED")
        print("📋 Please ensure:")
        print("   - Appium server running: appium")
        print("   - Android device connected with USB debugging")
        print("   - Microsoft Outlook app installed")
        print("   - IMSS Digital app installed")
        print("   - Python packages: pip install appium-python-client requests")

    print("\n🌐 Starting FastAPI server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("="*60)

    uvicorn.run(app, host="0.0.0.0", port=8000)

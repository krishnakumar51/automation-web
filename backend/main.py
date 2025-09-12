from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import random
import threading
import time
from datetime import datetime
from typing import List, Optional
import playwright.sync_api as pw
from utils.outlook import create_outlook_account
import asyncio
import sys
import logging

# Ensure Windows event loop policy supports subprocess in threads (Playwright)
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Outlook Account Creator API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data lists
FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
    "William", "Ashley", "James", "Amanda", "Christopher", "Stephanie", "Daniel",
    "Melissa", "Matthew", "Nicole", "Anthony", "Elizabeth", "Mark", "Heather",
    "Donald", "Michelle", "Steven", "Kimberly", "Paul", "Amy", "Andrew", "Angela",
    "Joshua", "Brenda", "Kenneth", "Emma", "Kevin", "Olivia", "Brian", "Cynthia",
    "George", "Marie", "Edward", "Janet", "Ronald", "Catherine", "Timothy", "Frances"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Database setup
def init_database():
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            birth_month TEXT NOT NULL,
            birth_day TEXT NOT NULL,
            birth_year TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            logs TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Pydantic models
class AccountRequest(BaseModel):
    count: int

class AccountResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    password: str
    birth_month: str
    birth_day: str
    birth_year: str
    status: str
    created_at: str
    logs: Optional[str] = None

class LogMessage(BaseModel):
    message: str
    timestamp: str
    account_id: Optional[int] = None

# Global variables for logging
current_logs = []
logs_lock = threading.Lock()

def add_log(message: str, account_id: Optional[int] = None):
    """Add a log message to the current logs list"""
    with logs_lock:
        log_entry = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "account_id": account_id
        }
        current_logs.append(log_entry)
        logger.info(f"Log: {message}")

def generate_demo_data():
    """Generate random demo data for account creation"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Generate 5 random numbers
    random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    
    # Create email in format: firstname + 5 random numbers + lastname@outlook.com
    email = f"{first_name.lower()}{random_numbers}{last_name.lower()}@outlook.com"
    username = f"{first_name.lower()}{random_numbers}{last_name.lower()}"
    
    # Generate random birth date
    birth_month = random.choice(MONTHS)
    birth_day = str(random.randint(1, 28))  # Using 28 to avoid month-specific day issues
    birth_year = str(random.randint(1980, 2000))
    
    password = "Test@12345"  # Hardcoded as requested
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "username": username,
        "password": password,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "birth_year": birth_year
    }

def save_account_to_db(account_data: dict, status: str = "pending", logs: str = ""):
    """Save account data to database"""
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO accounts (first_name, last_name, email, password, birth_month, birth_day, birth_year, status, logs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        account_data['first_name'],
        account_data['last_name'],
        account_data['email'],
        account_data['password'],
        account_data['birth_month'],
        account_data['birth_day'],
        account_data['birth_year'],
        status,
        logs
    ))
    account_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return account_id

def update_account_status(account_id: int, status: str, logs: str = ""):
    """Update account status in database"""
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE accounts SET status = ?, logs = ? WHERE id = ?
    ''', (status, logs, account_id))
    conn.commit()
    conn.close()

def create_account_worker(account_data: dict, account_id: int):
    """Worker function to create a single account"""
    try:
        add_log(f"Starting account creation for {account_data['email']}", account_id)
        
        # Debug output similar to app.py
        username = account_data['username']
        password = account_data['password']
        birth_month = account_data['birth_month']
        birth_day = account_data['birth_day']
        birth_year = account_data['birth_year']
        first_name = account_data['first_name']
        last_name = account_data['last_name']
        
        add_log(f"Account creation parameters - Username: {username}, Password length: {len(password)} characters", account_id)
        add_log(f"Birth date: {birth_month} {birth_day}, {birth_year}, Name: {first_name} {last_name}", account_id)
        
        # Use the same pattern as working app.py
        with pw.sync_playwright() as playwright:
            add_log(f"Playwright context initialized for {account_data['email']}", account_id)
            
            # Call create_outlook_account with all parameters (same as app.py)
            create_outlook_account(
                playwright, 
                username, 
                password, 
                birth_month, 
                birth_day, 
                birth_year, 
                first_name, 
                last_name
            )
        
        add_log(f"Successfully created account: {account_data['email']}", account_id)
        update_account_status(account_id, "success", "Account created successfully")
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"Failed to create account {account_data['email']}: {str(e)}"
        detailed_error = f"Error details: {error_details}"
        
        add_log(error_msg, account_id)
        add_log(detailed_error, account_id)
        update_account_status(account_id, "failed", f"{error_msg}\n{detailed_error}")

@app.get("/")
async def root():
    return {"message": "Outlook Account Creator API is running"}

@app.post("/create-accounts")
async def create_accounts(request: AccountRequest, background_tasks: BackgroundTasks):
    """Create multiple Outlook accounts"""
    if request.count <= 0 or request.count > 10:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 10")
    
    # Clear previous logs
    global current_logs
    with logs_lock:
        current_logs = []
    
    add_log(f"Starting creation of {request.count} accounts")
    
    account_ids = []
    
    for i in range(request.count):
        # Generate demo data
        account_data = generate_demo_data()
        
        # Save to database
        account_id = save_account_to_db(account_data)
        account_ids.append(account_id)
        
        # Add background task for account creation
        background_tasks.add_task(create_account_worker, account_data, account_id)
        
        add_log(f"Queued account {i+1}/{request.count}: {account_data['email']}")
    
    return {
        "message": f"Started creation of {request.count} accounts",
        "account_ids": account_ids
    }

@app.post("/demo")
async def create_demo_account(background_tasks: BackgroundTasks):
    """Create a single demo account"""
    # Clear previous logs
    global current_logs
    with logs_lock:
        current_logs = []
    
    add_log("Starting demo account creation")
    
    # Generate demo data
    account_data = generate_demo_data()
    
    # Save to database
    account_id = save_account_to_db(account_data)
    
    # Add background task for account creation
    background_tasks.add_task(create_account_worker, account_data, account_id)
    
    add_log(f"Queued demo account: {account_data['email']}")
    
    return {
        "message": "Started demo account creation",
        "account_id": account_id,
        "account_data": account_data
    }

@app.get("/accounts", response_model=List[AccountResponse])
async def get_accounts():
    """Get all accounts from database"""
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, first_name, last_name, email, password, birth_month, birth_day, birth_year, status, created_at, logs
        FROM accounts ORDER BY created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    accounts = []
    for row in rows:
        accounts.append(AccountResponse(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            password=row[4],
            birth_month=row[5],
            birth_day=row[6],
            birth_year=row[7],
            status=row[8],
            created_at=row[9],
            logs=row[10]
        ))
    
    return accounts

@app.get("/logs")
async def get_logs():
    """Get current logs"""
    with logs_lock:
        return {"logs": current_logs.copy()}

@app.delete("/accounts/{account_id}")
async def delete_account(account_id: int):
    """Delete an account from database"""
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Account not found")
    conn.commit()
    conn.close()
    return {"message": "Account deleted successfully"}

@app.delete("/accounts")
async def clear_all_accounts():
    """Clear all accounts from database"""
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts')
    conn.commit()
    conn.close()
    return {"message": "All accounts cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
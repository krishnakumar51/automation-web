# Outlook Account Creator API

A FastAPI-based backend service for automating Outlook account creation with a web interface.

## Features

- **Automated Account Creation**: Creates Outlook accounts using Playwright automation
- **Demo Data Generation**: Generates random user data with proper email formatting
- **Database Storage**: SQLite database to store account creation records
- **Real-time Logging**: Live logs of account creation process
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Configured for cross-origin requests

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Usage

### Start the Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### 1. Create Multiple Accounts
**POST** `/create-accounts`
```json
{
  "count": 3
}
```
Creates the specified number of accounts (1-10 max)

#### 2. Create Demo Account
**POST** `/demo`

Creates a single demo account with random data

#### 3. Get All Accounts
**GET** `/accounts`

Returns all created accounts with their status

#### 4. Get Live Logs
**GET** `/logs`

Returns real-time logs of the account creation process

#### 5. Delete Account
**DELETE** `/accounts/{account_id}`

Deletes a specific account from the database

#### 6. Clear All Accounts
**DELETE** `/accounts`

Clears all accounts from the database

## Data Format

### Generated Account Data
- **Email Format**: `firstname12345lastname@outlook.com`
- **Password**: `Test@12345` (hardcoded)
- **Names**: Random selection from predefined lists
- **Birth Date**: Random date between 1980-2000

### Account Status
- `pending`: Account creation queued
- `success`: Account created successfully
- `failed`: Account creation failed

## Database

The application uses SQLite database (`accounts.db`) with the following schema:

```sql
CREATE TABLE accounts (
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
);
```

## Frontend Integration

The API is designed to work with a frontend that:
1. Allows users to specify number of accounts to create
2. Shows real-time logs during creation process
3. Displays created accounts with their details and status
4. Provides a demo button for quick testing

## Notes

- Account creation runs in background tasks to avoid blocking the API
- Maximum 10 accounts can be created at once to prevent resource exhaustion
- All account creation activities are logged for debugging
- The `utils/outlook.py` script handles the actual Playwright automation
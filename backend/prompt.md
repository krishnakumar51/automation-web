# Outlook Account Creator - API Documentation & Frontend Prompt

## FastAPI Backend Routes

### Base URL: `http://localhost:8000`

---

### 1. **GET /** 
**Description:** Health check endpoint to verify API is running  
**Response:** `{"message": "Outlook Account Creator API is running"}`

---

### 2. **POST /create-accounts**
**Description:** Create multiple Outlook accounts (1-10 maximum)  
**Request Body:**
```json
{
  "count": 3
}
```
**Response:**
```json
{
  "message": "Started creation of 3 accounts",
  "account_ids": [1, 2, 3]
}
```
**Notes:** Runs in background, use `/logs` to monitor progress

---

### 3. **POST /demo**
**Description:** Create a single demo account with random data  
**Request Body:** None required  
**Response:**
```json
{
  "message": "Started demo account creation",
  "account_id": 1,
  "account_data": {
    "first_name": "John",
    "last_name": "Smith",
    "email": "john12345smith@outlook.com",
    "password": "Test@12345",
    "birth_month": "January",
    "birth_day": "15",
    "birth_year": "1995"
  }
}
```

---

### 4. **GET /accounts**
**Description:** Retrieve all created accounts with their status  
**Response:**
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Smith",
    "email": "john12345smith@outlook.com",
    "password": "Test@12345",
    "birth_month": "January",
    "birth_day": "15",
    "birth_year": "1995",
    "status": "success",
    "created_at": "2024-01-15T10:30:00",
    "logs": "Account created successfully"
  }
]
```
**Status Values:** `pending`, `success`, `failed`

---

### 5. **GET /logs**
**Description:** Get real-time logs of account creation process  
**Response:**
```json
{
  "logs": [
    {
      "message": "Starting account creation for john12345smith@outlook.com",
      "timestamp": "2024-01-15T10:30:00.123456",
      "account_id": 1
    }
  ]
}
```

---

### 6. **DELETE /accounts/{account_id}**
**Description:** Delete a specific account from database  
**Parameters:** `account_id` (integer)  
**Response:** `{"message": "Account deleted successfully"}`

---

### 7. **DELETE /accounts**
**Description:** Clear all accounts from database  
**Response:** `{"message": "All accounts cleared successfully"}`

---

## Account Data Format

- **Email Format:** `firstname12345lastname@outlook.com` (5 random digits)
- **Password:** `Test@12345` (hardcoded)
- **Names:** Random from predefined lists (46 first names, 48 last names)
- **Birth Date:** Random between 1980-2000

---

# Frontend Development Prompt (Vite + React)

## Project Requirements

Create a modern, responsive React frontend using Vite that integrates with the Outlook Account Creator FastAPI backend. The application should provide a clean interface for creating Outlook accounts and monitoring the process.

## Setup Instructions

```bash
npm create vite@latest outlook-frontend -- --template react
cd outlook-frontend
npm install
npm install axios lucide-react
npm run dev
```

## Core Features to Implement

### 1. **Main Dashboard**
- Clean, modern UI with a professional color scheme
- Header with application title "Outlook Account Creator"
- Two main action buttons:
  - "Create Multiple Accounts" (with number input 1-10)
  - "Demo Account" (creates 1 account by default)

### 2. **Account Creation Form**
- Number input field (1-10 accounts) with validation
- "Start Creation" button that calls `/create-accounts` endpoint
- "Demo" button that calls `/demo` endpoint
- Loading states and proper error handling

### 3. **Real-time Logs Display**
- Live log viewer that polls `/logs` endpoint every 2 seconds
- Auto-scroll to latest logs
- Timestamp formatting
- Color-coded log levels (info, success, error)
- Clear logs button

### 4. **Accounts Table**
- Display all created accounts from `/accounts` endpoint
- Columns: ID, Name, Email, Password, DOB, Status, Created At
- Status indicators with colors:
  - 🟡 Pending (yellow)
  - 🟢 Success (green) 
  - 🔴 Failed (red)
- Refresh button to update table
- Delete individual accounts
- Clear all accounts button

### 5. **Responsive Design**
- Mobile-friendly layout
- Grid/flexbox for proper spacing
- Loading spinners and skeleton screens
- Toast notifications for actions

## Technical Requirements

### API Integration
```javascript
// Base API configuration
const API_BASE_URL = 'http://localhost:8000';

// Example API calls
const createAccounts = async (count) => {
  const response = await axios.post(`${API_BASE_URL}/create-accounts`, { count });
  return response.data;
};

const createDemo = async () => {
  const response = await axios.post(`${API_BASE_URL}/demo`);
  return response.data;
};

const getAccounts = async () => {
  const response = await axios.get(`${API_BASE_URL}/accounts`);
  return response.data;
};

const getLogs = async () => {
  const response = await axios.get(`${API_BASE_URL}/logs`);
  return response.data;
};
```

### State Management
- Use React hooks (useState, useEffect, useCallback)
- Implement proper loading states
- Handle errors gracefully with try-catch
- Auto-refresh logs and accounts data

### UI Components Structure
```
src/
├── components/
│   ├── Header.jsx
│   ├── AccountForm.jsx
│   ├── LogsViewer.jsx
│   ├── AccountsTable.jsx
│   └── StatusBadge.jsx
├── hooks/
│   ├── useAccounts.js
│   └── useLogs.js
├── services/
│   └── api.js
├── App.jsx
└── main.jsx
```

### Styling Recommendations
- Use Tailwind CSS or styled-components
- Implement dark/light theme toggle
- Use consistent spacing and typography
- Add hover effects and smooth transitions
- Responsive breakpoints for mobile/tablet/desktop

### Key Features Implementation

1. **Auto-refresh logs** every 2 seconds when accounts are being created
2. **Real-time status updates** for account creation progress
3. **Form validation** for account count (1-10 range)
4. **Error boundaries** for graceful error handling
5. **Loading indicators** during API calls
6. **Success/error notifications** for user feedback

### Sample Component Structure

```jsx
function App() {
  const [accounts, setAccounts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isCreating, setIsCreating] = useState(false);

  // Auto-refresh logs when creating accounts
  useEffect(() => {
    if (isCreating) {
      const interval = setInterval(fetchLogs, 2000);
      return () => clearInterval(interval);
    }
  }, [isCreating]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <AccountForm onSubmit={handleCreateAccounts} />
            <LogsViewer logs={logs} />
          </div>
          <div>
            <AccountsTable accounts={accounts} onRefresh={fetchAccounts} />
          </div>
        </div>
      </main>
    </div>
  );
}
```

## Expected User Flow

1. User opens the application
2. Sees clean dashboard with creation options
3. Either:
   - Enters number of accounts (1-10) and clicks "Start Creation"
   - Clicks "Demo" for quick single account creation
4. Logs start appearing in real-time showing progress
5. Created accounts appear in the table with status updates
6. User can view account details, delete accounts, or clear all data

## Performance Considerations

- Implement debouncing for API calls
- Use React.memo for expensive components
- Lazy load components when possible
- Optimize re-renders with proper dependency arrays
- Add loading skeletons for better UX

This frontend should provide a seamless, professional interface for managing Outlook account creation with real-time feedback and comprehensive account management capabilities.
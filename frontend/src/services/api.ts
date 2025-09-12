import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface Account {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  birth_month: string;
  birth_day: string;
  birth_year: string;
  status: 'pending' | 'success' | 'failed';
  created_at: string;
  logs: string;
}

export interface LogEntry {
  message: string;
  timestamp: string;
  account_id: number;
}

export interface CreateAccountsResponse {
  message: string;
  account_ids: number[];
}

export interface DemoResponse {
  message: string;
  account_id: number;
  account_data: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    birth_month: string;
    birth_day: string;
    birth_year: string;
  };
}

// API Client
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Health check
export const healthCheck = async (): Promise<{ message: string }> => {
  const response = await api.get('/');
  return response.data;
};

// Create multiple accounts
export const createAccounts = async (count: number): Promise<CreateAccountsResponse> => {
  const response = await api.post('/create-accounts', { count });
  return response.data;
};

// Create demo account
export const createDemo = async (): Promise<DemoResponse> => {
  const response = await api.post('/demo');
  return response.data;
};

// Get all accounts
export const getAccounts = async (): Promise<Account[]> => {
  const response = await api.get('/accounts');
  return response.data;
};

// Get logs
export const getLogs = async (): Promise<{ logs: LogEntry[] }> => {
  const response = await api.get('/logs');
  return response.data;
};

// Delete specific account
export const deleteAccount = async (accountId: number): Promise<{ message: string }> => {
  const response = await api.delete(`/accounts/${accountId}`);
  return response.data;
};

// Clear all accounts
export const clearAllAccounts = async (): Promise<{ message: string }> => {
  const response = await api.delete('/accounts');
  return response.data;
};
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface Process {
  process_id: string;
  curp_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  email?: string;
  overall_status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress_percentage: number;
  current_stage: 'outlook_creation' | 'imss_processing' | 'email_monitoring' | 'pdf_ready' | 'error';
  created_at: string;
  updated_at: string;
  outlook_status?: string;
  imss_status?: string;
  email_status?: string;
  pdf_status?: string;
}

export interface LogEntry {
  message: string;
  timestamp: string;
  process_id?: string;
}

export interface ProcessCURPRequest {
  curp_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
}

export interface ProcessCURPResponse {
  message: string;
  process_id: string;
  curp_data: ProcessCURPRequest;
}

export interface DemoCURPResponse {
  message: string;
  process_ids: string[];
  demo_data: ProcessCURPRequest[];
}

export interface DemoCURP {
  curp_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
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

// Process real CURP
export const processRealCURP = async (curpData: ProcessCURPRequest): Promise<ProcessCURPResponse> => {
  const response = await api.post('/process-curp', curpData);
  return response.data;
};

// Process demo CURP
export const processDemoCURP = async (count: number): Promise<DemoCURPResponse> => {
  const response = await api.post('/demo-curp', { count });
  return response.data;
};

// Get all processes
export const getProcesses = async (): Promise<Process[]> => {
  const response = await api.get('/processes');
  return response.data;
};

// Get specific process status
export const getProcessStatus = async (processId: string): Promise<Process> => {
  const response = await api.get(`/process/${processId}`);
  return response.data;
};

// Get logs
export const getLogs = async (): Promise<{ logs: LogEntry[] }> => {
  const response = await api.get('/logs');
  return response.data;
};

// Get demo CURPs
export const getDemoCURPs = async (): Promise<DemoCURP[]> => {
  const response = await api.get('/demo-curps');
  return response.data;
};

// Delete specific process
export const deleteProcess = async (processId: string): Promise<{ message: string }> => {
  const response = await api.delete(`/process/${processId}`);
  return response.data;
};

// Clear all processes
export const clearAllProcesses = async (): Promise<{ message: string }> => {
  const response = await api.delete('/processes');
  return response.data;
};
export interface Project {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  task_id: string;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  project_id: number;
  agent_id: number;
  created_at: string;
  updated_at: string;
  started_at?: string;
  finished_at?: string;
  result?: any;
  error_message?: string;
  duration_seconds?: number;
  progress?: number;
  task_metadata?: any;
  project?: Project;
  agent?: Agent;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface WebSocketMessage {
  type: 'task_started' | 'task_finished' | 'task_error' | 'task_progress';
  data: any;
}

export interface UserSettings {
  id: number;
  user_id: string;
  key: string;
  value: any;
  description?: string;
  is_global?: string;
  created_at: string;
  updated_at?: string;
}
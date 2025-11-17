import axios from 'axios';
import type { Project, Task, PaginatedResponse, UserSettings } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add API key to requests
api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('api_key');
  if (apiKey) {
    config.headers.Authorization = `Bearer ${apiKey}`;
  }
  return config;
});

// Projects API
export const projectsApi = {
  getProjects: async (limit = 10, offset = 0): Promise<PaginatedResponse<Project>> => {
    const response = await api.get(`/api/projects?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  getProject: async (projectName: string): Promise<Project> => {
    const response = await api.get(`/api/projects/${projectName}`);
    return response.data;
  },
};

// Tasks API
export const tasksApi = {
  getTasks: async (
    projectName?: string,
    status?: string,
    limit = 10,
    offset = 0
  ): Promise<PaginatedResponse<Task>> => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });

    if (projectName) params.append('project_name', projectName);
    if (status) params.append('status', status);

    const response = await api.get(`/api/tasks?${params}`);
    return response.data;
  },

  getProjectTasks: async (
    projectName: string,
    status?: string,
    limit = 10,
    offset = 0
  ): Promise<PaginatedResponse<Task>> => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });

    if (status) params.append('status', status);

    const response = await api.get(`/api/projects/${projectName}/tasks?${params}`);
    return response.data;
  },

  searchTasks: async (
    taskName?: string,
    agent?: string,
    limit = 10,
    offset = 0
  ): Promise<PaginatedResponse<Task>> => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });

    if (taskName) params.append('task_name', taskName);
    if (agent) params.append('agent', agent);

    const response = await api.get(`/api/tasks/search?${params}`);
    return response.data;
  },
};

// Statistics API
export const statsApi = {
  getProjectsStats: async (): Promise<any> => {
    const response = await api.get('/api/stats/projects');
    return response.data;
  },

  getTasksStats: async (): Promise<any> => {
    const response = await api.get('/api/stats/tasks');
    return response.data;
  },
};

// Settings API
export const settingsApi = {
  getSettings: async (): Promise<UserSettings[]> => {
    const response = await api.get('/api/settings');
    return response.data;
  },

  updateSetting: async (key: string, value: any, description?: string): Promise<UserSettings> => {
    const response = await api.put('/api/settings', {
      key,
      value,
      description,
    });
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
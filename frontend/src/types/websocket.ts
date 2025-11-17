// WebSocket типы для real-time коммуникации

export type WebSocketMessageType =
  | 'connection'
  | 'pong'
  | 'task_started'
  | 'task_finished'
  | 'task_status_updated'
  | 'task_error';

export interface BaseWebSocketMessage {
  type: WebSocketMessageType;
  timestamp: string;
}

export interface ConnectionMessage extends BaseWebSocketMessage {
  type: 'connection';
  data: {
    status: 'connected' | 'authenticated' | 'error';
    message: string;
    project_name?: string;
    user_id?: string;
  };
}

export interface PongMessage extends BaseWebSocketMessage {
  type: 'pong';
  data: {
    timestamp: string;
  };
}

export interface TaskStartedMessage extends BaseWebSocketMessage {
  type: 'task_started';
  data: {
    task_id: string;
    project_name: string;
    agent_name: string;
    title: string;
    started_at: string;
  };
}

export interface TaskFinishedMessage extends BaseWebSocketMessage {
  type: 'task_finished';
  data: {
    task_id: string;
    project_name: string;
    agent_name: string;
    title: string;
    status: 'completed' | 'failed';
    finished_at: string;
    duration_seconds?: number;
    result?: any;
    error_message?: string;
  };
}

export interface TaskStatusUpdatedMessage extends BaseWebSocketMessage {
  type: 'task_status_updated';
  data: {
    task_id: string;
    project_name: string;
    agent_name: string;
    title: string;
    old_status: string;
    new_status: string;
    progress?: number;
    updated_at: string;
  };
}

export interface TaskErrorMessage extends BaseWebSocketMessage {
  type: 'task_error';
  data: {
    task_id: string;
    project_name: string;
    agent_name: string;
    title: string;
    error_message: string;
    error_type?: string;
    occurred_at: string;
  };
}

export type WebSocketMessage =
  | ConnectionMessage
  | PongMessage
  | TaskStartedMessage
  | TaskFinishedMessage
  | TaskStatusUpdatedMessage
  | TaskErrorMessage;

export interface WebSocketConnectionState {
  status: 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting';
  lastMessage?: WebSocketMessage;
  connectionCount: number;
  lastConnectedAt?: string;
  lastDisconnectedAt?: string;
  error?: string;
}

export interface WebSocketHookOptions {
  url?: string;
  apiKey?: string;
  projectName?: string;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  pingInterval?: number;
  enableNotifications?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
}

export type Timer = ReturnType<typeof setTimeout>;

export interface WebSocketHookReturn {
  connectionState: WebSocketConnectionState;
  sendMessage: (message: any) => void;
  connect: () => void;
  disconnect: () => void;
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
}
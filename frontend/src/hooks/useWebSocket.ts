import { useEffect, useRef, useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import {
  WebSocketMessage,
  WebSocketConnectionState,
  WebSocketHookOptions,
  WebSocketHookReturn,
  TaskStartedMessage,
  TaskFinishedMessage,
  TaskStatusUpdatedMessage,
  TaskErrorMessage,
  ConnectionMessage,
  Timer,
} from '../types/websocket';

const DEFAULT_WS_URL = 'ws://localhost:8002/ws';
const DEFAULT_RECONNECT_ATTEMPTS = 5;
const DEFAULT_RECONNECT_INTERVAL = 3000;
const DEFAULT_PING_INTERVAL = 30000;

export function useWebSocket(options: WebSocketHookOptions = {}): WebSocketHookReturn {
  const {
    url: customUrl,
    apiKey: customApiKey,
    projectName: customProjectName,
    reconnectAttempts = DEFAULT_RECONNECT_ATTEMPTS,
    reconnectInterval = DEFAULT_RECONNECT_INTERVAL,
    pingInterval = DEFAULT_PING_INTERVAL,
    enableNotifications = true,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
  } = options;

  const [connectionState, setConnectionState] = useState<WebSocketConnectionState>({
    status: 'disconnected',
    connectionCount: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<Timer | null>(null);
  const pingIntervalRef = useRef<Timer | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualDisconnect = useRef(false);

  const getWebSocketUrl = useCallback(() => {
    const baseUrl = customUrl || DEFAULT_WS_URL;
    const apiKey = customApiKey || localStorage.getItem('apiKey') || '';
    const projectName = customProjectName || localStorage.getItem('currentProject') || '';

    if (!apiKey) {
      console.warn('API ключ не найден в localStorage или параметрах');
    }

    const params = new URLSearchParams({
      api_key: apiKey,
      project: projectName,
    });

    return `${baseUrl}?${params.toString()}`;
  }, [customUrl, customApiKey, customProjectName]);

  const handleTaskNotification = useCallback((message: TaskStartedMessage | TaskFinishedMessage | TaskStatusUpdatedMessage | TaskErrorMessage) => {
    if (!enableNotifications) return;

    const { data } = message;

    switch (message.type) {
      case 'task_started':
        toast.success(`Задача "${data.title}" начата`, {
          icon: '🚀',
          duration: 4000,
        });
        break;

      case 'task_finished':
        const finishedData = message.data;
        if ('status' in finishedData) {
          if (finishedData.status === 'completed') {
            toast.success(`Задача "${finishedData.title}" завершена успешно!`, {
              icon: '✅',
              duration: 6000,
            });
          } else {
            toast.error(`Задача "${finishedData.title}" завершилась с ошибкой`, {
              icon: '❌',
              duration: 6000,
            });
          }
        }
        break;

      case 'task_status_updated':
        const statusData = message.data;
        if ('new_status' in statusData) {
          toast(`Статус задачи "${statusData.title}" изменен на "${statusData.new_status}"`, {
            icon: '🔄',
            duration: 4000,
          });
        }
        break;

      case 'task_error':
        const errorData = message.data;
        if ('error_message' in errorData) {
          toast.error(`Ошибка в задаче "${errorData.title}": ${errorData.error_message}`, {
            icon: '⚠️',
            duration: 8000,
          });
        }
        break;
    }
  }, [enableNotifications]);

  const processMessage = useCallback((data: string) => {
    try {
      const message: WebSocketMessage = JSON.parse(data);

      setConnectionState(prev => ({
        ...prev,
        lastMessage: message,
      }));

      switch (message.type) {
        case 'connection':
          const connectionMsg = message as ConnectionMessage;
          if (connectionMsg.data.status === 'authenticated') {
            setConnectionState(prev => ({
              ...prev,
              status: 'connected',
              lastConnectedAt: new Date().toISOString(),
              error: undefined,
            }));
            onConnect?.();
          } else if (connectionMsg.data.status === 'error') {
            setConnectionState(prev => ({
              ...prev,
              status: 'error',
              error: connectionMsg.data.message,
            }));
          }
          break;

        case 'pong':
          // Pong received, connection is alive
          break;

        case 'task_started':
          const taskStartedMsg = message as TaskStartedMessage;
          handleTaskNotification(taskStartedMsg);
          break;

        case 'task_finished':
          const taskFinishedMsg = message as TaskFinishedMessage;
          handleTaskNotification(taskFinishedMsg);
          break;

        case 'task_status_updated':
          const taskStatusMsg = message as TaskStatusUpdatedMessage;
          handleTaskNotification(taskStatusMsg);
          break;

        case 'task_error':
          const taskErrorMsg = message as TaskErrorMessage;
          handleTaskNotification(taskErrorMsg);
          break;
      }

      onMessage?.(message);
    } catch (error) {
      console.error('Ошибка при обработке WebSocket сообщения:', error);
    }
  }, [handleTaskNotification, onConnect, onMessage]);

  const startPingInterval = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }

    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ping',
          timestamp: new Date().toISOString(),
        }));
      }
    }, pingInterval);
  }, [pingInterval]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    isManualDisconnect.current = false;
    setConnectionState(prev => ({
      ...prev,
      status: 'connecting',
      error: undefined,
    }));

    try {
      const wsUrl = getWebSocketUrl();
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket соединение установлено');
        reconnectAttemptsRef.current = 0;
        startPingInterval();
      };

      ws.onmessage = (event) => {
        processMessage(event.data);
      };

      ws.onclose = (event) => {
        console.log('WebSocket соединение закрыто:', event.code, event.reason);

        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        const wasConnected = connectionState.status === 'connected';
        const connectionCount = connectionState.connectionCount + 1;

        setConnectionState(prev => ({
          ...prev,
          status: 'disconnected',
          connectionCount,
          lastDisconnectedAt: new Date().toISOString(),
        }));

        onDisconnect?.();

        // Автоматическое переподключение если не ручное отключение и еще есть попытки
        if (!isManualDisconnect.current && reconnectAttemptsRef.current < reconnectAttempts && wasConnected) {
          reconnectAttemptsRef.current++;
          setConnectionState(prev => ({
            ...prev,
            status: 'reconnecting',
          }));

          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Попытка переподключения ${reconnectAttemptsRef.current}/${reconnectAttempts}`);
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket ошибка:', error);
        setConnectionState(prev => ({
          ...prev,
          status: 'error',
          error: 'Ошибка соединения с WebSocket',
        }));
        onError?.(error);
      };

    } catch (error) {
      console.error('Ошибка при создании WebSocket соединения:', error);
      setConnectionState(prev => ({
        ...prev,
        status: 'error',
        error: 'Не удалось установить WebSocket соединение',
      }));
    }
  }, [getWebSocketUrl, processMessage, startPingInterval, reconnectAttempts, reconnectInterval, onConnect, onDisconnect, onError, connectionState.status, connectionState.connectionCount]);

  const disconnect = useCallback(() => {
    isManualDisconnect.current = true;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setConnectionState(prev => ({
      ...prev,
      status: 'disconnected',
      lastDisconnectedAt: new Date().toISOString(),
    }));
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket не подключен, сообщение не отправлено:', message);
    }
  }, []);

  // Автоматическое подключение при монтировании
  useEffect(() => {
    const apiKey = customApiKey || localStorage.getItem('apiKey');
    if (apiKey) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, []);

  // Очистка таймеров при размонтировании
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, []);

  return {
    connectionState,
    sendMessage,
    connect,
    disconnect,
    isConnected: connectionState.status === 'connected',
    isConnecting: connectionState.status === 'connecting' || connectionState.status === 'reconnecting',
    error: connectionState.error || null,
  };
}
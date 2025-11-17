import { createContext, useContext, ReactNode, useCallback, useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { WebSocketMessage, WebSocketHookOptions, Timer } from '../types/websocket';

interface WebSocketContextValue {
  // Состояние соединения
  isConnected: boolean;
  isConnecting: boolean;
  connectionState: any;
  error: string | null;

  // Методы управления
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;

  // Данные сообщений
  lastMessage: WebSocketMessage | undefined;
  messageHistory: WebSocketMessage[];
  clearHistory: () => void;

  // Статистика
  connectionStats: {
    totalConnections: number;
    messagesReceived: number;
    lastConnectedAt?: string;
    uptime?: number;
  };

  // Дополнительные методы
  reconnect: () => void;
  sendPing: () => void;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
  options?: WebSocketHookOptions;
}

export function WebSocketProvider({ children, options }: WebSocketProviderProps) {
  const [messageHistory, setMessageHistory] = useState<WebSocketMessage[]>([]);
  const [stats, setStats] = useState({
    totalConnections: 0,
    messagesReceived: 0,
    lastConnectedAt: undefined as string | undefined,
    uptime: 0,
  });

  const {
    connectionState,
    sendMessage: wsSendMessage,
    connect: wsConnect,
    disconnect: wsDisconnect,
    isConnected,
    isConnecting,
    error,
  } = useWebSocket(options);

  // Обновление статистики при изменении состояния соединения
  useEffect(() => {
    if (connectionState.lastConnectedAt && connectionState.status === 'connected') {
      setStats(prev => ({
        ...prev,
        totalConnections: connectionState.connectionCount,
        lastConnectedAt: connectionState.lastConnectedAt,
        uptime: connectionState.lastConnectedAt
          ? Math.floor((Date.now() - new Date(connectionState.lastConnectedAt).getTime()) / 1000)
          : 0,
      }));
    }
  }, [connectionState]);

  // Обработка входящих сообщений
  useEffect(() => {
    if (connectionState.lastMessage) {
      setMessageHistory(prev => {
        const newHistory = [...prev, connectionState.lastMessage!];
        // Храним только последние 100 сообщений для оптимизации памяти
        return newHistory.slice(-100);
      });

      setStats(prev => ({
        ...prev,
        messagesReceived: prev.messagesReceived + 1,
      }));
    }
  }, [connectionState.lastMessage]);

  // Обновление uptime каждую секунду при активном соединении
  useEffect(() => {
    let interval: Timer | null = null;

    if (isConnected && stats.lastConnectedAt) {
      interval = setInterval(() => {
        setStats(prev => ({
          ...prev,
          uptime: Math.floor((Date.now() - new Date(prev.lastConnectedAt!).getTime()) / 1000),
        }));
      }, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isConnected, stats.lastConnectedAt]);

  const connect = useCallback(() => {
    wsConnect();
  }, [wsConnect]);

  const disconnect = useCallback(() => {
    wsDisconnect();
  }, [wsDisconnect]);

  const sendMessage = useCallback((message: any) => {
    wsSendMessage(message);
  }, [wsSendMessage]);

  const reconnect = useCallback(() => {
    wsDisconnect();
    setTimeout(() => {
      wsConnect();
    }, 1000);
  }, [wsDisconnect, wsConnect]);

  const sendPing = useCallback(() => {
    wsSendMessage({
      type: 'ping',
      timestamp: new Date().toISOString(),
    });
  }, [wsSendMessage]);

  const clearHistory = useCallback(() => {
    setMessageHistory([]);
  }, []);

  const value: WebSocketContextValue = {
    // Состояние соединения
    isConnected,
    isConnecting,
    connectionState,
    error,

    // Методы управления
    connect,
    disconnect,
    sendMessage,

    // Данные сообщений
    lastMessage: connectionState.lastMessage,
    messageHistory,
    clearHistory,

    // Статистика
    connectionStats: stats,

    // Дополнительные методы
    reconnect,
    sendPing,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

// Хук для использования WebSocket контекста
export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (context === null) {
    throw new Error('useWebSocketContext должен использоваться внутри WebSocketProvider');
  }
  return context;
}

// Хук для удобного доступа к последним сообщениям определенного типа
export function useLastMessageType<T extends WebSocketMessage>(type: T['type']): T | undefined {
  const { lastMessage } = useWebSocketContext();

  if (lastMessage && lastMessage.type === type) {
    return lastMessage as T;
  }

  return undefined;
}

// Хук для получения истории сообщений определенного типа
export function useMessageHistoryType<T extends WebSocketMessage>(type: T['type']): T[] {
  const { messageHistory } = useWebSocketContext();

  return messageHistory
    .filter(msg => msg.type === type)
    .map(msg => msg as T);
}

// Хук для получения информации о соединении
export function useConnectionInfo() {
  const { connectionStats, connectionState, isConnected, isConnecting, error } = useWebSocketContext();

  return {
    status: connectionState.status,
    isConnected,
    isConnecting,
    error,
    connectionCount: connectionState.connectionCount,
    lastConnectedAt: connectionState.lastConnectedAt,
    lastDisconnectedAt: connectionState.lastDisconnectedAt,
    uptime: connectionStats.uptime,
    totalConnections: connectionStats.totalConnections,
    messagesReceived: connectionStats.messagesReceived,
  };
}
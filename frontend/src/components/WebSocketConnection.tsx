import { Wifi, WifiOff, AlertTriangle, RefreshCw, MessageSquare } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { useConnectionInfo, useWebSocketContext } from '../context/WebSocketContext';
import { cn } from '@/lib/utils';

interface WebSocketConnectionProps {
  showDetails?: boolean;
  compact?: boolean;
  className?: string;
}

export function WebSocketConnection({
  showDetails = false,
  compact = false,
  className
}: WebSocketConnectionProps) {
  const {
    status,
    isConnected,
    isConnecting,
    error,
    connectionCount,
    lastConnectedAt,
    lastDisconnectedAt,
    uptime,
    totalConnections,
    messagesReceived
  } = useConnectionInfo();

  const { reconnect, sendPing } = useWebSocketContext();

  const formatUptime = (seconds: number) => {
    if (seconds < 60) return `${seconds}с`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}м ${seconds % 60}с`;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}ч ${minutes}м`;
  };

  const formatTime = (dateString?: string) => {
    if (!dateString) return 'Никогда';
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU');
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'text-green-500';
      case 'connecting':
      case 'reconnecting':
        return 'text-yellow-500';
      case 'error':
        return 'text-red-500';
      case 'disconnected':
        return 'text-gray-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
        return <Wifi className="h-4 w-4" />;
      case 'connecting':
      case 'reconnecting':
        return <RefreshCw className="h-4 w-4 animate-spin" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4" />;
      case 'disconnected':
        return <WifiOff className="h-4 w-4" />;
      default:
        return <WifiOff className="h-4 w-4" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Подключено';
      case 'connecting':
        return 'Подключение...';
      case 'reconnecting':
        return 'Переподключение...';
      case 'error':
        return 'Ошибка';
      case 'disconnected':
        return 'Отключено';
      default:
        return 'Неизвестно';
    }
  };

  if (compact) {
    return (
      <div className={cn('flex items-center space-x-2', className)}>
        <div className={cn('flex items-center space-x-1', getStatusColor())}>
          {getStatusIcon()}
          <span className="text-xs font-medium">{getStatusText()}</span>
        </div>
        {uptime && uptime > 0 && (
          <div className="text-xs text-muted-foreground">
            {formatUptime(uptime)}
          </div>
        )}
      </div>
    );
  }

  return (
    <Card className={cn('w-full max-w-md', className)}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-4 w-4" />
            <span>WebSocket Соединение</span>
          </div>
          <div className={cn('flex items-center space-x-1', getStatusColor())}>
            {getStatusIcon()}
            <span className="text-sm font-medium">{getStatusText()}</span>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {error && (
          <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-2 rounded-md">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="space-y-1">
            <div className="text-muted-foreground">Статус</div>
            <div className={cn('font-medium', getStatusColor())}>
              {getStatusText()}
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-muted-foreground">Время работы</div>
            <div className="font-medium">
              {uptime && uptime > 0 ? formatUptime(uptime) : '-'}
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-muted-foreground">Подключений</div>
            <div className="font-medium">{totalConnections}</div>
          </div>

          <div className="space-y-1">
            <div className="text-muted-foreground">Сообщений</div>
            <div className="font-medium">{messagesReceived}</div>
          </div>
        </div>

        {showDetails && (
          <div className="space-y-2 pt-2 border-t">
            <div className="grid grid-cols-1 gap-2 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>Последнее подключение:</span>
                <span className="text-foreground">{formatTime(lastConnectedAt)}</span>
              </div>
              <div className="flex justify-between">
                <span>Последнее отключение:</span>
                <span className="text-foreground">{formatTime(lastDisconnectedAt)}</span>
              </div>
              <div className="flex justify-between">
                <span>Счетчик подключений:</span>
                <span className="text-foreground">{connectionCount}</span>
              </div>
            </div>
          </div>
        )}

        <div className="flex space-x-2 pt-2">
          <Button
            size="sm"
            variant="outline"
            onClick={reconnect}
            disabled={isConnecting}
            className="flex-1"
          >
            {isConnecting ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Подключение...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Переподключить
              </>
            )}
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={sendPing}
            disabled={!isConnected}
          >
            Ping
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default WebSocketConnection;

// Компонент для индикатора статуса в шапке
export function WebSocketStatusIndicator({ className }: { className?: string }) {
  const { isConnected, isConnecting } = useConnectionInfo();

  return (
    <div
      className={cn(
        'flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium transition-colors',
        isConnected
          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
          : isConnecting
          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
        className
      )}
    >
      <div className={cn(
        'w-2 h-2 rounded-full',
        isConnected
          ? 'bg-green-500'
          : isConnecting
          ? 'bg-yellow-500 animate-pulse'
          : 'bg-gray-500'
      )} />
      <span>
        {isConnected ? 'Онлайн' : isConnecting ? 'Подключение...' : 'Офлайн'}
      </span>
    </div>
  );
}
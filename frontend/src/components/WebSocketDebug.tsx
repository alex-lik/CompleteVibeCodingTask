import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useWebSocketContext, useMessageHistoryType } from '../context/WebSocketContext';
import { TaskStartedMessage, TaskFinishedMessage, TaskStatusUpdatedMessage } from '../types/websocket';
import { Play, Square, RefreshCw, Send, Trash2, MessageSquare, CheckCircle, XCircle, Clock } from 'lucide-react';

export function WebSocketDebug() {
  const [showRawMessages, setShowRawMessages] = useState(false);
  const [customMessage, setCustomMessage] = useState('{"type": "ping", "timestamp": "' + new Date().toISOString() + '"}');

  const {
    isConnected,
    isConnecting,
    connectionState,
    error,
    messageHistory,
    connectionStats,
    sendMessage,
    reconnect,
    sendPing,
    clearHistory
  } = useWebSocketContext();

  const taskStartedMessages = useMessageHistoryType<TaskStartedMessage>('task_started');
  const taskFinishedMessages = useMessageHistoryType<TaskFinishedMessage>('task_finished');
  const taskStatusMessages = useMessageHistoryType<TaskStatusUpdatedMessage>('task_status_updated');

  const sendCustomMessage = () => {
    try {
      const message = JSON.parse(customMessage);
      sendMessage(message);
    } catch (err) {
      console.error('Invalid JSON:', err);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ru-RU');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'reconnecting': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      case 'disconnected': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running': return <Play className="h-4 w-4 text-blue-500" />;
      case 'pending': return <Clock className="h-4 w-4 text-gray-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Панель управления */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>WebSocket Управление</span>
            </div>
            <Badge
              variant={isConnected ? "default" : "destructive"}
              className={getStatusColor(connectionState.status)}
            >
              {connectionState.status}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
              {error}
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            <Button
              onClick={reconnect}
              disabled={isConnecting}
              variant="outline"
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
              onClick={sendPing}
              disabled={!isConnected}
              variant="outline"
            >
              Send Ping
            </Button>

            <Button
              onClick={clearHistory}
              variant="outline"
              size="sm"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Очистить историю
            </Button>

            <Button
              onClick={() => setShowRawMessages(!showRawMessages)}
              variant="outline"
              size="sm"
            >
              {showRawMessages ? 'Скрыть' : 'Показать'} сырые сообщения
            </Button>
          </div>

          {/* Статистика */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl font-bold text-green-600">{connectionStats.totalConnections}</div>
              <div className="text-sm text-gray-600">Всего подключений</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl font-bold text-blue-600">{connectionStats.messagesReceived}</div>
              <div className="text-sm text-gray-600">Сообщений получено</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl font-bold text-purple-600">
                {connectionStats.uptime ? Math.floor(connectionStats.uptime / 60) : 0}м
              </div>
              <div className="text-sm text-gray-600">Время работы</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded">
              <div className="text-2xl font-bold text-orange-600">{messageHistory.length}</div>
              <div className="text-sm text-gray-600">В памяти</div>
            </div>
          </div>

          {/* Отправка кастомного сообщения */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Отправить сообщение:</label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                className="flex-1 px-3 py-2 border rounded-md text-sm"
                placeholder='{"type": "ping"}'
              />
              <Button onClick={sendCustomMessage} disabled={!isConnected}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Сообщения по типам */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Начатые задачи */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <Play className="h-5 w-5 text-blue-500" />
              <span>Начатые задачи ({taskStartedMessages.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {taskStartedMessages.length === 0 ? (
                <p className="text-gray-500 text-sm">Нет начатых задач</p>
              ) : (
                taskStartedMessages.slice(-10).reverse().map((msg, index) => (
                  <div key={index} className="p-3 bg-blue-50 rounded-md">
                    <div className="font-medium text-sm">{msg.data.title}</div>
                    <div className="text-xs text-gray-600 mt-1">
                      {msg.data.project_name} • {msg.data.agent_name}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatTimestamp(msg.timestamp)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Завершенные задачи */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <Square className="h-5 w-5 text-green-500" />
              <span>Завершенные задачи ({taskFinishedMessages.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {taskFinishedMessages.length === 0 ? (
                <p className="text-gray-500 text-sm">Нет завершенных задач</p>
              ) : (
                taskFinishedMessages.slice(-10).reverse().map((msg, index) => (
                  <div key={index} className="p-3 bg-green-50 rounded-md">
                    <div className="flex items-center space-x-2">
                      {getTaskStatusIcon(msg.data.status)}
                      <span className="font-medium text-sm">{msg.data.title}</span>
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {msg.data.project_name} • {msg.data.agent_name}
                    </div>
                    {msg.data.duration_seconds && (
                      <div className="text-xs text-gray-500 mt-1">
                        Длительность: {msg.data.duration_seconds}с
                      </div>
                    )}
                    <div className="text-xs text-gray-500 mt-1">
                      {formatTimestamp(msg.timestamp)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Обновления статуса */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <RefreshCw className="h-5 w-5 text-purple-500" />
              <span>Обновления статуса ({taskStatusMessages.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {taskStatusMessages.length === 0 ? (
                <p className="text-gray-500 text-sm">Нет обновлений статуса</p>
              ) : (
                taskStatusMessages.slice(-10).reverse().map((msg, index) => (
                  <div key={index} className="p-3 bg-purple-50 rounded-md">
                    <div className="font-medium text-sm">{msg.data.title}</div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-600">{msg.data.old_status}</span>
                      <RefreshCw className="h-3 w-3 text-purple-500" />
                      <span className="text-xs font-medium text-purple-700">{msg.data.new_status}</span>
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {msg.data.project_name} • {msg.data.agent_name}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatTimestamp(msg.timestamp)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Сырые сообщения */}
      {showRawMessages && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">История сообщений ({messageHistory.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto font-mono text-xs">
              {messageHistory.length === 0 ? (
                <p className="text-gray-500">Нет сообщений</p>
              ) : (
                messageHistory.slice(-50).reverse().map((msg, index) => (
                  <div key={index} className="p-2 bg-gray-100 rounded">
                    <div className="text-gray-600 mb-1">
                      {formatTimestamp(msg.timestamp)} - {msg.type}
                    </div>
                    <pre className="whitespace-pre-wrap break-all">
                      {JSON.stringify(msg, null, 2)}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default WebSocketDebug;
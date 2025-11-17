import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { settingsApi } from '../utils/api';
import { WebSocketDebug } from '../components/WebSocketDebug';
import type { UserSettings } from '../types';

function SettingsPage() {
  const [apiKey, setApiKey] = useState(localStorage.getItem('api_key') || '');
  const queryClient = useQueryClient();

  const {
    data: settings,
    isLoading,
    error,
  } = useQuery<UserSettings[]>({
    queryKey: ['settings'],
    queryFn: () => settingsApi.getSettings(),
  });

  const updateSettingMutation = useMutation({
    mutationFn: ({ key, value, description }: { key: string; value: any; description?: string }) =>
      settingsApi.updateSetting(key, value, description),
    onSuccess: () => {
      toast.success('Настройка сохранена');
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
    onError: (error) => {
      toast.error(`Ошибка сохранения: ${(error as Error).message}`);
    },
  });

  const handleApiKeyChange = (value: string) => {
    setApiKey(value);
    localStorage.setItem('api_key', value);
    toast.success('API ключ сохранен локально');
  };

  const handleSettingUpdate = (key: string, value: any, description?: string) => {
    updateSettingMutation.mutate({ key, value, description });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Загрузка настроек...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center">
        <div className="text-red-500 text-lg mb-4">Ошибка загрузки настроек</div>
        <div className="text-muted-foreground">
          {(error as Error).message}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Настройки</h1>

      <div className="space-y-6">
        {/* API Settings */}
        <div className="border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">API Настройки</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                API Ключ для доступа к эндпоинтам
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => handleApiKeyChange(e.target.value)}
                placeholder="Введите ваш API ключ"
                className="w-full border rounded px-3 py-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Ключ сохраняется локально в браузере и используется для аутентификации запросов
              </p>
            </div>
          </div>
        </div>

        {/* WebSocket Debug */}
        <div className="border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">WebSocket Отладка</h2>
          <WebSocketDebug />
        </div>

        {/* User Preferences */}
        <div className="border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Пользовательские настройки</h2>

          {settings && settings.length > 0 ? (
            <div className="space-y-3">
              {settings.map((setting) => (
                <div key={setting.id} className="flex justify-between items-center py-2 border-b">
                  <div>
                    <div className="font-medium">{setting.key}</div>
                    {setting.description && (
                      <div className="text-sm text-muted-foreground">{setting.description}</div>
                    )}
                  </div>
                  <div className="text-sm">
                    {typeof setting.value === 'object'
                      ? JSON.stringify(setting.value)
                      : String(setting.value)
                    }
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">Нет сохраненных настроек</p>
          )}
        </div>

        {/* App Info */}
        <div className="border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">О приложении</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Версия:</span>
              <span>1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Backend URL:</span>
              <span>http://localhost:8002</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">WebSocket:</span>
              <span>ws://localhost:8002</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
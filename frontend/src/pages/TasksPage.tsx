import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { tasksApi } from '../utils/api';
import type { Task, PaginatedResponse } from '../types';

function TasksPage() {
  const [page, setPage] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [agentFilter, setAgentFilter] = useState('');
  const pageSize = 10;

  const {
    data: tasksData,
    isLoading,
    error,
  } = useQuery<PaginatedResponse<Task>>({
    queryKey: ['tasks-search', page, searchTerm, agentFilter],
    queryFn: () => tasksApi.searchTasks(searchTerm, agentFilter, pageSize, page * pageSize),
  });

  const totalPages = tasksData ? Math.ceil(tasksData.total / pageSize) : 0;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'running':
        return 'text-blue-600 bg-blue-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Завершено';
      case 'running':
        return 'Выполняется';
      case 'failed':
        return 'Ошибка';
      case 'pending':
        return 'Ожидание';
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Загрузка задач...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center">
        <div className="text-red-500 text-lg mb-4">Ошибка загрузки задач</div>
        <div className="text-muted-foreground">
          {(error as Error).message}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-4">Задачи</h1>

        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          <input
            type="text"
            placeholder="Поиск по названию задачи..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(0);
            }}
            className="border rounded px-3 py-2 flex-1"
          />
          <input
            type="text"
            placeholder="Фильтр по агенту..."
            value={agentFilter}
            onChange={(e) => {
              setAgentFilter(e.target.value);
              setPage(0);
            }}
            className="border rounded px-3 py-2 flex-1"
          />
        </div>
      </div>

      {tasksData?.items.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-muted-foreground text-lg">Задачи не найдены</div>
          <div className="text-muted-foreground text-sm mt-2">
            Попробуйте изменить параметры поиска или фильтры
          </div>
        </div>
      ) : (
        <>
          <div className="mb-4">
            <div className="text-sm text-muted-foreground">
              Найдено задач: {tasksData?.total}
            </div>
          </div>

          <div className="space-y-4">
            {tasksData?.items.map((task) => (
              <div key={task.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold">{task.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(task.status)}`}>
                    {getStatusText(task.status)}
                  </span>
                </div>
                <p className="text-muted-foreground text-sm mb-2">
                  {task.description || 'Нет описания'}
                </p>
                <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  <div>Проект: {task.project?.name || 'Неизвестен'}</div>
                  <div>Агент: {task.agent?.name || 'Неизвестен'}</div>
                  <div>Создана: {new Date(task.created_at).toLocaleString('ru-RU')}</div>
                  {task.finished_at && (
                    <div>Завершена: {new Date(task.finished_at).toLocaleString('ru-RU')}</div>
                  )}
                  {task.duration_seconds && (
                    <div>Длительность: {task.duration_seconds} сек</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-8 space-x-2">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Назад
          </button>
          <span className="px-3 py-1">
            {page + 1} из {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page === totalPages - 1}
            className="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Вперед
          </button>
        </div>
      )}
    </div>
  );
}

export default TasksPage;
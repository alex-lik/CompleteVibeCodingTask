import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { projectsApi, tasksApi } from '../utils/api';
import type { Project, Task, PaginatedResponse } from '../types';

function ProjectDetailPage() {
  const { projectName } = useParams<{ projectName: string }>();
  const [page, setPage] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const pageSize = 10;

  const {
    data: project,
    isLoading: projectLoading,
    error: projectError,
  } = useQuery<Project>({
    queryKey: ['project', projectName],
    queryFn: () => projectsApi.getProject(projectName!),
    enabled: !!projectName,
  });

  const {
    data: tasksData,
    isLoading: tasksLoading,
    error: tasksError,
  } = useQuery<PaginatedResponse<Task>>({
    queryKey: ['project-tasks', projectName, page, statusFilter],
    queryFn: () => tasksApi.getProjectTasks(projectName!, statusFilter, pageSize, page * pageSize),
    enabled: !!projectName,
  });

  const totalPages = tasksData ? Math.ceil(tasksData.total / pageSize) : 0;

  if (projectLoading || tasksLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  if (projectError || tasksError) {
    return (
      <div className="text-center">
        <div className="text-red-500 text-lg mb-4">Ошибка загрузки</div>
        <div className="text-muted-foreground">
          {(projectError as Error)?.message || (tasksError as Error)?.message}
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center">
        <div className="text-red-500 text-lg mb-4">Проект не найден</div>
        <Link to="/" className="text-primary hover:underline">
          Вернуться к проектам
        </Link>
      </div>
    );
  }

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

  return (
    <div>
      <div className="mb-6">
        <Link to="/" className="text-primary hover:underline mb-4 block">
          ← Назад к проектам
        </Link>
        <h1 className="text-2xl font-bold mb-2">{project.name}</h1>
        <p className="text-muted-foreground">
          {project.description || 'Нет описания'}
        </p>
      </div>

      <div className="mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium">Фильтр по статусу:</label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(0);
            }}
            className="border rounded px-3 py-1"
          >
            <option value="">Все статусы</option>
            <option value="pending">Ожидание</option>
            <option value="running">Выполняется</option>
            <option value="completed">Завершено</option>
            <option value="failed">Ошибка</option>
          </select>
        </div>
      </div>

      {tasksData?.items.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-muted-foreground text-lg">Задачи не найдены</div>
        </div>
      ) : (
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
              <div className="text-xs text-muted-foreground">
                Агент: {task.agent?.name || 'Неизвестен'}
              </div>
              <div className="text-xs text-muted-foreground">
                Создана: {new Date(task.created_at).toLocaleString('ru-RU')}
              </div>
              {task.finished_at && (
                <div className="text-xs text-muted-foreground">
                  Завершена: {new Date(task.finished_at).toLocaleString('ru-RU')}
                </div>
              )}
              {task.duration_seconds && (
                <div className="text-xs text-muted-foreground">
                  Длительность: {task.duration_seconds} сек
                </div>
              )}
            </div>
          ))}
        </div>
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

export default ProjectDetailPage;
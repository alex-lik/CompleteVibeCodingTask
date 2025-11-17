import { useQuery } from '@tanstack/react-query';
import { statsApi } from '../utils/api';

function StatisticsPage() {
  const {
    data: projectsStats,
    isLoading: projectsLoading,
    error: projectsError,
  } = useQuery({
    queryKey: ['stats-projects'],
    queryFn: () => statsApi.getProjectsStats(),
  });

  const {
    data: tasksStats,
    isLoading: tasksLoading,
    error: tasksError,
  } = useQuery({
    queryKey: ['stats-tasks'],
    queryFn: () => statsApi.getTasksStats(),
  });

  if (projectsLoading || tasksLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Загрузка статистики...</div>
      </div>
    );
  }

  if (projectsError || tasksError) {
    return (
      <div className="text-center">
        <div className="text-red-500 text-lg mb-4">Ошибка загрузки статистики</div>
        <div className="text-muted-foreground">
          {(projectsError as Error)?.message || (tasksError as Error)?.message}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Статистика</h1>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Projects Statistics */}
        <div className="border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Статистика проектов</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Всего проектов:</span>
              <span className="font-medium">{projectsStats?.total_projects || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Активные проекты:</span>
              <span className="font-medium">{projectsStats?.active_projects || 0}</span>
            </div>
          </div>
        </div>

        {/* Tasks Statistics */}
        <div className="border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Статистика задач</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Всего задач:</span>
              <span className="font-medium">{tasksStats?.total_tasks || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Завершено:</span>
              <span className="font-medium text-green-600">{tasksStats?.completed_tasks || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Выполняется:</span>
              <span className="font-medium text-blue-600">{tasksStats?.running_tasks || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Ожидание:</span>
              <span className="font-medium text-yellow-600">{tasksStats?.pending_tasks || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Ошибки:</span>
              <span className="font-medium text-red-600">{tasksStats?.failed_tasks || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Statistics */}
      <div className="mt-6 border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Дополнительная информация</h2>
        <div className="text-sm text-muted-foreground">
          <p>Статистика обновляется в реальном времени по мере поступления данных от агентов.</p>
          <p className="mt-2">
            Для более детальной аналитики используйте API эндпоинты или подключите систему мониторинга.
          </p>
        </div>
      </div>
    </div>
  );
}

export default StatisticsPage;
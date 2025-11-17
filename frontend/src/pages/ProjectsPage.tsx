import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { projectsApi } from '../utils/api';
import type { Project, PaginatedResponse } from '../types';

function ProjectsPage() {
  const [page, setPage] = useState(0);
  const pageSize = 10;

  const {
    data: projectsData,
    isLoading,
    error,
  } = useQuery<PaginatedResponse<Project>>({
    queryKey: ['projects', page],
    queryFn: () => projectsApi.getProjects(pageSize, page * pageSize),
  });

  const totalPages = projectsData ? Math.ceil(projectsData.total / pageSize) : 0;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Загрузка проектов...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center">
        <div className="text-red-500 text-lg mb-4">Ошибка загрузки проектов</div>
        <div className="text-muted-foreground">
          {(error as Error).message}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Проекты</h1>
      </div>

      {projectsData?.items.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-muted-foreground text-lg">Проекты не найдены</div>
          <div className="text-muted-foreground text-sm mt-2">
            Когда агенты начнут работу, здесь появятся проекты
          </div>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projectsData?.items.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.name}`}
              className="block p-6 border rounded-lg hover:bg-accent/50 transition-colors"
            >
              <h3 className="text-lg font-semibold mb-2">{project.name}</h3>
              <p className="text-muted-foreground text-sm line-clamp-3">
                {project.description || 'Нет описания'}
              </p>
              <div className="mt-4 text-xs text-muted-foreground">
                Создан: {new Date(project.created_at).toLocaleDateString('ru-RU')}
              </div>
            </Link>
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

export default ProjectsPage;
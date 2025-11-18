const { execSync } = require('child_process');

async function runComprehensiveUITests() {
  console.log('🚀 Запск комплексного UI тестирования через curl');

  const results = {
    passed: 0,
    failed: 0,
    warnings: 0,
    details: [],
    performance: {},
    pages: {}
  };

  // Тест 1: Главная страница
  console.log('🏠 Тестирование главной страницы...');
  try {
    const timeStart = Date.now();
    const response = execSync('curl -s -w "%{http_code}|%{time_total}|%{size_download}" -o homepage_temp.html http://localhost:3002', { encoding: 'utf8' });
    const timeEnd = Date.now();

    const [httpCode, totalTime, size] = response.trim().split('|');
    const content = execSync('type homepage_temp.html', { encoding: 'utf8' });

    results.performance.homepage = {
      httpCode,
      totalTime: (parseFloat(totalTime) * 1000).toFixed(0) + 'ms',
      size: size + ' bytes',
      clientTime: (timeEnd - timeStart) + 'ms'
    };

    if (httpCode === '200') {
      results.passed++;
      results.pages.homepage = '✅ Доступна';

      if (content.includes('Agent Task Tracker')) {
        results.passed++;
        results.details.push('✅ Главная страница: корректный контент');
      } else {
        results.failed++;
        results.details.push('❌ Главная страница: неверный контент');
      }

      // Проверка на наличие ключевых элементов
      const hasNav = content.includes('<nav>') || content.includes('nav ');
      const hasButtons = content.includes('<button') || content.includes('btn');
      const hasForms = content.includes('<form') || content.includes('<input');

      results.details.push(`📊 Главная страница элементы:`);
      results.details.push(`   - Навигация: ${hasNav ? '✅' : '❌'}`);
      results.details.push(`   - Кнопки: ${hasButtons ? '✅' : '❌'}`);
      results.details.push(`   - Формы: ${hasForms ? '✅' : '❌'}`);

      if (hasNav && hasButtons) {
        results.passed++;
      } else {
        results.warnings++;
      }

    } else {
      results.failed++;
      results.pages.homepage = `❌ HTTP ${httpCode}`;
      results.details.push(`❌ Главная страница недоступна (HTTP ${httpCode})`);
    }
  } catch (error) {
    results.failed++;
    results.details.push(`❌ Ошибка главной страницы: ${error.message}`);
  }

  // Тест 2: Все страницы приложения
  const routes = [
    { path: '/projects', name: 'Проекты' },
    { path: '/tasks', name: 'Задачи' },
    { path: '/statistics', name: 'Статистика' },
    { path: '/settings', name: 'Настройки' }
  ];

  console.log('📁 Тестирование всех страниц...');
  for (const route of routes) {
    try {
      const response = execSync(`curl -s -w "%{http_code}|%{time_total}" -o temp_page.html http://localhost:3002${route.path}`, { encoding: 'utf8' });
      const [httpCode, totalTime] = response.trim().split('|');

      results.performance[route.name] = {
        httpCode,
        totalTime: (parseFloat(totalTime) * 1000).toFixed(0) + 'ms'
      };

      if (httpCode === '200') {
        results.passed++;
        results.pages[route.name] = '✅ Доступна';
        results.details.push(`✅ Страница "${route.name}" (${route.path}): загружена за ${(parseFloat(totalTime) * 1000).toFixed(0)}ms`);
      } else {
        results.failed++;
        results.pages[route.name] = `❌ HTTP ${httpCode}`;
        results.details.push(`❌ Страница "${route.name}" (${route.path}): недоступна`);
      }
    } catch (error) {
      results.failed++;
      results.pages[route.name] = '❌ Ошибка';
      results.details.push(`❌ Страница "${route.name}": ${error.message}`);
    }
  }

  // Тест 3: API эндпоинты
  console.log('🔗 Тестирование API...');
  const apiEndpoints = [
    { path: '/api/projects', name: 'API Проекты' },
    { path: '/api/stats', name: 'API Статистика' }
  ];

  for (const api of apiEndpoints) {
    try {
      const response = execSync(`curl -s -H "X-API-Key: dev-api-key-change-this-in-production" -H "Accept: application/json" -w "%{http_code}|%{time_total}" http://localhost:8004${api.path}`, { encoding: 'utf8' });
      const [httpCode, totalTime] = response.trim().split('|');

      if (httpCode === '200') {
        results.passed++;
        results.details.push(`✅ ${api.name}: работает (${(parseFloat(totalTime) * 1000).toFixed(0)}ms)`);
      } else {
        results.warnings++;
        results.details.push(`⚠️ ${api.name}: HTTP ${httpCode}`);
      }
    } catch (error) {
      results.failed++;
      results.details.push(`❌ ${api.name}: ${error.message}`);
    }
  }

  // Тест 4: Производительность
  console.log('⚡ Анализ производительности...');
  const loadTimes = Object.values(results.performance).map(p => parseFloat(p.totalTime));
  const avgLoadTime = loadTimes.reduce((a, b) => a + b, 0) / loadTimes.length;

  if (avgLoadTime < 0.1) { // 100ms
    results.passed++;
    results.details.push(`✅ Производительность: отличная (среднее ${avgLoadTime.toFixed(0)}ms)`);
  } else if (avgLoadTime < 0.5) { // 500ms
    results.passed++;
    results.details.push(`✅ Производительность: хорошая (среднее ${avgLoadTime.toFixed(0)}ms)`);
  } else {
    results.warnings++;
    results.details.push(`⚠️ Производительность: нужно улучшить (среднее ${avgLoadTime.toFixed(0)}ms)`);
  }

  // Тест 5: Проверка ошибок в контенте
  console.log('🐛 Проверка на ошибки...');
  try {
    const content = execSync('type homepage_temp.html', { encoding: 'utf8' });
    const hasErrors = content.includes('Error') || content.includes('error') || content.includes('Exception');

    if (!hasErrors) {
      results.passed++;
      results.details.push('✅ В контенте нет явных ошибок');
    } else {
      results.warnings++;
      results.details.push('⚠️ В контенте обнаружены ошибки');
    }
  } catch (error) {
    results.details.push('ℹ️ Не удалось проверить контент на ошибки');
  }

  // Очистка временных файлов
  try {
    execSync('del homepage_temp.html temp_page.html 2>nul', { encoding: 'utf8' });
  } catch (e) {
    // Игнорируем ошибки удаления
  }

  // Финальные результаты
  const total = results.passed + results.failed + results.warnings;
  const successRate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : 0;

  console.log('\n' + '='.repeat(60));
  console.log('🎊 КОМПЛЕКСНЫЙ ОТЧЕТ UI ТЕСТИРОВАНИЯ');
  console.log('='.repeat(60));
  console.log(`✅ Пройдено тестов: ${results.passed}`);
  console.log(`⚠️ Предупреждений: ${results.warnings}`);
  console.log(`❌ Провалено тестов: ${results.failed}`);
  console.log(`📈 Общая успешность: ${successRate}%`);

  console.log('\n📄 Статус страниц:');
  Object.entries(results.pages).forEach(([name, status]) => {
    console.log(`   ${name}: ${status}`);
  });

  console.log('\n⚡ Производительность:');
  Object.entries(results.performance).forEach(([page, perf]) => {
    console.log(`   ${page}: ${perf.httpCode} | ${perf.totalTime}${perf.size ? ` | ${perf.size}` : ''}`);
  });

  console.log('\n📋 Детали тестов:');
  results.details.forEach(detail => console.log(`   ${detail}`));

  // Оценка
  if (successRate >= 90) {
    console.log('\n🏆 Оценка: ОТЛИЧНО! Приложение готово к production.');
  } else if (successRate >= 75) {
    console.log('\n✨ Оценка: ХОРОШО! Приложение функционально, есть минорные проблемы.');
  } else if (successRate >= 50) {
    console.log('\n⚠️ Оценка: УДОВЛЕТВОРИТЕЛЬНО. Нужно исправить критические проблемы.');
  } else {
    console.log('\n❌ Оценка: НЕУДОВЛЕТВОРИТЕЛЬНО. Требуется серьезная доработка.');
  }

  console.log('='.repeat(60));

  return results;
}

// Запуск тестов
runComprehensiveUITests().catch(console.error);
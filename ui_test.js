const { chromium } = require('playwright');

async function runUITests() {
  console.log('🚀 Запуск UI тестирования Agent Task Tracker');

  const browser = await chromium.launch({
    headless: false, // Показать браузер для визуализации
    slowMo: 500 // Замедлить для наглядности
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  // Результаты тестов
  const testResults = {
    passed: 0,
    failed: 0,
    details: []
  };

  try {
    // Тест 1: Главная страница
    console.log('📋 Тест 1: Загрузка главной страницы');
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');

    const title = await page.title();
    if (title.includes('Agent Task Tracker')) {
      testResults.passed++;
      testResults.details.push('✅ Главная страница загружена успешно');
    } else {
      testResults.failed++;
      testResults.details.push('❌ Главная страница: неверный заголовок');
    }

    // Проверка наличия основных элементов
    const navElements = await page.locator('nav').count();
    testResults.details.push(`📊 Навигационных элементов найдено: ${navElements}`);

    // Тест 2: Навигация на страницу проектов
    console.log('📁 Тест 2: Переход на страницу проектов');
    const projectsLink = page.locator('a[href="/projects"]');
    if (await projectsLink.count() > 0) {
      await projectsLink.click();
      await page.waitForLoadState('networkidle');

      if (page.url().includes('/projects')) {
        testResults.passed++;
        testResults.details.push('✅ Переход на страницу проектов успешен');
      } else {
        testResults.failed++;
        testResults.details.push('❌ Переход на страницу проектов не сработал');
      }
    } else {
      testResults.failed++;
      testResults.details.push('❌ Ссылка на проекты не найдена');
    }

    // Тест 3: Навигация на страницу задач
    console.log('✅ Тест 3: Переход на страницу задач');
    const tasksLink = page.locator('a[href="/tasks"]');
    if (await tasksLink.count() > 0) {
      await tasksLink.click();
      await page.waitForLoadState('networkidle');

      if (page.url().includes('/tasks')) {
        testResults.passed++;
        testResults.details.push('✅ Переход на страницу задач успешен');
      } else {
        testResults.failed++;
        testResults.details.push('❌ Переход на страницу задач не сработал');
      }
    } else {
      testResults.failed++;
      testResults.details.push('❌ Ссылка на задачи не найдена');
    }

    // Тест 4: Навигация на страницу статистики
    console.log('📈 Тест 4: Переход на страницу статистики');
    const statsLink = page.locator('a[href="/statistics"]');
    if (await statsLink.count() > 0) {
      await statsLink.click();
      await page.waitForLoadState('networkidle');

      if (page.url().includes('/statistics')) {
        testResults.passed++;
        testResults.details.push('✅ Переход на страницу статистики успешен');
      } else {
        testResults.failed++;
        testResults.details.push('❌ Переход на страницу статистики не сработал');
      }
    } else {
      testResults.failed++;
      testResults.details.push('❌ Ссылка на статистику не найдена');
    }

    // Тест 5: Навигация на страницу настроек
    console.log('⚙️ Тест 5: Переход на страницу настроек');
    const settingsLink = page.locator('a[href="/settings"]');
    if (await settingsLink.count() > 0) {
      await settingsLink.click();
      await page.waitForLoadState('networkidle');

      if (page.url().includes('/settings')) {
        testResults.passed++;
        testResults.details.push('✅ Переход на страницу настроек успешен');
      } else {
        testResults.failed++;
        testResults.details.push('❌ Переход на страницу настроек не сработал');
      }
    } else {
      testResults.failed++;
      testResults.details.push('❌ Ссылка на настройки не найдена');
    }

    // Тест 6: Проверка кнопок и интерактивных элементов
    console.log('🖱️ Тест 6: Проверка интерактивных элементов');

    // Возврат на главную для проверки кнопок
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');

    // Поиск всех кнопок
    const buttons = await page.locator('button, [role="button"]').count();
    testResults.details.push(`📊 Кнопок найдено: ${buttons}`);

    if (buttons > 0) {
      testResults.passed++;
      testResults.details.push('✅ Интерактивные элементы присутствуют');

      // Пробуем кликнуть на первую кнопку
      const firstButton = page.locator('button, [role="button"]').first();
      await firstButton.hover();
      testResults.details.push('✅ Кнопки интерактивны (hover работает)');
    } else {
      testResults.failed++;
      testResults.details.push('❌ Кнопки не найдены');
    }

    // Тест 7: Проверка форм
    console.log('📝 Тест 7: Проверка форм');
    const inputs = await page.locator('input, textarea, select').count();
    const forms = await page.locator('form').count();

    testResults.details.push(`📊 Форм найдено: ${forms}`);
    testResults.details.push(`📊 Полей ввода найдено: ${inputs}`);

    if (forms > 0 || inputs > 0) {
      testResults.passed++;
      testResults.details.push('✅ Формы и поля ввода присутствуют');
    } else {
      testResults.details.push('ℹ️ Формы не найдены (может быть нормально для данного приложения)');
    }

    // Тест 8: Responsive дизайн
    console.log('📱 Тест 8: Проверка responsive дизайна');

    // Тест мобильного разрешения
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);

    const mobileNavElements = await page.locator('nav').count();
    if (mobileNavElements > 0) {
      testResults.passed++;
      testResults.details.push('✅ Мобильная версия работает');
    } else {
      testResults.failed++;
      testResults.details.push('❌ Проблемы с мобильной версией');
    }

    // Возврат к десктопному разрешению
    await page.setViewportSize({ width: 1280, height: 720 });

    // Тест 9: Консольные ошибки
    console.log('🐛 Тест 9: Проверка консольных ошибок');
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    if (errors.length === 0) {
      testResults.passed++;
      testResults.details.push('✅ Консольных ошибок нет');
    } else {
      testResults.failed++;
      testResults.details.push(`❌ Найдено ${errors.length} консольных ошибок`);
      errors.slice(0, 3).forEach(error => {
        testResults.details.push(`   - ${error}`);
      });
    }

  } catch (error) {
    testResults.failed++;
    testResults.details.push(`❌ Критическая ошибка: ${error.message}`);
  } finally {
    await browser.close();
  }

  // Вывод результатов
  console.log('\n' + '='.repeat(50));
  console.log('📊 РЕЗУЛЬТАТЫ UI ТЕСТИРОВАНИЯ');
  console.log('='.repeat(50));
  console.log(`✅ Пройдено тестов: ${testResults.passed}`);
  console.log(`❌ Провалено тестов: ${testResults.failed}`);
  console.log(`📈 Успешность: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);
  console.log('\n📋 Детали:');
  testResults.details.forEach(detail => console.log(detail));
  console.log('='.repeat(50));

  return testResults;
}

// Запуск тестов
runUITests().catch(console.error);
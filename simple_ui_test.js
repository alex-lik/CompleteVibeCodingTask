const puppeteer = require('puppeteer');

async function runSimpleUITests() {
  console.log('🚀 Запуск упрощенного UI тестирования');

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  } catch (error) {
    console.log('❌ Puppeteer недоступен, создаем альтернативный тест...');
    return runAlternativeTest();
  }

  const page = await browser.newPage();
  const results = { passed: 0, failed: 0, details: [] };

  try {
    // Тест 1: Загрузка главной страницы
    console.log('📋 Тест 1: Главная страница');
    await page.goto('http://localhost:3002', { waitUntil: 'networkidle2' });

    const title = await page.title();
    if (title.includes('Agent Task Tracker')) {
      results.passed++;
      results.details.push('✅ Главная страница загружена');
    } else {
      results.failed++;
      results.details.push('❌ Главная страница: неверный заголовок');
    }

    // Тест 2: Проверка навигации
    console.log('🧭 Тест 2: Навигация');
    const navLinks = await page.$$('nav a, header a');
    results.details.push(`📊 Навигационных ссылок найдено: ${navLinks.length}`);

    // Тест 3: Проверка кнопок
    console.log('🖱️ Тест 3: Кнопки');
    const buttons = await page.$$('button, [role="button"], .btn');
    results.details.push(`📊 Кнопок найдено: ${buttons.length}`);

    // Скриншот главной страницы
    await page.screenshot({ path: 'homepage_screenshot.png' });
    results.details.push('📸 Скриншот главной страницы сохранен');

  } catch (error) {
    results.failed++;
    results.details.push(`❌ Ошибка: ${error.message}`);
  } finally {
    if (browser) await browser.close();
  }

  return results;
}

async function runAlternativeTest() {
  console.log('🔄 Запуск альтернативного теста через curl');

  const { execSync } = require('child_process');
  const results = { passed: 0, failed: 0, details: [] };

  try {
    // Тест загрузки главной страницы
    console.log('📋 Тест 1: HTTP проверка главной страницы');
    const response = execSync('curl -s -w "%{http_code}" -o /dev/null http://localhost:3002', { encoding: 'utf8' });

    if (response.trim() === '200') {
      results.passed++;
      results.details.push('✅ Главная страница доступна по HTTP');
    } else {
      results.failed++;
      results.details.push(`❌ Главная страница недоступна, код: ${response}`);
    }

    // Тест контента
    console.log('📝 Тест 2: Проверка контента');
    const content = execSync('curl -s http://localhost:3002', { encoding: 'utf8' });

    if (content.includes('Agent Task Tracker')) {
      results.passed++;
      results.details.push('✅ Контент страницы корректен');
    } else {
      results.failed++;
      results.details.push('❌ Контент страницы некорректен');
    }

    // Проверка всех маршрутов
    const routes = ['/projects', '/tasks', '/statistics', '/settings'];
    for (const route of routes) {
      console.log(`🧭 Тест маршрута: ${route}`);
      try {
        const routeResponse = execSync(`curl -s -w "%{http_code}" -o /dev/null http://localhost:3002${route}`, { encoding: 'utf8' });
        if (routeResponse.trim() === '200') {
          results.passed++;
          results.details.push(`✅ Маршрут ${route} доступен`);
        } else {
          results.failed++;
          results.details.push(`❌ Маршрут ${route} недоступен`);
        }
      } catch (error) {
        results.failed++;
        results.details.push(`❌ Ошибка маршрута ${route}: ${error.message}`);
      }
    }

    // Проверка времени загрузки
    console.log('⚡ Тест 3: Производительность');
    const loadTime = execSync('curl -s -w "%{time_total}" -o /dev/null http://localhost:3002', { encoding: 'utf8' });
    const timeMs = (parseFloat(loadTime.trim()) * 1000).toFixed(0);

    if (timeMs < 1000) {
      results.passed++;
      results.details.push(`✅ Быстрая загрузка: ${timeMs}ms`);
    } else {
      results.details.push(`⚠️ Медленная загрузка: ${timeMs}ms`);
    }

  } catch (error) {
    results.failed++;
    results.details.push(`❌ Критическая ошибка: ${error.message}`);
  }

  return results;
}

// Запуск тестов
runSimpleUITests().then(results => {
  console.log('\n' + '='.repeat(50));
  console.log('📊 РЕЗУЛЬТАТЫ UI ТЕСТИРОВАНИЯ');
  console.log('='.repeat(50));
  console.log(`✅ Пройдено: ${results.passed}`);
  console.log(`❌ Провалено: ${results.failed}`);
  console.log(`📈 Успешность: ${results.passed > 0 ? ((results.passed / (results.passed + results.failed)) * 100).toFixed(1) : 0}%`);
  console.log('\n📋 Детали:');
  results.details.forEach(detail => console.log(detail));
  console.log('='.repeat(50));
}).catch(console.error);
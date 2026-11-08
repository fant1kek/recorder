import os
import shutil
import time
import random
from playwright.sync_api import Page

# Глобальная переменная для папки с видео
PATH_TO_VIDEO_FOLDER = "./video"

def smooth_move(page: Page, target_x: float, target_y: float, steps: int = 55):
    """Ультра-плавное и размеренное перемещение курсора мыши."""
    try:
        current = page.evaluate("window.__lastMousePos")
    except Exception:
        current = None
        
    if not current:
        current = {"x": 100, "y": 100}
        
    start_x, start_y = current["x"], current["y"]
    
    for i in range(1, steps + 1):
        t = i / steps
        # Естественное ускорение в начале и замедление в конце (smoothstep)
        t = t * t * (3 - 2 * t)
        
        x = start_x + (target_x - start_x) * t
        y = start_y + (target_y - start_y) * t
        page.mouse.move(x, y)
        time.sleep(0.015)

def trigger_red_ripple(page: Page, x: float, y: float):
    """Принудительно рисует красную волну в указанных координатах экрана."""
    try:
        page.evaluate(f"window.CreateRipple({x}, {y});")
        time.sleep(0.05)  # Небольшая задержка, чтобы анимация успела начаться на видео
    except Exception:
        pass

def move_and_click(page: Page, selector: str):
    """Находит элемент, плавно ведет туда курсор, гарантированно рисует волну и кликает."""
    el = page.wait_for_selector(selector, state="attached", timeout=5000)
    box = el.bounding_box()
    if box:
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2
        
        # Плавно двигаем мышь к центру элемента
        smooth_move(page, target_x, target_y)
        
        # Принудительно пускаем красную волну в точке клика
        trigger_red_ripple(page, target_x, target_y)
        
        # Совершаем физический клик
        page.mouse.down()
        time.sleep(0.05)
        page.mouse.up()
        return target_x, target_y
    raise Exception(f"Element not found for click: {selector}")

def human_type(page: Page, selector: str, text: str):
    """Реалистичная неторопливая печать текста с человеческими задержками."""
    el = page.wait_for_selector(selector)
    el.focus()
    for char in text:
        page.keyboard.type(char)
        time.sleep(0.15 + random.random() * 0.1)

def CaptureVideo_Magento(
    url,
    company_name,
    language,
    country,
    postcode,
    city,
    street,
    house_no,
):
    """Основная функция автоматизации браузера и записи сценария."""
    from playwright.sync_api import sync_playwright
    
    os.makedirs(PATH_TO_VIDEO_FOLDER, exist_ok=True)
    
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    
    context = browser.new_context(
        record_video_dir=PATH_TO_VIDEO_FOLDER,
        record_video_size={"width": 1280, "height": 720},
        viewport={"width": 1280, "height": 720}
    )
    
    # Скрипт инициализации для инъекции курсора и функции Ripple
    init_script = """
    (() => {
        window.__lastMousePos = { x: 100, y: 100 };
        
        const container = document.createElement('div');
        container.id = 'custom-playwright-cursor-container';
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.pointerEvents = 'none';
        container.style.zIndex = '999999';
        
        const cursor = document.createElement('div');
        cursor.style.position = 'absolute';
        cursor.style.width = '64px';
        cursor.style.height = '64px';
        cursor.style.transform = 'translate(-32px, -32px)';
        cursor.style.display = 'none';
        
        const circle = document.createElement('div');
        circle.style.position = 'absolute';
        circle.style.width = '64px';
        circle.style.height = '64px';
        circle.style.borderRadius = '50%';
        circle.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
        
        const arrow = document.createElement('div');
        arrow.style.position = 'absolute';
        arrow.style.top = '32px';
        arrow.style.left = '32px';
        arrow.style.width = '32px';
        arrow.style.height = '32px';
        arrow.innerHTML = `
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://w3.org">
                <path d="M2 2L14 30L19 19L30 14L2 2Z" fill="white" stroke="black" stroke-width="2" stroke-linejoin="round"/>
            </svg>
        `;
        
        cursor.appendChild(circle);
        cursor.appendChild(arrow);
        container.appendChild(cursor);
        
        const inject = () => {
            if (!document.getElementById('custom-playwright-cursor-container') && document.body) {
                document.body.appendChild(container);
            }
        };
        
        window.addEventListener('mousemove', (e) => {
            inject();
            window.__lastMousePos = { x: e.clientX, y: e.clientY };
            cursor.style.display = 'block';
            cursor.style.left = `${e.clientX}px`;
            cursor.style.top = `${e.clientY}px`;
        });
        
        // Экспортируем глобальную функцию контролируемой отрисовки волн
        window.CreateRipple = (x, y) => {
            inject();
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.style.width = '0px';
            ripple.style.height = '0px';
            ripple.style.borderRadius = '50%';
            ripple.style.border = '4px solid rgba(255, 0, 0, 0.9)';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.transition = 'all 0.4s ease-out';
            ripple.style.pointerEvents = 'none';
            
            container.appendChild(ripple);
            
            setTimeout(() => {
                ripple.style.width = '70px';
                ripple.style.height = '70px';
                ripple.style.opacity = '0';
            }, 10);
            
            setTimeout(() => { ripple.remove(); }, 500);
        };
        
        window.addEventListener('mousedown', (e) => {
            window.CreateRipple(e.clientX, e.clientY);
        });
        
        window.ShowCallout = (text, bgColor = '#ffff00', textColor = '#000000', fade = 2000) => {
            inject();
            const callout = document.createElement('div');
            callout.style.position = 'fixed';
            callout.style.bottom = '40px';
            callout.style.right = '40px';
            callout.style.backgroundColor = bgColor;
            callout.style.color = textColor;
            callout.style.padding = '15px 25px';
            callout.style.fontFamily = 'sans-serif';
            callout.style.fontSize = '16pt';
            callout.style.fontWeight = 'bold';
            callout.style.borderRadius = '8px';
            callout.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
            callout.style.zIndex = '9999999';
            callout.style.opacity = '0';
            callout.style.transition = `opacity ${fade}ms ease-in-out`;
            callout.innerText = text;
            
            document.body.appendChild(callout);
            setTimeout(() => { callout.style.opacity = '1'; }, 50);
            
            setTimeout(() => {
                callout.style.opacity = '0';
                setTimeout(() => { callout.remove(); }, fade);
            }, fade + 2000);
        };
    })();
    """
    context.add_init_script(init_script)
    page = context.new_page()
    
    try:
        # 1. Открытие страницы
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        page.evaluate(f"window.ShowCallout('Searching for Magento developers in {city}...', '#ffff00', '#000000', 300)")
        time.sleep(0.4)
        
        # 2-3. Плавное движение к поисковой строке и гарантированный клик с красной волной
        search_input_selector = 'textarea[name="q"], input[name="q"], #search_form_input_homepage'
        move_and_click(page, search_input_selector)
        time.sleep(0.1)
        
        # 4. Ввод запроса
        query_text = f"Magento developer in {city}"
        human_type(page, search_input_selector, query_text)
        time.sleep(0.6)  # Пауза ПОСЛЕ ввода текста, чтобы зафиксировать написанное на видео
        
        # 5. Перемещение к синей кнопке поиска
        try:
            search_button_selector = 'button[class*="footerSearchButton"]'
            move_and_click(page, search_button_selector)
        except Exception:
            page.keyboard.press("Enter")
        
        time.sleep(0.4)
        
        # 6. Ожидание результатов поиска
        result_link_selector = '[data-testid="mainline-result-list"] a[data-testid="result-title-a"], article h2 a[href^="http"], .links_main a.result__url'
        page.wait_for_selector(result_link_selector, state="visible", timeout=15000)
        time.sleep(0.5)
        
        # 7. Движение к первому результату выдачи и клик с красной волной
        move_and_click(page, result_link_selector)
        
        # Ожидание для красивой фиксации перехода на видео
        time.sleep(3)  
        raw_video_path = page.video.path()
        
    except Exception as e:
        print(f"Error during execution for {company_name}: {e}")
        raw_video_path = None
    finally:
        context.close()
        browser.close()
        p.stop()
        
    if raw_video_path and os.path.exists(raw_video_path):
        final_filename = f"{company_name}.webm"
        dest_path = os.path.join(PATH_TO_VIDEO_FOLDER, final_filename)
        shutil.move(raw_video_path, dest_path)
        return os.path.abspath(dest_path)
        
    return None

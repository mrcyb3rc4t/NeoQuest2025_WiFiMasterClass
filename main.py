import requests
import time
import random
import logging
from urllib.parse import urljoin

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

SERVER_URL = "http://192.168.1.103:8080"

class AdminBot:
    def __init__(self, server_url):
        self.server_url = server_url
        self.session = requests.Session()
        
    def login(self):
        """Выполняет вход на сервер и возвращает успешность"""
        try:
            login_data = {
                'username': 'admin',
                'password': 'nRUs9snyXMRwXnmXCLFnOCoaRF98aWZT4UugpLtrDXnA6ypo'
            }
            
            logger.info("🔐 Выполняю вход...")
            
            # Отправляем POST запрос на логин
            response = self.session.post(
                urljoin(self.server_url, "/login"), 
                data=login_data,
                allow_redirects=False
            )
            
            # Проверяем редирект на /admin (признак успешного входа)
            if response.status_code in [302, 303] and '/admin' in response.headers.get('Location', ''):
                logger.info("✅ Вход выполнен успешно")
                return True
            else:
                logger.error("❌ Ошибка входа")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка при входе: {e}")
            return False
    
    def visit_page(self, path, description):
        """Посещает указанную страницу"""
        try:
            response = self.session.get(urljoin(self.server_url, path))
            logger.info(f"🌐 {description}")
            time.sleep(1)  # Пауза между посещениями
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при посещении {path}: {e}")
            return False
    
    def logout(self):
        """Выходит из системы"""
        try:
            response = self.session.get(urljoin(self.server_url, "/logout"))
            logger.info("🚪 Вышел из системы")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка при выходе: {e}")
            return False
    
    def run_cycle(self):
        """Один полный цикл: вход → посещение страниц → выход"""
        logger.info("=" * 50)
        logger.info("🔄 Начало нового цикла")
        
        # Шаг 1: Вход
        if not self.login():
            return False
        
        # Шаг 2: Посещение страниц
        pages_to_visit = [
            ("/admin", "Посещаю админку"),
            ("/logs", "Проверяю логи доступа"),
            ("/", "Захожу на главную страницу"),
            ("/decode_jwt", "Использую JWT декодер")
        ]
        
        # Случайно выбираем 2-3 страницы для посещения
        num_pages = random.randint(2, 3)
        selected_pages = random.sample(pages_to_visit, num_pages)
        
        for path, description in selected_pages:
            self.visit_page(path, description)
        
        # Шаг 3: Выход
        self.logout()
        
        logger.info("✅ Цикл завершен")
        return True
    
    def run(self):
        """Основной цикл работы бота"""
        logger.info("🤖 Запуск Admin Bot")
        logger.info(f"🎯 Сервер: {self.server_url}")
        logger.info("📝 Режим: Вход → Посещение страниц → Выход")
        logger.info("=" * 50)
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                logger.info(f"🔄 Цикл #{cycle_count}")
                
                # Выполняем один полный цикл
                success = self.run_cycle()
                
                # Случайный интервал между циклами (25-45 секунд)
                sleep_time = random.randint(25, 45)
                if success:
                    logger.info(f"💤 Ожидаю {sleep_time} секунд до следующего цикла...")
                else:
                    logger.info(f"💤 Ожидаю {sleep_time} секунд после ошибки...")
                
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Остановка бота по запросу пользователя")
                break
            except Exception as e:
                logger.error(f"💥 Критическая ошибка: {e}")
                logger.info("🔄 Перезапуск через 20 секунд...")
                time.sleep(20)

def main():
    """Основная функция"""
    print("=" * 60)
    print("🤖 Admin Bot для мастер-класса по ИБ")
    print("🎯 Режим: Вход → Посещение страниц → Выход")
    print("📡 Имитирует поведение администратора")
    print("=" * 60)
    
    import sys
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    else:
        server_url = SERVER_URL
    
    bot = AdminBot(server_url)
    
    try:
        bot.run()
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")

if __name__ == '__main__':
    main()
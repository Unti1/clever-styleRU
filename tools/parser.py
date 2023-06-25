from settings import *
import time

class Pars():#Thread):
    def __init__(self, invisable=False) -> None:
        """Шаблон для парсера с антидетект браузером Dolphin Anty

        Args:
            profile_id (str, optional): профиль ID от бразуера.
            invisable (bool, optional): запуск в свернутом режиме. Defaults to False.
            Версии эмуляторов: https://anty.dolphin.ru.com/docs/basic-automation/
            Для Linux сделать предвартилеьно chmo+x ..utils/cromedriver-linux
        """
        self.based_browser_startUp(invisable) # обычный запуск без dolphin
        #self.dolphin_browser_startUp(False) # запуск c dolphin
        self.wait = WebDriverWait(self.driver,6)
        self.action = ActionChains(self.driver,250)

    def authorithation(self):
        self.driver.get("https://clever-style.ru/catalog/")
        # //div[@data-modal="auth"]/span - вход кнопка
        self.wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@data-modal='auth']/span")))
        self.driver.find_element(By.XPATH,"//div[@data-modal='auth']/span").click()

        # //input[@name="email"] - почта
        # //input[@name="password"] - пароль
        self.wait.until(EC.element_to_be_clickable((By.XPATH,"//input[@name='email']")))
        self.driver.find_element(By.XPATH,"//input[@name='email']").send_keys("kashaewa.oxana@yandex.ru")
        self.driver.find_element(By.XPATH,"//input[@name='password']").send_keys("210807Martin220485Tatyana")

        # //form[@class="auth__form form js-auth-form"]//button[@type="submit"] - кнопка входа
        self.wait.until(EC.element_to_be_clickable((By.XPATH,'//form[@class="auth__form form js-auth-form"]//button[@type="submit"]')))
        self.driver.find_element(By.XPATH, '//form[@class="auth__form form js-auth-form"]//button[@type="submit"]').click()
        time.sleep(5)

    
    def dolphin_browser_startUp(self, PROFILE_ID,invisable):
        """Создание настройка и создания эмуляции браузера
        """ 
        options = webdriver.ChromeOptions()
        match platform.system():
            case "Windows":
                if platform.architecture() == "64bit":
                    chrome_drive_path = Service('/utils/chromedriver-win-x64')
                else: 
                    chrome_drive_path = Service('/utils/chromedriver-win-x86')
            case "Linux":
                chrome_drive_path = Service('./utils/chromedriver-linux')
                options.add_argument('--no-sandbox')
            case "Darwin":
                if platform.architecture() == "m1":
                    chrome_drive_path = Service('./utils/chromedriver-mac-m1')
                else:
                    chrome_drive_path = Service('./utils/chromedriver-mac-intel')


        response = requests.get(f'http://localhost:3001/v1.0/browser_profiles/{PROFILE_ID}/start?automation=1')
        respons_json = response.json()
        options.debugger_address = f"127.0.0.1:{respons_json['automation']['port']}"
        if invisable:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=chrome_drive_path,chrome_options=options)
    
    def based_browser_startUp(self, invisable):
        options = webdriver.ChromeOptions()
        if invisable:
            options.add_argument('--headless')
        # Отключаем уведомления
        options.add_argument("--disable-notifications")
        # Отключаем логирование
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.set_window_size(1920, 1080)

    def write_to_csv(self, filename, data):
        print(f"\n>Сохраняю \"{filename}.csv\" в папку \"data\"")
        # Открываем файл в режиме дозаписи ('a') или создаем новый файл ('w')
        with open(f"data/{filename}.csv", 'a' if self.file_exists(filename) else 'w', newline='', encoding='cp1251') as csvfile:
            writer = csv.writer(csvfile)
            # Записываем каждую строку данных в файл CSV
            for row in data:
                writer.writerow(row)
        print(f">Данные сохранены")

    def file_exists(self, filename):
        try:
            with open(f'data/{filename}.csv', 'r') as file:
                return True
        except FileNotFoundError:
            return False

    def catalog(self):
        self.driver.get("https://clever-style.ru/catalog/")
        self.wait.until(EC.element_to_be_clickable((By.XPATH,'//a[@href="/catalog/zhenskoe/"]'))) # ожидание
        try:
            for el in self.driver.find_elements(By.XPATH,"//nav/section/button"):
                self.action.move_to_element(el)
                self.action.click(el)
                self.action.perform()  
        except:
            pass
        time.sleep(2)
        catalog_links = []
        sections = self.driver.find_elements(By.XPATH,"//nav/section")
        for i in range(len(sections)):
            catalog = self.driver.find_element(By.XPATH,f"//nav/section[{i+1}]/h2").text
            catalog_links.append(list(
                    map(
                        lambda x: [ f"{catalog}-{x.text}", x.get_attribute('href')],
                        self.driver.find_elements(By.XPATH,f"//nav/section[{i+1}]/ul/li/a")
                    )
                ))
        return(sum(catalog_links,[]))

    def sale_catalog(self,catalog_data:list[str,str]):
        sale_link = catalog_data[1][:catalog_data[1].find('catalog/') + len('catalog/')] + "sale/" + catalog_data[1][catalog_data[1].find('catalog/') + len("catalog/"):]
        regenerate_data = [catalog_data[0],sale_link]
        return(regenerate_data)

    def subcatalogs(self,catalog_data):
        """Позволяет получить все ссылки на подкаталоги на сайте

        Args:
            catalog_data (_type_): _description_
        """
        cat_name = catalog_data[0]
        self.driver.get(catalog_data[1])
        try:
            self.driver.find_element(By.XPATH,"//section/div/button").click()# ещё
            # time.sleep(1.2)
        except:
            pass
        try:
            return(list(map(lambda x: (cat_name + "-" +x.text,x.get_attribute("href")),self.driver.find_elements(By.XPATH,"/html/body/main/div/section/div[1]/div/ul/li/a"))))
        except:
            return None

    
    def parse_subcatalog_page_links(self,link):
        self.driver.get(link)
        # //a[@class="card-product js-card-product"]
        links_list = []
        try: 
            page_num = int(self.driver.find_elements(By.XPATH,'//a[@class="paginations__item"]')[-2].text)
        except:
            page_num = 1
        for i in range(page_num):
            links_list.extend(list(map(lambda x: x.get_attribute('href'),self.driver.find_elements(By.XPATH,'//a[@class="card-product js-card-product"]'))))
            if page_num != 1 and i != page_num-1:
                self.driver.find_elements(By.XPATH,'//a[@class="paginations__item"]')[-1].click()
        return(links_list)
    
    def parse_subcatalogs(self,subcatalogs):
        """Основной модуль парсинга

        Args:
            subcatalogs (_type_): [(подкаталог, ссылки подкаталога), ...]
        """
        for s in subcatalogs:
            try:
                title = s[0]
                print(f"Начинаю сбор для \"{title}\"")
                links = self.parse_subcatalog_page_links(s[-1]) # собирает ссылки на товари из подкаталога
                # links = links[:len(links)//5]
                tovar_data = []
                # собирает конкретные значения из товаров
                for step,link in enumerate(links):
                    sys.stdout.write(f"\r>Просмотренно товаров [{step+1}/{len(links)}] |  {link}")
                    sys.stdout.flush()
                    tovar_data.append(self.single_tovar_grab(link))
                self.write_to_csv(title,tovar_data)
            except:
                logging.error(f"Ошибка сбора данных в каталоге {s[0]} \n{traceback.format_exc()}")
        return
    
    def single_tovar_grab(self,link):
        self.driver.get(link)
        try:
            more = self.driver.find_element(By.XPATH,'//section[1]/div/div[2]/section[3]/button')
            self.action.move_to_element(more)
            self.action.click(more)
            self.action.perform()
            time.sleep(0.25)
        except: 
            pass
        
        title = self.driver.find_element(By.XPATH,'//h1[@class="product__title main-title"]').text.replace("\n","")

        articul = self.driver.find_element(By.XPATH,'//div[@class="product-about__list-item js-product-qualities-item"][5]').text.replace("\n","")
        
        try:
            sizes = list(map(lambda x: x.text, self.driver.find_elements(By.XPATH,'//div[@class="product-sizes__size js-size-wrap positioned-right"]/button')))
        except:
            sizes = []
        
        try:
            img = list(map(lambda x: x.get_attribute("src"), self.driver.find_elements(By.XPATH,'//div[@class="product__slider-container visible"]//img')))
        except:
            img = "Не найдены"
        
        colors = []
        try:
            for color_button in self.driver.find_elements(By.XPATH,'//section[1]/div[2]/div//button'):
                self.action.move_to_element(color_button)
                self.action.click(color_button)
                self.action.perform()
                colors.append( self.driver.find_element(By.XPATH,'//span[@class="product-color__name js-color-name"]').text )
        except:
            pass
        
        try:
            base_cost = self.driver.find_element(By.XPATH,'//b[@class="product__price-price js-basic-price"]').text
        except:
            base_cost = "Отсутствует"

        try:
            sale_cost = self.driver.find_element(By.XPATH,'//b[@class="product__price-price js-discount-price"]').text
        except:
            sale_cost = "Отсутствует"

        try:
            description = self.driver.find_element(By.XPATH,'//section[@class="product-descr hidden-mobile"]/p').text
        except exceptions.NoSuchElementException:
            description = "Отсутствует"
        
        return (title, base_cost, sale_cost, articul, sizes, colors, description, img)
    
    def test(self):
        self.authorithation()
        catalog_data = self.catalog()
        logging.info(catalog_data)
        sale_cat = list(map(lambda x: self.sale_catalog(x),catalog_data))
        subcatalogs = self.subcatalogs(catalog_data[0])
        subcatalogs = list(filter(lambda x: x != None, subcatalogs))
        self.parse_subcatalogs(subcatalogs)
        
    def main(self):
        self.authorithation()
        catalog_data = self.catalog()
        sale_cat = list(map(lambda x: self.sale_catalog(x),catalog_data))
        catalog_data.extend(sale_cat)
        catalog_data.reverse()
        # print(catalog_data)
        subcatalogs = list(map(lambda data: self.subcatalogs(data),catalog_data))
        subcatalogs = sum(subcatalogs,[])
        subcatalogs = list(filter(lambda x: x != None, subcatalogs))
        # print(subcatalogs)
        self.parse_subcatalogs(subcatalogs)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
PATH = "D:\\FREEDOM\\chromedriver.exe"

# 创建 Service 对象
service = Service(PATH)
# 初始化 Chrome 选项
options = Options()
options.add_argument('--ignore-certificate-errors')
# 初始化 Chrome 驱动
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.recordedfuture.com/blog")  # 替换为实际的 URL
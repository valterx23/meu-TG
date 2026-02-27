import gymnasium as gym

# Criando um ambiente para que a IA possa treinar -> Jogo de equilibrar um pau KKKK
env = gym.make('Taxi-v3', render_mode="human")

# Reiniciar o ambiente para começar um novo episódio
observation, info = env.reset()

print(f"Começando observação: {observation}")

episode_over = False
total_reward = 0

while not episode_over:
    # A IA escolhe uma ação: 0 = puxar o carrinho pra esquerda; 1 = puxar o carrinho para a direita
    action = env.action_space.sample() # Faz uma ação aleatória por enquanto - o agente vai ficar inteligente

    # Faz a ação e mostra o que acontece
    observation, reward, terminated, truncated, info = env.step(action)

    # Reward: +1 para cada passo que o PAU tiver equilibrado kkkk
    # terminated: Verifica se a IA deixou o PAU cair (IA perde)
    # truncated: Verifica se a IA chegou no tempo limite determinado (500 steps)

    total_reward += reward
    episode_over = terminated or truncated

print(f"Episódio Terminado! Recompensa total: {total_reward}")
env.close()

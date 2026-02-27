# Biblioteca de criação de Arrays
import numpy as np

# Todo array é uma lista que pode ser de 1 ou mais dimensões
# Array de 1 dimensão:
n1 = np.array([1,2,3,4])
print(n1)

# Array de 2 dimensões:
n2 = np.array([[1,2],[3,4]])
print(n2)
print("\n")



# ATRIBUTOS IMPORTANTES DE UM ARRAY
a = np.array([[1,2,3],
             [4,5,6]])
print(a.ndim) # Mostra o número de dimensões que tem o Array
print(a.shape) # Formato (2, 3) - 2 linhas por 3 colunas
print(a.size) # Mostra o total de elementos -> 6 -> 2 linhas * 3 colunas
print(a.dtype) # tipo dos elementos -> int64, float64, etc...




# CRIANDO ARRAYS ESPECIAIS
np.zeros(3) # Cria um array de 3 colunas cheia de número zero -> [0, 0, 0]
np.ones((2,3)) # Cria 2 arrays com 3 colunas cheia de número 1 -> [1,1,1] [1,1,1]
np.arange(5) # Cria um array de 0 até 4 colunas (como se fosse um for) -> intervalo de números
np.linspace(0,10,5) # Cria um array que vai de 0 até 10 em um tamanho de 5 colunas

# Você pode escolher o tipo de dado:
x = np.ones(3, dtype=int) # Cria um array com 3 colunas cheio de ńúmeros 1 inteiro

# INDEXANDO E FATIANDO
a = np.array([10,20,30,40]) # vetor
print(a[0]) # Primeiro índice
print(a[1:3]) # Do índice 1 até antes do 3 -> [20] e [30]
print(a[-2:]) # Últimos dois elementos

# 2D
b = np.array([[1,2,3],[4,5,6]]) # Matriz
print(b[1,2]) # linha 1 coluna 2
print(b[:,1]) # Toda coluna 1

# Indexação condicional:
print(b[b > 2]) # [3 4 5 6] -> Todos os maiores que 2



# COPIANDO E CRIANDO VIEWS
b = np.array([1,2,3,4])
c = b[1:3]  # view → altera b se mudar c
c[0] = 99
print(b)    # [1 99 3 4]
# Basicamente o que ele fez foi pegar de um vetor [1,2,3,4] os indices 1 até antes do 3, armazenar isso em uma nova variavel chamada "c"
# e depois dizer que c[0] que na verdade vale 2, mas passa a valer 99

d = b.copy()  # cópia → alterações não afetam b




# OPERAÇÕES MATEMÁTICAS BÁSICAS
x = np.array([1,2,3])
y = np.array([10,20,30])
print("\n")

# As duas variáveis de array x e y podem fazer as 4 operações matemáticas básicas! + - * /
print(x.sum())        # Do array X,Soma todos os índices de apenas 1 array
print(x.mean())       # Faz uma média aritmética dos valores do array
print(x.max())        # Do array X, Percebe qual é o maior número do array
print(x.min())        # Do array X, Percebe qual é o menor número do array
print(x.std())        # Faz o cálculo do desvio padrão do array X
print(np.argmax(x)) # Mostra o Índice que tem o maior valor
print(np.argmin(x)) # Mostra o Índice que tem o menor valor

# Para arrays 2D:
arr = np.array([[1,2],
                [3,4]])
print("\n")
print(arr.sum(axis=0)) # Faz Soma entre colunas
print(arr.sum(axis=1)) # Faz Soma entre linhas
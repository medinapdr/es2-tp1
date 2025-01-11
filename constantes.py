from cartas import CartaCriatura
from banco_de_dados import BancoSimulado

# Carrega cartas do banco
banco = BancoSimulado('cartas_game.csv')
cartas = banco.obter_cartas()

# Gera o dicionário de criaturas disponíveis
CRIATURAS_DISPONIVEIS = {carta.nome: carta.resistencia for carta in cartas if isinstance(carta, CartaCriatura)}

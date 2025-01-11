import random
import copy
from banco_de_dados import BancoSimulado
from  jogo import Jogo
from  jogador import Jogador
    
banco = BancoSimulado('cartas_game.csv')
cartas = banco.obter_cartas()

jogador1 = Jogador("Jogador", eh_humano=True)
jogador2 = Jogador("Máquina", eh_humano=False)
jogador1.baralho.extend([copy.deepcopy(carta) for carta in random.choices(cartas, k=30)])
jogador2.baralho.extend([copy.deepcopy(carta) for carta in random.choices(cartas, k=30)])

if __name__ == "__main__":
    jogo = Jogo([jogador1, jogador2])
    jogo.iniciar()

    while jogo.jogar_turno():
        pass
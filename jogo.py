import random
import utils
from typing import List

class Jogo:
    """Representa o jogo de cartas."""
    def __init__(self, jogadores: list):
        self.jogadores = jogadores
        self.turno = 0
        self.historico: List[str] = []
        self.encerrar_jogo = False

    def iniciar(self):
        """Inicia o jogo."""
        print("Iniciando o jogo!")
        for jogador in self.jogadores:
            random.shuffle(jogador.baralho)
            for _ in range(3):
                jogador.comprar_carta()

    def jogar_turno(self):
        """Joga um turno do jogo."""
        if self.encerrar_jogo: 
            return False
        utils.limpar_tela()
        rodada_atual = self.turno + 1
        jogador_atual = self.jogadores[self.turno % len(self.jogadores)]
        print(f"\nRodada número {rodada_atual}.\nÉ a vez de {jogador_atual.nome}!")
        jogador_atual.mana += 1
        print(f"{jogador_atual.nome} ganha 1 mana. Mana total: {jogador_atual.mana}")
        jogador_atual.comprar_carta()

        # Ação do jogador
        jogador_alvo = self.jogadores[(self.turno + 1) % len(self.jogadores)]
        jogador_atual.escolher_acao(jogador_alvo, self)

        if self.encerrar_jogo:
            return False

        # Verificar se algum jogador perdeu
        if jogador_alvo.saude <= 0:
            print(f"{jogador_alvo.nome} foi derrotado!")
            self.historico.append(f"Rodada {rodada_atual}: {jogador_alvo.nome} foi derrotado!")
            self.jogadores.remove(jogador_alvo)

        self.turno += 1
        if len(self.jogadores) == 1:
            vencedor = self.jogadores[0].nome
            print(f"{vencedor} é o vencedor!")
            self.historico.append(f"Rodada {rodada_atual}: {vencedor} é o vencedor!")
            return False
        return True
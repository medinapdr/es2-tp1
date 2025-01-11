from cartas import Carta, CartaCriatura, CartaFeitico, CartaFeiticoRevive, CartaTerreno, CartaAleatoria
from constantes import CRIATURAS_DISPONIVEIS

class JogadorAcao:
    """Define as ações de cartas que um jogador pode realizar."""
    
    def jogar_carta(self, indice_carta: int, alvo=None, jogador_alvo=None, jogo=None) -> bool:
        """Joga uma carta da mão."""
        if not self._indice_valido(indice_carta, self.mao):
            print("Índice de carta inválido.")
            return False

        carta: Carta = self.mao[indice_carta]

        if isinstance(carta, CartaFeiticoRevive) and not self.cemiterio:
            print(f"Não é possível utilizar {carta.nome} pois o cemitério está vazio!")
            return False

        if isinstance(carta, CartaCriatura):
            if self.mana >= carta.custo_mana:
                self.mana -= carta.custo_mana
                self.campo_de_batalha.append(carta)
                self.mao.pop(indice_carta)
                print(f"{self.nome} jogou {carta.nome}.")
                if jogo:
                    jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Jogou {carta.nome}")
                return True
            else:
                print(f"Mana insuficiente para jogar {carta.nome}.")
                return False

        if isinstance(carta, CartaTerreno):
            if self.mana >= carta.custo_mana:
                self.mana -= carta.custo_mana
            print(f"{self.nome} joga o terreno {carta.nome}.")
            carta.ativar_efeito(self)
            self.mao.pop(indice_carta)
            if jogo:
                jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Jogou {carta.nome}")
            return True

        if isinstance(carta, CartaAleatoria):
            if self.mana >= carta.custo_mana:
                self.mana -= carta.custo_mana
            print(f"{self.nome} joga {carta.nome}.")
            carta.ativar_efeito(self, jogador_alvo)
            self.mao.pop(indice_carta)
            if jogo:
                jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Jogou {carta.nome}")
            return True

        if isinstance(carta, CartaFeitico):
            if isinstance(carta, CartaFeiticoRevive):
                if carta.lancar(self, CRIATURAS_DISPONIVEIS, alvo, jogador_alvo):
                    self.cemiterio.append(self.mao.pop(indice_carta))
                    print(f"{self.nome} lançou {carta.nome}.")
                    if jogo:
                        jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Usou {carta.nome}")
                    return True
            else:
                if carta.lancar(self, alvo, jogador_alvo):
                    self.cemiterio.append(self.mao.pop(indice_carta))
                    print(f"{self.nome} lançou {carta.nome}.")
                    if jogo:
                        jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Usou {carta.nome}")
                    return True

        return False

    def _indice_valido(self, indice: int, lista) -> bool:
        """Verifica se o índice é válido para a lista."""
        return 0 <= indice < len(lista)

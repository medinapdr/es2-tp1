from typing import Optional
from cartas import CartaCriatura
import utils

class JogadorCombate:
    """Métodos relacionados ao combate do jogador."""
    
    def atacar(self, jogador_alvo, indice_atacante: int, indice_alvo: Optional[int] = None, jogo=None):
        """Ataca o jogador alvo ou suas criaturas com uma criatura."""
        if not self._indice_valido(indice_atacante, self.campo_de_batalha):
            print("Índice de atacante inválido.")
            return

        atacante = self.campo_de_batalha[indice_atacante]

        if isinstance(atacante, CartaCriatura):
            # Se o adversário não tiver criaturas, ataca diretamente o jogador
            if not jogador_alvo.campo_de_batalha:
                print(f"{self.nome}'s {atacante.nome} ataca {jogador_alvo.nome} diretamente.")
                utils.custom_sleep(1.5)
                jogador_alvo.receber_dano(atacante.poder)
                if jogo:
                    jogo.historico.append(
                        f"Rodada {jogo.turno + 1} - {self.nome}: {atacante.nome}(P:{atacante.poder}, R:{atacante.resistencia}) atacou diretamente {jogador_alvo.nome}"
                    )
                return

            # Se houver criaturas no campo adversário, valida o índice de alvo
            if indice_alvo is None or not self._indice_valido(indice_alvo, jogador_alvo.campo_de_batalha):
                print("Índice de criatura alvo inválido.")
                return

            criatura_alvo = jogador_alvo.campo_de_batalha[indice_alvo]
            print(
                f"{self.nome}'s {atacante.nome} (Poder: {atacante.poder}, Resistência: {atacante.resistencia}) "
                f"ataca {jogador_alvo.nome}'s {criatura_alvo.nome} (Poder: {criatura_alvo.poder}, Resistência: {criatura_alvo.resistencia})."
            )
            utils.custom_sleep(1.5)
            if criatura_alvo.sofrer_dano(atacante.poder):
                jogador_alvo.campo_de_batalha.remove(criatura_alvo)
                jogador_alvo.cemiterio.append(criatura_alvo)

            if jogo:
                jogo.historico.append(
                    f"Rodada {jogo.turno + 1} - {self.nome}: {atacante.nome}(P:{atacante.poder}, R:{atacante.resistencia}) atacou {criatura_alvo.nome}(P:{criatura_alvo.poder}, R:{criatura_alvo.resistencia})"
                )

    def _indice_valido(self, indice: int, lista) -> bool:
        """Verifica se o índice é válido para a lista."""
        return 0 <= indice < len(lista)

import jogo_estrutura.utils as utils
from banco.cartas import CartaFeitico, CartaCriatura

class JogadorIA:
    def __init__(self, jogador):
        
        self.jogador = jogador

    def escolher_acao(self, jogador_alvo, jogo):
        print(f"{self.jogador.nome} está escolhendo uma ação...")
        utils.custom_sleep(1.5)

        # Se a saúde estiver baixa, tenta se curar
        if self.jogador.saude < 10:
            for i, carta in enumerate(self.jogador.mao):
                if carta.custo_mana <= self.jogador.mana and isinstance(carta, CartaFeitico) and getattr(carta, 'tipo_magia', None) == "cura":
                    print(f"{self.jogador.nome} decidiu se curar jogando {carta.nome}")
                    utils.custom_sleep(1.5)
                    self.jogador.jogar_carta(i, jogo=jogo)
                    return

        # Se o oponente tiver criaturas, tenta usar cartas de dano
        if jogador_alvo.campo_de_batalha:
            for i, carta in enumerate(self.jogador.mao):
                if carta.custo_mana <= self.jogador.mana and isinstance(carta, CartaFeitico) and getattr(carta, 'tipo_magia', None) in ["dano_unico", "dano_coletivo"]:
                    if getattr(carta, 'tem_alvo', False) and jogador_alvo.campo_de_batalha:
                        # Escolhe a criatura com menor resistência
                        criatura_alvo = min(jogador_alvo.campo_de_batalha, key=lambda c: c.resistencia)
                        print(f"{self.jogador.nome} usa {carta.nome} na criatura inimiga {criatura_alvo.nome}")
                        utils.custom_sleep(1.5)
                        self.jogador.jogar_carta(i, alvo=criatura_alvo, jogador_alvo=jogador_alvo, jogo=jogo)
                        return
                    else:
                        print(f"{self.jogador.nome} usa {carta.nome} para danificar o campo inimigo.")
                        utils.custom_sleep(1.5)
                        self.jogador.jogar_carta(i, jogador_alvo=jogador_alvo, jogo=jogo)
                        return

        # Tenta invocar uma criatura
        for i, carta in enumerate(self.jogador.mao):
            if carta.custo_mana <= self.jogador.mana and isinstance(carta, CartaCriatura):
                print(f"{self.jogador.nome} decide invocar a criatura {carta.nome}")
                utils.custom_sleep(1.5)
                self.jogador.jogar_carta(i, jogo=jogo)
                return

        # Se tiver criatura no campo, tenta atacar com a de maior poder (maior dano)
        if self.jogador.campo_de_batalha:
            # Seleciona a criatura com o maior poder
            atacante = max(self.jogador.campo_de_batalha, key=lambda c: c.poder)
            indice_atacante = self.jogador.campo_de_batalha.index(atacante)
            print(f"{self.jogador.nome} decide atacar com {atacante.nome} (Poder: {atacante.poder}).")
            utils.custom_sleep(1.5)
            if jogador_alvo.campo_de_batalha:
                # Se o adversário tiver criaturas, ataca aquela com menor resistência
                criatura_alvo = min(jogador_alvo.campo_de_batalha, key=lambda c: c.resistencia)
                indice_alvo = jogador_alvo.campo_de_batalha.index(criatura_alvo)
                self.jogador.atacar(jogador_alvo, indice_atacante, indice_alvo, jogo=jogo)
            else:
                # Ataque direto ao jogador adversário
                self.jogador.atacar(jogador_alvo, indice_atacante, jogo=jogo)
            return

        # Se não houver nenhuma ação possível, passa a vez.
        print(f"{self.jogador.nome} não jogou cartas e nem atacou. Passando a vez...")
        jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.jogador.nome}: Passou a vez")
        utils.custom_sleep(1.5)

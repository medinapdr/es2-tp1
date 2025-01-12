from colorama import Fore, init
init(autoreset=True)

class JogadorTabuleiro:
    """Métodos para exibição do tabuleiro e interatividade do jogador."""
    
    def exibir_tabuleiro(self, jogador_alvo):
        print("\n--- TABULEIRO DO JOGO ---")
        print("\nCampo de Batalha:")
        print(f"{Fore.BLUE}{self.nome}'s Campo de Batalha:")
        for i, criatura in enumerate(self.campo_de_batalha):
            print(f"  [{i}] {Fore.BLUE}{criatura}")
        print(f"{Fore.RED}{jogador_alvo.nome}'s Campo de Batalha:")
        for i, criatura in enumerate(jogador_alvo.campo_de_batalha):
            print(f"  [{i}] {Fore.RED}{criatura}")
        print("\nInformações dos Jogadores:")
        for jogador in [self, jogador_alvo]:
            cor = Fore.BLUE if jogador == self else Fore.RED
            print(f"{cor}{jogador.nome} - Saúde: {jogador.saude}, Mana: {jogador.mana}")
            if jogador.eh_humano:
                print("Mão:")
                for i, carta in enumerate(jogador.mao):
                    print(f"  [{i}] {carta}")
            else:
                print(f"Mão: {len(jogador.mao)} cartas escondidas")
            print("----------------------")

    def escolher_acao(self, jogador_alvo, jogo):
        """Método que permite ao jogador (ou IA) escolher uma ação."""
        self.exibir_tabuleiro(jogador_alvo)
        
        if self.eh_humano:
            print(f"\n{self.nome}, é a sua vez!")
            while True:
                acao = input("Escolha uma ação: (1) Jogar carta, (2) Atacar com Criatura, (3) Passar a vez, (4) Histórico, (5) Mostrar cemitério, (6) Encerrar: ")
                
                if acao == "1":
                    if not self.mao:
                        print("Você não tem cartas na mão para jogar.")
                        continue
                    try:
                        indice_carta = int(input("Escolha o índice da carta para jogar: "))
                    except ValueError:
                        print("Índice inválido.")
                        continue
                    # Para este exemplo, chamamos jogar_carta; a lógica completa pode ser expandida
                    if self.jogar_carta(indice_carta, jogador_alvo=jogador_alvo, jogo=jogo):
                        break
                    else:
                        print("Tente outra ação.")
                elif acao == "2":
                    # Um exemplo simplificado de ataque
                    if not self.campo_de_batalha:
                        print("Não há criaturas no seu campo para atacar.")
                        continue
                    try:
                        indice_atacante = int(input("Escolha o índice da sua criatura para atacar: "))
                    except ValueError:
                        print("Índice inválido.")
                        continue
                    # Se o adversário tiver criaturas, escolheremos o primeiro
                    if jogador_alvo.campo_de_batalha:
                        indice_alvo = 0
                    else:
                        indice_alvo = None
                    self.atacar(jogador_alvo, indice_atacante, indice_alvo, jogo=jogo)
                    break
                elif acao == "3":
                    print("Passando a vez.")
                    jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Passou a vez.")
                    break
                elif acao == "4":
                    print("\n--- HISTÓRICO DAS ÚLTIMAS AÇÕES ---")
                    for h in jogo.historico[-10:]:
                        print(h)
                    print("-----------------------------------")
                    continue
                elif acao == "5":
                    self.mostrar_cemiterio()
                elif acao == "6":
                    print("Encerrando o jogo...")
                    jogo.encerrar_jogo = True
                    break
                else:
                    print("Ação inválida. Tente novamente.")
        else:
            print(f"{self.nome} está escolhendo uma ação...")
            # Lógica simplificada para IA
            import jogo_estrutura.utils as utils
            utils.custom_sleep(1.5)
            # Exemplo: se tiver carta para jogar, jogar a primeira
            if self.mao and self.mana >= self.mao[0].custo_mana:
                self.jogar_carta(0, jogador_alvo=jogador_alvo, jogo=jogo)
            else:
                print(f"{self.nome} passou a vez.")
                jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Passou a vez.")

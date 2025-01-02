import random
import copy
import os
from typing import List, Optional
from colorama import Fore, Style, init
import time

init(autoreset=True)  # Inicializa o colorama para compatibilidade entre plataformas

def custom_sleep(duration: int):
    if os.getenv("RUNNING_TESTS") != "1":
        time.sleep(duration)
        
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

class Carta:
    """Representa uma carta genérica."""
    def __init__(self, nome: str, custo_mana: int, descricao: str, tipo_magia: Optional[str] = None):
        self.nome = nome
        self.custo_mana = custo_mana
        self.descricao = descricao
        self.tipo_magia = tipo_magia

    def __str__(self):
        return f"{self.nome} (Mana: {self.custo_mana}) - {self.descricao}"

class CartaCriatura(Carta):
    """Representa uma carta de criatura."""
    def __init__(self, nome: str, custo_mana: int, descricao: str, poder: int, resistencia: int):
        super().__init__(nome, custo_mana, descricao)
        self.poder = poder
        self.resistencia = resistencia

    def __str__(self):
        return f"{self.nome} (Mana: {self.custo_mana}) [Poder: {self.poder}, Resistência: {self.resistencia}] - {self.descricao}"
    
    def sofrer_dano(self, quantidade: int, jogador=None):
        """Aplica dano à criatura e envia ao cemitério se a resistência for menor ou igual a zero."""
        self.resistencia -= quantidade
        print(f"{self.nome} sofre {quantidade} de dano. Resistência restante: {self.resistencia}")
        if self.resistencia <= 0:
            if jogador:
                jogador.campo_de_batalha.remove(self)
                jogador.cemiterio.append(self)
                print(f"{self.nome} foi removida do campo de batalha e enviada ao cemitério.")
            return True
        return False

class CartaFeitico(Carta):
    """Representa uma carta de feitiço."""
    def __init__(self, nome: str, custo_mana: int, descricao: str, tipo_magia: str, poder: int, tem_alvo: bool = False, afeta_todos: bool = False):
        super().__init__(nome, custo_mana, descricao, tipo_magia)
        self.poder = poder
        self.tem_alvo = tem_alvo
        self.afeta_todos = afeta_todos

    def lancar(self, lancador, alvo=None, jogador_adversario=None):
        """Lança o feitiço."""
        if lancador.mana < self.custo_mana:
            print(f"Mana insuficiente para lançar {self.nome}.")
            return False
        
        lancador.mana -= self.custo_mana
        
        if self.tipo_magia == "dano_direto":
            print(f"{lancador.nome} lança {self.nome} em {alvo.nome if alvo else 'o jogador adversário'}, causando {self.poder} de dano.")
            alvo.receber_dano(self.poder) if hasattr(alvo, 'receber_dano') else print("Alvo inválido.")
        
        elif self.tipo_magia == "dano_unico":
            if alvo and hasattr(alvo, 'sofrer_dano'):
                print(f"{lancador.nome} lança {self.nome} em {alvo.nome}, causando {self.poder} de dano.")
                alvo.sofrer_dano(self.poder, jogador_adversario)
            elif alvo and hasattr(alvo, 'receber_dano'):
                alvo.receber_dano(self.poder)

        elif self.tipo_magia == "cura":
            print(f"{lancador.nome} usa {self.nome} e restaura {self.poder} de saúde.")
            lancador.saude += self.poder
        
        elif self.tipo_magia == "buff_coletivo":
            print(f"{lancador.nome} usa {self.nome} para fortalecer suas criaturas.")
            for criatura in lancador.campo_de_batalha:
                criatura.resistencia += self.poder
        
        elif self.tipo_magia == "dano_coletivo" and jogador_adversario is not None:
            print(f"{lancador.nome} lança {self.nome}, causando {self.poder} de dano a todas as criaturas do adversário.")
            for criatura in jogador_adversario.campo_de_batalha[:]:
                criatura.sofrer_dano(self.poder, jogador_adversario) 
        return True
    
class CartaFeiticoRevive(CartaFeitico):
    """Representa um feitiço que revive uma criatura do cemitério."""
    def __init__(self, nome: str, custo_mana: int, descricao: str):
        super().__init__(nome, custo_mana, descricao, tipo_magia="revive", poder=0, tem_alvo=False, afeta_todos=False)

    def lancar(self, lancador, alvo=None, jogador_adversario=None):
        """Lança o feitiço de reviver criatura."""
        if lancador.mana < self.custo_mana:
            print(f"Mana insuficiente para lançar {self.nome}.")
            return False
        lancador.mana -= self.custo_mana
        criaturas_no_cemiterio = [c for c in lancador.cemiterio if isinstance(c, CartaCriatura)]
        if criaturas_no_cemiterio:
            criatura_para_revivir = random.choice(criaturas_no_cemiterio)
            lancador.cemiterio.remove(criatura_para_revivir)
            resistencia_original = CRIATURAS_DISPONIVEIS.get(criatura_para_revivir.nome, criatura_para_revivir.resistencia)
            criatura_para_revivir.resistencia = resistencia_original
            lancador.campo_de_batalha.append(criatura_para_revivir)
            print(f"{lancador.nome} reviveu {criatura_para_revivir.nome} do cemitério!")
        else:
            print(f"{lancador.nome} tentou reviver uma criatura, mas não há nenhuma no cemitério.")

        # O feitiço após ser lançado é consumido, será movido para o cemitério em jogar_carta
        return True

class CartaTerreno(Carta):
    """Representa uma carta de terreno."""
    def __init__(self, nome: str, descricao: str, efeito: str):
        super().__init__(nome, custo_mana=0, descricao=descricao)
        self.efeito = efeito

    def ativar_efeito(self, jogador):
        """Ativa o efeito do terreno."""
        if self.efeito == "mana_extra":
            jogador.mana += 1
            print(f"{jogador.nome} ganha 1 mana extra devido ao efeito do terreno {self.nome}.")
        elif self.efeito == "cura":
            jogador.saude += 3
            print(f"{jogador.nome} recupera 3 pontos de saúde devido ao efeito do terreno {self.nome}.")

class CartaAleatoria(Carta):
    """Representa uma carta com efeito aleatório."""
    def __init__(self, nome: str, custo_mana: int, descricao: str, efeitos: List[str]):
        super().__init__(nome, custo_mana, descricao)
        self.efeitos = efeitos

    def ativar_efeito(self, jogador, alvo=None):
        """Ativa um efeito aleatório."""
        self.efeito_atual = random.choice(self.efeitos)
        print(f"{jogador.nome} ativa {self.nome} com efeito aleatório: {self.efeito_atual}.")
        if self.efeito_atual == "dano":
            if alvo:
                alvo.receber_dano(3)
        elif self.efeito_atual == "cura":
            if alvo:
                alvo.receber_dano(3)
        elif self.efeito_atual == "mana_extra":
            if alvo:
                alvo.receber_dano(3)

class Jogador:
    """Representa um jogador no jogo."""
    def __init__(self, nome: str, eh_humano: bool = True):
        self.nome = nome
        self.saude = 20
        self.mana = 0
        self.baralho: List[Carta] = []
        self.mao: List[Carta] = []
        self.campo_de_batalha: List[CartaCriatura] = []
        self.cemiterio: List[Carta] = []
        self.eh_humano = eh_humano

    def comprar_carta(self):
        """Compra uma carta do baralho."""
        if not self.baralho:
            print(f"{self.nome} não pode comprar uma carta, o baralho está vazio!")
            return None
        carta = self.baralho.pop(0)
        self.mao.append(carta)
        print(f"{self.nome} comprou uma carta.")
        return carta

    def descricao_carta_para_historico(self, carta: Carta) -> str:
        """Retorna uma descrição da carta para o histórico."""
        if isinstance(carta, CartaCriatura):
            return f"{carta.nome} (Mana: {carta.custo_mana}, Poder: {carta.poder}, Resistência: {carta.resistencia})"
        elif isinstance(carta, CartaFeitico):
            return f"{carta.nome} (Mana: {carta.custo_mana}, Tipo: {carta.tipo_magia}, Poder: {carta.poder})"
        elif isinstance(carta, CartaTerreno):
            return f"{carta.nome} (Terreno: {carta.descricao})"
        elif isinstance(carta, CartaAleatoria):
            return f"{carta.nome} (Mana: {carta.custo_mana}, Efeito: {carta.efeito_atual})"
        return carta.nome

    def jogar_carta(self, indice_carta: int, alvo=None, jogador_alvo=None, jogo=None):
        """Joga uma carta da mão."""
        if indice_carta < 0 or indice_carta >= len(self.mao):
            print("Índice de carta inválido.")
            return False
        carta = self.mao[indice_carta]
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
                    jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Jogou {self.descricao_carta_para_historico(carta)}")
                return True
            else:
                print(f"Mana insuficiente para jogar {carta.nome}.")

        if isinstance(carta, CartaTerreno):
            print(f"{self.nome} joga o terreno {carta.nome}.")
            carta.ativar_efeito(self)
            self.mao.pop(indice_carta)
            if jogo:
                jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Jogou {self.descricao_carta_para_historico(carta)}")
            return True

        if isinstance(carta, CartaAleatoria):
            print(f"{self.nome} joga {carta.nome}.")
            carta.ativar_efeito(self, jogador_alvo)
            self.mao.pop(indice_carta)
            if jogo:
                jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Jogou {self.descricao_carta_para_historico(carta)}")            
            return True

        elif isinstance(carta, CartaFeitico):
            if carta.lancar(self, alvo, jogador_alvo):
                self.cemiterio.append(self.mao.pop(indice_carta))
                print(f"{self.nome} lançou {carta.nome}.")
                if jogo:
                    jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Usou {self.descricao_carta_para_historico(carta)}")
                return True
        return False

    def atacar(self, jogador_alvo, indice_atacante: int, indice_alvo: Optional[int] = None, jogo=None):
        """Ataca o jogador alvo ou suas criaturas com uma criatura."""
        
        # Verificação do índice do atacante
        if indice_atacante < 0 or indice_atacante >= len(self.campo_de_batalha):
            print("Índice de atacante inválido.")
            return
        atacante = self.campo_de_batalha[indice_atacante]
        
        # Verifica se o atacante é uma criatura
        if isinstance(atacante, CartaCriatura):
            
            # Se o jogador alvo não tiver criaturas, ataca a saúde diretamente
            if not jogador_alvo.campo_de_batalha:
                print(f"{self.nome}'s {atacante.nome} ataca {jogador_alvo.nome} diretamente.")
                custom_sleep(1.5)
                jogador_alvo.receber_dano(atacante.poder)
                if jogo:
                    jogo.historico.append(
                        f"Rodada {jogo.turno + 1} - {self.nome}: {atacante.nome}(P:{atacante.poder},R:{atacante.resistencia}) atacou diretamente {jogador_alvo.nome}")
                return
            
            # Caso o jogador alvo tenha criaturas, verifica o índice de alvo
            if indice_alvo is None:
                print(f"{self.nome}, escolha um alvo para seu ataque!")
                return  # Se não foi fornecido um índice de alvo
            
            if indice_alvo < 0 or indice_alvo >= len(jogador_alvo.campo_de_batalha):
                print("Índice de criatura alvo inválido.")
                return
            
            # Realiza o ataque à criatura alvo
            criatura_alvo = jogador_alvo.campo_de_batalha[indice_alvo]
            # Mensagem detalhando o ataque
            print(
                f"{self.nome}'s {atacante.nome} (Poder: {atacante.poder}, Resistência: {atacante.resistencia}) \n"
                f"ataca {jogador_alvo.nome}'s {criatura_alvo.nome} (Poder: {criatura_alvo.poder}, Resistência: {criatura_alvo.resistencia}).")
            custom_sleep(1.5)
            
            # Aplica o dano à criatura escolhida
            if criatura_alvo.sofrer_dano(atacante.poder):
                jogador_alvo.campo_de_batalha.remove(criatura_alvo)
                jogador_alvo.cemiterio.append(criatura_alvo)

            if jogo:
                jogo.historico.append(
                    f"Rodada {jogo.turno + 1} - {self.nome}: {atacante.nome}(P:{atacante.poder},R:{atacante.resistencia}) atacou {criatura_alvo.nome}(P:{criatura_alvo.poder},R:{criatura_alvo.resistencia + atacante.poder})"
                )

    def receber_dano(self, quantidade: int):
        """Recebe dano."""
        self.saude -= quantidade
        print(f"{self.nome} recebe {quantidade} de dano. Saúde restante: {self.saude}")

    def mostrar_cemiterio(self):
        """Exibe todas as cartas no cemitério do jogador."""
        if not self.cemiterio:
            print(f"O cemitério de {self.nome} está vazio.")
        else:
            print(f"\n--- Cemitério de {self.nome} ---")
            for i, carta in enumerate(self.cemiterio):
                print(f"[{i}] {carta}")
            print("------------------------------")

    def escolher_acao(self, jogador_alvo: 'Jogador', jogo: 'Jogo'):
        """Escolhe uma ação para o jogador."""
        def exibir_tabuleiro():
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

        exibir_tabuleiro()

        if self.eh_humano:
            print(f"\n{self.nome}, é a sua vez!")
            while True:
                acao = input("Escolha uma ação: (1) Jogar carta, (2) Atacar com Criatura, (3) Passar a vez, (4) Histórico, (5) Mostrar cemitério, (6) Encerrar: ")

                if acao == "1":
                    if not self.mao:
                        print("Você não tem cartas na mão para jogar.")
                        continue
                    try:
                        índice_carta = int(input("Escolha o índice da carta para jogar: "))
                    except ValueError:
                        print("Índice inválido")
                        continue
                    if índice_carta < 0 or índice_carta >= len(self.mao):
                        print("Índice inválido")
                        continue
                    carta = self.mao[índice_carta]
                    alvo = None
                    
                    if isinstance(carta, CartaFeitico) and carta.tem_alvo:
                           
                        if jogador_alvo.campo_de_batalha:
                            print(f"Criaturas de {jogador_alvo.nome}:")
                            for i, criatura in enumerate(jogador_alvo.campo_de_batalha):
                                print(f"  [{i}] {criatura}")
                            try:
                                indice_alvo = int(input("Escolha o índice da criatura alvo: "))
                            except ValueError:
                                print("Índice inválido.")
                                continue
                            if indice_alvo < 0 or indice_alvo >= len(jogador_alvo.campo_de_batalha):
                                print("Índice de criatura alvo inválido.")
                                continue
                            alvo = jogador_alvo.campo_de_batalha[indice_alvo]
                        else:
                            print(f"{jogador_alvo.nome} não tem criaturas. Atacando o jogador diretamente.")
                            alvo = jogador_alvo
                        if self.jogar_carta(índice_carta, alvo, jogador_alvo, jogo):
                            break
                        else:
                            print("Tente outra ação.")
                            continue

                    elif isinstance(carta, CartaFeitico) and carta.tipo_magia == "dano_direto":
                        if self.jogar_carta(índice_carta, jogador_alvo, jogo=jogo):
                            break
                        else:
                            print("Tente outra ação")
                            continue
                    else:
                        if self.jogar_carta(índice_carta, jogador_alvo=jogador_alvo, jogo=jogo):
                            break
                        else:
                            print("Tente outra ação")
                            continue

                elif acao == "2":
                    if not self.campo_de_batalha:
                        print("Não há criaturas no seu campo de batalha para atacar. Escolha outra ação")
                        continue 
                    if not jogador_alvo.campo_de_batalha:
                        print(f"{jogador_alvo.nome} não tem criaturas no campo de batalha.")
                        print("Você pode atacar diretamente a saúde de seu oponente!")
                        try:
                            indice_atacante = int(input("Escolha o índice da sua criatura para atacar: "))
                        except ValueError:
                            print("Índice inválido.")
                            continue
                        if indice_atacante < 0 or indice_atacante >= len(self.campo_de_batalha):
                            print("Índice de criatura atacante inválido.")
                            continue
                        self.atacar(jogador_alvo, indice_atacante, jogo=jogo)  # Ataca diretamente a saúde do adversário
                        break
                    else:
                        try:
                            # Se o adversário tem criaturas, pedimos os índices
                            indice_atacante = int(input("Escolha o índice da sua criatura para atacar: "))
                            indice_alvo = int(input(f"Escolha o índice da criatura de {jogador_alvo.nome} para atacar: "))
                        except ValueError:
                            print("Índice inválido")
                            continue
                        if indice_atacante < 0 or indice_atacante >= len(self.campo_de_batalha):
                            print("Índice de criatura atacante inválido.")
                            continue
                        if indice_alvo < 0 or indice_alvo >= len(jogador_alvo.campo_de_batalha):
                            print("Índice de criatura alvo inválido.")
                            continue
                        self.atacar(jogador_alvo, indice_atacante, indice_alvo, jogo=jogo)
                        break

                elif acao == "3":
                    print("Passando a vez.")
                    jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome} passou a vez.")
                    break

                elif acao == "4":
                    # Mostra o histórico (últimas 10 ações)
                    print("\n--- HISTÓRICO DAS ÚLTIMAS AÇÕES ---")
                    for h in jogo.historico[-10:]:
                        print(h)
                    print("-----------------------------------")
                    # Não sai do turno, apenas mostra o histórico e pede outra ação.
                    continue

                elif acao == "5":
                    self.mostrar_cemiterio()

                elif acao == "6":
                    # Encerrar o jogo
                    print("Encerrando o jogo...")
                    jogo.encerrar_jogo = True
                    break
                else:
                    print("Ação inválida. Por favor escolha novamente")

        else:
            print(f"{self.nome} está escolhendo uma ação...")
            custom_sleep(1.5)

            # Se a saúde da IA estiver baixa, prioriza cura (se possível)
            if self.saude < 10:
                for i, carta in  enumerate(self.mao):
                    if carta.custo_mana <= self.mana and isinstance(carta, CartaFeitico) and carta.tipo_magia == "cura":
                        print(f"{self.nome} decidiu se curar jogando {carta.nome}")
                        custom_sleep(1.5)
                        self.jogar_carta(i, jogo=jogo)
                        return 
            
            # Se o oponente tem criaturas fortes, tenta usar dano primeiro
            if jogador_alvo.campo_de_batalha:
                for i, carta in enumerate(self.mao):
                    if carta.custo_mana <= self.mana and isinstance(carta, CartaFeitico) and (carta.tipo_magia == "dano_unico" or carta.tipo_magia == "dano_coletivo"):
                    # Escolhe o alvo mais fraco para garantir morte (se tiver alvo)
                        if carta.tem_alvo and jogador_alvo.campo_de_batalha:
                        # Escolhe a criatura com menor resistência
                            criatura_alvo = min(jogador_alvo.campo_de_batalha, key=lambda c: c.resistencia)
                            indice_alvo = jogador_alvo.campo_de_batalha.index(criatura_alvo)
                            print(f"{self.nome} usa {carta.nome} na criatura inimiga {criatura_alvo.nome}")
                            custom_sleep(1.5)
                            self.jogar_carta(i, alvo=criatura_alvo, jogador_alvo=jogador_alvo, jogo=jogo)
                        else:
                            # Se não tem alvo específico (dano_coletivo), só lança
                            print(f"{self.nome} usa {carta.nome} para danificar o campo inimigo.")
                            custom_sleep(1.5)
                            self.jogar_carta(i, jogador_alvo=jogador_alvo, jogo=jogo)
                        return
                    
             # Caso não tenha prioridades especiais, joga a primeira criatura que puder
            for i, carta in enumerate(self.mao):
                if carta.custo_mana <= self.mana and isinstance(carta, CartaCriatura):
                    print(f"{self.nome} decide invocar a criatura {carta.nome}")
                    custom_sleep(1.5)
                    self.jogar_carta(i, jogo=jogo)
                    return
            
            # Se não conseguiu jogar nada, ataca se tiver criaturas
            if self.campo_de_batalha:
                print(f"{self.nome} decide atacar.")
                custom_sleep(1.5)
                # Tenta atacar a criatura com menor resistência do oponente, senão o jogador
                if jogador_alvo.campo_de_batalha:
                    criatura_alvo = min(jogador_alvo.campo_de_batalha, key=lambda c: c.resistencia)
                    indice_alvo = jogador_alvo.campo_de_batalha.index(criatura_alvo)
                    indice_atacante = 0  # Ataca com a primeira criatura
                    self.atacar(jogador_alvo, indice_atacante, indice_alvo, jogo=jogo)
                else:
                    # Ataca diretamente o jogador
                    indice_atacante = 0
                    self.atacar(jogador_alvo, indice_atacante, jogo=jogo)

            else:
                # Se não tem criaturas no campo e não pode jogar nada
                print(f"{self.nome} não jogou cartas e nem atacou. Passando a vez...")
                jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: passou a vez")
                custom_sleep(1.5)

    def __str__(self):
        return f"Jogador {self.nome}: Saúde = {self.saude}, Mana = {self.mana}, Mão = {len(self.mao)}, Campo de Batalha = {len(self.campo_de_batalha)}"

class Jogo:
    """Representa o jogo de cartas."""
    def __init__(self, jogadores: List[Jogador]):
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
        limpar_tela()
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
    
cartas = [
    CartaCriatura("Guerreiro Esquelético", 1, "Um lutador esquelético.", 1, 1),
    CartaCriatura("Esqueleto Gigante", 5, "Um esqueleto massivo com imensa força.", 5, 5),
    CartaCriatura("Zumbi", 2, "Uma criatura morta-viva sem cérebro.", 2, 2),
    CartaCriatura("Vampiro", 4, "Uma criatura sanguinária.", 3, 4),
    CartaCriatura("Explorador Goblin", 1, "Um goblin sorrateiro.", 1, 1),
    CartaCriatura("Guerreiro Orc", 3, "Um orc forte.", 4, 3),
    CartaCriatura("Dragão Filhote", 2, "Um jovem dragão.", 2, 3),
    CartaCriatura("Elemental de Fogo", 4, "Uma criatura de fogo.", 4, 4),
    CartaCriatura("Elemental de Água", 4, "Uma criatura de água.", 3, 5),
    CartaCriatura("Golem de Pedra", 6, "Um gigante feito de pedra.", 6, 6),
    
    CartaFeitico("Bola de Fogo", 3, "Causa 3 de dano a um alvo.", "dano_unico", 3, tem_alvo=True),
    CartaFeitico("Raio", 2, "Causa 2 de dano a um alvo.", "dano_unico", 2, tem_alvo=True),
    CartaFeitico("Explosão de Gelo", 4, "Causa 4 de dano ao oponente.", "dano_direto", 4),
    CartaFeitico("Terremoto", 5, "Causa 5 de dano a todas as criaturas do oponente.", "dano_coletivo", 5, afeta_todos=True),
    CartaFeitico("Escudo", 2, "Aumenta a resistência de todas as criaturas amigas em 1.", "buff_coletivo", 1),
    CartaFeitico("Cura Menor", 1, "Restaura 2 de saúde.", "cura", 2),
    CartaFeitico("Cura Média", 3, "Restaura 5 de saúde.", "cura", 5),
    CartaFeitico("Cura Superior", 5, "Restaura 10 de saúde.", "cura", 10),

    CartaFeiticoRevive("Necromante Sombrio", 0, "Revive uma criatura aleatória do cemitério."),

    CartaTerreno("Floresta Encantada", "Um terreno que concede mana extra.", "mana_extra"),
    CartaTerreno("Fonte da Vida", "Um terreno que cura o jogador.", "cura"),

    CartaAleatoria("Caos Mágico", 3, "Ativa um efeito aleatório.", ["dano", "cura", "mana_extra"])
]

# Tabela de referência para as resistências originais das criaturas
CRIATURAS_DISPONIVEIS = {
    "Guerreiro Esquelético": 1,
    "Esqueleto Gigante": 5,
    "Zumbi": 2,
    "Vampiro": 4,
    "Explorador Goblin": 1,
    "Guerreiro Orc": 3,
    "Dragão Filhote": 3,
    "Elemental de Fogo": 4,
    "Elemental de Água": 5,
    "Golem de Pedra": 6
}


jogador1 = Jogador("Jogador", eh_humano=True)
jogador2 = Jogador("Máquina", eh_humano=False)
jogador1.baralho.extend([copy.deepcopy(carta) for carta in random.choices(cartas, k=30)])
jogador2.baralho.extend([copy.deepcopy(carta) for carta in random.choices(cartas, k=30)])

if __name__ == "__main__":
    jogo = Jogo([jogador1, jogador2])
    jogo.iniciar()

    while jogo.jogar_turno():
        pass
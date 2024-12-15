import random
import copy

from typing import List, Optional
from colorama import Fore, Style, init

init(autoreset=True)  # Inicializa o colorama para compatibilidade entre plataformas

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

    def jogar_carta(self, indice_carta: int, alvo=None, jogador_alvo=None):
        """Joga uma carta da mão."""
        if indice_carta < 0 or indice_carta >= len(self.mao):
            print("Índice de carta inválido.")
            return False
        carta = self.mao[indice_carta]
        if isinstance(carta, CartaCriatura):
            if self.mana >= carta.custo_mana:
                self.mana -= carta.custo_mana
                self.campo_de_batalha.append(carta)
                self.mao.pop(indice_carta)
                print(f"{self.nome} jogou {carta.nome}.")
                return True
            else:
                print(f"Mana insuficiente para jogar {carta.nome}.")
        elif isinstance(carta, CartaFeitico):
            if carta.lancar(self, alvo, jogador_alvo):
                self.cemiterio.append(self.mao.pop(indice_carta))
                print(f"{self.nome} lançou {carta.nome}.")
                return True
        return False

    def atacar(self, jogador_alvo, indice_atacante: int, indice_alvo: Optional[int] = None):
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
                jogador_alvo.receber_dano(atacante.poder)
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
            print(f"{self.nome}'s {atacante.nome} ataca {jogador_alvo.nome}'s {criatura_alvo.nome}.")
            
            # Aplica o dano à criatura escolhida
            if criatura_alvo.sofrer_dano(atacante.poder):
                jogador_alvo.campo_de_batalha.remove(criatura_alvo)
                jogador_alvo.cemiterio.append(criatura_alvo)

    def receber_dano(self, quantidade: int):
        """Recebe dano."""
        self.saude -= quantidade
        print(f"{self.nome} recebe {quantidade} de dano. Saúde restante: {self.saude}")

    def escolher_acao(self, jogador_alvo: 'Jogador'):
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
                if jogador == self:
                    print("Mão:")
                    for i, carta in enumerate(jogador.mao):
                        print(f"  [{i}] {carta}")
                else:
                    print(f"Mão: {len(jogador.mao)} cartas escondidas")
                print("----------------------")

        exibir_tabuleiro()

        if self.eh_humano:
            print(f"\n{self.nome}, é a sua vez!")
            acao = input("Escolha uma ação: (1) Jogar carta, (2) Atacar, (3) Passar a vez: ")

            if acao == "1":
                índice_carta = int(input("Escolha o índice da carta para jogar: "))
                carta = self.mao[índice_carta]
                if isinstance(carta, CartaFeitico) and carta.tem_alvo:
                    if jogador_alvo.campo_de_batalha:
                        print(f"Criaturas de {jogador_alvo.nome}:")
                        for i, criatura in enumerate(jogador_alvo.campo_de_batalha):
                            print(f"  [{i}] {criatura}")
                        índice_alvo = int(input("Escolha o índice da criatura alvo: "))
                        alvo = jogador_alvo.campo_de_batalha[índice_alvo]
                    else:
                        print(f"{jogador_alvo.nome} não tem criaturas. Atacando o jogador diretamente.")
                        alvo = jogador_alvo
                    self.jogar_carta(índice_carta, alvo, jogador_alvo)
                elif carta.tipo_magia == "dano_direto":
                    self.jogar_carta(índice_carta, jogador_alvo)
                else:
                    self.jogar_carta(índice_carta, jogador_alvo=jogador_alvo)

            elif acao == "2":
                if not self.campo_de_batalha:
                    print("Não há criaturas no seu campo de batalha para atacar.")
                    return
                if not jogador_alvo.campo_de_batalha:
                    print(f"{jogador_alvo.nome} não tem criaturas no campo de batalha.")
                    print("Você pode atacar diretamente a saúde de seu oponente!")

                    indice_atacante = int(input("Escolha o índice da sua criatura para atacar: "))
                    self.atacar(jogador_alvo, indice_atacante)  # Ataca diretamente a saúde do adversário
                else:
                    # Se o adversário tem criaturas, pedimos os índices
                    indice_atacante = int(input("Escolha o índice da sua criatura para atacar: "))
                    # Solicita ao jogador qual criatura do oponente ele quer atacar
                    indice_alvo = int(input(f"Escolha o índice da criatura de {jogador_alvo.nome} para atacar: "))
                    self.atacar(jogador_alvo, indice_atacante, indice_alvo)

            elif acao == "3":
                print("Passando a vez.")
            else:
                print("Ação inválida.")
        else:
            print(f"{self.nome} está escolhendo uma ação...")
            # Jogar uma carta se possível
            for i, carta in enumerate(self.mao):
                if carta.custo_mana <= self.mana:
                    self.jogar_carta(i)
                    return

            # Atacar se houver criaturas no campo de batalha
            if self.campo_de_batalha:
                indice_atacante = random.randint(0, len(self.campo_de_batalha) - 1)
                print(f"{self.nome} decide atacar.")
                if jogador_alvo.campo_de_batalha:
                    # Se o oponente tem criaturas, escolhe uma aleatória para atacar
                    indice_alvo = random.randint(0, len(jogador_alvo.campo_de_batalha) - 1)
                    self.atacar(jogador_alvo, indice_atacante, indice_alvo)
                else:
                    # Se não tiver criaturas, ataca o jogador diretamente
                    self.atacar(jogador_alvo, indice_atacante)

    def __str__(self):
        return f"Jogador {self.nome}: Saúde = {self.saude}, Mana = {self.mana}, Mão = {len(self.mao)}, Campo de Batalha = {len(self.campo_de_batalha)}"

class Jogo:
    """Representa o jogo de cartas."""
    def __init__(self, jogadores: List[Jogador]):
        self.jogadores = jogadores
        self.turno = 0

    def iniciar(self):
        """Inicia o jogo."""
        print("Iniciando o jogo!")
        for jogador in self.jogadores:
            random.shuffle(jogador.baralho)
            for _ in range(3):
                jogador.comprar_carta()

    def jogar_turno(self):
        """Joga um turno do jogo."""
        jogador_atual = self.jogadores[self.turno % len(self.jogadores)]
        print(f"\nÉ a vez de {jogador_atual.nome}!")
        jogador_atual.mana += 1
        print(f"{jogador_atual.nome} ganha 1 mana. Mana total: {jogador_atual.mana}")
        jogador_atual.comprar_carta()

        # Ação do jogador
        jogador_alvo = self.jogadores[(self.turno + 1) % len(self.jogadores)]
        jogador_atual.escolher_acao(jogador_alvo)

        # Verificar se algum jogador perdeu
        if jogador_alvo.saude <= 0:
            print(f"{jogador_alvo.nome} foi derrotado!")
            self.jogadores.remove(jogador_alvo)

        self.turno += 1
        if len(self.jogadores) == 1:
            print(f"{self.jogadores[0].nome} é o vencedor!")
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
]

jogador1 = Jogador("Jogador", eh_humano=True)
jogador2 = Jogador("Máquina", eh_humano=False)
jogador1.baralho.extend([copy.deepcopy(carta) for carta in random.choices(cartas, k=20)])
jogador2.baralho.extend([copy.deepcopy(carta) for carta in random.choices(cartas, k=20)])

jogo = Jogo([jogador1, jogador2])
jogo.iniciar()

while jogo.jogar_turno():
    pass
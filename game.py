import random
from typing import List, Optional
from colorama import Fore, Style, init

init(autoreset=True)  # Inicializa o colorama para compatibilidade entre plataformas

class Carta:
    """Representa uma carta genérica."""
    def __init__(self, nome: str, custo_mana: int, descricao: str):
        self.nome = nome
        self.custo_mana = custo_mana
        self.descricao = descricao

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
    
    def sofrer_dano(self, quantidade: int):
        """Aplica dano à criatura."""
        self.resistencia -= quantidade
        print(f"{self.nome} sofre {quantidade} de dano. Resistência restante: {self.resistencia}")
        if self.resistencia <= 0:
            print(f"{self.nome} foi destruída!")
            return True
        return False

class CartaFeitico(Carta):
    """Representa uma carta de feitico."""
    def __init__(self, nome: str, custo_mana: int, descricao: str, efeito, tem_alvo: bool = False, afeta_todos: bool = False):
        super().__init__(nome, custo_mana, descricao)
        self.efeito = efeito
        self.tem_alvo = tem_alvo
        self.afeta_todos = afeta_todos

    def lancar(self, lancador, alvo=None):
        """Lanca o feitico."""
        if lancador.mana < self.custo_mana:
            print(f"Mana insuficiente para lancar {self.nome}.")
            return False
        if self.tem_alvo and alvo is None:
            print(f"O feitico {self.nome} requer um alvo!")
            return False
        if self.afeta_todos and not hasattr(alvo, 'campo_de_batalha'):
            print(f"O feitico {self.nome} requer um oponente com criaturas no campo de batalha!")
            return False
        lancador.mana -= self.custo_mana
        self.efeito(lancador, alvo)
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
            print(f"{self.nome} nao pode comprar uma carta, o baralho está vazio!")
            return None
        carta = self.baralho.pop(0)
        self.mao.append(carta)
        print(f"{self.nome} comprou uma carta.")
        return carta

    def jogar_carta(self, índice_carta: int, alvo=None):
        """Joga uma carta da mao."""
        if índice_carta < 0 or índice_carta >= len(self.mao):
            print("Índice de carta inválido.")
            return False
        carta = self.mao[índice_carta]
        if isinstance(carta, CartaCriatura):
            if self.mana >= carta.custo_mana:
                self.mana -= carta.custo_mana
                self.campo_de_batalha.append(carta)
                self.mao.pop(índice_carta)
                print(f"{self.nome} jogou {carta.nome}.")
                return True
            else:
                print(f"Mana insuficiente para jogar {carta.nome}.")
        elif isinstance(carta, CartaFeitico):
            if carta.lancar(self, alvo):
                self.cemiterio.append(self.mao.pop(índice_carta))
                print(f"{self.nome} lancou {carta.nome}.")
                return True
        return False

    def atacar(self, jogador_alvo: 'Jogador', índice_atacante: int):
        """Ataca o jogador alvo ou suas criaturas com uma criatura."""
        if índice_atacante < 0 or índice_atacante >= len(self.campo_de_batalha):
            print("Índice de atacante inválido.")
            return
        atacante = self.campo_de_batalha[índice_atacante]
        if isinstance(atacante, CartaCriatura):
            if jogador_alvo.campo_de_batalha:
                print(f"A {self.nome}'s {atacante.nome} ataca uma criatura no campo de batalha de {jogador_alvo.nome}.")
            else:
                print(f"A {self.nome}'s {atacante.nome} ataca {jogador_alvo.nome} diretamente.")
                jogador_alvo.receber_dano(atacante.poder)

    def receber_dano(self, quantidade: int):
        """Recebe dano."""
        self.saude -= quantidade
        print(f"{self.nome} recebe {quantidade} de dano. Saude restante: {self.saude}")

    def escolher_acao(self, jogador_alvo: 'Jogador'):
        """Escolhe uma acao para o jogador."""
        def exibir_tabuleiro():
            print("\n--- TABULEIRO DO JOGO ---")
            print("\nCampo de Batalha:")
            print(f"{Fore.BLUE}{self.nome}'s Campo de Batalha:")
            for i, criatura in enumerate(self.campo_de_batalha):
                print(f"  [{i}] {Fore.BLUE}{criatura}")
            print(f"{Fore.RED}{jogador_alvo.nome}'s Campo de Batalha:")
            for i, criatura in enumerate(jogador_alvo.campo_de_batalha):
                print(f"  [{i}] {Fore.RED}{criatura}")

            print("\nInformacões dos Jogadores:")
            for jogador in [self, jogador_alvo]:
                cor = Fore.BLUE if jogador == self else Fore.RED
                print(f"{cor}{jogador.nome} - Saude: {jogador.saude}, Mana: {jogador.mana}")
                if jogador == self:
                    print("Mao:")
                    for i, carta in enumerate(jogador.mao):
                        print(f"  [{i}] {carta}")
                else:
                    print(f"Mao: {len(jogador.mao)} cartas escondidas")
                print("----------------------")

        exibir_tabuleiro()

        if self.eh_humano:
            print(f"\n{self.nome}, é a sua vez!")
            acao = input("Escolha uma acao: (1) Jogar carta, (2) Atacar, (3) Passar a vez: ")

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
                        print(f"{jogador_alvo.nome} nao tem criaturas. Atacando o jogador diretamente.")
                        alvo = jogador_alvo
                    self.jogar_carta(índice_carta, alvo)
                else:
                    self.jogar_carta(índice_carta)

            elif acao == "2":
                if not self.campo_de_batalha:
                    print("Nao há criaturas para atacar.")
                    return
                if not jogador_alvo.campo_de_batalha:
                    print(f"{jogador_alvo.nome} nao tem criaturas no campo de batalha.")
                    índice_atacante = int(input("Escolha o índice da criatura para atacar: "))
                    self.atacar(jogador_alvo, índice_atacante)
                else:
                    índice_atacante = int(input("Escolha o índice da criatura para atacar: "))
                    self.atacar(jogador_alvo, índice_atacante)

            elif acao == "3":
                print("Passando a vez.")
            else:
                print("Acao inválida.")
        else:
            print(f"{self.nome} está escolhendo uma acao...")
            # Jogar uma carta se possível
            for i, carta in enumerate(self.mao):
                if carta.custo_mana <= self.mana:
                    self.jogar_carta(i)
                    return

            # Atacar se houver criaturas no campo de batalha
            if self.campo_de_batalha:
                índice_atacante = random.randint(0, len(self.campo_de_batalha) - 1)
                print(f"{self.nome} decide atacar.")
                self.atacar(jogador_alvo, índice_atacante)

    def __str__(self):
        return f"Jogador {self.nome}: Saude = {self.saude}, Mana = {self.mana}, Mao = {len(self.mao)}, Campo de Batalha = {len(self.campo_de_batalha)}"
    
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

        # Acao do jogador
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
    CartaCriatura("Dragao Filhote", 2, "Um jovem dragao.", 2, 3),
    CartaCriatura("Elemental de Fogo", 4, "Uma criatura de fogo.", 4, 4),
    CartaCriatura("Elemental de Água", 4, "Uma criatura de água.", 3, 5),
    CartaCriatura("Golem de Pedra", 6, "Um gigante feito de pedra.", 6, 6),
    
    CartaFeitico("Cura Menor", 1, "Restaura 2 de saude.", lambda lancador, _: setattr(lancador, 'saude', lancador.saude + 2)),
    CartaFeitico("Cura Média", 3, "Restaura 5 de saude.", lambda lancador, _: setattr(lancador, 'saude', lancador.saude + 5)),
    CartaFeitico("Cura Superior", 5, "Restaura 10 de saude.", lambda lancador, _: setattr(lancador, 'saude', lancador.saude + 10)),
    CartaFeitico("Bola de Fogo", 3, "Causa 3 de dano a um alvo.", 
        lambda lancador, alvo: alvo.sofrer_dano(3) if hasattr(alvo, 'sofrer_dano') else print("Alvo inválido."), tem_alvo=True),
    CartaFeitico("Raio", 2, "Causa 2 de dano a um alvo.", 
        lambda lancador, alvo: alvo.sofrer_dano(2) if hasattr(alvo, 'sofrer_dano') else print("Alvo inválido."), tem_alvo=True),
    CartaFeitico("Explosao de Gelo", 4, "Causa 4 de dano ao oponente.",
        lambda lancador, alvo: alvo.sofrer_dano(4) if hasattr(alvo, 'sofrer_dano') else print("Alvo inválido."), tem_alvo=True),
    CartaFeitico("Terremoto", 5, "Causa 5 de dano a todas as criaturas do oponente.", 
        lambda lancador, alvo: [criatura.sofrer_dano(5) for criatura in alvo.campo_de_batalha], afeta_todos=True),
    CartaFeitico("Escudo", 2, "Aumenta a resistência de todas as criaturas amigas em 1.", 
        lambda lancador, _: [setattr(criatura, 'resistencia', criatura.resistencia + 1) for criatura in lancador.campo_de_batalha]),
]

jogador1 = Jogador("Jogador", eh_humano=True)
jogador2 = Jogador("Máquina", eh_humano=False)
jogador1.baralho.extend(random.choices(cartas, k=20))
jogador2.baralho.extend(random.choices(cartas, k=20))

jogo = Jogo([jogador1, jogador2])
jogo.iniciar()

while jogo.jogar_turno():
    pass

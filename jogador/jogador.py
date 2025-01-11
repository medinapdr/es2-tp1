from typing import List
from cartas import Carta, CartaCriatura
from .jogador_acao import JogadorAcao
from .jogador_combate import JogadorCombate
from .jogador_tabuleiro import JogadorTabuleiro

class Jogador(JogadorAcao, JogadorCombate, JogadorTabuleiro):
    """
    Classe principal do jogador que combina ações, combate e exibição do tabuleiro.
    """
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
        print(f"{self.nome} comprou a carta: {carta.nome}.")
        return carta

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

    def __str__(self):
        return (f"Jogador {self.nome}: Saúde = {self.saude}, Mana = {self.mana}, "
                f"Mão = {len(self.mao)}, Campo = {len(self.campo_de_batalha)}")

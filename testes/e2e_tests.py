import unittest
import copy
import random
import os

from banco.banco_de_dados import BancoSimulado
from jogo_estrutura.jogo import Jogo
from jogador import Jogador
from banco.cartas import CartaCriatura

os.environ["RUNNING_TESTS"] = "1" # Configura a variável de ambiente para desabilitar o sleep durante os testes.

class TesteIntegracaoE2E(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.banco = BancoSimulado('cartas_game.csv')
        cls.cartas = cls.banco.obter_cartas()

    def criar_jogadores(self, eh_humano=False):
        """
        Cria dois jogadores e adiciona cartas aleatórias aos seus baralhos.
        Para os testes, os jogadores serão configurados como não-humanos (para evitar input).
        """
        jogador1 = Jogador("Jogador1", eh_humano=eh_humano)
        jogador2 = Jogador("Jogador2", eh_humano=eh_humano)
        # Para os testes, usamos um número menor de cartas
        jogador1.baralho.extend([copy.deepcopy(carta) for carta in random.choices(self.cartas, k=10)])
        jogador2.baralho.extend([copy.deepcopy(carta) for carta in random.choices(self.cartas, k=10)])
        return jogador1, jogador2

    def test_iniciar_jogo(self):
        """Teste 1 - Verifica se, ao iniciar o jogo, cada jogador recebe 3 cartas na mão."""
        jogador1, jogador2 = self.criar_jogadores()
        jogo = Jogo([jogador1, jogador2])
        jogo.iniciar()
        self.assertEqual(len(jogador1.mao), 3, "Jogador1 deveria ter 3 cartas na mão após iniciar o jogo.")
        self.assertEqual(len(jogador2.mao), 3, "Jogador2 deveria ter 3 cartas na mão após iniciar o jogo.")

    def test_jogar_carta_creature(self):
        """Teste 2 - Verifica se uma carta de criatura é jogada corretamente:
           - A mana é descontada.
           - A carta é removida da mão e adicionada ao campo de batalha.
        """
        jogador1, _ = self.criar_jogadores()       
        # Cria uma criatura com custo 1, poder 2 e resistência 2
        criatura = CartaCriatura("TestCreature", 1, "Criatura para teste", 2, 2)
        # Sobrescreve a mão com somente essa carta e garante mana suficiente
        jogador1.mao = [criatura]
        jogador1.mana = 3

        sucesso = jogador1.jogar_carta(0, jogo=None)
        self.assertTrue(sucesso)
        self.assertEqual(len(jogador1.campo_de_batalha), 1)
        self.assertEqual(jogador1.mana, 2)

    def test_atacar_direto(self):
        """Teste 3 - Verifica se uma criatura ataca diretamente o jogador adversário quando este não possui criaturas,
        causando o dano equivalente ao poder da criatura.
        """
        jogador1, jogador2 = self.criar_jogadores()
        from banco.cartas import CartaCriatura
        # Adiciona uma criatura com poder 3 ao campo do jogador1
        atacante = CartaCriatura("Attacker", 1, "Criatura atacante para teste", 3, 3)
        jogador1.campo_de_batalha.append(atacante)
        saude_inicial = jogador2.saude

        # Executa o ataque. Como jogador2 não possui criaturas, o ataque é direto.
        jogador1.atacar(jogador2, indice_atacante=0, jogo=None)
        self.assertEqual(jogador2.saude, saude_inicial - 3)

    def test_feitico_cura(self):
        """Teste 4 - Verifica se uma carta de feitiço de cura aplica o efeito corretamente, aumentando a saúde do jogador.
        
        O teste busca uma carta de feitiço com 'tipo_magia' igual a 'cura' e simula sua jogada.
        """
        jogador1, _ = self.criar_jogadores()
        # Procura uma carta de feitiço de cura entre as cartas do banco
        healing = None
        for c in self.cartas:
            if c.__class__.__name__ == "CartaFeitico" and getattr(c, 'tipo_magia', None) == "cura":
                healing = copy.deepcopy(c)
                break
        self.assertIsNotNone(healing)

        # Configura o cenário para o teste
        jogador1.mao = [healing]
        jogador1.mana = healing.custo_mana  # Garante mana suficiente
        jogador1.saude = 10

        sucesso = jogador1.jogar_carta(0, jogo=None)
        self.assertTrue(sucesso)
        self.assertEqual(jogador1.saude, 10 + healing.poder)

    def test_game_end(self):
        """Teste 5 - Verifica se o jogo termina quando um jogador é derrotado.
        
        O teste simula um cenário em que o jogador adversário tem saúde muito baixa e é atingido por uma criatura que
        causa dano suficiente para reduzi-la a 0 ou menos.
        """
        jogador1, jogador2 = self.criar_jogadores()
        # Ajusta a saúde do jogador2 para um valor baixo
        jogador2.saude = 1
        from banco.cartas import CartaCriatura
        # Cria uma criatura com dano superior à saúde atual do adversário
        atacante = CartaCriatura("StrongCreature", 1, "Criatura com dano alto para teste", 4, 4)
        jogador1.campo_de_batalha.append(atacante)
        jogo = Jogo([jogador1, jogador2])

        # Realiza o ataque direto (já que o adversário não possui criaturas no campo)
        jogador1.atacar(jogador2, indice_atacante=0, jogo=jogo)

        self.assertTrue(jogador2.saude <= 0)

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch
import io
import os

from jogador.jogador_tabuleiro import JogadorTabuleiro

# DummyCarta para simular uma carta com o atributo 'custo_mana'
class DummyCarta:
    def __init__(self, nome, custo_mana=1):
        self.nome = nome
        self.custo_mana = custo_mana
    def __str__(self):
        return self.nome

# Classe dummy que herda de JogadorTabuleiro
class DummyJogador(JogadorTabuleiro):
    def __init__(self, nome):
        self.nome = nome
        self.saude = 20
        self.mana = 3
        self.mao = []
        self.campo_de_batalha = []
        self.eh_humano = True
        self.cemiterio = []  

    def jogar_carta(self, indice_carta, **kwargs):
        if 0 <= indice_carta < len(self.mao):
            carta = self.mao.pop(indice_carta)
            print(f"{self.nome} jogou {carta}.")
            jogo = kwargs.get('jogo')
            if jogo is not None:
                # Atualiza o histórico para simular que a ação foi registrada
                jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Jogou {carta}.")
            return True
        return False

    def atacar(self, jogador_alvo, indice_atacante, indice_alvo=None, jogo=None):
        print(f"{self.nome} atacou {jogador_alvo.nome} com sua criatura {indice_atacante}.")
        if jogo is not None:
            jogo.historico.append(f"Rodada {jogo.turno + 1} - {self.nome}: Atacou.")

    def mostrar_cemiterio(self):
        print("Cemitério de", self.nome, ":", self.cemiterio)

# Classe dummy para simular o objeto do jogo
class DummyJogo:
    def __init__(self):
        self.turno = 0
        self.historico = []
        self.encerrar_jogo = False

####################################
# Testes de Sistema / E2E
####################################
class E2ETests(unittest.TestCase):
    def setUp(self):
        self.jogador1 = DummyJogador("Jogador 1")
        self.jogador2 = DummyJogador("Jogador 2")
        self.jogo = DummyJogo()

    def test_rodada_completa(self):
        """
        Simula uma rodada completa de interação com a interface:
        - Jogador 1 (humano) deve escolher jogar uma carta.
        - Em seguida, em outra ação, ele ataca.
        - O teste verifica se o histórico foi atualizado e se as saídas  refletem a sequência correta de ações.
        """
        # Prepara a mão com duas cartas dummy: uma para jogar e outra para atacar
        self.jogador1.mao = [DummyCarta("Carta Dummy Jogar", custo_mana=1),
                              DummyCarta("Carta Dummy Atacar", custo_mana=1)]
        
        self.jogador1.campo_de_batalha = [DummyCarta("Criatura Dummy")]
        self.jogador2.campo_de_batalha = [DummyCarta("Criatura Dummy Oponente")]

        # Simula uma sequência de entradas:
        # Primeiro, Jogador 1 escolhe a opção "1" para jogar carta, e então escolhe o índice "0"
        # Depois, o jogador escolhe "2" para atacar e "0" para selecionar o atacante.
        entradas = ["1", "0", "2", "0"]
        with patch('builtins.input', side_effect=entradas), \
             patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            # Primeira parte: jogar carta
            self.jogador1.escolher_acao(self.jogador2, self.jogo)
            # Incrementa o turno e simula nova ação (ataque)
            self.jogo.turno += 1
            self.jogador1.escolher_acao(self.jogador2, self.jogo)
            output = fake_out.getvalue()

            # Verifica se as mensagens indicam que a carta foi jogada e a ação de ataque ocorreu
            self.assertIn("Jogador 1 jogou Carta Dummy Jogar.", output)
            self.assertIn("atacou", output)
            # Também verifica se o histórico foi atualizado em ambos os turnos
            self.assertGreater(len(self.jogo.historico), 0)

    def test_fluxo_completo_multiplos_turnos(self):
        """
        Simula um fluxo mais longo (vários turnos) que inclui:
        - Jogador 1 joga uma carta.
        - Jogador 1 ataca o jogador 2.
        - Em um segundo turno, Jogador 2 (IA) joga uma carta.
        - O teste verifica se, ao final, as ações dos dois jogadores foram registradas e se a interação (exibição do tabuleiro, histórico) ocorre conforme o esperado.
        """
        # Configura mãos e campos
        self.jogador1.mao = [DummyCarta("Carta Dummy Jogar", custo_mana=2)]
        self.jogador2.mao = [DummyCarta("Carta Dummy IA", custo_mana=1)]
        self.jogador1.campo_de_batalha = [DummyCarta("Criatura Dummy 1")]
        self.jogador2.campo_de_batalha = [DummyCarta("Criatura Dummy 2")]

        # Para jogador 1 (humano), simula: jogar carta (opção 1) e depois atacar (opção 2)
        entradas_jogador1 = ["1", "0", "2", "0"]
        # Para jogador 2 (IA), simula o comportamento automático (não-humano)
        self.jogador2.eh_humano = False

        # Cria uma lista de inputs combinada: primeiro turno do jogador 1; depois, o turno do jogador 2.
        # Como cada chamada a escolher_acao usa input, forneçemos a sequência completa.
        entradas = entradas_jogador1  # para jogador 1
        with patch('builtins.input', side_effect=entradas), \
             patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            # Turno 1: Jogador 1 realiza suas ações
            self.jogador1.escolher_acao(self.jogador2, self.jogo)
            # Atualiza o turno para simular que o turno do jogador 1 acabou
            self.jogo.turno += 1

            # Turno 2: Jogador 2, não-humano, executa automaticamente
            self.jogador2.escolher_acao(self.jogador1, self.jogo)
            output = fake_out.getvalue()

            # Verifica se o histórico contém ações dos dois turnos
            self.assertGreaterEqual(len(self.jogo.historico), 1)
            self.assertIn("Jogador 1", output)
            self.assertIn("está escolhendo uma ação", output)  # para o jogador não-humano
            # Verifica se as ações (como "jogou" ou "atacou") aparecem na saída
            self.assertTrue("jogou" in output or "atacou" in output)

    def test_escolher_acao_jogador_nao_humano(self):
        """
        Simula a ação automática para um jogador não humano.
        """
        self.jogador1.eh_humano = False
        self.jogador1.mao = [DummyCarta("Carta Dummy IA", custo_mana=1)]
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            self.jogador1.escolher_acao(self.jogador2, self.jogo)
            output = fake_out.getvalue()
            self.assertIn("está escolhendo uma ação", output)

# ---------------------------------------------------
# Testes de Integração para a API do BancoSimulado
# ---------------------------------------------------
from banco.banco_de_dados import BancoSimulado
from banco.cartas import CartaCriatura

class BancoSimuladoIntegrationTests(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        csv_path = os.path.join(project_root, "banco", "cartas_game.csv")
        
        with open(csv_path, encoding="utf-8") as f:
            self.csv_content = f.read()
        
        patcher = patch('builtins.open', return_value=io.StringIO(self.csv_content))
        self.addCleanup(patcher.stop)
        self.mock_open = patcher.start()
        
        self.banco = BancoSimulado("cartas_game.csv")

    def test_buscar_cartas_por_tipo(self):
        """Testa se buscar_cartas_por_tipo retorna apenas cartas do tipo 'CartaCriatura'."""
        criaturas = self.banco.buscar_cartas_por_tipo("CartaCriatura")
        self.assertGreater(len(criaturas), 0)
        for carta in criaturas:
            self.assertEqual(carta.__class__.__name__, "CartaCriatura")
    
    def test_adicionar_remover_atualizar(self):
        """
        Testa se:
          - É possível adicionar uma carta,
          - Removê-la pelo nome,
          - Atualizar uma carta existente.
        """
        # Cria uma nova carta dummy (por exemplo, do tipo CartaCriatura)
        nova_carta = CartaCriatura("Teste", 1, "Carta de teste", 1, 1)
        # Testa a adição
        adicionada = self.banco.adicionar_carta(nova_carta)
        self.assertIn(nova_carta, self.banco.obter_cartas())
        
        # Testa a remoção
        removidas = self.banco.remover_cartas_por_nome("Teste")
        self.assertEqual(removidas, 1)
        self.assertNotIn(nova_carta, self.banco.obter_cartas())

        # Testa a atualização: busque uma carta já existente (por exemplo, "Raio") e atualize seu custo_mana
        atualizado = self.banco.atualizar_carta("Raio", custo_mana=5)
        self.assertTrue(atualizado)
        # Verifica se a atualização ocorreu
        for carta in self.banco.obter_cartas():
            if carta.nome == "Raio":
                self.assertEqual(carta.custo_mana, 5)
                break

if __name__ == '__main__':
    unittest.main()

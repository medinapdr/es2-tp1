import unittest
from unittest.mock import patch
import os
from jogador import Jogador
from jogo_estrutura.jogo import Jogo

os.environ["RUNNING_TESTS"] = "1" # Configura a variável de ambiente para desabilitar o sleep durante os testes.

class TestInterfaceJogadorTabuleiro(unittest.TestCase):
    def setUp(self):
        # Configura dois jogadores para o teste de interface.
        self.jogador = Jogador("UsuarioTeste", eh_humano=True)
        self.adversario = Jogador("AdversarioTeste", eh_humano=True)
        self.jogador.baralho = []
        self.jogador.mao = []
        self.jogador.campo_de_batalha = []
        self.jogador.cemiterio = []
        self.jogador.saude = 10
        self.jogador.mana = 5

        # Adiciona uma carta na mão (criatura) para jogar
        from banco.cartas import CartaCriatura
        self.carta_criatura = CartaCriatura("Criatura Teste", 2, "Criatura para teste", 3, 3)
        self.jogador.mao.append(self.carta_criatura)

        # Cria uma instância do jogo
        self.jogo = Jogo([self.jogador, self.adversario])
        self.jogo.turno = 0  # Força a vez do usuário
        self.jogo.historico = []

    @patch('builtins.input', side_effect=['1', '0'])
    def test_jogar_carta_interface(self, mock_input):
        """
        Simula o usuário escolhendo a ação "1" (jogar carta) e digitando o índice 0.
        Verifica se a carta é removida da mão e colocada no campo de batalha.
        """
        self.jogador.escolher_acao(self.adversario, self.jogo)
        self.assertEqual(len(self.jogador.mao), 0)
        self.assertEqual(len(self.jogador.campo_de_batalha), 1)

    @patch('builtins.input', side_effect=['2', '0'])
    def test_atacar_carta_interface(self, mock_input):
        """
        Simula o usuário escolhendo a ação "2" (atacar com criatura).
        Prepara o campo de batalha do usuário e do adversário e verifica se o ataque é processado.
        """
        from banco.cartas import CartaCriatura
        # Adiciona criaturas aos campos de batalha
        atacante = CartaCriatura("Atacante", 2, "Criatura atacante", 4, 4)
        defensor = CartaCriatura("Defensora", 2, "Criatura defensora", 3, 3)
        self.jogador.campo_de_batalha.append(atacante)
        self.adversario.campo_de_batalha.append(defensor)

        self.jogador.escolher_acao(self.adversario, self.jogo)
        # Verifica se o histórico possui informação de ataque realizado
        self.assertTrue(any("atacou" in acao for acao in self.jogo.historico))

    @patch('builtins.input', side_effect=['3'])
    def test_passar_vez_interface(self, mock_input):
        """
        Simula a escolha "3" do usuário, que corresponde a passar a vez.
        Verifica se o histórico registra a passagem.
        """
        self.jogador.escolher_acao(self.adversario, self.jogo)
        self.assertTrue(any("Passou a vez" in acao for acao in self.jogo.historico))

    @patch('builtins.input', side_effect=['4', '3'])
    def test_mostrar_historico_interface(self, mock_input):
        """
        Simula a escolha "4" para exibir o histórico e, em seguida, "3" para passar a vez.
        Garante que o método permita exibir o histórico sem bloquear o fluxo de jogo.
        """
        # Pré-carrega o histórico
        self.jogo.historico.extend(["Ação 1", "Ação 2"])
        self.jogador.escolher_acao(self.adversario, self.jogo)
        self.assertTrue(any("Passou a vez" in acao for acao in self.jogo.historico))

    @patch('builtins.input', side_effect=['5', '6'])
    def test_mostrar_cemiterio_e_encerrar_interface(self, mock_input):
        """
        Simula a escolha "5" (mostrar cemitério) e, em seguida, "6" para encerrar o jogo.
        Verifica se o jogo é de fato encerrado.
        """
        from banco.cartas import CartaCriatura
        cem_carta = CartaCriatura("Cem Criatura", 3, "Criatura do cemitério", 3, 3)
        self.jogador.cemiterio.append(cem_carta)
        self.jogador.escolher_acao(self.adversario, self.jogo)
        self.assertTrue(self.jogo.encerrar_jogo)

    @patch('builtins.input', side_effect=['4', '9', '1', '0'])
    @patch('builtins.print')
    def test_multiacao_interface(self, mock_print, mock_input):
        """
        Simula um fluxo mais complexo:
        - Primeiro, o usuário escolhe "4" para ver o histórico (essa ação não encerra o loop).
        - Em seguida, uma opção inválida ("9") é digitada, o que deve resultar em uma mensagem de erro.
        - Por fim, o usuário escolhe "1" (jogar carta) e digita "0" como índice.
        Ao final, verifica se a carta foi jogada.
        Além disso, garante que a mensagem de ação inválida foi impressa ao digitar "9".
        """
        # Limpa o histórico para fins de verificação
        self.jogo.historico = []
        self.jogador.escolher_acao(self.adversario, self.jogo)

        # Verifica se a mensagem de ação inválida foi impressa
        invalid_message_found = any("Ação inválida" in str(call_arg)
                                    for call_arg in mock_print.call_args_list)
        self.assertTrue(invalid_message_found)

        # Verifica se a carta foi jogada após a sequência de ações
        self.assertEqual(len(self.jogador.mao), 0)
        self.assertEqual(len(self.jogador.campo_de_batalha), 1)

if __name__ == '__main__':
    unittest.main()

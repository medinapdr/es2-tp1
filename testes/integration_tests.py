import unittest
import os
from banco.cartas import (
    CartaCriatura,
    CartaFeitico,
    CartaFeiticoRevive,
    CartaTerreno
)
from jogador import Jogador

os.environ["RUNNING_TESTS"] = "1" # Configura a variável de ambiente para desabilitar o sleep durante os testes.

class TestIntegracaoTurnos(unittest.TestCase):
    def setUp(self):
        # Inicializa dois jogadores (não-humanos para evitar input)
        self.jogador1 = Jogador("Jogador 1", eh_humano=False)
        self.jogador2 = Jogador("Jogador 2", eh_humano=False)
        
        # Define estados iniciais, se necessário
        self.jogador1.mana = 0
        self.jogador1.saude = 20
        self.jogador2.saude = 20
        
        # Cria instâncias de cartas usadas nos testes:
        self.criatura = CartaCriatura("Zumbi", 2, "Um zumbi comum.", 2, 2)
        self.dano_direto = CartaFeitico("Raio", 2, "Causa 3 de dano no oponente.", "dano_direto", 3, True, False)
        self.terreno = CartaTerreno("Floresta Encantada", "Concede mana extra.", "mana_extra")
        self.revive = CartaFeiticoRevive("Necromante", 5, "Revive uma criatura.")

    def test_interacao_terreno_e_feitico_em_turnos_diferentes(self):
        """Testa interação entre terreno que concede mana e jogar feitiço em turnos diferentes."""
        # Primeiro turno: joga o terreno.
        self.jogador1.mao.append(self.terreno)
        self.jogador1.jogar_carta(0)
        # O efeito do terreno concede 1 de mana
        self.assertEqual(self.jogador1.mana, 1)
        
        # Segundo turno: joga o feitiço de dano direto.
        self.jogador1.mao.append(self.dano_direto)
        self.jogador1.mana = 3  # Simula o próximo turno com mana suficiente
        jogou = self.jogador1.jogar_carta(0, alvo=self.jogador2)
        self.assertTrue(jogou)
        self.assertEqual(self.jogador2.saude, 17)

    def test_criatura_e_feitico_dano_em_turnos_diferentes(self):
        """Testa jogar criatura e usar feitiço de dano em turnos diferentes."""
        # Primeiro turno: joga a criatura.
        self.jogador1.mana = 2  # Mana suficiente para jogar a criatura
        self.jogador1.mao.append(self.criatura)
        jogou_criatura = self.jogador1.jogar_carta(0)
        self.assertTrue(jogou_criatura)
        self.assertIn(self.criatura, self.jogador1.campo_de_batalha)
        
        # Segundo turno: joga o feitiço de dano.
        self.jogador1.mao.append(self.dano_direto)
        self.jogador1.mana = 3  # Simula o próximo turno com mana suficiente
        jogou_feitico = self.jogador1.jogar_carta(0, alvo=self.jogador2)
        self.assertTrue(jogou_feitico)
        self.assertEqual(self.jogador2.saude, 17)

    def test_revivendo_varias_criaturas_em_turnos(self):
        """Testa reviver várias criaturas do cemitério em turnos diferentes."""
        # Cria duas criaturas mortas
        criatura_morta1 = CartaCriatura("Morto 1", 2, "Uma criatura morta.", 2, 2)
        criatura_morta2 = CartaCriatura("Morto 2", 3, "Outra criatura morta.", 3, 3)
        # Adiciona as criaturas ao cemitério do jogador1
        self.jogador1.cemiterio.append(criatura_morta1)
        self.jogador1.cemiterio.append(criatura_morta2)
        
        # Primeiro turno: joga o feitiço de revive
        self.jogador1.mana = 5
        self.jogador1.mao.append(self.revive)
        jogou_revive = self.jogador1.jogar_carta(0)
        self.assertTrue(jogou_revive)
        self.assertTrue(
            criatura_morta1 in self.jogador1.campo_de_batalha or 
            criatura_morta2 in self.jogador1.campo_de_batalha)
        
        # Segundo turno: joga o feitiço de revive novamente
        self.jogador1.mao.append(self.revive)
        self.jogador1.mana = 5  # Simula o próximo turno com mana suficiente
        jogou_revive_segundo = self.jogador1.jogar_carta(0)
        self.assertTrue(jogou_revive_segundo)
        self.assertIn(criatura_morta1, self.jogador1.campo_de_batalha)
        self.assertIn(criatura_morta2, self.jogador1.campo_de_batalha)

    def test_efeito_terreno_e_ataque_em_turnos(self):
        """Testa efeito de terreno seguido de ataque em turnos diferentes."""
        # Primeiro turno: joga o terreno.
        self.jogador1.mao.append(self.terreno)
        self.jogador1.jogar_carta(0)
        self.assertEqual(self.jogador1.mana, 1)
        
        # Segundo turno: simula o ataque direto.
        self.jogador1.campo_de_batalha.append(self.criatura)
        self.jogador1.atacar(self.jogador2, 0)
        self.assertEqual(self.jogador2.saude, 18)

if __name__ == '__main__':
    unittest.main()

import unittest
import os
from game import CartaCriatura, CartaFeitico, CartaFeiticoRevive, CartaTerreno, CartaAleatoria, Jogador

class TestGame(unittest.TestCase):
    def setUp(self):
        os.environ["RUNNING_TESTS"] = "1"
        self.jogador1 = Jogador("Jogador 1")
        self.jogador2 = Jogador("Jogador 2")
        self.criatura = CartaCriatura("Zumbi", 2, "Um zumbi comum.", 2, 2)
        self.dano_direto = CartaFeitico("Raio", 2, "Causa 3 de dano no oponente.", "dano_direto", 3)
        self.cura = CartaFeitico("Cura Menor", 1, "Restaura 2 de saúde.", "cura", 2)
        self.revive = CartaFeiticoRevive("Necromante", 5, "Revive uma criatura.")
        self.terreno = CartaTerreno("Floresta Encantada", "Concede mana extra.", "mana_extra")
        self.aleatoria = CartaAleatoria("Caos Mágico", 3, "Efeito aleatório.", ["dano", "cura", "mana_extra"])       

    def test_comprar_carta(self):
        """Testa se o jogador pode comprar cartas corretamente."""
        self.jogador1.baralho.append(self.criatura)
        carta_comprada = self.jogador1.comprar_carta()
        self.assertEqual(carta_comprada, self.criatura)
        self.assertIn(carta_comprada, self.jogador1.mao)

    def test_jogar_carta_criatura(self):
        """Testa se o jogador pode jogar uma carta de criatura."""
        self.jogador1.mana = 3
        self.jogador1.mao.append(self.criatura)
        jogou = self.jogador1.jogar_carta(0)
        self.assertTrue(jogou)
        self.assertIn(self.criatura, self.jogador1.campo_de_batalha)

    def test_nao_jogar_carta_mana_insuficiente(self):
        """Testa se o jogador não consegue jogar cartas sem mana suficiente."""
        self.jogador1.mana = 1
        self.jogador1.mao.append(self.criatura)
        jogou = self.jogador1.jogar_carta(0)
        self.assertFalse(jogou)
        self.assertNotIn(self.criatura, self.jogador1.campo_de_batalha)

    def test_jogar_carta_feitico_dano(self):
        """Testa se um feitiço de dano é corretamente usado contra o oponente."""
        self.jogador1.mana = 3
        self.jogador1.mao.append(self.dano_direto)
        vida_inicial = self.jogador2.saude
        self.jogador1.jogar_carta(0, alvo=self.jogador2)
        self.assertEqual(self.jogador2.saude, vida_inicial - 3)

    def test_jogar_carta_feitico_cura(self):
        """Testa se um feitiço de cura funciona corretamente."""
        self.jogador1.saude = 10
        self.jogador1.mana = 2
        self.jogador1.mao.append(self.cura)
        self.jogador1.jogar_carta(0)
        self.assertEqual(self.jogador1.saude, 12)

    def test_atacar_direto(self):
        """Testa se uma criatura pode atacar diretamente o jogador oponente."""
        self.jogador1.campo_de_batalha.append(self.criatura)
        vida_inicial = self.jogador2.saude
        self.jogador1.atacar(self.jogador2, 0)
        self.assertEqual(self.jogador2.saude, vida_inicial - self.criatura.poder)

    def test_atacar_criatura(self):
        """Testa se uma criatura pode atacar outra criatura."""
        criatura_adversaria = CartaCriatura("Guerreiro", 3, "Um guerreiro forte.", 3, 3)
        self.jogador1.campo_de_batalha.append(self.criatura)
        self.jogador2.campo_de_batalha.append(criatura_adversaria)
        self.jogador1.atacar(self.jogador2, 0, 0)
        self.assertEqual(criatura_adversaria.resistencia, 1)

    def test_criatura_destruida_apos_dano(self):
        """Testa se uma criatura é destruída ao sofrer dano letal."""
        criatura_adversaria = CartaCriatura("Fraco", 1, "Uma criatura fraca.", 1, 1)
        self.jogador1.campo_de_batalha.append(self.criatura)
        self.jogador2.campo_de_batalha.append(criatura_adversaria)
        self.jogador1.atacar(self.jogador2, 0, 0)
        self.assertNotIn(criatura_adversaria, self.jogador2.campo_de_batalha)
        self.assertIn(criatura_adversaria, self.jogador2.cemiterio)
        
    def test_criatura_sofre_dano_e_permanece_viva(self):
        """Testa se a criatura continua viva após receber dano não letal."""
        self.jogador1.campo_de_batalha.append(self.criatura)
        self.criatura.sofrer_dano(1)
        self.assertEqual(self.criatura.resistencia, 1)
        self.assertIn(self.criatura, self.jogador1.campo_de_batalha)

    def test_revivendo_criatura(self):
        """Testa se uma criatura pode ser revivida do cemitério."""
        criatura_morta = CartaCriatura("Morto", 2, "Uma criatura morta.", 2, 2)
        self.jogador1.cemiterio.append(criatura_morta)
        self.jogador1.mana = 5
        self.jogador1.mao.append(self.revive)
        self.jogador1.jogar_carta(0)
        self.assertIn(criatura_morta, self.jogador1.campo_de_batalha)

    def test_nao_revivendo_sem_criaturas(self):
        """Testa se não há criaturas para reviver, nenhuma ação ocorre."""
        self.jogador1.mana = 5
        self.jogador1.mao.append(self.revive)
        jogou = self.jogador1.jogar_carta(0)
        self.assertFalse(jogou)

    def test_nao_comprar_carta_baralho_vazio(self):
        """Testa se o jogador não consegue comprar cartas com baralho vazio."""
        carta_comprada = self.jogador1.comprar_carta()
        self.assertIsNone(carta_comprada)

    def test_aumentar_resistencia_feitico(self):
        """Testa se um feitiço de buff aumenta a resistência de criaturas corretamente."""
        buff = CartaFeitico("Escudo", 2, "Aumenta resistência de todas as criaturas.", "buff_coletivo", 1)
        criatura_no_campo = CartaCriatura("Pequeno", 1, "Criatura pequena.", 1, 1)
        self.jogador1.mana = 3
        self.jogador1.mao.append(buff)
        self.jogador1.campo_de_batalha.append(criatura_no_campo)
        self.jogador1.jogar_carta(0)
        self.assertEqual(criatura_no_campo.resistencia, 2)

    def test_dano_coletivo(self):
        """Testa se dano coletivo afeta todas as criaturas inimigas."""
        terremoto = CartaFeitico("Terremoto", 5, "Dano coletivo a todas criaturas do oponente.", "dano_coletivo", 5)
        criatura1 = CartaCriatura("Criatura 1", 1, "Primeira criatura.", 1, 5)
        criatura2 = CartaCriatura("Criatura 2", 1, "Segunda criatura.", 1, 6)
        self.jogador1.mana = 5
        self.jogador1.mao.append(terremoto)
        self.jogador2.campo_de_batalha.append(criatura1)
        self.jogador2.campo_de_batalha.append(criatura2)
        self.jogador1.jogar_carta(0, jogador_alvo=self.jogador2)
        self.assertNotIn(criatura1, self.jogador2.campo_de_batalha)
        self.assertIn(criatura1, self.jogador2.cemiterio)
        self.assertEqual(criatura2.resistencia, 1)
        
    def test_jogador_perde_quando_saude_zero(self):
        """Testa se o jogador perde ao atingir 0 de saúde."""
        self.jogador1.saude = 1
        self.jogador1.receber_dano(1)
        self.assertEqual(self.jogador1.saude, 0)

    def test_interacao_terreno_e_feitico_em_turnos_diferentes(self):
        """Testa interação entre terreno que concede mana e jogar feitiço em turnos diferentes."""
        self.jogador1.mao.append(self.terreno)
        self.jogador1.jogar_carta(0)
        self.assertEqual(self.jogador1.mana, 1)
        self.jogador1.mao.append(self.dano_direto)
        self.jogador1.mana = 3  # Simula o próximo turno com mana suficiente
        jogou = self.jogador1.jogar_carta(0, alvo=self.jogador2)
        self.assertTrue(jogou)
        self.assertEqual(self.jogador2.saude, 17)

    def test_feitico_aleatorio_impacto_varios_efeitos(self):
        """Testa o impacto de um feitiço aleatório com vários efeitos."""
        self.jogador1.mana = 3
        self.jogador1.mao.append(self.aleatoria)
        vida_inicial = self.jogador1.saude
        self.jogador1.jogar_carta(0, jogador_alvo=self.jogador2)
        self.assertNotIn(self.aleatoria, self.jogador1.mao)
        self.assertTrue(
            self.jogador1.saude != vida_inicial or
            self.jogador1.mana > 3 or
            self.jogador2.saude < 20
        )

    def test_criatura_e_feitico_dano_em_turnos_diferentes(self):
        """Testa jogar criatura e usar feitiço de dano em turnos diferentes."""
        self.jogador1.mana = 2
        self.jogador1.mao.append(self.criatura)
        jogou_criatura = self.jogador1.jogar_carta(0)
        self.assertTrue(jogou_criatura)
        self.assertIn(self.criatura, self.jogador1.campo_de_batalha)
        self.jogador1.mao.append(self.dano_direto)
        self.jogador1.mana = 3  # Simula o próximo turno com mana suficiente
        jogou_feitico = self.jogador1.jogar_carta(0, alvo=self.jogador2)
        self.assertTrue(jogou_feitico)
        self.assertEqual(self.jogador2.saude, 17)

    def test_revivendo_varias_criaturas_em_turnos(self):
        """Testa reviver várias criaturas do cemitério em turnos diferentes."""
        criatura_morta1 = CartaCriatura("Morto 1", 2, "Uma criatura morta.", 2, 2)
        criatura_morta2 = CartaCriatura("Morto 2", 3, "Outra criatura morta.", 3, 3)
        self.jogador1.cemiterio.append(criatura_morta1)
        self.jogador1.cemiterio.append(criatura_morta2)
        self.jogador1.mana = 5
        self.jogador1.mao.append(self.revive)
        jogou_revive = self.jogador1.jogar_carta(0)
        self.assertTrue(jogou_revive)
        self.assertTrue(
            criatura_morta1 in self.jogador1.campo_de_batalha or 
            criatura_morta2 in self.jogador1.campo_de_batalha
        )
        self.jogador1.mao.append(self.revive)
        self.jogador1.mana = 5  # Simula o próximo turno com mana suficiente
        jogou_revive_segundo = self.jogador1.jogar_carta(0)
        self.assertTrue(jogou_revive_segundo)
        self.assertIn(criatura_morta1, self.jogador1.campo_de_batalha)
        self.assertIn(criatura_morta2, self.jogador1.campo_de_batalha)

    def test_efeito_terreno_e_ataque_em_turnos(self):
        """Testa efeito de terreno seguido de ataque em turnos diferentes."""
        self.jogador1.mao.append(self.terreno)
        self.jogador1.jogar_carta(0)
        self.assertEqual(self.jogador1.mana, 1)
        self.jogador1.campo_de_batalha.append(self.criatura)
        self.jogador1.atacar(self.jogador2, 0)
        self.assertEqual(self.jogador2.saude, 18)

if __name__ == "__main__":
    unittest.main()
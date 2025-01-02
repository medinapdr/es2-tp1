from typing import List, Optional
import random

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

    def lancar(self, lancador, criaturas_disponiveis, alvo=None, jogador_adversario=None):
        """Lança o feitiço de reviver criatura."""
        if lancador.mana < self.custo_mana:
            print(f"Mana insuficiente para lançar {self.nome}.")
            return False
        lancador.mana -= self.custo_mana
        criaturas_no_cemiterio = [c for c in lancador.cemiterio if isinstance(c, CartaCriatura)]
        if criaturas_no_cemiterio:
            criatura_para_revivir = random.choice(criaturas_no_cemiterio)
            lancador.cemiterio.remove(criatura_para_revivir)
            resistencia_original = criaturas_disponiveis.get(criatura_para_revivir.nome, criatura_para_revivir.resistencia)
            criatura_para_revivir.resistencia = resistencia_original
            lancador.campo_de_batalha.append(criatura_para_revivir)
            print(f"{lancador.nome} reviveu {criatura_para_revivir.nome} do cemitério!")
        else:
            print(f"{lancador.nome} tentou reviver uma criatura, mas não há nenhuma no cemitério.")

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
            jogador.saude += 3
        elif self.efeito_atual == "mana_extra":
            jogador.mana += 1
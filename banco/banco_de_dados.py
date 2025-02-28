import csv
import os
from banco.cartas import CartaAleatoria, CartaCriatura, CartaFeitico, CartaFeiticoRevive, CartaTerreno

class BancoSimulado:
    def __init__(self, arquivo_csv):
        self.arquivo_csv = arquivo_csv
        self.cartas = self.carregar_cartas()

    def carregar_cartas(self):
        cartas = []
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_path, self.arquivo_csv)
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['tipo'] == 'CartaCriatura':
                    cartas.append(CartaCriatura(row['nome'], int(row['custo_mana']), row['descricao'], int(row['poder']), int(row['resistencia'])))
                elif row['tipo'] == 'CartaFeitico':
                    cartas.append(CartaFeitico(row['nome'], int(row['custo_mana']), row['descricao'], row['tipo_magia'], int(row['poder']), row['tem_alvo'] == 'True', row['afeta_todos'] == 'True'))
                elif row['tipo'] == 'CartaFeiticoRevive':
                    cartas.append(CartaFeiticoRevive(row['nome'], int(row['custo_mana']), row['descricao']))
                elif row['tipo'] == 'CartaTerreno':
                    cartas.append(CartaTerreno(row['nome'], row['descricao'], row['tipo_magia']))
                elif row['tipo'] == 'CartaAleatoria':
                    cartas.append(CartaAleatoria(row['nome'], int(row['custo_mana']), row['descricao'], row['efeitos'].split(';')))
        return cartas

    def obter_cartas(self):
        return self.cartas
    
    def adicionar_carta(self, carta):
        """Adiciona uma carta à coleção e retorna-a."""
        self.cartas.append(carta)
        return carta

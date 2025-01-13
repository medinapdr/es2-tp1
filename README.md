# README

## 1. Membros do Grupo
- Pedro Medina
- Marco Machado

## 2. Explicação do Sistema

### Visão Geral
Este projeto implementa um jogo de cartas estratégico para dois jogadores: um jogador humano e uma IA (Máquina). Os jogadores competem utilizando um baralho de cartas contendo criaturas e feitiços, com o objetivo de reduzir a saúde do adversário a zero.

### Mecânica de Jogo

#### Componentes Principais
- **Cartas**: Existem dois tipos principais de cartas:
  - **Criaturas**: Possuem atributos de poder (dano que causam) e resistência (dano que suportam).
  - **Feitiços**: Podem causar dano, curar, reviver criaturas ou fornecer buffs às criaturas aliadas.
  - **Terrenos**: Fornecem efeitos especiais como mana aumento de resistência de criatura(s).
  - **Aleatórias**: Ativam efeitos aleatórios como dano, cura ou mana extra.
- **Jogadores**: Cada jogador possui um baralho de 30 cartas, uma mão para cartas compradas, um campo de batalha para criaturas invocadas, e um cemitério para cartas descartadas ou destruídas.

#### Regras do Jogo
1. Cada jogador começa com 20 pontos de saúde e 0 de mana.
2. A cada turno, o jogador ganha 1 ponto de mana e compra uma carta.
3. Os jogadores podem:
   - Invocar criaturas para o campo de batalha (se tiverem mana suficiente).
   - Usar feitiços para atacar diretamente o adversário, suas criaturas ou ajudar aliados.
   - Atacar com criaturas invocadas.
4. Criaturas podem atacar diretamente o adversário ou combater criaturas inimigas no campo de batalha.
5. O jogo termina quando a saúde de um dos jogadores chega a zero ou quando o adversário não possui mais cartas.

### Fluxo de Jogo
1. **Início**: Cada jogador embaralha seu baralho e compra 3 cartas.
2. **Turnos Alternados**:
   - Ganhar mana e comprar uma carta.
   - Realizar ações (invocar cartas, usar feitiços, atacar, ou passar a vez).
3. **Condições de Vitória**:
   - Derrotar o adversário reduzindo sua saúde a zero.

#### IA (Inteligência Artificial)
A IA avalia o estado do jogo e toma decisões com base em regras básicas:
- Prioriza cura se a saúde estiver baixa.
- Usa feitiços para lidar com ameaças no campo de batalha.
- Invoca criaturas ou ataca diretamente caso não tenha outras prioridades.

## 3. Tecnologias Utilizadas

### Linguagem e Bibliotecas
- **Python 3**: Linguagem principal do projeto.
- **Colorama**: Para exibição de cores no terminal, melhorando a interface visual do jogo.
- **Random**: Para aleatoriedade na escolha de cartas e comportamentos.
- **Copy**: Para duplicação de objetos de cartas sem alterar o original.
- **Time**: Para criar pausas e melhorar a experiência visual.

### Estrutura do Código
- **Classes**:
  - `Carta`: Classe base para todos os tipos de cartas.
  - `CartaCriatura`, `CartaFeitico`, `CartaFeiticoRevive`, `CartaTerreno`, `CartaAleatoria`: Especializações de cartas com funcionalidades específicas.
  - `Jogador`: Gerencia ações e estado do jogador.
  - `Jogo`: Controla o fluxo do jogo e as regras.
  - `BancoSimulado`: Carrega e gerencia as cartas do banco de dados.

### Ambiente de Execução
- Sistema compatível com Windows, MacOS e Linux.
- Terminal interativo para entrada e saída de informações.

## 4. Testes

### Estrutura de Testes
- **Testes Unitários**: Verificam funcionalidades individuais das classes e métodos.
- **Testes de Integração**: Validam a interação entre diferentes componentes do jogo.
- **Testes de Sistema (E2E)**: Simulam a interação do usuário à partir da interface com diversas ações presentes no jogo.

### Execução dos Testes
Os testes são executados automaticamente utilizando GitHub Actions. Para rodar os testes localmente, utilize os seguintes comandos:
```sh
python -m unittest testes.unit_tests
python -m unittest testes.e2e_tests
python -m unittest testes.integration_tests
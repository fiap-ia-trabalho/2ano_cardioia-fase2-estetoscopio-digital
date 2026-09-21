# CardioIA — Fase 2: Diagnóstico Automatizado (IA no Estetoscópio Digital)

Módulo de apoio ao diagnóstico que lê relatos de sintomas escritos por pacientes,
identifica os sintomas mencionados, sugere um diagnóstico a partir de um mapa de
conhecimento e classifica o nível de risco com um modelo de Machine Learning.

Projeto acadêmico — FIAP, 2º ano de Inteligência Artificial.

> **Aviso:** este repositório é um exercício de faculdade. A base é sintética, os rótulos
> foram atribuídos por estudantes e nenhum conteúdo foi validado clinicamente. Nada aqui
> deve ser usado para decisão médica.

---

## Grupo

| Integrante | RM |
|---|---|
| Cauan Otto Rodrigues Sousa | RM567940 |
| Fernando A. Gurgel | RM567606 |
| Iraci Monteiro Souza | RM567544 |
| Maria Luisa Rodrigues Nascimento | RM567659 |
| Rafaela Torres Martins | RM567735 |

**Tutor:** Leonardo Ruiz Orabona · **Coordenador:** André Godoi

## Estrutura do repositório

```
2ano_cardioia-fase2-estetoscopio-digital/

├── dados/
│   ├── frases_pacientes.txt          # Parte 1 — 10 relatos de pacientes
│   ├── mapa_conhecimento.csv         # Parte 1 — 48 linhas sintoma → doença
│   ├── resultado_extracao.csv        # Parte 1 — saída da execução
│   ├── frases_risco.csv              # Parte 2 — 80 frases rotuladas
│   └── resultado_classificador.csv   # Parte 2 — métricas dos modelos

## Parte 1 — Extração de sintomas e sugestão de diagnóstico

**Entrada:** 10 relatos em `dados/frases_pacientes.txt`, cada um com o que o paciente
sente, quando começou e como afeta a rotina. Três relatos foram escritos sem acentuação
e um parcialmente em caixa alta, de propósito, para testar a normalização.

**Mapa de conhecimento:** 48 linhas em `dados/mapa_conhecimento.csv` (96 expressões,
duas por linha), cobrindo 7
condições — Infarto Agudo do Miocárdio, Angina, Insuficiência Cardíaca, Arritmia,
Hipertensão Arterial, Pericardite e Acidente Vascular Cerebral.

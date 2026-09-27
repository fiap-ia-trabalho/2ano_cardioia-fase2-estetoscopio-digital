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

---

## Vídeo de demonstração

▶️ **[SUBSTITUIR POR: link do YouTube não listado]**

> Este é o único campo do repositório que ainda precisa ser preenchido à mão. O vídeo
> tem até 4 minutos e deve ser publicado como **não listado**. O roteiro cronometrado
> está em [`docs/roteiro_video.md`](docs/roteiro_video.md).

---

## Continuidade com a Fase 1

Fase 1 — *Batimentos de Dados*:
https://github.com/fiap-ia-trabalho/2ano_cardioia-fase1-batimentos-de-dados

O que foi reaproveitado, e como:

- **Corpus textual.** O vocabulário de sintomas do mapa de conhecimento foi construído a
  partir dos dois textos do SciELO entregues na Fase 1. A coluna `origem` do
  `mapa_conhecimento.csv` registra, termo a termo, se ele vem de
  `texto_02_sindrome_coronariana_scielo`, de `texto_01_hipertensao_scielo` ou de
  `conhecimento_geral_equipe`.
- **Base numérica.** O `cardio_train_amostra_100` **não** foi usado nesta fase. Ele contém
  variáveis clínicas tabulares (pressão, colesterol, IMC), não texto, e não alimenta um
  modelo de NLP. Registramos isso em vez de forçar um uso artificial.
- **Base de imagens.** Não se aplica à Fase 2, que é inteiramente textual.

### Controle de vazamento entre treino e teste

Quando uma base contém amostras derivadas da mesma origem, dividir treino e teste ao
acaso faz com que variações de um mesmo caso caiam dos dois lados. O modelo passa a ser
avaliado em algo que ele praticamente já viu, e a acurácia sobe sem que ele tenha
melhorado.

A base rotulada desta fase tem uma coluna `grupo_semantico`: frases que são variações da
mesma ideia clínica pertencem ao mesmo grupo, e a divisão treino/teste é feita **por
grupo**, nunca por frase.

Medimos o efeito. Rodando a mesma validação cruzada das duas formas:

| divisão | acurácia média |
|---|---|
| por grupo (correta) | 77,5% |
| por frase (com vazamento) | 83,8% |
| **inflação causada pelo vazamento** | **+6,2 pontos percentuais** |

---

## Estrutura do repositório

```
2ano_cardioia-fase2-estetoscopio-digital/
├── README.md
├── requirements.txt
├── dados/
│   ├── frases_pacientes.txt          # Parte 1 — 10 relatos de pacientes
│   ├── mapa_conhecimento.csv         # Parte 1 — 48 linhas sintoma → doença
│   ├── resultado_extracao.csv        # Parte 1 — saída da execução
│   ├── frases_risco.csv              # Parte 2 — 80 frases rotuladas
│   └── resultado_classificador.csv   # Parte 2 — métricas dos modelos
├── src/
│   └── extracao_sintomas.py          # Parte 1 — lógica de extração
├── notebooks/
│   ├── 01_extracao_sintomas.ipynb    # Parte 1 — comentado, já executado
│   └── 02_classificador_risco.ipynb  # Parte 2 — comentado, já executado
└── docs/
    ├── GOVERNANCA_FASE2.md           # proveniência, vieses, limitações
    └── roteiro_video.md              # roteiro cronometrado de 4 min
```

Os dois notebooks estão salvos **com as saídas**. Dá para ler o resultado sem executar.

---

## Como executar

Requer Python 3.9 ou superior.

```bash
git clone https://github.com/fiap-ia-trabalho/2ano_cardioia-fase2-estetoscopio-digital.git
cd 2ano_cardioia-fase2-estetoscopio-digital
pip install -r requirements.txt
```

Parte 1 pela linha de comando:

```bash
python src/extracao_sintomas.py
```

Ou abrir os notebooks:

```bash
jupyter notebook notebooks/
```

Dependências: apenas `pandas` e `scikit-learn`. O restante é biblioteca padrão do Python.
A matriz de confusão é apresentada como tabela do pandas, não como gráfico, para manter
essa restrição.

---

## Parte 1 — Extração de sintomas e sugestão de diagnóstico

**Entrada:** 10 relatos em `dados/frases_pacientes.txt`, cada um com o que o paciente
sente, quando começou e como afeta a rotina. Três relatos foram escritos sem acentuação
e um parcialmente em caixa alta, de propósito, para testar a normalização.

**Mapa de conhecimento:** 48 linhas em `dados/mapa_conhecimento.csv` (96 expressões,
duas por linha), cobrindo 7
condições — Infarto Agudo do Miocárdio, Angina, Insuficiência Cardíaca, Arritmia,
Hipertensão Arterial, Pericardite e Acidente Vascular Cerebral.

Colunas: `sintoma_1 | sintoma_2 | doenca_associada | peso | origem`.

As duas últimas vão além do que o enunciado pedia:

- **`peso`** (1 a 3) — sem ele, "dor no peito" e "irradiou para o braço esquerdo" valem o
  mesmo, e o sistema não separa infarto de qualquer desconforto torácico.
- **`origem`** — rastreabilidade: permite distinguir o que tem respaldo nas fontes
  científicas do que é síntese da equipe.

**Como funciona o código:**

1. **Normalização** (`NFKD` + remoção de acentos + minúsculas + limpeza de pontuação),
   aplicada dos dois lados da comparação. É o que faz `coracao`, `coração` e `CORAÇÃO`
   virarem o mesmo termo.
2. **Busca por trecho** de cada expressão do mapa dentro do relato normalizado.
3. **Regra anti-contagem-dupla:** quando um termo longo casa com um trecho, aquele trecho
   fica ocupado, e um termo curto contido nele é descartado. Sem isso, em
   *"falta de ar quando deito"* o sistema somaria também `falta de ar` e inflaria a
   própria confiança sem evidência nova.
4. **Soma dos pesos por doença.** Vence a mais pontuada. Se nada casar, ou se houver
   empate, a saída é *"Inconclusivo — encaminhar para avaliação humana"*, nunca um chute.

**Resultado:** os 10 relatos recebem o diagnóstico pretendido. Isso prova pouco, porque
as frases e o mapa foram escritos pela mesma equipe — é circular. O teste que vale está
na seção 8 do notebook, com frases que não participaram da construção do mapa. Lá o
sistema acerta duas, devolve inconclusivo corretamente em duas e **falha em uma**.

### Falha documentada

A frase *"Meu coracao fica acelerado e sinto falta de ar quando subo a escada"* não casou
com o termo `coração acelerado`, porque a palavra "fica" está no meio e a busca por
trecho exige as palavras coladas. O sinal de arritmia se perdeu e o sistema respondeu
Angina com 60% de confiança.

Não é erro de digitação: é o limite do método. Está registrado no notebook em vez de
corrigido com uma frase de teste mais conveniente.

---

## Parte 2 — Classificador de risco

**Base:** `dados/frases_risco.csv` — 80 frases (40 alto risco, 40 baixo risco) em 40
grupos semânticos. Colunas: `frase | situacao | grupo_semantico`.

A base foi construída com **sobreposição de vocabulário entre as classes**, de propósito.
Se "peito" só aparecesse em alto risco, o classificador seria um `Ctrl+F` e a acurácia
alta não significaria nada:

| termo | alto risco | baixo risco |
|---|---|---|
| peito | 14 | 6 |
| coração | 3 | 4 |
| falta de ar | 2 | 1 |
| inchado | 1 | 1 |
| dor de cabeça | 1 | 1 |

A distinção depende do contexto — esforço, duração, se alivia — e não da palavra isolada.

**Pipeline:** TF-IDF (unigramas e bigramas, com a mesma normalização da Parte 1) →
classificador. O TF-IDF fica dentro de um `Pipeline` do scikit-learn para ser ajustado
apenas com os dados de treino de cada divisão; ajustá-lo na base inteira antes de dividir
vazaria o vocabulário do teste.

### Resultados

| modelo | split único | validação cruzada (5 folds, por grupo) |
|---|---|---|
| Regressão Logística | 90,0% | **77,5% ± 5,0%** |
| Árvore de Decisão | 70,0% | 63,7% ± 8,3% |
| Baseline por palavra-chave | 60,0% | — |

**O número de referência é 77,5%, não 90%.** O split único usa 20 frases de teste; trocar
a semente aleatória muda o resultado em vários pontos. O baseline burro — chutar alto
risco se a frase contém "peito", "coração", "falta de ar" ou "braço" — acerta 60%, então
o ganho real do modelo treinado é de cerca de 17 pontos.

**Matriz de confusão (Regressão Logística, split único):**

| real \ previsto | alto risco | baixo risco |
|---|---|---|
| **alto risco** | 10 | 0 |
| **baixo risco** | 2 | 8 |

Zero falsos negativos e dois falsos positivos. Em triagem é a direção tolerável do erro:
melhor chamar um paciente leve do que deixar um grave na fila. Mas isso não foi projetado
— é resultado desta divisão específica, e com 20 frases de teste nenhuma conclusão sobre
tipo de erro é estável.

---

## Três achados que mudam a leitura do resultado

Documentados com evidência nos notebooks, não como ressalva genérica.

**1. Parte da acurácia vem de estilo de escrita, não de medicina.** Inspecionando os
coeficientes da Regressão Logística, os termos de maior peso para baixo risco são
`quando`, `depois`, `da`, `um` — palavras sem conteúdo clínico. Como as 40 frases de cada
classe saíram das mesmas pessoas, cada classe ganhou uma estrutura própria (as de baixo
risco tendem a ser condicionais: *"dói quando eu aperto"*), e o modelo usou esse padrão
de redação como atalho.

**2. O modelo tratou "não" como sinal de gravidade.** O termo `nao` tem peso forte para
alto risco, aprendido de *"não consigo respirar"*. Funcionou por acaso. Em *"não sinto dor
no peito"*, esse mesmo peso levaria à conclusão oposta à correta — é a limitação de
negação do TF-IDF, com evidência.

**3. As probabilidades são fracas.** Testando com frases novas, *"nao consigo respirar e
meus labios estao roxos"* — cianose com dificuldade respiratória — recebeu apenas **64%**
de alto risco. Todas as previsões ficaram entre 35% e 65%. Um corte de 70% para acionar
atendimento prioritário deixaria esse paciente de fora.

---

## Governança, ética e viés

Detalhamento em [`docs/GOVERNANCA_FASE2.md`](docs/GOVERNANCA_FASE2.md). Em resumo:

- **Origem dos dados.** As 10 frases de paciente e as 80 frases rotuladas são
  **sintéticas**, escritas pela equipe. Nenhuma vem de prontuário, paciente real ou base
  pública. O vocabulário clínico se apoia nos textos do SciELO da Fase 1, com a coluna
  `origem` registrando o que tem respaldo e o que é síntese nossa.
- **Qualidade dos rótulos.** "Alto risco" e "baixo risco" foram atribuídos pela equipe a
  partir de sinais de alarme clássicos, sem revisão clínica. Um modelo nunca fica melhor
  que o próprio gabarito.
- **Ponto mais frágil do mapa.** O `texto_01_hipertensao_scielo` trata hipertensão como
  condição frequentemente assintomática e não lista cefaleia, tontura ou visão embaçada.
  Quase todas as linhas de Hipertensão estão marcadas como `conhecimento_geral_equipe`.
- **Viés de linguagem.** Ver achado 1 acima. A consequência real é que quem escreve fora
  do padrão da equipe — pouca escolaridade, outro regionalismo, idade avançada, erro de
  digitação — seria classificado pelo jeito de escrever em vez de pelo que sente. O erro
  cairia sobre quem já tem menos acesso a saúde.
- **Privacidade.** Como não há dado real de paciente, não há dado pessoal sensível no
  repositório. Isso é consequência de a base ser sintética, não uma proteção implementada.
- **Segurança clínica.** O sistema devolve "inconclusivo" em vez de chutar, e o texto de
  saída encaminha para avaliação humana.

---

## Limitações

1. O sistema da Parte 1 não entende a frase, só procura pedaços de texto. Negação, ironia
   e hipótese passam batido.
2. Palavra intrusa quebra o casamento de sintoma (ver falha documentada).
3. Os pesos do mapa são opinião da equipe, não estatística calibrada.
4. Cobertura de 7 condições. Fora disso, inconclusivo.
5. Base de 80 frases com mais de mil termos no TF-IDF: muito mais coluna que linha, com
   espaço de sobra para o modelo decorar.
6. As probabilidades não foram calibradas e não servem para definir limiar clínico.
7. Nenhuma etapa foi revisada por profissional de saúde.

**Conclusão honesta:** este projeto demonstra o mecanismo de um triador automático. Ele
não é um triador. Usar isso com paciente real, sem base clínica, sem rótulo validado e
sem auditoria de viés, causaria dano.

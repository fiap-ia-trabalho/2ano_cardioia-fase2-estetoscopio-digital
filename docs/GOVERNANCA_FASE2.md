# Governança, Ética e Viés — CardioIA Fase 2

Documento complementar ao README. Segue a estrutura do `FONTES_E_GOVERNANCA.md` da Fase 1
e registra proveniência, limitações e riscos desta entrega.

---

## 1. Proveniência dos dados

### 1.1 Relatos de pacientes (`dados/frases_pacientes.txt`)

**Natureza: sintética.** As 10 frases foram escritas pela equipe. Não há paciente real,
prontuário, transcrição de consulta ou base pública por trás delas.

Critério de construção: cada frase contém o que a pessoa sente, quando começou e como
afeta a rotina, conforme o enunciado. Variamos o registro de propósito — três frases sem
acentuação e uma parcialmente em caixa alta — para exercitar a normalização.

**Implicação:** frases escritas por quem conhece a resposta são mais limpas e mais
informativas do que relatos reais. Um relato de verdade é confuso, incompleto e
frequentemente contraditório.

### 1.2 Mapa de conhecimento (`dados/mapa_conhecimento.csv`)

48 linhas (96 expressões, duas por linha), 7 condições, com coluna `origem` indicando a
procedência de cada termo:

| origem | significado |
|---|---|
| `texto_02_sindrome_coronariana_scielo` | termo presente no corpus de síndrome coronariana da Fase 1 |
| `texto_01_hipertensao_scielo` | termo presente no corpus de hipertensão da Fase 1 |
| `conhecimento_geral_equipe` | termo escrito pela equipe, sem respaldo direto nesses corpora |

Os corpora da Fase 1 derivam de diretrizes brasileiras publicadas no SciELO
(DOI 10.36660/abc.20201238 e DOI 10.36660/abc.20250619), sob licença Creative Commons
Attribution. Nenhum trecho foi reproduzido literalmente nesta fase — usamos apenas
terminologia.

**Ponto mais frágil, registrado explicitamente.** Ao conferir o
`texto_01_hipertensao_scielo`, verificamos que ele trata hipertensão como condição
frequentemente assintomática e **não** lista cefaleia, tontura, visão embaçada ou zumbido.
Portanto quase todas as linhas de Hipertensão do nosso mapa estão marcadas como
`conhecimento_geral_equipe`. Seria trivial escrever `texto_01` nessas linhas e ninguém
verificaria. Não fizemos isso.

**Divergência consciente do enunciado.** O enunciado sugere como exemplo
`"falta de ar", "dificuldade para respirar" → Angina`. Mapeamos esses termos para
Insuficiência Cardíaca. Dispneia é sinal de congestão; angina se define por dor ao esforço
que alivia em repouso. A divergência é deliberada e está documentada.

### 1.3 Base rotulada de risco (`dados/frases_risco.csv`)

**Natureza: sintética.** 80 frases escritas pela equipe, 40 por classe, em 40 grupos
semânticos.

Os rótulos foram atribuídos pela equipe com base em sinais de alarme clássicos: dor
torácica em repouso ou prolongada, irradiação, início súbito, déficit neurológico,
síncope, cianose, dispneia sem esforço. **Nenhum rótulo foi revisado por profissional de
saúde.** Alguns casos são discutíveis — classificamos crise hipertensiva com cefaleia
como alto risco, mas um triador experiente poderia decidir diferente conforme o serviço.

Um modelo nunca fica melhor que o próprio gabarito. Este gabarito é frágil.

---

## 2. Vazamento de dados

Quando amostras derivadas da mesma origem são distribuídas ao acaso entre treino e teste,
o modelo é avaliado sobre material que ele praticamente já viu. A acurácia sobe sem
ganho real de generalização. Em bases pequenas e construídas por variação, como esta, o
risco é alto.

**Controle adotado.** A coluna `grupo_semantico` agrupa frases que são variações da
mesma ideia clínica. A divisão treino/teste usa `StratifiedGroupKFold`, que mantém grupos
inteiros de um lado só e equilibra as classes. O notebook 02 tem uma verificação com
`assert` que falha se algum grupo aparecer nos dois lados.

**Efeito medido:**

| divisão | acurácia média (5 folds) |
|---|---|
| por grupo | 77,5% |
| por frase | 83,8% |
| inflação | +6,2 pontos percentuais |

O TF-IDF também é ajustado dentro de um `Pipeline`, para que o vocabulário do conjunto de
teste não vaze para o treino durante a validação cruzada.

---

## 3. Vieses identificados

### 3.1 Viés de linguagem (o mais grave)

Inspecionando os coeficientes da Regressão Logística, os termos de maior peso para a
classe de baixo risco são `quando`, `depois`, `da`, `um`, `um pouco` — palavras sem
conteúdo clínico.

Causa: as 40 frases de cada classe foram escritas pelas mesmas pessoas. Cada classe
acabou com uma estrutura de redação própria, e o modelo encontrou esse padrão antes de
encontrar o sintoma.

Consequência real, se o sistema fosse usado: pessoas que escrevem fora desse padrão —
baixa escolaridade, regionalismo diferente, idade avançada, erros de digitação, uso de
áudio transcrito — seriam classificadas pelo jeito de escrever em vez de pelo que sentem.
O erro recairia sobre quem já tem menos acesso a serviços de saúde.

Mitigação necessária (fora do escopo desta fase): frases coletadas de pessoas diferentes,
com escolaridades e regiões diferentes, e auditoria de desempenho por subgrupo.

### 3.2 Viés de negação

O termo `nao` recebeu peso forte para alto risco, aprendido de construções como "não
consigo respirar". Funcionou por coincidência nesta base. Em "não sinto dor no peito", o
mesmo peso empurraria para a conclusão oposta à correta.

TF-IDF não modela negação. Resolver exigiria modelos sensíveis a contexto.

### 3.3 Viés de representatividade clínica

Sete condições, todas cardiovasculares ou neurovasculares, e em apresentações típicas.
Apresentações atípicas — comuns em mulheres, idosos e pessoas com diabetes, que podem ter
infarto sem dor torácica clássica — estão sub-representadas. Incluímos um caso de dor
epigástrica atípica, mas um caso não corrige a distribuição.

### 3.4 Ausência de dados demográficos

As frases não trazem idade, sexo, região ou escolaridade. Isso impede qualquer auditoria
de desempenho por subgrupo — não conseguimos verificar se o modelo funciona pior para
algum recorte da população. A ausência de dado demográfico não é neutralidade; é
impossibilidade de fiscalizar.

---

## 4. Privacidade

Não há dado pessoal no repositório, porque não há paciente real. Isso é consequência de a
base ser sintética, não uma medida de proteção que tenhamos implementado. Um sistema
equivalente com dados reais exigiria base legal, consentimento, minimização, controle de
acesso e registro de tratamento conforme a LGPD — nada disso foi construído aqui.

---

## 5. Segurança clínica

Decisões tomadas para reduzir o risco de uso indevido:

- a Parte 1 devolve **"Inconclusivo — encaminhar para avaliação humana"** quando nenhum
  sintoma casa ou quando há empate, em vez de escolher a doença mais provável;
- a saída do script traz aviso explícito de que não substitui avaliação médica;
- README e notebooks afirmam que o projeto é acadêmico e que a base é sintética;
- não publicamos limiar de decisão recomendado, porque as probabilidades não foram
  calibradas.

O que **não** foi feito, e seria obrigatório num sistema real: validação clínica
prospectiva, registro como dispositivo médico quando aplicável, monitoramento contínuo de
desempenho, canal de contestação para o paciente e responsabilidade humana definida para
cada decisão automatizada.

---

## 6. Licenças

- Corpora textuais da Fase 1: derivados de publicações SciELO sob Creative Commons
  Attribution. Uso acadêmico, com atribuição.
- Frases e mapa de conhecimento desta fase: produção própria da equipe.
- Base numérica da Fase 1 (Kaggle): licença registrada como *Unknown*. **Não utilizada
  nesta fase.** A indefinição de licença exige cautela em qualquer uso além do contexto
  estritamente acadêmico.

---

## 7. Resumo do que impede este projeto de ser usado de verdade

1. Base sintética, sem paciente real.
2. Rótulos sem validação clínica.
3. Viés de linguagem medido e não corrigido.
4. Probabilidades não calibradas.
5. Sem dados demográficos, logo sem auditoria por subgrupo possível.
6. Sem responsabilidade humana definida no fluxo.

Qualquer um dos seis, isoladamente, já bastaria.

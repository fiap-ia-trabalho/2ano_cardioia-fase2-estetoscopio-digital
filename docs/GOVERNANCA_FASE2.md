# Governança, ética e limitações - CardioIA Fase 2

Este documento registra a origem dos dados, as observações do experimento e os
riscos que ainda precisam de investigação. O projeto tem finalidade acadêmica.

## 1. Origem dos dados

Os dez relatos e as 80 frases de risco são sintéticos, escritos pela equipe.
Não há prontuários, consultas ou relatos de pacientes reais. Os rótulos foram
atribuídos pelos estudantes, sem revisão clínica. A acurácia mede concordância
com esses rótulos, cuja qualidade limita a interpretação dos resultados.

Cada um dos dez relatos inclui sintomas, início e impacto na rotina. A base de
risco tem 40 frases por classe e 40 grupos semânticos.

### Mapa de conhecimento e continuidade com a Fase 1

O mapa contém 48 linhas, 96 expressões e sete condições. Os pesos de 1 a 3 são
regras didáticas da equipe, sem calibração clínica. A coluna `origem` registra:

| Origem declarada | Linhas | Referência |
|---|---:|---|
| `texto_02_sindrome_coronariana_scielo` | 15 | [Corpus de síndrome coronariana da Fase 1](https://github.com/fiap-ia-trabalho/2ano_cardioia-fase1-batimentos-de-dados/blob/main/docs/textos/texto_02_sindrome_coronariana_scielo.txt) |
| `texto_01_hipertensao_scielo` | 1 | [Corpus de hipertensão da Fase 1](https://github.com/fiap-ia-trabalho/2ano_cardioia-fase1-batimentos-de-dados/blob/main/docs/textos/texto_01_hipertensao_scielo.txt) |
| `conhecimento_geral_equipe` | 32 | Associações elaboradas pela equipe |

Os corpora são textos acadêmicos autorais e parafraseados, preparados a partir de
publicações identificadas pelos DOI `10.36660/abc.20201238` e
`10.36660/abc.20250619`. Não são a íntegra das diretrizes. A origem declarada de uma
expressão não comprova a associação a uma doença nem valida o peso atribuído.

O corpus de hipertensão não lista cefaleia, tontura ou visão embaçada como sintomas.
Quase todas as associações de Hipertensão do mapa são marcadas como
`conhecimento_geral_equipe` e precisam de revisão fundamentada em referências.

O enunciado apresenta `falta de ar` associada a Angina como exemplo. Nesta solução,
a expressão foi associada a Insuficiência Cardíaca. É uma escolha didática sem
validação clínica: a expressão isolada não distingue doenças. A regra não deve
ser apresentada como uma correção médica do enunciado.

A base numérica e as imagens da Fase 1 não entram nos métodos de texto desta entrega.

## 2. Divisão dos dados e prevenção de vazamento

Variações da mesma ideia pertencem ao mesmo `grupo_semantico`. A divisão por
`StratifiedGroupKFold` mantém cada grupo inteiro em um único lado e busca preservar
a proporção das classes. O notebook verifica a ausência de grupos compartilhados
entre treino e teste. O TF-IDF é ajustado em um `Pipeline`, somente sobre o treino.

| Estratégia | Acurácia média da regressão logística em cinco divisões |
|---|---:|
| Por grupo semântico, avaliação principal | 77,50% |
| Por frase, comparação | 83,75% |
| Diferença observada | 6,25 pontos percentuais |

A divisão por frase é mais otimista nesta base. A diferença é compatível com o
risco de compartilhar variações semelhantes, mas não mede uma contribuição causal
exclusiva de vazamento: os conjuntos de teste também mudam.

Referência: [StratifiedGroupKFold no scikit-learn](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html).

## 3. Resultados e limites da interpretação

O teste isolado teve acurácia de 90%, dois falsos positivos e nenhum falso negativo
em 20 frases. Nas previsões agregadas das 80 frases, cada uma avaliada sem seu grupo
no treino, houve **dez falsos negativos e oito falsos positivos**, com acurácia de
**77,5%**. Para alto risco, a sensibilidade foi de 75%. O zero do teste isolado não
se mantém na avaliação completa.

A regra por palavras-chave foi avaliada nas mesmas cinco divisões: média de 58,75%.
O desvio-padrão entre divisões não é um intervalo de confiança. Os números são
exportados em `resultado_classificador.csv` e `metricas_cv_agregada.csv`.

### Estilo de escrita e sinal dos coeficientes

Termos como `quando`, `depois`, `da` e `um` favorecem baixo risco. Isso sugere
sensibilidade à redação, mas não quantifica quanto da acurácia depende do estilo.
Não medimos diferenças por idade, região ou escolaridade.

As classes observadas são `['alto risco', 'baixo risco']`. No modelo binário,
coeficientes positivos favorecem a segunda classe, baixo risco; negativos favorecem
alto risco. A previsão combina todos os atributos.

Referência: [LogisticRegression no scikit-learn](https://scikit-learn.org/1.8/modules/generated/sklearn.linear_model.LogisticRegression.html).

### Negação, contexto e cobertura

A extração por trecho não trata negação, hipótese, tempo ou sujeito. `Não sinto
dor no peito` ainda corresponde a `dor no peito`. Termos genéricos como `subo a
escada` podem somar pontos sem desconforto. Uma palavra intermediária impede
reconhecer `coração fica acelerado` como `coração acelerado`.

Na classificação, bigramas capturam combinações locais, sem garantir interpretação
geral de negação. O coeficiente de `nao` não determina sozinho a previsão.

Um relato fora das sete condições pode receber uma sugestão inadequada se contiver
termos do mapa. A saída inconclusiva ocorre sem correspondências ou com empate;
não garante a detecção de todos os casos fora do domínio.

### Generalização, calibração e representatividade

A base é pequena e sintética, sem avaliação externa. Há risco de sobreajuste,
mas a diferença entre o teste isolado e a validação cruzada não o comprova sozinha.

As estimativas de `predict_proba` nos seis exemplos novos não representam risco
clínico. A calibração não foi avaliada e nenhum limiar de atendimento foi definido.

Não há dados estruturados de subgrupos para medir diferenças entre populações.
Diversificar autores e contextos, revisar rótulos e avaliar paráfrases são etapas
futuras para investigar os riscos de viés.

## 4. Privacidade e uso acadêmico

Os dados de sintomas não descrevem pacientes reais. Isso não equivale à implementação
de controles de proteção de dados para um sistema com dados reais.

O aviso de uso acadêmico aparece no README, no script e nos notebooks. Nenhum método
foi validado para diagnóstico ou triagem clínica. A pontuação da extração é didática,
e o campo `confianca` não é probabilidade de doença.

## 5. Referências e licenças declaradas

O [registro de fontes da Fase 1](https://github.com/fiap-ia-trabalho/2ano_cardioia-fase1-batimentos-de-dados/blob/main/FONTES_E_GOVERNANCA.md)
identifica as publicações textuais sob Creative Commons Attribution e registra
a licença da base numérica do Kaggle como `Unknown`. Essa base numérica não é
utilizada aqui. A declaração da Fase 1 não amplia permissões de uso.

As frases e regras de associação desta fase são da equipe. As fontes devem ser
citadas ao explicar a continuidade do projeto, sem apresentar a terminologia como
validação das regras didáticas.

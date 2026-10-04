# CardioIA — Fase 2: Diagnóstico Automatizado (IA no Estetoscópio Digital)

Protótipo acadêmico que analisa relatos de sintomas por dois métodos: extração de
expressões associadas a possíveis doenças e classificação de frases em alto ou baixo
risco com aprendizado de máquina.

Projeto acadêmico — FIAP, 2º ano de Inteligência Artificial.

> As bases são sintéticas, os rótulos foram atribuídos por estudantes e as associações
> não foram validadas clinicamente. As saídas demonstram o funcionamento dos métodos e
> não devem ser utilizadas para diagnóstico ou triagem de pacientes.

## Grupo

| Integrante | RM |
|---|---|
| Cauan Otto Rodrigues Sousa | RM567940 |
| Fernando A. Gurgel | RM567606 |
| Iraci Monteiro Souza | RM567544 |
| Maria Luisa Rodrigues Nascimento | RM567659 |
| Rafaela Torres Martins | RM567735 |

**Tutor:** Leonardo Ruiz Orabona · **Coordenador:** André Godoi

## Entregáveis e organização

| Arquivo | Finalidade |
|---|---|
| [dados/frases_pacientes.txt](dados/frases_pacientes.txt) | 10 relatos, um por linha, com sintomas, início e impacto na rotina |
| [dados/mapa_conhecimento.csv](dados/mapa_conhecimento.csv) | 48 associações entre expressões de sintomas e possíveis doenças |
| [src/extracao_sintomas.py](src/extracao_sintomas.py) | Leitura dos arquivos, extração, pontuação e exportação |
| [notebooks/01_extracao_sintomas.ipynb](notebooks/01_extracao_sintomas.ipynb) | Demonstração comentada da Parte 1 |
| [dados/resultado_extracao.csv](dados/resultado_extracao.csv) | Resultados dos 10 relatos |
| [dados/frases_risco.csv](dados/frases_risco.csv) | 80 frases rotuladas para classificação de risco |
| [notebooks/02_classificador_risco.ipynb](notebooks/02_classificador_risco.ipynb) | Treinamento, comparação de modelos e avaliação da Parte 2 |
| [dados/resultado_classificador.csv](dados/resultado_classificador.csv) | Acurácias e estatísticas de validação cruzada |
| [docs/GOVERNANCA_FASE2.md](docs/GOVERNANCA_FASE2.md) | Proveniência, limitações e discussão de vieses |
| [requirements.txt](requirements.txt) | Dependências para instalação |
| [docs/roteiro_video.md](docs/roteiro_video.md) | Arquivo reservado ao roteiro de vídeo, ainda sem conteúdo |

Os notebooks possuem saídas salvas. Para reproduzir o projeto, baixe ou clone o
repositório completo, mantendo as pastas `dados/`, `src/` e `notebooks/`.
Os dois notebooks importam funções de `src/extracao_sintomas.py`.

## Vídeo de demonstração

**Status: link ainda não informado.** O roteiro também está pendente de preenchimento.
O planejamento da equipe prevê um vídeo não listado de até 4 minutos; as exigências de
formato e duração devem ser conferidas no enunciado completo da atividade.

## Como executar

O projeto declara Python 3.9 ou superior. As dependências usam versões mínimas em
`requirements.txt`, portanto as versões instaladas podem variar conforme o Python e a
data da instalação. A revisão de execução reproduziu os resultados com Python 3.12.14,
pandas 2.2.3, NumPy 2.3.5 e scikit-learn 1.8.0.

```bash
git clone https://github.com/fiap-ia-trabalho/2ano_cardioia-fase2-estetoscopio-digital.git
cd 2ano_cardioia-fase2-estetoscopio-digital
python -m pip install -r requirements.txt
```

Execute a Parte 1 a partir da raiz do projeto:

```bash
python src/extracao_sintomas.py
```

O script lê os relatos e o mapa, mostra as sugestões no terminal e grava
`dados/resultado_extracao.csv`.

Para executar os notebooks:

```bash
jupyter notebook notebooks/
```

Abra cada notebook, reinicie o kernel e execute todas as células em ordem. A Parte 2
grava `dados/resultado_classificador.csv`. A execução substitui os respectivos CSVs de
resultados.

O projeto utiliza pandas, scikit-learn e Jupyter. O notebook 02 também importa NumPy,
instalado como dependência dessas bibliotecas. As matrizes de confusão são tabelas,
sem dependência de uma biblioteca de gráficos.

## Continuidade com a Fase 1

Repositório anterior: [Batimentos de Dados](https://github.com/fiap-ia-trabalho/2ano_cardioia-fase1-batimentos-de-dados).

- **Corpus textual:** a coluna `origem` registra 15 linhas atribuídas ao texto de
  síndrome coronariana, uma ao texto de hipertensão e 32 a `conhecimento_geral_equipe`.
  Essa identificação registra a procedência declarada pela equipe; não equivale a
  validação clínica da associação ou de seu peso.
- **Base numérica:** `cardio_train_amostra_100` não foi utilizada nesta implementação.
  O classificador recebe frases sintéticas, sem integração com as variáveis tabulares.
- **Base de imagens:** não foi utilizada, pois os métodos implementados trabalham com texto.

## Parte 1 — Extração de sintomas

### Dados e método

As 10 frases simulam relatos de pacientes e incluem variações de acentuação e maiúsculas.
O mapa contém 48 linhas e 96 expressões, distribuídas em sete condições: Infarto Agudo
do Miocárdio, Angina, Insuficiência Cardíaca, Arritmia, Hipertensão Arterial, Pericardite
e Acidente Vascular Cerebral.

| Coluna | Significado |
|---|---|
| `sintoma_1` e `sintoma_2` | Expressões pesquisadas nos relatos |
| `doenca_associada` | Hipótese associada pela regra didática |
| `peso` | Pontuação de 1 a 3 definida pela equipe, sem calibração clínica |
| `origem` | Procedência declarada da expressão |

O processamento segue quatro etapas:

1. Normaliza relato e expressões: remove acentos, converte para minúsculas e limpa
   pontuação e espaços.
2. Procura cada expressão como trecho do relato, começando pelas mais longas.
3. Descarta um termo inteiramente contido em outro trecho já reconhecido. Isso evita
   somar `falta de ar` ao mesmo trecho de `falta de ar quando deito`.
4. Soma os pesos por doença e apresenta a mais pontuada. Sem correspondências ou com
   empate na maior pontuação, retorna `Inconclusivo - encaminhar para avaliação humana`.

**A coluna `confianca` não é uma probabilidade de doença.** Ela contém a pontuação da
hipótese mais pontuada dividida pela soma de todas as pontuações. Um valor de 100% pode
resultar de uma única expressão associada a uma única condição no mapa.

### Resultados e testes adicionais

Os 10 relatos geram sugestões, sem resultados inconclusivos. Como frases e mapa foram
construídos pela mesma equipe, sem gabarito clínico independente, isso demonstra
funcionamento, não acurácia diagnóstica validada.

A seção 8 do notebook contém **quatro testes adicionais**:

| Caso | Saída observada | Interpretação |
|---|---|---|
| Tornozelo torcido ao jogar bola | Inconclusivo | Nenhuma expressão encontrada |
| Coração fica acelerado, falta de ar e subida de escada | Angina, proporção de pontuação de 60% | Não reconhece a variante `coração fica acelerado` |
| Dor de garganta e febre | Inconclusivo | Nenhuma expressão encontrada |
| Peso no peito e suor frio | Infarto Agudo do Miocárdio, proporção de pontuação de 100% | Correspondência com as regras; não confirma a doença |

O segundo teste expõe uma falha de extração: a palavra intermediária `fica` impede a
correspondência com `coração acelerado`. Ele não estabelece o diagnóstico clínico correto.

### Limitações da extração

- Não interpreta negação, hipótese, tempo do evento ou quem apresenta o sintoma.
  `Não sinto dor no peito` ainda corresponde a `dor no peito`.
- Expressões genéricas, como `subo a escada` e `respiro fundo`, podem gerar pontuação
  mesmo sem relato de desconforto.
- A regra de sobreposição não elimina sinônimos em trechos distintos: `dor no peito`
  e `dor torácica` podem ser contados separadamente no mesmo relato.
- Variantes como `palpitações` podem não ser reconhecidas.
- Um relato de condição fora das sete categorias pode receber uma sugestão incorreta
  se contiver uma expressão do mapa. Estar fora da cobertura não garante saída inconclusiva.

## Parte 2 — Classificação de risco

### Dados, representação e divisão

A base possui **80 frases sintéticas**, 40 de alto risco e 40 de baixo risco, em
**40 grupos semânticos**. As colunas são `frase`, `situacao` e `grupo_semantico`.
Há vocabulário compartilhado entre as classes; uma palavra como `peito` não determina
sozinha o rótulo atribuído pela equipe.

O texto é convertido em atributos por TF-IDF com unigramas, bigramas e a normalização
da Parte 1. Regressão logística e árvore de decisão são avaliadas em pipelines que
ajustam o TF-IDF somente nos dados de treinamento de cada divisão.

A avaliação principal usa `StratifiedGroupKFold`, mantendo cada grupo inteiro em um
único lado da divisão e buscando preservar a proporção das classes. Isso reduz o risco
de testar o modelo sobre variações muito próximas das frases usadas no treinamento.

### Resultados

| Modelo | Acurácia no teste isolado | Acurácia média na validação cruzada por grupo |
|---|---:|---:|
| Regressão logística | 90,0% | 77,5% ± 5,0 pontos percentuais |
| Árvore de decisão | 70,0% | 63,75% ± 8,29 pontos percentuais |
| Regra por palavras-chave | 60,0% | Não calculada no notebook |

O teste isolado usa 60 frases para treinamento e 20 para teste. A validação cruzada
avalia cinco divisões da base. O valor após `±` é o desvio-padrão das acurácias entre
divisões, não um intervalo de confiança.

**Comparação equivalente:** no teste isolado, a regressão logística supera a regra por
palavras-chave em **30 pontos percentuais** (90% menos 60%). Não se deve comparar os
60% desse teste diretamente com os 77,5% da validação cruzada. Para isso, a regra precisa
ser avaliada nas mesmas divisões dos modelos.

### Matriz de confusão do teste isolado

| Rótulo da base / Previsão | Alto risco | Baixo risco |
|---|---:|---:|
| Alto risco | 10 | 0 |
| Baixo risco | 2 | 8 |

Houve zero falsos negativos e dois falsos positivos **nessa divisão**. Isso não garante
o mesmo comportamento em outras divisões ou em novos dados.

### Avaliação agregada das cinco divisões

Uma verificação complementar reuniu as previsões de teste das 80 frases, usando a mesma
regressão logística e as mesmas divisões por grupo do notebook. Cada frase foi avaliada
por um modelo treinado sem o seu grupo.

| Rótulo da base / Previsão | Alto risco | Baixo risco |
|---|---:|---:|
| Alto risco | 30 | 10 |
| Baixo risco | 8 | 32 |

A acurácia foi de **77,5%**. Para alto risco, a sensibilidade foi de **75%** (30/40),
a precisão de **78,9%** (30/38) e o F1 de **76,9%**. Houve **10 falsos negativos e
8 falsos positivos**, tomando os rótulos sintéticos da equipe como referência.

Essa matriz complementar ainda não é exportada pelo notebook ou pelo CSV de métricas.
Para reproduzi-la, execute após a seção de validação cruzada do notebook 02:

```python
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix, classification_report

pred_cv = cross_val_predict(
    montar_pipeline(
        LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42
        )
    ),
    X, y, groups=grupos, cv=cv_grupo,
)

ordem = ["alto risco", "baixo risco"]
print(pd.DataFrame(
    confusion_matrix(y, pred_cv, labels=ordem),
    index=pd.Index(ordem, name="rotulo"),
    columns=pd.Index(ordem, name="previsao"),
))
print(classification_report(y, pred_cv, labels=ordem, digits=3))
```

### Comparação entre divisões por grupo e por frase

O notebook também avalia a regressão logística dividindo por frase, como comparação:

| Divisão | Acurácia média |
|---|---:|
| Por grupo semântico | 77,50% |
| Por frase | 83,75% |
| Diferença observada | 6,25 pontos percentuais |

O resultado por frase é mais otimista nesta base. É compatível com o risco de
compartilhar variações semelhantes entre treino e teste, mas a diferença isolada não
mede uma contribuição causal exclusiva de vazamento. As estratégias também alteram
a dificuldade e a composição dos conjuntos de avaliação.

## Interpretação, vieses e governança

O documento [GOVERNANCA_FASE2.md](docs/GOVERNANCA_FASE2.md) registra a discussão da
equipe. A interpretação dos resultados exige as seguintes distinções:

- **Estilo de escrita:** termos como `quando`, `depois`, `da` e `um` favorecem baixo
  risco. Isso sugere sensibilidade a padrões de redação, mas os coeficientes sozinhos
  não quantificam quanto da acurácia decorre desses padrões.
- **Sinal dos coeficientes:** a ordem observada é `['alto risco', 'baixo risco']`.
  Coeficientes positivos favorecem baixo risco; negativos favorecem alto risco.
  As listagens de termos do código usam essa interpretação. A frase introdutória da
  seção 11 do notebook 02 apresenta o sentido invertido e precisa de revisão.
- **Negação:** `nao` contribui para alto risco no modelo treinado, mas a decisão combina
  todos os atributos. Seu coeficiente não determina sozinho a previsão de uma frase.
  Bigramas capturam algumas combinações, sem garantir interpretação geral de negação.
- **Probabilidades:** nos seis exemplos novos, as estimativas de alto risco ficaram
  entre aproximadamente 35% e 64,3%. A faixa, sozinha, não comprova descalibração.
  A calibração não foi avaliada e as estimativas não representam risco clínico validado.
- **Representatividade:** os relatos foram escritos pela equipe. Não há avaliação
  externa nem dados estruturados de subgrupos para medir diferenças por idade, região
  ou escolaridade. Desvantagens para esses grupos são riscos a investigar, não
  resultados demonstrados pelo experimento.
- **Rótulos e pesos:** foram definidos pela equipe, sem revisão clínica. A avaliação
  mede concordância com esses rótulos, cuja qualidade limita as conclusões.
- **Privacidade:** as bases de relatos não contêm dados de pacientes reais. Isso não
  constitui uma implementação de controles de proteção de dados para uso clínico.
- **Generalização:** a base é pequena e o vocabulário é amplo. Há risco de sobreajuste,
  mas a diferença entre o teste isolado e a validação cruzada não o comprova sozinha.

## Melhorias propostas

1. Revisar expressões genéricas e exigir contexto que indique um sintoma.
2. Tratar negação, sujeito do relato e variantes de expressão.
3. Agrupar sinônimos por conceito para evitar pontuação duplicada e permitir que um
   mesmo sintoma contribua para mais de uma hipótese.
4. Relacionar cada associação à referência e ao trecho que a sustenta, mantendo os
   pesos identificados como regras didáticas.
5. Exportar métricas por classe e a matriz agregada da validação cruzada; avaliar a
   regra por palavras-chave nas mesmas divisões dos modelos.
6. Revisar os textos dos notebooks e de governança conforme as distinções metodológicas
   descritas neste README e completar os materiais do vídeo.

Essas melhorias são propostas para versões futuras. A implementação atual mantém as
limitações de extração e classificação descritas acima.

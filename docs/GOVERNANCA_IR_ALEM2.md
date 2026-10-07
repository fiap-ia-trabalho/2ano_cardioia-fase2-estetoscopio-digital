# Governança e limites do Ir Além 2

Este documento acompanha o notebook `03_diagnostico_visual.ipynb`. O experimento
classifica imagens de traçados derivados de batimentos ECG. Seus resultados são
medidas de concordância com os rótulos dessa base, sem validação para uso clínico.

## Origem e representação

A [base ECG Heartbeat Categorization, versão 1](https://www.kaggle.com/datasets/shayanfazeli/heartbeat)
é a recomendada no enunciado da FIAP. O download público fornece CSVs com 187
amplitudes temporais e uma coluna de classe. Os sinais já foram segmentados,
reamostrados e preenchidos com zeros; não são imagens de exames completos.
A preparação é descrita no [artigo de Kachuee, Fazeli e Sarrafzadeh](https://arxiv.org/abs/1805.00794).
A fonte original é o [MIT-BIH Arrhythmia Database](https://physionet.org/content/mitdb/1.0.0/).

Há uma diferença entre o formato dessa base recomendada e a descrição visual do
enunciado. A adaptação deste projeto gera um traçado RGB 256×256, converte para
cinza e redimensiona para 64×64. A MLP recebe os pixels dessas imagens, normalizados
e achatados. O repositório inclui exemplos antes e depois do processamento, com
arquivo de origem, número da linha contado a partir de zero e classe da base.
Essa adaptação é explícita e não transforma os exemplos em fotografias clínicas.

`dados/ecg_origem.json` registra versão, endereço público, tamanho original e
SHA-256 dos dois CSVs. Eles são armazenados localmente com compressão sem perdas;
o hash é calculado sobre o conteúdo descompactado. Os arquivos grandes e o modelo
binário ficam fora do Git. O script de download verifica o manifesto versionado.

## Rótulos e seleção

O grupo N (código 0) recebe o rótulo binário zero. S, V e F (códigos 1, 2 e 3)
recebem um. Q (código 4) é excluída por corresponder a batimentos não classificados;
não a presumimos uma anomalia confirmada. A classificação normal/alterado vale
para esses grupos de batimentos, não para a condição de saúde de uma pessoa.

Selecionamos 6.000 exemplos de cada classe binária, sem reposição, do arquivo
de treino, usando semente 42. Esse limite permite reprodução em CPU com memória
moderada. O balanceamento é uma escolha de treinamento; não estima prevalência
clínica. A divisão estratificada da amostra é 80% treino e 20% validação.

O teste vem do arquivo de teste do dataset e conserva sua proporção após excluir
Q. Duplicatas exatas do pool de treino e duplicatas do treino/validação encontradas
no teste são tratadas e contabilizadas no notebook. Isso não verifica se
batimentos semelhantes ou de uma mesma pessoa aparecem nos dois arquivos.
`dados/ecg_divisao.csv` permite reconstruir as linhas usadas em cada conjunto.

## Treinamento e avaliação

Os exemplos de imagens publicados são retirados do conjunto de treino.
Rótulos, textos, títulos e cores de classe não são inseridos nos pixels recebidos
pela rede. A mesma escala e o mesmo processamento são usados em todos os conjuntos.

A arquitetura, dez épocas e limiar de 0,5 são definidos antes da avaliação final.
A validação é acompanhada durante o treino; o teste não define esses parâmetros.
A semente é aplicada ao Keras e ao embaralhamento, e o kernel é iniciado com
`PYTHONHASHSEED=0`. Registramos as versões e usamos CPU com operações determinísticas.
Hardware e versões diferentes ainda podem
alterar os resultados; não prometemos reprodução universal dos mesmos números.

O notebook verifica a acurácia da validação contra a última época, salva e
recarrega o modelo e compara suas previsões. As matrizes, métricas por classe,
histórico e relatório JSON são gerados pelo mesmo treinamento.
Em 07/10/2026, duas execuções completas com a configuração final produziram as
mesmas métricas e matriz de confusão nesta máquina. A comparação está em
`dados/ecg_reproducao.json`; não é uma garantia para outros ambientes.

Tomando S/V/F como positivo:

| Medida | Cálculo e interpretação |
|---|---|
| Precisão | TP/(TP+FP): proporção correta entre os alertas S/V/F |
| Recall | TP/(TP+FN): proporção dos S/V/F identificados |
| Taxa de falsos positivos | FP/(FP+TN): proporção dos N classificados como S/V/F |
| Fração de alertas incorretos | FP/(TP+FP): complemento da precisão |
| F1 | Combinação de precisão e recall |

A referência que sempre prevê N é apresentada para mostrar o efeito do
desbalanceamento na acurácia. Ela tem recall zero para S/V/F. Exibimos as
contagens de falsos negativos e positivos, além dos percentuais.

## Limitações e conclusões permitidas

- O dataset original reúne gravações de 47 participantes e foi selecionado em
  parte para incluir arritmias menos comuns. Sua distribuição não é uma amostra
  representativa da prevalência clínica geral.
- O CSV derivado não contém IDs dos participantes. Não verificamos generalização
  para pacientes independentes dos usados no treino.
- Q é excluída. O modelo não possui mecanismo validado de rejeição de classes
  desconhecidas, sinais inválidos ou condições fora de N/S/V/F.
- A rasterização e a resolução reduzida podem perder detalhes do sinal. Não
  avaliamos fotografias, papel, equipamentos diferentes ou ruído de aquisição.
- Dropout é uma medida de regularização, sem comprovar que o sobreajuste foi eliminado.
- A saída Sigmoid é uma estimativa da rede. Não avaliamos sua calibração nem a
  interpretamos como probabilidade validada de doença.
- Não há auditoria de desempenho por idade, sexo ou outros subgrupos no CSV.
  Diferenças populacionais são riscos a investigar, não resultados demonstrados.
- Boa acurácia ou precisão não garante segurança dos alertas para diagnóstico ou triagem.

Os resultados sustentam uma demonstração acadêmica da MLP sobre esta preparação
de dados. O vídeo deve mostrar os erros e essas limitações junto com os acertos.

Referências técnicas: [reprodução em Keras](https://keras.io/examples/keras_recipes/reproducibility_recipes/)
e [definição de precisão no scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html).

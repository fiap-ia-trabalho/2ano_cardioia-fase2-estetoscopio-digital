# Roteiro do vídeo do Ir Além 2

Alvo: **3min30s**, com limite de **4 minutos**. Grave a tela com voz ou legendas
e publique como **não listado** no YouTube. Inclua o link na seção Ir Além 2 do README.
Esta gravação demonstra a MLP; a entrega principal e o portal têm seus próprios roteiros.

## Antes de gravar

Abra `abrir_ir_alem2.bat` e selecione **CardioIA ECG (.venv)**. Os dados e o ambiente
já estão preparados neste computador. Execute todas as células e deixe o notebook
aberto. Assim, durante a gravação, poderá reexecutar a avaliação da seção 7 sem
aguardar novamente a preparação de imagens e o treinamento.

Deixe o README e as seções 2, 4, 5, 6, 7 e 9 do notebook disponíveis. Aumente o zoom
para os números ficarem legíveis. Use os resultados da execução concluída, sem
trocar épocas, amostra ou limiar entre o treino mostrado e a avaliação.

## 1. Apresentação e dados — 0:00 a 0:35

**Mostre:** README com integrantes; notebook, seções 1 e 2 e contagem das classes.

**Fala sugerida:**

> Este é o Ir Além 2 do CardioIA. Usamos a base pública recomendada pela FIAP,
> derivada do MIT-BIH. Ela oferece sinais em CSV. Para a atividade visual,
> transformamos os batimentos em imagens e treinamos uma rede MLP em Keras.
> N é o grupo chamado normal na base, e S, V e F formam o grupo alterado.
> Excluímos a categoria Q, de batimentos não classificados.

## 2. Imagens e divisão — 0:35 a 1:15

**Mostre:** seções 3 e 4; imagens originais e versões em cinza.

**Fala sugerida:**

> Cada traçado começa em RGB, com 256 por 256 pixels. Convertemos para cinza
> e redimensionamos para 64 por 64. Não colocamos rótulos ou texto nos pixels.
> Selecionamos seis mil exemplos de cada classe, com semente fixa: nove mil
> e seiscentos para treino e dois mil e quatrocentos para validação.
> O teste usa outro arquivo, mantendo a proporção de seus rótulos restantes.

## 3. Arquitetura e treino — 1:15 a 1:55

**Mostre:** seção 5, construção da rede e dez épocas executadas; seção 6, gráficos.

**Fala sugerida:**

> A rede normaliza e achata os pixels. Em seguida, usa camadas densas com
> 128, 64 e 32 neurônios, ReLU e Dropout. A saída Sigmoid tem limiar de meio.
> Treinamos dez épocas com Adam e binary cross-entropy. A validação terminou
> em 93,17 por cento, e conferimos esse valor com o modelo atual.
> A perda da validação oscila; o Dropout não garante ausência de sobreajuste.

## 4. Avaliação e erros — 1:55 a 2:50

**Mostre:** reexecute a célula da seção 7, depois a matriz e os percentuais.

**Fala sugerida:**

> No teste separado, com 20.284 batimentos, a acurácia foi 94,53 por cento.
> Para o grupo alterado, o recall foi 92,61 por cento e a precisão foi 67,86.
> Houve 950 falsos positivos e 160 falsos negativos.
> Precisão mede acertos entre os alertas. A taxa de falsos positivos tem
> outro denominador: entre os casos N, foi 5,24 por cento.
> Sempre prever N daria 89,32 por cento de acurácia, mas não identificaria
> nenhum caso alterado. Por isso mostramos as métricas por classe e os erros.

## 5. Limites e entrega — 2:50 a 3:30

**Mostre:** seção 8, conferência do modelo salvo; seção 9 e README.

**Fala sugerida:**

> Também salvamos e recarregamos a rede e conferimos as previsões.
> Os CSVs, gráficos e relatório são gerados pela mesma execução.
> Essas imagens são traçados derivados de sinais, não fotografias de exames.
> A base não permite conferir separação por paciente, e não avaliamos
> calibração ou uso clínico. Este é um experimento acadêmico.
> O código, os exemplos, os integrantes e as instruções estão no GitHub.

## Conferência final

- Vídeo com até quatro minutos, números legíveis e áudio ou legendas claros.
- Mostrar dados, processamento das imagens, código, treino, resultados e limitações.
- Publicar como não listado, testar o acesso e incluir o link no README.
- Entregar na FIAP conforme os campos da atividade e conferir a confirmação.

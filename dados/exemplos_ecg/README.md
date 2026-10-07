# Imagens de exemplo de ECG

Os PNGs são traçados derivados de sinais públicos da base
[ECG Heartbeat Categorization, versão 1](https://www.kaggle.com/datasets/shayanfazeli/heartbeat).
São exemplos do conjunto de treinamento; não são fotografias de exames completos.

Para N, S, V e F, há uma imagem RGB 256×256 e sua versão em cinza 64×64.
`origem.json` identifica o CSV, a linha contada a partir de zero e a classe original.
Os rótulos ficam somente nos nomes e no manifesto, sem serem desenhados nos pixels.

O notebook regenera esses arquivos. A MLP usa os pixels da versão em cinza,
com normalização e Flatten. Consulte `docs/GOVERNANCA_IR_ALEM2.md` para os limites.

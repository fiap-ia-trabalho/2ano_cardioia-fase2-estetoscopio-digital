# Roteiro do vídeo — CardioIA Fase 2

**Duração alvo:** 3min50s (o limite é 4min — a folga de 10s é proposital)
**Formato:** gravação de tela com narração
**Publicação:** YouTube, **não listado**, link no README

Ritmo considerado: ~2,5 palavras por segundo. Se você fala mais devagar, corte o bloco 6
primeiro — é o mais sacrificável.

Antes de gravar: deixe abertos, em abas separadas, o repositório no GitHub, o
`01_extracao_sintomas.ipynb` e o `02_classificador_risco.ipynb`, os dois já executados.

---

## Bloco 1 — Abertura (0:00 – 0:20)

**Tela:** README no GitHub, topo da página.

> Oi, eu sou a Iraci, do grupo CardioIA. Esta é a Fase 2 do projeto: um módulo que lê
> relatos de sintomas escritos por pacientes, sugere um diagnóstico e classifica o risco.
> São duas partes. A primeira usa regras e um mapa de conhecimento. A segunda treina um
> classificador de texto. Vou mostrar as duas rodando e, no final, o que a gente
> descobriu que não funciona.

---

## Bloco 2 — Parte 1: os dados (0:20 – 0:55)

**Tela:** abrir `dados/frases_pacientes.txt`, depois `dados/mapa_conhecimento.csv`.

> Começando pelos dados. São dez relatos de pacientes, cada um dizendo o que sente,
> quando começou e como aquilo atrapalha a rotina.
>
> Repare que alguns estão sem acento e um está em caixa alta. Isso é de propósito — é o
> caso de teste da normalização.
>
> O mapa de conhecimento tem quarenta e sete linhas ligando expressões de sintoma a sete
> doenças. Além das colunas que o enunciado pediu, eu coloquei mais duas. **Peso**,
> porque "dor no peito" e "irradiou para o braço esquerdo" não podem valer a mesma coisa.
> E **origem**, dizendo se o termo veio dos textos do SciELO da Fase 1 ou se foi a equipe
> que escreveu.

---

## Bloco 3 — Parte 1: o código rodando (0:55 – 1:25)

**Tela:** notebook 01, rolar até a saída da seção 7 (tabela dos 10 relatos).

> O código normaliza o texto dos dois lados, tira acento e maiúscula, e procura as
> expressões do mapa dentro do relato.
>
> Tem uma regra que eu quero destacar: quando um termo longo casa com um trecho, aquele
> trecho fica ocupado, e um termo curto que caiba dentro dele é descartado. Sem isso,
> "falta de ar quando deito" contaria junto com "falta de ar", e o sistema inflaria a
> própria confiança sem evidência nova.
>
> Aqui está o resultado nos dez relatos. Todos recebem o diagnóstico esperado.

---

## Bloco 4 — A falha (1:25 – 1:55)

**Tela:** notebook 01, seção 8, apontar o caso 2.

> Só que acertar dez de dez aqui prova pouco, porque eu escrevi as frases e o mapa. É
> circular.
>
> Então eu testei com frases que não participaram da construção do mapa. E uma falhou.
>
> Esta aqui: "meu coração fica acelerado". O mapa tem "coração acelerado", mas a palavra
> "fica" está no meio, e a busca por trecho exige as palavras coladas. O sinal de
> arritmia se perdeu e o sistema respondeu Angina.
>
> Não é erro de digitação. É o limite do método, e ficou registrado no notebook.

---

## Bloco 5 — Parte 2: a base e o vazamento (1:55 – 2:40)

**Tela:** `dados/frases_risco.csv`, depois notebook 02 seções 2 e 9.

> Na Parte 2, oitenta frases rotuladas como alto ou baixo risco.
>
> A coluna que interessa é a terceira: **grupo semântico**. Frases que são variação da
> mesma ideia clínica ficam no mesmo grupo, e a divisão entre treino e teste é feita por
> grupo, nunca por frase.
>
> Se variações da mesma ideia caírem em lados opostos, o modelo é testado em algo que
> ele já viu, e a acurácia sobe sem ele ter melhorado. Isso se chama vazamento.
>
> E dá para medir. Dividindo por grupo, setenta e sete e meio por cento. Dividindo por
> frase, oitenta e três e oito. O vazamento infla o resultado em seis pontos.

---

## Bloco 6 — Resultados (2:40 – 3:15)

**Tela:** notebook 02, seções 5, 7 e 8.

> O TF-IDF transforma cada frase em números, e a Regressão Logística classifica.
>
> Aqui está o resultado, e eu quero ser clara sobre qual número vale. Numa divisão única
> deu noventa por cento. Mas são só vinte frases de teste. Na validação cruzada, com
> cinco divisões, dá setenta e sete e meio, mais ou menos cinco. Esse é o número que está
> no README.
>
> Para comparar, um chute burro por palavra-chave acerta sessenta por cento. Então o
> ganho real é de uns dezessete pontos.
>
> Na matriz de confusão: nenhum falso negativo, dois falsos positivos. Em triagem é a
> direção certa de errar — mas foi sorte desta divisão, não projeto.

---

## Bloco 7 — O que não funciona (3:15 – 3:40)

**Tela:** notebook 02, seção 11 (coeficientes).

> E aqui está a parte mais importante. Eu abri os pesos do modelo para ver o que ele
> usa para decidir.
>
> Os termos que mais empurram para baixo risco são "quando", "depois", "da", "um".
> Palavras sem nenhum conteúdo médico.
>
> Isso aconteceu porque as frases das duas classes saíram das mesmas pessoas, e cada
> classe ganhou um jeito de escrever. O modelo achou o estilo de redação antes de achar
> o sintoma.
>
> Na prática isso quer dizer que quem escreve diferente do nosso padrão seria
> classificado pelo jeito de escrever, e não pelo que sente.

---

## Bloco 8 — Fechamento (3:40 – 3:50)

**Tela:** README, seção de governança.

> Tudo isso está documentado no README e no arquivo de governança. O projeto mostra o
> mecanismo de um triador automático — mas não é um triador, e a gente escreveu por quê.
> Obrigada.

---

## Checklist antes de publicar

- [ ] Vídeo com no máximo 4 minutos
- [ ] Áudio audível, sem ruído de fundo forte
- [ ] Notebooks visíveis **com as saídas** na gravação
- [ ] Upload no YouTube como **não listado**
- [ ] Link colado no README, substituindo o marcador
- [ ] Repositório público antes de enviar na plataforma

---

## Se precisar cortar tempo

Na ordem: corte o Bloco 6 até "dezessete pontos" (economiza ~12s), depois encurte o
Bloco 2 falando só de uma das duas colunas extras (~8s).

**Não corte os blocos 4, 5 e 7.** São eles que mostram pensamento crítico — é o que
diferencia a entrega de um trabalho que só faz o código rodar.

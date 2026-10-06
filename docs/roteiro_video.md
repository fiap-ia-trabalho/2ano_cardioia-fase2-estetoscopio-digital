# Roteiro do vídeo - CardioIA Fase 2

Duração-alvo: **3min35s**. Limite do enunciado: **4 minutos**.
Grave a tela com narração ou legendas. Publique no YouTube como **não listado**.
Este roteiro cobre a entrega principal de texto; os desafios Ir Além têm demonstrações próprias.

## Preparação

1. Abra o README e a pasta do projeto no editor.
2. Abra os três arquivos de entrada: `frases_pacientes.txt`, `mapa_conhecimento.csv`
   e `frases_risco.csv`.
3. Abra os dois notebooks no JupyterLab. Escolha o kernel **CardioIA Fase 2 (.venv)**
   e execute tudo antes de gravar.
4. Deixe o notebook 01 na seção 8 e o notebook 02 na seção 4. Durante o vídeo,
   reexecute a célula de treinamento da seção 4; as outras saídas já estarão prontas.
5. Deixe um terminal aberto na raiz do projeto. Aumente o zoom e role devagar.

No Windows, `abrir_notebooks.bat` abre o JupyterLab no ambiente preparado.
`executar_extracao.bat` roda a Parte 1 e mantém a saída na tela.

## 1. Apresentação - 0:00 a 0:15

**Mostre:** README e integrantes.

**Fala:**
> Olá! Este é o CardioIA, Fase 2, do nosso grupo da FIAP. Criamos dois módulos:
> extração de sintomas com regras e classificação de frases em alto ou baixo risco.
> Os dados são sintéticos e o projeto é acadêmico.

## 2. Dados da Parte 1 - 0:15 a 0:35

**Mostre:** um relato completo e as colunas do mapa.

**Fala:**
> Temos dez relatos, cada um com sintomas, início e impacto na rotina.
> O mapa contém 48 associações entre expressões e sete condições. Os pesos de um a três
> foram definidos pela equipe, e a coluna de origem registra a procedência do vocabulário.

## 3. Extração funcionando - 0:35 a 1:05

**Mostre:** execute no terminal, sem depender de ativação do ambiente:

```powershell
.\.venv\Scripts\python.exe src\extracao_sintomas.py
```

Pare nos relatos **[07]** e **[01]**, depois no resumo final.

**Fala:**
> O programa normaliza acentos e maiúsculas, encontra expressões e soma os pesos por
> condição. No relato sete, encontrou dor no peito, irradiação, suor frio e enjoo,
> e sugeriu infarto. No primeiro, Angina recebeu seis pontos contra dois de infarto.
> Os 75% representam a proporção da pontuação, não probabilidade de doença.
> Sem correspondências ou com empate, o resultado é inconclusivo.

## 4. Limite da extração - 1:05 a 1:25

**Mostre:** notebook 01, seção 8, saída do caso 2.

**Fala:**
> Testamos quatro frases adicionais. Aqui, coração fica acelerado não corresponde
> a coração acelerado, porque há uma palavra no meio. A busca perde essa expressão.
> Também não interpreta negação: não sinto dor no peito ainda encontra dor no peito.
> Essas limitações estão documentadas.

## 5. Dados e divisão da Parte 2 - 1:25 a 1:45

**Mostre:** `frases_risco.csv`, distribuição das classes e ausência de grupos compartilhados.

**Fala:**
> A base de risco tem 80 frases: 40 de cada classe. Os rótulos são da equipe.
> Os grupos semânticos reúnem variações da mesma ideia, e cada grupo fica inteiro no
> treino ou no teste. O TF-IDF aprende o vocabulário somente no treinamento.

## 6. Treinamento e avaliação - 1:45 a 2:45

**Mostre:** reexecute a célula de treinamento da seção 4 e depois as saídas indicadas.

| Seção | Resultado a mostrar |
|---|---|
| 3 | TF-IDF: 60 frases por 858 termos |
| 4 | Treinamento da regressão logística e teste isolado de 90% |
| 5 | Matriz: alto risco 10/0; baixo risco 2/8 |
| 8 | Cinco divisões por grupo: 77,5% e desvio-padrão de 5 pontos |
| 8.1 | Matriz agregada: alto risco 30/10; baixo risco 8/32; baseline 58,75% |

**Fala:**
> O TF-IDF transforma palavras e pares de palavras em atributos numéricos.
> Treinamos uma regressão logística e comparamos com uma árvore de decisão e uma
> regra por palavras-chave. Neste teste isolado de 20 frases, a regressão acertou 90%,
> com dois falsos positivos e nenhum falso negativo. Na validação cruzada por grupo,
> a média foi 77,5%. Na matriz agregada, aparecem dez falsos negativos e oito falsos
> positivos. A regra simples acertou 58,75% nas mesmas divisões: diferença de
> 18,75 pontos. São resultados sobre nossos rótulos sintéticos.

## 7. Vieses e frases novas - 2:45 a 3:15

**Mostre:** notebook 02, seções 11 e 12.

**Fala:**
> Nos coeficientes, termos como quando, depois e um favorecem baixo risco.
> Isso sugere sensibilidade ao estilo de escrita, mas não mede o impacto desse viés
> na acurácia. Também testamos seis frases novas. As estimativas de probabilidade não
> foram avaliadas quanto à calibração e não representam risco clínico.

## 8. Encerramento - 3:15 a 3:35

**Mostre:** `docs/GOVERNANCA_FASE2.md` e instruções de execução no README.

**Fala:**
> A governança registra a origem dos dados e as limitações: base pequena, rótulos
> sem revisão clínica e ausência de avaliação externa e por subgrupos. O repositório
> contém código, dados, notebooks executados e instruções para reproduzir os resultados.
> O projeto demonstra os métodos, sem validação para atender pacientes. Obrigada!

## Antes de publicar

- Ensaie com cronômetro. Se ultrapassar 3min50s, reduza a fala para ter margem.
- Confira se os números estão legíveis e se a voz ou as legendas estão claras.
- Confira a duração final, até 4 minutos.
- Publique como **não listado**, teste o acesso ao link e inclua-o no README.
- A entrega da atividade ocorre na plataforma da FIAP, no formato solicitado nela.

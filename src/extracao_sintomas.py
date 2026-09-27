"""
CardioIA - Fase 2 - Parte 1
Extração de sintomas a partir de relatos de pacientes e sugestão de diagnóstico.

Lê:
  dados/frases_pacientes.txt   -> 10 relatos de pacientes (um por linha)
  dados/mapa_conhecimento.csv  -> mapa sintoma -> doença, com peso e origem

Escreve:
  dados/resultado_extracao.csv -> uma linha por relato, com sintomas achados,
                                  diagnóstico sugerido e nível de confiança

Dependências: pandas + biblioteca padrão do Python.

AVISO: este é um exercício acadêmico. O resultado é uma sugestão baseada em
busca de palavras, não um diagnóstico médico.
"""

import csv
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd

# Pastas do projeto: este arquivo mora em src/, então a raiz é a pasta de cima.
RAIZ = Path(__file__).resolve().parent.parent
ARQ_FRASES = RAIZ / "dados" / "frases_pacientes.txt"
ARQ_MAPA = RAIZ / "dados" / "mapa_conhecimento.csv"
ARQ_SAIDA = RAIZ / "dados" / "resultado_extracao.csv"

# Se nenhum termo do mapa aparecer no relato, não inventamos diagnóstico.
ROTULO_INCONCLUSIVO = "Inconclusivo - encaminhar para avaliação humana"


# ---------------------------------------------------------------------------
# 1. Normalização
# ---------------------------------------------------------------------------
def normalizar(texto):
    """Deixa o texto em um formato único para comparação.

    Faz quatro coisas, nesta ordem:
      1. separa a letra do acento (NFKD: "ç" vira "c" + cedilha solta);
      2. joga fora os acentos soltos;
      3. passa tudo para minúsculo;
      4. troca pontuação por espaço e colapsa espaços repetidos.

    Por que isso importa: os relatos reais têm "coracao" e "coração",
    "CANSAÇO CONSTANTE" e "cansaço constante". Sem normalizar, o mesmo
    sintoma seria tratado como duas coisas diferentes e o sistema erraria.

    >>> normalizar("CANSAÇO  constante!")
    'cansaco constante'
    """
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


# ---------------------------------------------------------------------------
# 2. Leitura dos arquivos
# ---------------------------------------------------------------------------
def carregar_frases(caminho=ARQ_FRASES):
    """Lê o .txt e devolve uma lista de relatos, ignorando linhas em branco."""
    with open(caminho, encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]


def carregar_mapa(caminho=ARQ_MAPA):
    """Lê o mapa de conhecimento e devolve uma lista de termos prontos para busca.

    Cada linha do CSV tem duas expressões (sintoma_1 e sintoma_2) que apontam
    para a mesma doença. Nós "achatamos" isso: cada expressão vira um termo
    independente, já normalizado, carregando a doença, o peso e a origem.

    O peso (1 a 3) existe porque nem todo sintoma vale o mesmo. "Dor no peito"
    é inespecífica (peso 2); "irradiou para o braço esquerdo" é muito mais
    sugestiva de infarto (peso 3).
    """
    mapa = pd.read_csv(caminho)

    colunas_esperadas = {"sintoma_1", "sintoma_2", "doenca_associada", "peso", "origem"}
    faltando = colunas_esperadas - set(mapa.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes no mapa de conhecimento: {faltando}")

    termos = []
    for _, linha in mapa.iterrows():
        for coluna in ("sintoma_1", "sintoma_2"):
            expressao = str(linha[coluna]).strip()
            if not expressao or expressao.lower() == "nan":
                continue
            termos.append(
                {
                    "expressao": expressao,
                    "expressao_norm": normalizar(expressao),
                    "doenca": linha["doenca_associada"],
                    "peso": int(linha["peso"]),
                    "origem": linha["origem"],
                }
            )

    # Ordena do termo mais longo para o mais curto. Isso é importante para o
    # passo seguinte: queremos que "falta de ar quando deito" seja testado
    # ANTES de "falta de ar", para não contar o mesmo trecho duas vezes.
    termos.sort(key=lambda t: len(t["expressao_norm"]), reverse=True)
    return termos


# ---------------------------------------------------------------------------
# 3. Extração de sintomas de um relato
# ---------------------------------------------------------------------------
def extrair_sintomas(relato, termos):
    """Procura no relato todas as expressões do mapa de conhecimento.

    Regra anti-contagem-dupla: quando um termo longo casa com um trecho do
    relato, aquele trecho fica "ocupado". Um termo mais curto que caia inteiro
    dentro de um trecho já ocupado é descartado.

    Exemplo: no relato "estou com falta de ar quando deito", o termo
    "falta de ar quando deito" (peso 3) casa primeiro. O termo "falta de ar"
    (peso 2) cairia dentro dele, então é ignorado. Sem essa regra, a
    Insuficiência Cardíaca somaria 5 pontos onde deveria somar 3, e a
    confiança do sistema ficaria artificialmente inflada.
    """
    relato_norm = normalizar(relato)
    trechos_ocupados = []  # lista de pares (inicio, fim)
    achados = []

    for termo in termos:
        posicao = relato_norm.find(termo["expressao_norm"])
        if posicao == -1:
            continue

        inicio, fim = posicao, posicao + len(termo["expressao_norm"])
        dentro_de_outro = any(ini <= inicio and fim <= f for ini, f in trechos_ocupados)
        if dentro_de_outro:
            continue

        trechos_ocupados.append((inicio, fim))
        achados.append(termo)

    # Devolve na ordem em que aparecem no relato, que é mais fácil de ler.
    achados.sort(key=lambda t: relato_norm.find(t["expressao_norm"]))
    return achados


# ---------------------------------------------------------------------------
# 4. Sugestão de diagnóstico
# ---------------------------------------------------------------------------
def sugerir_diagnostico(achados):
    """Soma os pesos por doença e devolve a mais pontuada.

    Devolve um dicionário com:
      diagnostico  -> doença vencedora (ou 'Inconclusivo...')
      pontuacao    -> soma dos pesos da vencedora
      confianca    -> pontuação da vencedora / soma de todas as pontuações
      placar       -> lista completa (doença, pontos), da maior para a menor
      empate       -> True se duas ou mais doenças empataram na frente

    A "confiança" NÃO é probabilidade. É só a fatia da evidência que aponta
    para a doença vencedora. Um valor de 1.0 significa "todos os sintomas
    encontrados apontam para a mesma doença", e não "temos certeza".
    """
    if not achados:
        return {
            "diagnostico": ROTULO_INCONCLUSIVO,
            "pontuacao": 0,
            "confianca": 0.0,
            "placar": [],
            "empate": False,
        }

    placar = defaultdict(int)
    for termo in achados:
        placar[termo["doenca"]] += termo["peso"]

    ordenado = sorted(placar.items(), key=lambda par: par[1], reverse=True)
    doenca_topo, pontos_topo = ordenado[0]
    total = sum(placar.values())
    empate = len(ordenado) > 1 and ordenado[1][1] == pontos_topo

    return {
        "diagnostico": doenca_topo if not empate else ROTULO_INCONCLUSIVO,
        "pontuacao": pontos_topo,
        "confianca": round(pontos_topo / total, 2),
        "placar": ordenado,
        "empate": empate,
    }


# ---------------------------------------------------------------------------
# 5. Processa todos os relatos e monta a tabela final
# ---------------------------------------------------------------------------
def analisar_relatos(relatos, termos):
    """Roda a extração e a sugestão para cada relato, devolvendo um DataFrame."""
    linhas = []
    for numero, relato in enumerate(relatos, start=1):
        achados = extrair_sintomas(relato, termos)
        resultado = sugerir_diagnostico(achados)

        linhas.append(
            {
                "id_relato": numero,
                "relato": relato,
                "sintomas_encontrados": "; ".join(t["expressao"] for t in achados),
                "qtd_sintomas": len(achados),
                "diagnostico_sugerido": resultado["diagnostico"],
                "pontuacao": resultado["pontuacao"],
                "confianca": resultado["confianca"],
                "placar_completo": " | ".join(
                    f"{doenca}:{pontos}" for doenca, pontos in resultado["placar"]
                ),
                "origens_consultadas": "; ".join(
                    sorted({t["origem"] for t in achados})
                ),
            }
        )

    return pd.DataFrame(linhas)


def imprimir_relatorio(df):
    """Mostra o resultado no terminal em formato legível."""
    for _, linha in df.iterrows():
        print(f"\n[{linha['id_relato']:02d}] {linha['relato']}")
        print(f"     sintomas    : {linha['sintomas_encontrados'] or '(nenhum)'}")
        print(f"     diagnóstico : {linha['diagnostico_sugerido']}")
        print(f"     confiança   : {linha['confianca']:.0%}  ({linha['placar_completo']})")


def main():
    termos = carregar_mapa()
    relatos = carregar_frases()

    print(f"Mapa de conhecimento: {len(termos)} expressões carregadas.")
    print(f"Relatos de pacientes: {len(relatos)} frases carregadas.")

    df = analisar_relatos(relatos, termos)
    df.to_csv(ARQ_SAIDA, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)

    imprimir_relatorio(df)

    inconclusivos = (df["diagnostico_sugerido"] == ROTULO_INCONCLUSIVO).sum()
    print(f"\nResumo: {len(df) - inconclusivos} sugestões / {inconclusivos} inconclusivos.")
    print(f"Arquivo gerado: {ARQ_SAIDA}")
    print("\nLembrete: sistema de apoio acadêmico. Não substitui avaliação médica.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

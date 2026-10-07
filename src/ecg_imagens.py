"""Leitura validada dos sinais públicos e geração de imagens, sem usar o rótulo no desenho."""

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

IMAGE_SIZE = (64, 64)
CLASS_NAMES = {0: "N", 1: "S", 2: "V", 3: "F", 4: "Q"}


def carregar_csv(path):
    """Retorna as 187 amplitudes normalizadas e o rótulo original de cada linha."""
    path = Path(path)
    if not path.is_file() and path.with_suffix(path.suffix + ".gz").is_file():
        path = path.with_suffix(path.suffix + ".gz")
    if not path.is_file():
        raise FileNotFoundError(
            f"Base ausente: {path}. Execute python src/baixar_ecg.py na raiz do projeto."
        )
    frame = pd.read_csv(path, header=None, dtype=np.float32)
    if frame.shape[1] != 188 or frame.empty:
        raise ValueError("O CSV deve ter 187 amostras de sinal e uma coluna de rótulo, sem cabeçalho.")
    values = frame.to_numpy(copy=False)
    if not np.isfinite(values).all():
        raise ValueError("A base contém valores ausentes ou não finitos.")
    signals, labels = values[:, :187], values[:, 187]
    if not np.isin(labels, list(CLASS_NAMES)).all():
        raise ValueError("Os rótulos devem ser os códigos inteiros 0, 1, 2, 3 ou 4.")
    if signals.min() < 0 or signals.max() > 1:
        raise ValueError("Esperavam-se amplitudes previamente normalizadas entre zero e um.")
    return signals, labels.astype(np.int32)


def separar_classes(signals, original_labels):
    """N -> 0; S/V/F -> 1. Q é excluída por ser a categoria de batimentos não classificados."""
    mask = original_labels != 4
    return signals[mask], (original_labels[mask] != 0).astype(np.int32), np.flatnonzero(mask)


def amostra_balanceada(labels, por_classe=6000, seed=42):
    """Seleção determinística sem reposição; o conjunto de teste não é balanceado."""
    rng = np.random.default_rng(seed)
    selected = []
    for label in (0, 1):
        pool = np.flatnonzero(labels == label)
        if len(pool) < por_classe:
            raise ValueError(f"A classe {label} tem menos de {por_classe} exemplos.")
        selected.extend(rng.choice(pool, size=por_classe, replace=False))
    return np.sort(np.array(selected, dtype=np.int32))


def rasterizar_sinal(signal):
    """Traçado derivado do CSV em RGB 256x256, sem eixos, texto, rótulo ou decoração."""
    signal = np.asarray(signal, dtype=np.float32)
    if signal.shape != (187,) or not np.isfinite(signal).all():
        raise ValueError("Cada batimento deve conter 187 amplitudes finitas.")
    if signal.min() < 0 or signal.max() > 1:
        raise ValueError("As amplitudes devem estar entre zero e um.")
    image = Image.new("RGB", (256, 256), "white")
    xs = np.linspace(4, 251, len(signal))
    ys = 251 - signal * 247
    ImageDraw.Draw(image).line([(float(x), float(y)) for x, y in zip(xs, ys)], fill="black", width=4)
    return image


def preprocessar_imagem(image):
    """Converte para tons de cinza e redimensiona para o formato de entrada da MLP."""
    gray = image.convert("L").resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
    return np.asarray(gray, dtype=np.uint8)[..., None]


def sinais_para_imagens(signals, descricao="Base"):
    """Mantém pixels em uint8; a normalização float32 é feita em lotes na rede."""
    images = np.empty((len(signals), 64, 64, 1), dtype=np.uint8)
    for index, signal in enumerate(signals):
        images[index] = preprocessar_imagem(rasterizar_sinal(signal))
        if (index + 1) % 4000 == 0:
            print(f"{descricao}: {index + 1}/{len(signals)} imagens", flush=True)
    return images


def hash_sinais(signals):
    """Identifica duplicatas exatas de amplitudes, sem depender dos nomes de arquivos."""
    return [hashlib.sha256(np.asarray(row, dtype="<f4").tobytes()).hexdigest() for row in signals]

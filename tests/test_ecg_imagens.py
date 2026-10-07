"""Verifica o formato de dados, o mapeamento de classes e a transformação visual."""
import sys
import tempfile
import gzip
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ecg_imagens import (
    amostra_balanceada, carregar_csv, preprocessar_imagem,
    rasterizar_sinal, separar_classes, hash_sinais,
)


class ECGTests(unittest.TestCase):
    def test_q_nao_e_tratada_como_anomalia_confirmada(self):
        signals = np.zeros((5, 187), dtype=np.float32)
        result, labels, indices = separar_classes(signals, np.arange(5))
        self.assertEqual(result.shape, (4, 187))
        self.assertEqual(labels.tolist(), [0, 1, 1, 1])
        self.assertEqual(indices.tolist(), [0, 1, 2, 3])

    def test_imagem_e_cinza_64_por_64_sem_metadados_de_classe(self):
        signal = np.linspace(0, 1, 187, dtype=np.float32)
        original = rasterizar_sinal(signal)
        image = preprocessar_imagem(original)
        self.assertEqual(original.mode, "RGB")
        self.assertEqual(image.shape, (64, 64, 1))
        self.assertEqual(image.dtype, np.uint8)
        self.assertGreater(np.ptp(image), 0)
        self.assertTrue(np.array_equal(image, preprocessar_imagem(rasterizar_sinal(signal.copy()))))
        self.assertFalse(np.array_equal(image, preprocessar_imagem(rasterizar_sinal(signal[::-1]))))

    def test_amostra_e_balanceada_sem_reposicao_e_reproduzivel(self):
        labels = np.array([0] * 20 + [1] * 10)
        selected = amostra_balanceada(labels, por_classe=6)
        self.assertEqual(len(set(selected)), 12)
        self.assertEqual(np.bincount(labels[selected]).tolist(), [6, 6])
        self.assertTrue(np.array_equal(selected, amostra_balanceada(labels, por_classe=6)))
        with self.assertRaises(ValueError):
            amostra_balanceada(labels, por_classe=11)

    def test_csv_sem_cabecalho_validado_e_entrada_invalida_rejeitada(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ecg.csv"
            frame = pd.DataFrame(np.zeros((2, 188)))
            frame.iloc[1, -1] = 2
            frame.to_csv(path, index=False, header=False)
            signals, labels = carregar_csv(path)
            self.assertEqual(signals.shape, (2, 187))
            self.assertEqual(labels.tolist(), [0, 2])
            compressed = path.with_suffix(".csv.gz")
            with gzip.open(compressed, "wb") as stream:
                stream.write(path.read_bytes())
            path.unlink()
            zipped_signals, zipped_labels = carregar_csv(path)
            self.assertTrue(np.array_equal(signals, zipped_signals))
            self.assertTrue(np.array_equal(labels, zipped_labels))
            frame.iloc[1, -1] = 1.5
            frame.to_csv(path, index=False, header=False)
            with self.assertRaises(ValueError):
                carregar_csv(path)
            with self.assertRaises(FileNotFoundError):
                carregar_csv(Path(directory) / "ausente.csv")

    def test_sinal_invalido_e_rejeitado(self):
        for signal in (np.zeros(186), np.full(187, np.nan), np.full(187, 1.1)):
            with self.assertRaises(ValueError):
                rasterizar_sinal(signal)

    def test_hash_identifica_duplicata_exata(self):
        values = np.array([np.zeros(187), np.ones(187), np.zeros(187)], dtype=np.float32)
        hashes = hash_sinais(values)
        self.assertEqual(hashes[0], hashes[2])
        self.assertNotEqual(hashes[0], hashes[1])


if __name__ == "__main__":
    unittest.main()

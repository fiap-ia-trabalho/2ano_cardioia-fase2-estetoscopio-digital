"""Executa o notebook ECG do zero e salva suas saídas somente se concluir sem erro."""
from pathlib import Path
import os
import sys

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
os.environ["PYTHONHASHSEED"] = "0"  # Aplicado ao novo processo do kernel.

import nbformat
from nbclient import NotebookClient


def main():
    root = Path(__file__).resolve().parents[1]
    path = root / "notebooks" / "03_diagnostico_visual.ipynb"
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None

    def started(**kwargs):
        if kwargs["cell"].cell_type == "code":
            print(f"Executando célula {kwargs['cell_index'] + 1}...", flush=True)

    def completed(**kwargs):
        if kwargs["cell"].cell_type == "code":
            for output in kwargs["cell"].get("outputs", []):
                if output.output_type == "stream" and output.name == "stdout":
                    print(output.text, end="", flush=True)

    client = NotebookClient(notebook, timeout=1800, kernel_name="cardioia-ecg",
        resources={"metadata": {"path": str(root / "notebooks")}},
        allow_errors=False, on_cell_start=started, on_cell_executed=completed)
    client.execute()
    nbformat.validate(notebook)
    codes = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert [c.execution_count for c in codes] == list(range(1, len(codes) + 1))
    nbformat.write(notebook, path)
    print("Notebook ECG executado em ordem e salvo sem erros.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())

"""Baixa somente os CSVs MIT-BIH da versão 1 da base pública recomendada pela FIAP."""

from pathlib import Path
import hashlib
import gzip
import json
import shutil
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados"
FILES = ("mitbih_train.csv", "mitbih_test.csv")
URL = "https://www.kaggle.com/api/v1/datasets/download/shayanfazeli/heartbeat?datasetVersionNumber=1"


def sha256(path):
    digest = hashlib.sha256()
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def arquivo_local(name):
    compressed = DATA / (name + ".gz")
    return compressed if compressed.is_file() else DATA / name


def main():
    DATA.mkdir(exist_ok=True)
    manifest_path = DATA / "ecg_origem.json"
    if not manifest_path.is_file():
        raise FileNotFoundError("ecg_origem.json ausente. Baixe o repositório completo, com o manifesto da base.")
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    if all(arquivo_local(name).is_file() for name in FILES):
        for name in FILES:
            if sha256(arquivo_local(name)) != expected["arquivos"][name]["sha256"]:
                raise ValueError(f"O arquivo {name} difere da versão usada na validação.")
        print("Os dois CSVs já estão disponíveis e foram conferidos.")
        return 0

    # O ZIP temporário é apagado ao terminar; CSVs grandes ficam fora do Git.
    if shutil.disk_usage(ROOT).free < 200 * 1024 * 1024:
        raise OSError("São necessários ao menos 200 MB livres para preparar a base compactada.")
    temp = ROOT / "tmp" / "heartbeat-v1.zip.part"
    temp.parent.mkdir(exist_ok=True)
    request = urllib.request.Request(URL, headers={"User-Agent": "CardioIA-Academic/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response, temp.open("wb") as output:
            downloaded = 0
            last_progress = 0
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
                downloaded += len(chunk)
                if downloaded - last_progress >= 25 * 1024 * 1024:
                    print(f"Base recebida: {downloaded // (1024 * 1024)} MB", flush=True)
                    last_progress = downloaded
        if not zipfile.is_zipfile(temp):
            raise ValueError("A resposta do Kaggle não é um ZIP. Baixe a versão 1 pelo link do README.")
        with zipfile.ZipFile(temp) as archive:
            for name in FILES:
                matches = [i for i in archive.infolist() if Path(i.filename).name == name]
                if len(matches) != 1:
                    raise ValueError(f"O ZIP não contém exatamente um {name}.")
                info = matches[0]
                if info.file_size > 700 * 1024 * 1024:
                    raise ValueError(f"Tamanho inesperado para {name}.")
                # Extrai apenas nomes conhecidos, sem seguir caminhos recebidos no ZIP.
                partial = DATA / (name + ".gz.part")
                with archive.open(info) as source, partial.open("wb") as raw_target, gzip.GzipFile(filename="", mode="wb", fileobj=raw_target, mtime=0) as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
                partial.replace(DATA / (name + ".gz"))
                print(f"Disponível: dados/{name}.gz", flush=True)
        hashes = {name: {"sha256": sha256(arquivo_local(name))} for name in FILES}
        for name in FILES:
            if hashes[name]["sha256"] != expected["arquivos"][name]["sha256"]:
                raise ValueError(f"O download de {name} não corresponde ao manifesto versionado.")
        print("Download concluído. Conteúdo conferido contra dados/ecg_origem.json.")
    finally:
        temp.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Não foi possível preparar a base: {error}", file=sys.stderr)
        raise SystemExit(1)

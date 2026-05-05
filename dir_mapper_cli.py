"""
dir_mapper_cli.py — Entry point empacotado pelo PyInstaller.
Lê um JSON de stdin com os parâmetros e imprime o resultado em JSON no stdout.

Build:
    pyinstaller --onefile --name dir_mapper --noconsole dir_mapper_cli.py
    (ou com --console se quiser ver erros)

Uso (igual ao chamado pelo main.js):
    echo '{"path":"C:\\\\foo","format_type":"uml"}' | dir_mapper.exe
"""
import sys
import io
import json

# Garante UTF-8 no stdout/stderr mesmo no Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dir_mapper import map_directory_api


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"error": "Nenhum input recebido"}))
            return 1
        data = json.loads(raw)
        result_json = map_directory_api(
            path=data.get("path", ""),
            hidden_folders=data.get("hidden_folders", "") or "",
            hidden_extensions=data.get("hidden_extensions", "") or "",
            hide_files=bool(data.get("hide_files", False)),
            max_depth=data.get("max_depth"),
            format_type=data.get("format_type", "uml") or "uml",
            max_items=data.get("max_items"),
        )
        # map_directory_api já retorna uma string JSON
        sys.stdout.write(result_json)
        sys.stdout.flush()
        return 0
    except Exception as e:
        sys.stderr.write(f"ERRO: {e}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())

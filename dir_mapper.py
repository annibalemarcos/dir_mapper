"""
DIR MAP - Backend de varredura de diretórios
v0.2 - Versão estável com proteção contra travamento em diretórios gigantes
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any


# Pastas comumente pesadas que NUNCA devem ser varridas a menos que o usuário
# explicitamente queira. São adicionadas como ignoradas por padrão na UI.
DEFAULT_HEAVY_FOLDERS = [
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache", "target", ".idea",
    ".vscode", ".pytest_cache", ".mypy_cache", "coverage",
]

# Limites duros de segurança para impedir que a aplicação trave
# mesmo se o usuário esquecer de configurar filtros.
DEFAULT_MAX_ITEMS = 100_000      # itens (arquivos+pastas) totais
DEFAULT_MAX_DEPTH_HARD = 50      # profundidade máxima absoluta


class ScanLimitExceeded(Exception):
    """Disparada quando os limites de segurança são atingidos."""
    pass


class DirectoryMapper:
    def __init__(self):
        self.hidden_folders: List[str] = []
        self.hidden_extensions: List[str] = []
        self.hide_files: bool = False
        self.max_depth: Optional[int] = None
        self.max_items: int = DEFAULT_MAX_ITEMS
        self._items_seen: int = 0
        self._truncated: bool = False

    def set_filters(
        self,
        hidden_folders: str = "",
        hidden_extensions: str = "",
        hide_files: bool = False,
        max_depth: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> None:
        self.hidden_folders = [f.strip() for f in hidden_folders.split(",") if f.strip()]
        self.hidden_extensions = [
            e.strip().lower().lstrip(".") for e in hidden_extensions.split(",") if e.strip()
        ]
        self.hide_files = hide_files
        self.max_depth = max_depth
        if max_items is not None and max_items > 0:
            self.max_items = max_items

    def _should_skip(self, name: str, is_file: bool) -> bool:
        if is_file and self.hide_files:
            return True
        if not is_file and name in self.hidden_folders:
            return True
        if is_file and self.hidden_extensions:
            ext = Path(name).suffix.lower().lstrip(".")
            if ext in self.hidden_extensions:
                return True
        return False

    def scan_directory(self, root_path: str) -> Dict[str, Any]:
        """Varre o diretório de forma iterativa (sem recursão profunda) usando os.scandir."""
        root = Path(root_path)
        if not root.exists():
            return {"error": "Diretório não encontrado"}
        if not root.is_dir():
            return {"error": "Caminho não é um diretório"}

        self._items_seen = 0
        self._truncated = False

        max_depth = self.max_depth if self.max_depth is not None else DEFAULT_MAX_DEPTH_HARD
        max_depth = min(max_depth, DEFAULT_MAX_DEPTH_HARD)

        result: Dict[str, Any] = {
            "name": root.name or str(root),
            "type": "directory",
            "children": [],
        }

        # Pilha iterativa: (Path, node, depth)
        stack = [(root, result, 0)]

        try:
            while stack:
                current_path, current_node, depth = stack.pop()

                if depth >= max_depth:
                    continue

                try:
                    with os.scandir(current_path) as entries:
                        items = list(entries)
                except PermissionError:
                    current_node["error"] = "Permissão negada"
                    continue
                except OSError:
                    continue

                # Ordena: pastas primeiro, depois arquivos, ambos alfabéticos
                items.sort(key=lambda e: (e.is_file(follow_symlinks=False), e.name.lower()))

                for entry in items:
                    try:
                        is_file = entry.is_file(follow_symlinks=False)
                        is_dir = entry.is_dir(follow_symlinks=False)
                    except OSError:
                        continue

                    if not is_file and not is_dir:
                        continue  # ignora symlinks/sockets

                    if self._should_skip(entry.name, is_file):
                        continue

                    self._items_seen += 1
                    if self._items_seen > self.max_items:
                        self._truncated = True
                        raise ScanLimitExceeded()

                    if is_file:
                        current_node["children"].append({"name": entry.name, "type": "file"})
                    else:
                        child_node = {
                            "name": entry.name,
                            "type": "directory",
                            "children": [],
                        }
                        current_node["children"].append(child_node)
                        stack.append((Path(entry.path), child_node, depth + 1))
        except ScanLimitExceeded:
            pass

        result["_meta"] = {
            "items_seen": self._items_seen,
            "truncated": self._truncated,
            "max_items": self.max_items,
        }
        return result

    # ----- formatadores -----
    def generate_uml(self, data: Dict[str, Any]) -> str:
        if "error" in data and "children" not in data:
            return f"Erro: {data['error']}\n"

        lines: List[str] = []
        meta = data.get("_meta") or {}

        def walk(node: Dict[str, Any], prefix: str, is_last: bool, is_root: bool) -> None:
            name = node.get("name", "root")
            if is_root:
                lines.append(f"{name}/\n")
            else:
                connector = "└── " if is_last else "├── "
                suffix = "/" if node.get("type") == "directory" else ""
                lines.append(f"{prefix}{connector}{name}{suffix}\n")

            children = node.get("children", []) or []
            for i, child in enumerate(children):
                last = i == len(children) - 1
                if is_root:
                    new_prefix = ""
                else:
                    new_prefix = prefix + ("    " if is_last else "│   ")
                walk(child, new_prefix, last, False)

        walk(data, "", True, True)

        if meta.get("truncated"):
            lines.append(
                f"\n... [TRUNCADO: limite de {meta.get('max_items')} itens atingido. "
                f"Aplique filtros para continuar.]\n"
            )
        return "".join(lines)

    def generate_json(self, data: Dict[str, Any]) -> str:
        clean = self._strip_meta(data)
        return json.dumps(clean, indent=2, ensure_ascii=False)

    def generate_diagram(self, data: Dict[str, Any]) -> str:
        if "error" in data and "children" not in data:
            return f"Erro: {data['error']}\n"

        lines: List[str] = []

        def walk(node: Dict[str, Any], level: int) -> None:
            name = node.get("name", "root")
            indent = "  " * level
            box_width = max(len(name) + 2, 9)
            lines.append(f"{indent}┌{'─' * box_width}┐\n")
            lines.append(f"{indent}│{name.center(box_width)}│\n")
            lines.append(f"{indent}└{'─' * box_width}┘\n")

            children = node.get("children", []) or []
            if children:
                lines.append(f"{indent}{' ' * (box_width // 2)}│\n")
                for child in children:
                    if child.get("type") == "directory":
                        walk(child, level + 1)
                    else:
                        file_indent = "  " * (level + 1)
                        lines.append(f"{file_indent}• {child['name']}\n")

        walk(data, 0)
        if (data.get("_meta") or {}).get("truncated"):
            lines.append(
                f"\n... [TRUNCADO: limite de itens atingido. Aplique filtros.]\n"
            )
        return "".join(lines)

    def _strip_meta(self, node: Dict[str, Any]) -> Dict[str, Any]:
        out = {k: v for k, v in node.items() if k != "_meta"}
        if "children" in out and out["children"]:
            out["children"] = [self._strip_meta(c) for c in out["children"]]
        return out

    def map_directory(self, path: str, format_type: str = "uml") -> Dict[str, Any]:
        started = time.time()
        data = self.scan_directory(path)
        elapsed = time.time() - started

        ft = (format_type or "uml").lower()
        if ft == "json":
            content = self.generate_json(data)
        elif ft == "diagram":
            content = self.generate_diagram(data)
        else:
            content = self.generate_uml(data)

        meta = data.get("_meta") or {}
        return {
            "content": content,
            "items": meta.get("items_seen", 0),
            "truncated": bool(meta.get("truncated")),
            "elapsed_ms": int(elapsed * 1000),
            "error": data.get("error") if "children" not in data else None,
        }


# API para integração com Electron
def map_directory_api(
    path: str,
    hidden_folders: str = "",
    hidden_extensions: str = "",
    hide_files: bool = False,
    max_depth: Optional[int] = None,
    format_type: str = "uml",
    max_items: Optional[int] = None,
) -> str:
    """Retorna JSON string com {content, items, truncated, elapsed_ms, error}"""
    mapper = DirectoryMapper()
    mapper.set_filters(
        hidden_folders=hidden_folders,
        hidden_extensions=hidden_extensions,
        hide_files=hide_files,
        max_depth=max_depth,
        max_items=max_items,
    )
    payload = mapper.map_directory(path, format_type)
    return json.dumps(payload, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dir_mapper.py <caminho> [formato]")
        sys.exit(1)
    path = sys.argv[1]
    fmt = sys.argv[2] if len(sys.argv) > 2 else "uml"
    print(map_directory_api(path, format_type=fmt))

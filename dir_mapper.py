"""
DIR MAP - Backend de varredura de diretórios
v0.3.2 - Dashboard com tamanho real independente dos filtros
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

DEFAULT_HEAVY_FOLDERS = [
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache", "target", ".idea",
    ".vscode", ".pytest_cache", ".mypy_cache", "coverage",
]

DEFAULT_MAX_ITEMS = 100_000
DEFAULT_MAX_DEPTH_HARD = 50
TOP_LIMIT = 12


class ScanLimitExceeded(Exception):
    """Disparada quando os limites de segurança são atingidos."""
    pass


def human_size(num: int) -> str:
    try:
        value = float(num or 0)
    except Exception:
        value = 0.0
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} PB"


class DirectoryMapper:
    def __init__(self):
        self.hidden_folders: List[str] = []
        self.hidden_extensions: List[str] = []
        self.hide_files: bool = False
        self.max_depth: Optional[int] = None
        self.max_items: int = DEFAULT_MAX_ITEMS
        self._items_seen: int = 0
        self._truncated: bool = False
        self._stats: Dict[str, Any] = {}

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
            self.max_items = int(max_items)

    def _reset_stats(self, root: Path) -> None:
        self._items_seen = 0
        self._truncated = False
        self._stats = {
            "root": str(root),
            "root_name": root.name or str(root),
            "total_size": 0,
            "total_size_human": "0 B",
            "files": 0,
            "directories": 1,  # inclui a raiz
            "skipped": 0,
            "permission_errors": 0,
            "max_depth_reached": 0,
            "extensions": {},
            "largest_files": [],
            "largest_dirs": [],
            "avg_file_size": 0,
            "avg_file_size_human": "0 B",
        }

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

    def _tick_item(self) -> bool:
        self._items_seen += 1
        if self._items_seen > self.max_items:
            self._truncated = True
            return False
        return True

    def _push_top(self, bucket: str, item: Dict[str, Any]) -> None:
        arr = self._stats[bucket]
        arr.append(item)
        arr.sort(key=lambda x: x.get("size", 0), reverse=True)
        del arr[TOP_LIMIT:]


    def _measure_full_tree(self, path: Path, depth: int = 0) -> Dict[str, Any]:
        """Mede a pasta real, sem aplicar filtros visuais.

        O mapa pode ocultar node_modules/dist/build/etc., mas o dashboard deve mostrar
        o tamanho real do diretório no disco. Assim o número bate com as Propriedades do Windows.
        Symlinks/junctions não são seguidos para evitar loops e contagens fantasma.
        """
        stats = {
            "size": 0,
            "files": 0,
            "directories": 1,
            "permission_errors": 0,
            "max_depth": depth,
        }
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            try:
                                stats["size"] += int(entry.stat(follow_symlinks=False).st_size)
                            except OSError:
                                pass
                            stats["files"] += 1
                        elif entry.is_dir(follow_symlinks=False):
                            child = self._measure_full_tree(Path(entry.path), depth + 1)
                            stats["size"] += child["size"]
                            stats["files"] += child["files"]
                            stats["directories"] += child["directories"]
                            stats["permission_errors"] += child["permission_errors"]
                            stats["max_depth"] = max(stats["max_depth"], child["max_depth"])
                    except OSError:
                        stats["permission_errors"] += 1
        except PermissionError:
            stats["permission_errors"] += 1
        except OSError:
            stats["permission_errors"] += 1
        return stats

    def _scan_node(self, path: Path, depth: int, max_depth: int, rel: str) -> Tuple[Dict[str, Any], int]:
        node: Dict[str, Any] = {
            "name": path.name or str(path),
            "type": "directory",
            "children": [],
            "size": 0,
            "size_human": "0 B",
        }
        self._stats["max_depth_reached"] = max(self._stats["max_depth_reached"], depth)

        if depth >= max_depth:
            return node, 0

        try:
            with os.scandir(path) as entries:
                items = list(entries)
        except PermissionError:
            node["error"] = "Permissão negada"
            self._stats["permission_errors"] += 1
            return node, 0
        except OSError as exc:
            node["error"] = str(exc) or "Erro de leitura"
            return node, 0

        items.sort(key=lambda e: (e.is_file(follow_symlinks=False), e.name.lower()))

        total = 0
        for entry in items:
            if self._truncated:
                break
            try:
                is_file = entry.is_file(follow_symlinks=False)
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                self._stats["skipped"] += 1
                continue

            if not is_file and not is_dir:
                self._stats["skipped"] += 1
                continue

            if self._should_skip(entry.name, is_file):
                self._stats["skipped"] += 1
                continue

            if not self._tick_item():
                break
            child_rel = f"{rel}/{entry.name}" if rel else entry.name

            if is_file:
                try:
                    size = int(entry.stat(follow_symlinks=False).st_size)
                except OSError:
                    size = 0
                ext = Path(entry.name).suffix.lower().lstrip(".") or "[sem extensão]"
                ext_data = self._stats["extensions"].setdefault(ext, {"count": 0, "size": 0})
                ext_data["count"] += 1
                ext_data["size"] += size
                self._stats["files"] += 1
                total += size
                file_node = {
                    "name": entry.name,
                    "type": "file",
                    "size": size,
                    "size_human": human_size(size),
                }
                node["children"].append(file_node)
                self._push_top("largest_files", {
                    "name": entry.name,
                    "path": child_rel,
                    "size": size,
                    "size_human": human_size(size),
                })
            else:
                self._stats["directories"] += 1
                child_node, child_size = self._scan_node(Path(entry.path), depth + 1, max_depth, child_rel)
                total += child_size
                node["children"].append(child_node)

        node["size"] = total
        node["size_human"] = human_size(total)
        self._push_top("largest_dirs", {
            "name": node["name"],
            "path": rel or node["name"],
            "size": total,
            "size_human": human_size(total),
            "children": len(node.get("children", [])),
        })
        return node, total

    def _finalize_stats(self, total_size: int) -> None:
        self._stats["total_size"] = total_size
        self._stats["total_size_human"] = human_size(total_size)
        files = max(int(self._stats.get("files", 0)), 0)
        avg = int(total_size / files) if files else 0
        self._stats["avg_file_size"] = avg
        self._stats["avg_file_size_human"] = human_size(avg)
        ext_rows = []
        for ext, data in self._stats.get("extensions", {}).items():
            size = int(data.get("size", 0))
            ext_rows.append({
                "extension": ext,
                "count": int(data.get("count", 0)),
                "size": size,
                "size_human": human_size(size),
            })
        ext_rows.sort(key=lambda x: (x["size"], x["count"]), reverse=True)
        self._stats["top_extensions"] = ext_rows[:TOP_LIMIT]

    def scan_directory(self, root_path: str) -> Dict[str, Any]:
        root = Path(root_path)
        if not root.exists():
            return {"error": "Diretório não encontrado"}
        if not root.is_dir():
            return {"error": "Caminho não é um diretório"}

        self._reset_stats(root)
        full_stats = self._measure_full_tree(root)
        max_depth = self.max_depth if self.max_depth is not None else DEFAULT_MAX_DEPTH_HARD
        max_depth = min(int(max_depth), DEFAULT_MAX_DEPTH_HARD)

        result, mapped_size = self._scan_node(root, 0, max_depth, "")
        self._finalize_stats(mapped_size)

        # Totais reais do disco, sem filtros. O mapa/tree continua obedecendo os filtros.
        self._stats["mapped_size"] = mapped_size
        self._stats["mapped_size_human"] = human_size(mapped_size)
        self._stats["mapped_files"] = self._stats.get("files", 0)
        self._stats["mapped_directories"] = self._stats.get("directories", 0)
        self._stats["total_size"] = int(full_stats.get("size", 0))
        self._stats["total_size_human"] = human_size(self._stats["total_size"])
        self._stats["files"] = int(full_stats.get("files", 0))
        self._stats["directories"] = int(full_stats.get("directories", 0))
        self._stats["max_depth_reached"] = max(
            int(self._stats.get("max_depth_reached", 0)),
            int(full_stats.get("max_depth", 0)),
        )
        self._stats["permission_errors"] = max(
            int(self._stats.get("permission_errors", 0)),
            int(full_stats.get("permission_errors", 0)),
        )
        files = max(int(self._stats.get("files", 0)), 0)
        avg = int(self._stats["total_size"] / files) if files else 0
        self._stats["avg_file_size"] = avg
        self._stats["avg_file_size_human"] = human_size(avg)

        result["_meta"] = {
            "items_seen": self._items_seen,
            "truncated": self._truncated,
            "max_items": self.max_items,
            "stats": self._stats,
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
            size = node.get("size_human")
            size_tag = f"  [{size}]" if size else ""
            if is_root:
                lines.append(f"{name}/{size_tag}\n")
            else:
                connector = "└── " if is_last else "├── "
                suffix = "/" if node.get("type") == "directory" else ""
                lines.append(f"{prefix}{connector}{name}{suffix}{size_tag}\n")

            children = node.get("children", []) or []
            for i, child in enumerate(children):
                last = i == len(children) - 1
                new_prefix = "" if is_root else prefix + ("    " if is_last else "│   ")
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
            size = node.get("size_human", "")
            label = f"{name} | {size}" if size else name
            indent = "  " * level
            box_width = max(len(label) + 2, 9)
            lines.append(f"{indent}┌{'─' * box_width}┐\n")
            lines.append(f"{indent}│{label.center(box_width)}│\n")
            lines.append(f"{indent}└{'─' * box_width}┘\n")

            children = node.get("children", []) or []
            if children:
                lines.append(f"{indent}{' ' * (box_width // 2)}│\n")
                for child in children:
                    if child.get("type") == "directory":
                        walk(child, level + 1)
                    else:
                        file_indent = "  " * (level + 1)
                        lines.append(f"{file_indent}• {child['name']} [{child.get('size_human', '0 B')}]\n")

        walk(data, 0)
        if (data.get("_meta") or {}).get("truncated"):
            lines.append("\n... [TRUNCADO: limite de itens atingido. Aplique filtros.]\n")
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
        stats = meta.get("stats") or {}
        return {
            "content": content,
            "items": meta.get("items_seen", 0),
            "truncated": bool(meta.get("truncated")),
            "elapsed_ms": int(elapsed * 1000),
            "error": data.get("error") if "children" not in data else None,
            "stats": stats,
        }


def map_directory_api(
    path: str,
    hidden_folders: str = "",
    hidden_extensions: str = "",
    hide_files: bool = False,
    max_depth: Optional[int] = None,
    format_type: str = "uml",
    max_items: Optional[int] = None,
) -> str:
    """Retorna JSON string com {content, items, truncated, elapsed_ms, error, stats}."""
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

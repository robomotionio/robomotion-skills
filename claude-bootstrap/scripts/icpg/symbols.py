"""Language-aware symbol extraction from source files."""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

from .models import Symbol

# --- Language detection ---

LANG_MAP = {
    '.py': 'python',
    '.ts': 'typescript', '.tsx': 'typescript',
    '.js': 'javascript', '.jsx': 'javascript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.c': 'c', '.h': 'c',
    '.cpp': 'cpp', '.hpp': 'cpp',
    '.cs': 'csharp',
    '.scala': 'scala',
    '.lua': 'lua',
    '.vue': 'vue',
    '.svelte': 'svelte',
    '.ex': 'elixir', '.exs': 'elixir'
}


def detect_language(file_path: str) -> str | None:
    ext = Path(file_path).suffix.lower()
    return LANG_MAP.get(ext)


def checksum_content(content: str) -> str:
    """SHA256 hash of content for drift detection."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# --- Python extraction (AST-based) ---

def _extract_python(file_path: str, source: str) -> list[Symbol]:
    symbols = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return symbols

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            body = ast.get_source_segment(source, node) or ''
            symbols.append(Symbol(
                name=node.name,
                file_path=file_path,
                symbol_type='class',
                language='python',
                signature=_python_class_sig(node),
                checksum=checksum_content(body)
            ))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = ast.get_source_segment(source, node) or ''
            sig = _python_func_sig(node)
            stype = 'function'
            if any(
                isinstance(d, ast.Name) and d.id == 'staticmethod'
                for d in node.decorator_list
            ):
                stype = 'function'
            symbols.append(Symbol(
                name=node.name,
                file_path=file_path,
                symbol_type=stype,
                language='python',
                signature=sig,
                checksum=checksum_content(body)
            ))

    return symbols


def _python_func_sig(node: ast.FunctionDef) -> str:
    args = []
    for a in node.args.args:
        ann = ''
        if a.annotation:
            ann = f': {ast.dump(a.annotation)}'
        args.append(f'{a.arg}{ann}')
    ret = ''
    if node.returns:
        ret = f' -> {ast.dump(node.returns)}'
    prefix = 'async def' if isinstance(node, ast.AsyncFunctionDef) else 'def'
    return f'{prefix} {node.name}({", ".join(args)}){ret}'


def _python_class_sig(node: ast.ClassDef) -> str:
    bases = [ast.dump(b) for b in node.bases]
    if bases:
        return f'class {node.name}({", ".join(bases)})'
    return f'class {node.name}'


# --- TypeScript/JavaScript extraction (regex) ---

_TS_PATTERNS = [
    # export function name(...)
    (r'export\s+(?:async\s+)?function\s+(\w+)\s*\([^)]*\)',
     'function'),
    # export class Name
    (r'export\s+(?:abstract\s+)?class\s+(\w+)',
     'class'),
    # export const Name = ...
    (r'export\s+const\s+(\w+)\s*[=:]',
     'constant'),
    # export interface Name
    (r'export\s+interface\s+(\w+)',
     'interface'),
    # export type Name
    (r'export\s+type\s+(\w+)',
     'type'),
    # React components: export const Name = (...) =>
    (r'export\s+const\s+((?:[A-Z]\w+))\s*=\s*(?:\([^)]*\)|[^=])\s*=>',
     'component'),
    # Hooks: export function use*
    (r'export\s+(?:async\s+)?function\s+(use\w+)',
     'hook'),
]


def _extract_typescript(file_path: str, source: str) -> list[Symbol]:
    lang = 'typescript' if file_path.endswith(('.ts', '.tsx')) else 'javascript'
    symbols = []
    seen = set()

    for pattern, stype in _TS_PATTERNS:
        for match in re.finditer(pattern, source):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            # Get the line for signature
            line_start = source.rfind('\n', 0, match.start()) + 1
            line_end = source.find('\n', match.end())
            if line_end == -1:
                line_end = len(source)
            sig = source[line_start:line_end].strip()
            symbols.append(Symbol(
                name=name,
                file_path=file_path,
                symbol_type=stype,
                language=lang,
                signature=sig[:200],
                checksum=checksum_content(sig)
            ))

    return symbols


# --- Go extraction (regex) ---

_GO_PATTERNS = [
    (r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(', 'function'),
    (r'type\s+(\w+)\s+struct\s*\{', 'class'),
    (r'type\s+(\w+)\s+interface\s*\{', 'interface'),
]


def _extract_go(file_path: str, source: str) -> list[Symbol]:
    symbols = []
    seen = set()
    for pattern, stype in _GO_PATTERNS:
        for match in re.finditer(pattern, source):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            line_start = source.rfind('\n', 0, match.start()) + 1
            line_end = source.find('\n', match.end())
            if line_end == -1:
                line_end = len(source)
            sig = source[line_start:line_end].strip()
            symbols.append(Symbol(
                name=name,
                file_path=file_path,
                symbol_type=stype,
                language='go',
                signature=sig[:200],
                checksum=checksum_content(sig)
            ))
    return symbols


# --- Rust extraction (regex) ---

_RUST_PATTERNS = [
    (r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)', 'function'),
    (r'(?:pub\s+)?struct\s+(\w+)', 'class'),
    (r'(?:pub\s+)?enum\s+(\w+)', 'type'),
    (r'(?:pub\s+)?trait\s+(\w+)', 'interface'),
    (r'impl\s+(\w+)', 'class'),
]


def _extract_rust(file_path: str, source: str) -> list[Symbol]:
    symbols = []
    seen = set()
    for pattern, stype in _RUST_PATTERNS:
        for match in re.finditer(pattern, source):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            line_start = source.rfind('\n', 0, match.start()) + 1
            line_end = source.find('\n', match.end())
            if line_end == -1:
                line_end = len(source)
            sig = source[line_start:line_end].strip()
            symbols.append(Symbol(
                name=name,
                file_path=file_path,
                symbol_type=stype,
                language='rust',
                signature=sig[:200],
                checksum=checksum_content(sig)
            ))
    return symbols


# --- Elixir extraction (regex) ---

_ELIXIR_PATTERNS = [
    (r'defmodule\s+([\w.]+)', 'module'),
    (r'def\s+(\w+)\s*\(', 'function'),
    (r'defp\s+(\w+)\s*\(', 'function'),
    (r'schema\s+"(\w+)"', 'schema'),
]


def _extract_elixir(file_path: str, source: str) -> list[Symbol]:
    symbols = []
    seen = set()
    for pattern, stype in _ELIXIR_PATTERNS:
        for match in re.finditer(pattern, source):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            line_start = source.rfind('\n', 0, match.start()) + 1
            line_end = source.find('\n', match.end())
            if line_end == -1:
                line_end = len(source)
            sig = source[line_start:line_end].strip()
            symbols.append(Symbol(
                name=name,
                file_path=file_path,
                symbol_type=stype,
                language='elixir',
                signature=sig[:200],
                checksum=checksum_content(sig)
            ))
    return symbols


# --- Public API ---

EXTRACTORS = {
    'python': _extract_python,
    'typescript': _extract_typescript,
    'javascript': _extract_typescript,
    'go': _extract_go,
    'rust': _extract_rust,
    'elixir': _extract_elixir,
}


def extract_symbols(file_path: str) -> list[Symbol]:
    """Extract symbols from a source file."""
    lang = detect_language(file_path)
    if not lang:
        return []

    path = Path(file_path)
    if not path.exists():
        return []

    try:
        source = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return []

    extractor = EXTRACTORS.get(lang)
    if not extractor:
        return []

    return extractor(str(file_path), source)


def extract_symbols_from_files(file_paths: list[str]) -> list[Symbol]:
    """Extract symbols from multiple files."""
    all_symbols = []
    for fp in file_paths:
        all_symbols.extend(extract_symbols(fp))
    return all_symbols

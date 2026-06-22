#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapping Cache Search Tool

Searches a specific version's mapping cache for entries matching a boolean expression.

Usage:
    mapping_search.py <version> <expression> [page]

Arguments:
    version      Minecraft version (e.g., "1.12.2", "1.20.1")
    expression   Boolean search expression (see below)
    page         Page number starting from 1 (default: 1, 10 results per page)

Expression syntax:
    term         Single word, case-insensitive substring match
    a&b          AND: both a and b must match
    a|b          OR:  either a or b must match
    (expr)       Grouping
    & has higher precedence than |, both are left-associative.

    Examples:
        KeyBinding                 entries containing "KeyBinding"
        KeyBinding&client          entries containing both "KeyBinding" AND "client"
        Entity|Player              entries containing "Entity" OR "Player"
        (Entity|Player)&client     entries containing ("Entity" OR "Player") AND "client"
        (a|b)&(c|d)                complex grouping
"""

import csv
import json
import os
import sys
from pathlib import Path

CACHE_DIR = ".mapping-caches"
PAGE_SIZE = 10
SEARCH_COLUMNS = ["obf_class", "deobf_class", "obf_name", "deobf_name", "srg_name"]


# ============================================================================
# Boolean Expression Parser
# ============================================================================

class _TermNode:
    """Leaf node: a single search term."""
    __slots__ = ("term",)

    def __init__(self, term: str):
        self.term = term.lower()


class _AndNode:
    """Binary AND node (left-associative)."""
    __slots__ = ("left", "right")

    def __init__(self, left, right):
        self.left = left
        self.right = right


class _OrNode:
    """Binary OR node (left-associative)."""
    __slots__ = ("left", "right")

    def __init__(self, left, right):
        self.left = left
        self.right = right


def _tokenize(expr: str) -> list:
    """
    Tokenize a boolean expression into a list of tokens.
    Tokens: '&', '|', '(', ')' , or a term string.
    """
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]
        if ch == '&':
            tokens.append('&')
            i += 1
        elif ch == '|':
            tokens.append('|')
            i += 1
        elif ch == '(':
            tokens.append('(')
            i += 1
        elif ch == ')':
            tokens.append(')')
            i += 1
        elif ch in (' ', '\t'):
            # skip whitespace inside expression
            i += 1
        else:
            # read a term (consecutive non-special characters)
            j = i
            while j < n and expr[j] not in ('&', '|', '(', ')', ' '):
                j += 1
            tokens.append(expr[i:j])
            i = j

    return tokens


def _parse_expr(tokens: list, pos: int):
    """
    Recursive descent parser (left-associative).

    Grammar:
        or_expr  = and_expr ('|' and_expr)*
        and_expr = atom ('&' atom)*
        atom     = '(' or_expr ')' | term

    Returns (node, next_pos).
    Raises ValueError on syntax errors.
    """
    node, pos = _parse_and(tokens, pos)

    while pos < len(tokens) and tokens[pos] == '|':
        pos += 1  # consume '|'
        right, pos = _parse_and(tokens, pos)
        node = _OrNode(node, right)

    return node, pos


def _parse_and(tokens: list, pos: int):
    """Parse AND expression (left-associative)."""
    node, pos = _parse_atom(tokens, pos)

    while pos < len(tokens) and tokens[pos] == '&':
        pos += 1  # consume '&'
        right, pos = _parse_atom(tokens, pos)
        node = _AndNode(node, right)

    return node, pos


def _parse_atom(tokens: list, pos: int):
    """Parse an atom: '(' or_expr ')' | term."""
    if pos >= len(tokens):
        raise ValueError("Unexpected end of expression")

    tok = tokens[pos]

    if tok == '(':
        pos += 1  # consume '('
        node, pos = _parse_expr(tokens, pos)
        if pos >= len(tokens) or tokens[pos] != ')':
            raise ValueError("Missing closing parenthesis")
        pos += 1  # consume ')'
        return node, pos

    if tok in ('&', '|', ')'):
        raise ValueError("Unexpected token '" + tok + "' at position " + str(pos))

    # It's a term
    pos += 1
    return _TermNode(tok), pos


def parse_expression(expr: str):
    """Parse a boolean expression string into an AST. Returns root node."""
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")

    node, pos = _parse_expr(tokens, 0)
    if pos < len(tokens):
        raise ValueError("Unexpected token '" + tokens[pos] + "' at position " + str(pos))

    return node


def _row_matches_term(row: dict, term_lower: str) -> bool:
    """Check if any SEARCH_COLUMNS in the row contain the term (case-insensitive)."""
    for col in SEARCH_COLUMNS:
        if term_lower in row.get(col, "").lower():
            return True
    return False


def evaluate_node(node, row: dict) -> bool:
    """Evaluate an AST node against a CSV row."""
    if isinstance(node, _TermNode):
        return _row_matches_term(row, node.term)
    elif isinstance(node, _AndNode):
        return evaluate_node(node.left, row) and evaluate_node(node.right, row)
    elif isinstance(node, _OrNode):
        return evaluate_node(node.left, row) or evaluate_node(node.right, row)
    else:
        raise ValueError("Unknown node type: " + str(type(node)))


# ============================================================================
# Cache Search
# ============================================================================

def print_usage():
    """Print usage information."""
    print("Usage: mapping_search.py <version> <expression> [page]")
    print("")
    print("Arguments:")
    print("  version     Minecraft version (e.g., 1.12.2, 1.20.1)")
    print("  expression  Boolean search expression")
    print("  page        Page number from 1 (default: 1, 10 per page)")
    print("")
    print("Expression syntax:")
    print("  term          case-insensitive substring match")
    print("  a&b           AND (both must match)")
    print("  a|b           OR  (either must match)")
    print("  (expr)        grouping")
    print("  & has higher precedence than |, both left-associative")
    print("")
    print("Examples:")
    print('  mapping_search.py 1.12.2 "KeyBinding"')
    print('  mapping_search.py 1.12.2 "Entity|Player"')
    print('  mapping_search.py 1.12.2 "KeyBinding&client"')
    print('  mapping_search.py 1.12.2 "(Entity|Player)&client"')


def validate_cache(version: str) -> bool:
    """
    Validate that the mapping cache exists and is valid.

    Checks:
    1. .mapping-caches/<version>.csv exists
    2. .mapping-caches/mapping-info.json exists
    3. mapping-info.json[version] matches info.json's mapping-caches-version
    """
    cache_file = Path(CACHE_DIR) / (version + ".csv")
    mapping_info_path = Path(CACHE_DIR) / "mapping-info.json"
    info_path = Path("info.json")

    if not cache_file.exists():
        return False
    if not mapping_info_path.exists():
        return False
    if not info_path.exists():
        return False

    with open(info_path, "r", encoding="utf-8") as f:
        root_info = json.load(f)
    expected_version = root_info.get("mapping-caches-version", "")

    with open(mapping_info_path, "r", encoding="utf-8") as f:
        mapping_info = json.load(f)

    actual_version = mapping_info.get(version, "")
    if actual_version != expected_version:
        return False

    return True


def search_cache(version: str, ast_root) -> list:
    """
    Search the cache CSV for rows matching the boolean expression AST.

    Returns list of dicts for matching rows.
    """
    cache_file = Path(CACHE_DIR) / (version + ".csv")
    results = []

    with open(cache_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if evaluate_node(ast_root, row):
                results.append(row)

    return results


def format_row(row: dict) -> str:
    """Format a single result row for display."""
    desc = row.get("desc", "")
    desc_part = "  desc=" + desc if desc else ""
    return (
        "[" + row.get("type", "?") + "] "
        + row.get("obf_class", "") + "." + row.get("obf_name", "")
        + " -> " + row.get("deobf_class", "") + "." + row.get("deobf_name", "")
        + "  srg=" + row.get("srg_name", "")
        + desc_part
        + "  sideonly=" + row.get("sideonly", "")
    )


def main():
    # Ensure working directory is the script's own directory
    os.chdir(Path(__file__).resolve().parent)

    # Parse arguments
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    version = sys.argv[1]
    search_expr = sys.argv[2]

    # Parse page number
    page = 1
    if len(sys.argv) >= 4:
        try:
            page = int(sys.argv[3])
            if page < 1:
                print("[ERROR] Page number must be >= 1")
                sys.exit(1)
        except ValueError:
            print("[ERROR] Invalid page number: " + sys.argv[3])
            sys.exit(1)

    # Parse boolean expression
    try:
        ast_root = parse_expression(search_expr)
    except ValueError as e:
        print("[ERROR] Invalid expression: " + str(e))
        sys.exit(1)

    # Validate cache
    if not validate_cache(version):
        print("Mapping cache does not exist or invalid.")
        sys.exit(1)

    # Search
    results = search_cache(version, ast_root)

    if not results:
        print("No results found for '" + search_expr + "' in MC " + version)
        return

    total = len(results)

    # If 10 or fewer, output all regardless of page
    if total <= PAGE_SIZE:
        print("Found " + str(total) + " results for '" + search_expr + "' in MC " + version + ":")
        print("")
        for i, row in enumerate(results, 1):
            print("  " + str(i) + ". " + format_row(row))
    else:
        # Paginate
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        if page > total_pages:
            print("[ERROR] Page " + str(page) + " does not exist. Total pages: " + str(total_pages))
            sys.exit(1)

        start = (page - 1) * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)
        page_results = results[start:end]

        print("Found " + str(total) + " results for '" + search_expr + "' in MC " + version
              + " (page " + str(page) + "/" + str(total_pages) + "):")
        print("")
        for i, row in enumerate(page_results, start + 1):
            print("  " + str(i) + ". " + format_row(row))


if __name__ == "__main__":
    main()

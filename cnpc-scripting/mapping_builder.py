#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Mapping Cache Builder

Builds unified mapping caches for Minecraft versions following the workflow
described in native-mc-access.md. Uses MCP stable versions (not snapshot) for 1.7.10-1.16.5,
and Mojang ProGuard + TSRGv2 for 1.17+.

Output: ./mapping-caches/<mc-version>.csv
Format: obf_class,deobf_class,type,obf_name,deobf_name,srg_name,desc,is_static,sideonly
"""

import csv
import json
import os
import sys
import tempfile
import zipfile
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# ============================================================================
# Version-to-URL Mapping Table (Complete URLs)
# ============================================================================

# MCP Maven base URL
NEOFORGE_MAVEN_BASE = "https://maven.neoforged.net/releases/de/oceanlabs/mcp"

# Version configuration with complete URLs
# Each version has:
#   - tsrg_url: MCPConfig TSRG ZIP URL
#   - mcp_stable_url: MCP Stable ZIP URL (for 1.12.2-1.15.2 only)
#   - proguard_url: Mojang ProGuard URL (for 1.17+ only)
#   - workflow: "legacy" (1.12.2-1.16.5) or "modern" (1.17+)
#
# Note: 1.7.10-1.11.2 are NOT available (NeoForge repo missing MCPConfig)
# Note: 1.16.x has no MCP Stable (MCP abandoned after 1.15.2)
# Note: 1.21+ not included (MCPConfig not available)

VERSION_TABLE = {
    # ========================================================================
    # Legacy workflow: SRG + MCP Stable CSV
    # Available: 1.7.10 - 1.11.2
    # ========================================================================
    "1.7.10": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.7.10/mcp-1.7.10-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/12-1.7.10/mcp_stable-12-1.7.10.zip",
        "proguard_url": None,
    },
    "1.8": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.8/mcp-1.8-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/18-1.8/mcp_stable-18-1.8.zip",
        "proguard_url": None,
    },
    "1.8.8": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.8.8/mcp-1.8.8-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/20-1.8.8/mcp_stable-20-1.8.8.zip",
        "proguard_url": None,
    },
    "1.8.9": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.8.9/mcp-1.8.9-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/22-1.8.9/mcp_stable-22-1.8.9.zip",
        "proguard_url": None,
    },
    "1.9": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.9/mcp-1.9-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/24-1.9/mcp_stable-24-1.9.zip",
        "proguard_url": None,
    },
    "1.9.4": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.9.4/mcp-1.9.4-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/26-1.9.4/mcp_stable-26-1.9.4.zip",
        "proguard_url": None,
    },
    "1.10.2": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.10.2/mcp-1.10.2-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/29-1.10.2/mcp_stable-29-1.10.2.zip",
        "proguard_url": None,
    },
    "1.11": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.11/mcp-1.11-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/32-1.11/mcp_stable-32-1.11.zip",
        "proguard_url": None,
    },
    "1.11.2": {
        "workflow": "legacy_srg",
        "srg_url": f"{NEOFORGE_MAVEN_BASE}/mcp/1.11.2/mcp-1.11.2-srg.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/32-1.11/mcp_stable-32-1.11.zip",
        "proguard_url": None,
    },
    # ========================================================================
    # Legacy workflow: TSRGv1 + MCP Stable CSV
    # Available: 1.12.2 - 1.15.2
    # ========================================================================
    "1.12.2": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.12.2/mcp_config-1.12.2.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/39-1.12/mcp_stable-39-1.12.zip",
        "proguard_url": None,
    },
    "1.13": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.13/mcp_config-1.13.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/43-1.13/mcp_stable-43-1.13.zip",
        "proguard_url": None,
    },
    "1.13.1": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.13.1/mcp_config-1.13.1.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/45-1.13.1/mcp_stable-45-1.13.1.zip",
        "proguard_url": None,
    },
    "1.13.2": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.13.2/mcp_config-1.13.2.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/47-1.13.2/mcp_stable-47-1.13.2.zip",
        "proguard_url": None,
    },
    "1.14": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.14/mcp_config-1.14.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/49-1.14/mcp_stable-49-1.14.zip",
        "proguard_url": None,
    },
    "1.14.1": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.14.1/mcp_config-1.14.1.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/51-1.14.1/mcp_stable-51-1.14.1.zip",
        "proguard_url": None,
    },
    "1.14.2": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.14.2/mcp_config-1.14.2.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/53-1.14.2/mcp_stable-53-1.14.2.zip",
        "proguard_url": None,
    },
    "1.14.3": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.14.3/mcp_config-1.14.3.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/56-1.14.3/mcp_stable-56-1.14.3.zip",
        "proguard_url": None,
    },
    "1.14.4": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.14.4/mcp_config-1.14.4.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/58-1.14.4/mcp_stable-58-1.14.4.zip",
        "proguard_url": None,
    },
    "1.15": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.15/mcp_config-1.15.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/60-1.15/mcp_stable-60-1.15.zip",
        "proguard_url": None,
    },
    "1.15.1": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.15.1/mcp_config-1.15.1.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/60-1.15/mcp_stable-60-1.15.zip",
        "proguard_url": None,
    },
    "1.15.2": {
        "workflow": "legacy",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.15.2/mcp_config-1.15.2.zip",
        "mcp_stable_url": f"{NEOFORGE_MAVEN_BASE}/mcp_stable/60-1.15/mcp_stable-60-1.15.zip",
        "proguard_url": None,
    },
    # ========================================================================
    # Legacy workflow: TSRGv1 + ProGuard (1.16.x)
    # MCP was abandoned, so we use Mojang ProGuard instead
    # ========================================================================
    "1.16.1": {
        "workflow": "legacy_proguard",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.16.1/mcp_config-1.16.1.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/ddf517a4f6750f4c15189de4e03246ae1f916cf5/client.txt",
    },
    "1.16.2": {
        "workflow": "legacy_proguard",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.16.2/mcp_config-1.16.2.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/16d12d67cd5341bfc848340f61f3ff6b957537fe/client.txt",
    },
    "1.16.3": {
        "workflow": "legacy_proguard",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.16.3/mcp_config-1.16.3.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/faac5028fbca3859db970cc4ca041aeec55f6d9d/client.txt",
    },
    "1.16.4": {
        "workflow": "legacy_proguard",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.16.4/mcp_config-1.16.4.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/0837de813d1a6b67e23da3c520a84e872c8d2f0e/client.txt",
    },
    "1.16.5": {
        "workflow": "legacy_proguard",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.16.5/mcp_config-1.16.5.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/374c6b789574afbdc901371207155661e0509e17/client.txt",
    },
    # ========================================================================
    # Modern workflow: TSRGv2 + Mojang ProGuard
    # Available: 1.17 - 1.20.1
    # ========================================================================
    "1.17": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.17/mcp_config-1.17.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/227d16f520848747a59bef6f490ae19dc290a804/client.txt",
    },
    "1.17.1": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.17.1/mcp_config-1.17.1.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/e4d540e0cba05a6097e885dffdf363e621f87d3f/client.txt",
    },
    "1.18": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.18/mcp_config-1.18.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/e824c89c612c0b9cb438ef739c44726c59bbf679/client.txt",
    },
    "1.18.1": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.18.1/mcp_config-1.18.1.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/99ade839eacf69b8bed88c91bd70ca660aee47bb/client.txt",
    },
    "1.18.2": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.18.2/mcp_config-1.18.2.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/a661c6a55a0600bd391bdbbd6827654c05b2109c/client.txt",
    },
    "1.19": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.19/mcp_config-1.19.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/150346d1c0b4acec0b4eb7f58b86e3ea1aa730f3/client.txt",
    },
    "1.19.1": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.19.1/mcp_config-1.19.1.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/fc8e22d42c0e4eb1899e2acf7e97eae917e1cb94/client.txt",
    },
    "1.19.2": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.19.2/mcp_config-1.19.2.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/8e8c9be5dc27802caba47053d4fdea328f7f89bd/client.txt",
    },
    "1.19.3": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.19.3/mcp_config-1.19.3.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/42366909cc612e76208d34bf1356f05a88e08a1d/client.txt",
    },
    "1.19.4": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.19.4/mcp_config-1.19.4.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/f14771b764f943c154d3a6fcb47694477e328148/client.txt",
    },
    "1.20": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.20/mcp_config-1.20.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/a4cd9a97400f7ecfe4dba23e427549ebc5815d66/client.txt",
    },
    "1.20.1": {
        "workflow": "modern",
        "tsrg_url": f"{NEOFORGE_MAVEN_BASE}/mcp_config/1.20.1/mcp_config-1.20.1.zip",
        "mcp_stable_url": None,
        "proguard_url": "https://piston-data.mojang.com/v1/objects/6c48521eed01fe2e8ecdadbd5ae348415f3c47da/client.txt",
    },
}


# ============================================================================
# Data Structures
# ============================================================================

SIDE_MAP = {"0": "common", "1": "server", "2": "client"}


@dataclass
class MappingEntry:
    """Unified mapping entry"""
    obf_class: str
    deobf_class: str
    type: str  # 'field' or 'method'
    obf_name: str
    deobf_name: str
    srg_name: str
    desc: str
    is_static: bool
    sideonly: str  # 'common', 'server', or 'client'


# ============================================================================
# Download Helpers
# ============================================================================

def fetch_bytes(url: str) -> bytes:
    """Fetch bytes from a URL."""
    print("  Downloading: " + url)
    req = Request(url, headers={"User-Agent": "MinecraftMappingCacheBuilder/1.0"})
    try:
        with urlopen(req, timeout=120) as response:
            return response.read()
    except HTTPError as e:
        raise RuntimeError("HTTP error " + str(e.code) + " fetching " + url + ": " + str(e.reason))
    except URLError as e:
        raise RuntimeError("URL error fetching " + url + ": " + str(e.reason))


def fetch_text(url: str) -> str:
    """Fetch text from a URL."""
    return fetch_bytes(url).decode("utf-8")


def extract_from_zip(zip_bytes: bytes, path: str) -> str:
    """Extract a file from a ZIP archive."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        # Try exact path first
        if path in zf.namelist():
            return zf.read(path).decode("utf-8")

        # Try with leading slash removed
        path_no_slash = path.lstrip("/")
        for name in zf.namelist():
            if name == path_no_slash or name.endswith("/" + path_no_slash):
                return zf.read(name).decode("utf-8")

        raise FileNotFoundError("File " + path + " not found in ZIP archive")


def extract_optional_from_zip(zip_bytes: bytes, path: str, label: str = "") -> Optional[str]:
    """Extract a file from a ZIP archive, returning None if not found."""
    try:
        return extract_from_zip(zip_bytes, path)
    except FileNotFoundError:
        if label:
            print("  Note: " + label + " not found, skipping")
        return None


# ============================================================================
# SRG Parser (1.7.10 - 1.11.2)
# ============================================================================

def parse_srg(content: str) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    """
    Parse SRG format (1.7.10 - 1.11.2).
    
    Format:
        PK: . net/minecraft/src                    # Package mapping (ignored)
        CL: a net/minecraft/util/EnumChatFormatting # Class mapping
        FD: bdb/w net/minecraft/client/gui/GuiCreateWorld/field_146337_w  # Field: obf_class/obf_field deobf_class/srg_field
        MD: als/b ()I net/minecraft/block/BlockLadder/func_149645_b ()I   # Method: obf_class/obf_method obf_desc deobf_class/srg_method srg_desc

    Returns:
        - methods: srg_name -> { deobf_class, obf_class, obf_name, descriptor }
        - fields: srg_name -> { obf_class, obf_name, deobf_class }
    """
    methods = {}
    fields = {}

    for line in content.splitlines():
        if not line.strip():
            continue

        parts = line.strip().split()
        if len(parts) < 2:
            continue

        prefix = parts[0]

        if prefix == "CL:":
            # Class mapping: CL: <obf_class> <deobf_class>
            # We don't need to store this separately, it's embedded in FD/MD lines
            pass

        elif prefix == "FD:":
            # Field mapping: FD: <obf_class>/<obf_field> <deobf_class>/<srg_field>
            # Example: FD: bdb/w net/minecraft/client/gui/GuiCreateWorld/field_146337_w
            if len(parts) >= 3:
                obf_full = parts[1]      # bdb/w
                deobf_full = parts[2]    # net/minecraft/client/gui/GuiCreateWorld/field_146337_w
                
                # Parse obf side
                if "/" in obf_full:
                    obf_class, obf_field = obf_full.split("/", 1)
                else:
                    obf_class = ""
                    obf_field = obf_full
                
                # Parse deobf side
                if "/" in deobf_full:
                    deobf_class, srg_name = deobf_full.rsplit("/", 1)
                else:
                    deobf_class = ""
                    srg_name = deobf_full
                
                fields[srg_name] = {
                    "obf_class": obf_class,
                    "obf_name": obf_field,
                    "deobf_class": deobf_class,
                }

        elif prefix == "MD:":
            # Method mapping: MD: <obf_class>/<obf_method> <obf_desc> <deobf_class>/<srg_method> <srg_desc>
            # Example: MD: als/b ()I net/minecraft/block/BlockLadder/func_149645_b ()I
            if len(parts) >= 5:
                obf_full = parts[1]      # als/b
                obf_desc = parts[2]      # ()I
                deobf_full = parts[3]    # net/minecraft/block/BlockLadder/func_149645_b
                srg_desc = parts[4]      # ()I
                
                # Parse obf side
                if "/" in obf_full:
                    obf_class, obf_method = obf_full.split("/", 1)
                else:
                    obf_class = ""
                    obf_method = obf_full
                
                # Parse deobf side
                if "/" in deobf_full:
                    deobf_class, srg_name = deobf_full.rsplit("/", 1)
                else:
                    deobf_class = ""
                    srg_name = deobf_full
                
                methods[srg_name] = {
                    "deobf_class": deobf_class,
                    "obf_class": obf_class,
                    "obf_name": obf_method,
                    "descriptor": obf_desc,
                }

    return methods, fields


# ============================================================================
# TSRGv1 Parser (1.12.2 - 1.16.5)
# ============================================================================

def parse_tsrgv1(content: str) -> Tuple[Dict[str, dict], Dict[Tuple[str, str], dict]]:
    """
    Parse TSRGv1 format (1.12.2 - 1.16.5).

    Returns:
        - methods: srg_name -> { deobf_class, obf_class, obf_name, descriptor }
        - fields: (obf_class, mojang_name) -> { obf_class, obf_name }
    """
    methods = {}
    fields = {}

    current_obf_class = None
    current_deobf_class = None

    for line in content.splitlines():
        if not line.strip():
            continue

        # Check indentation
        if line.startswith("\t") or line.startswith("    "):
            # Member line
            parts = line.strip().split()
            if not parts:
                continue

            # Check if this is a method (has descriptor with parentheses)
            # Method format: <obf> <descriptor> <srg_name>
            # Field format: <obf> <mojang_name>
            is_method = False
            for part in parts:
                if "(" in part and ")" in part:
                    is_method = True
                    break

            if is_method:
                # Method: <obf> <descriptor> <srg_name>
                if len(parts) >= 3:
                    obf_name = parts[0]
                    # Find the descriptor (contains parentheses)
                    descriptor = ""
                    srg_name = ""
                    for j, part in enumerate(parts[1:], 1):
                        if "(" in part and ")" in part:
                            descriptor = part
                            # SRG name is the next part after descriptor
                            if j + 1 < len(parts):
                                srg_name = parts[j + 1]
                            break
                    if srg_name:
                        methods[srg_name] = {
                            "deobf_class": current_deobf_class,
                            "obf_class": current_obf_class,
                            "obf_name": obf_name,
                            "descriptor": descriptor,
                        }
            else:
                # Field: <obf> <mojang_name>
                if len(parts) >= 2:
                    obf_name = parts[0]
                    mojang_name = parts[1]
                    if current_obf_class:
                        fields[(current_obf_class, mojang_name)] = {
                            "obf_class": current_obf_class,
                            "obf_name": obf_name,
                        }
        else:
            # Class line: <obf_class> <mojang_class_path>
            parts = line.strip().split()
            if len(parts) >= 2:
                current_obf_class = parts[0]
                current_deobf_class = parts[1]

    return methods, fields


# ============================================================================
# TSRGv2 Parser (1.17+)
# ============================================================================

def parse_tsrgv2(content: str) -> List[dict]:
    """
    Parse TSRGv2 format (1.17+).
    
    Format:
        <obf_class> <srg_class_path> <srg_class_id>
            <obf_field> <srg_field> <srg_id>           # Field (3 parts)
            <obf_method> <descriptor> <srg_method> <srg_id>  # Method (4 parts, descriptor starts with '(')
                static                                  # Optional static marker
                <param_index> o <param_srg> <param_id>  # Parameter lines (skip)

    Returns list of entries: { obf_class, obf_name, descriptor, srg_name, type, is_static }
    """
    entries = []

    current_obf_class = None
    current_srg_class = None

    lines = content.splitlines()
    i = 0

    # Skip header line if present
    if lines and lines[0].startswith("tsrg2"):
        i = 1

    while i < len(lines):
        line = lines[i]
        i += 1

        if not line.strip():
            continue

        # Calculate indent level
        indent = len(line) - len(line.lstrip())

        if indent == 0:
            # Class line: <obf_class> <srg_class_path> <srg_class_id>
            parts = line.strip().split()
            if len(parts) >= 2:
                current_obf_class = parts[0]
                current_srg_class = parts[1]
            continue

        if current_obf_class is None:
            continue

        # Member line
        parts = line.strip().split()
        if not parts:
            continue

        # Check for static sub-line
        is_static = False
        if i < len(lines):
            next_line = lines[i].strip()
            if next_line == "static":
                is_static = True
                i += 1

        # Check for parameter sub-lines (skip them)
        while i < len(lines):
            next_line = lines[i]
            next_indent = len(next_line) - len(next_line.lstrip())
            if next_indent > indent:
                next_parts = next_line.strip().split()
                if next_parts and next_parts[0].isdigit():
                    i += 1
                else:
                    break
            else:
                break

        # Determine if this is a method or field
        # Methods have descriptor starting with '(' as the second part
        # Fields have SRG name as the second part (starts with 'f_' or is a special name)
        if len(parts) >= 2 and parts[1].startswith("("):
            # Method: <obf> <descriptor> <srg_name> <srg_id>
            if len(parts) >= 3:
                obf_name = parts[0]
                descriptor = parts[1]
                srg_name = parts[2]
                entries.append({
                    "obf_class": current_obf_class,
                    "obf_name": obf_name,
                    "descriptor": descriptor,
                    "srg_name": srg_name,
                    "type": "method",
                    "is_static": is_static,
                })
        else:
            # Field: <obf> <srg_name> <srg_id>
            if len(parts) >= 2:
                obf_name = parts[0]
                srg_name = parts[1]
                entries.append({
                    "obf_class": current_obf_class,
                    "obf_name": obf_name,
                    "descriptor": "",
                    "srg_name": srg_name,
                    "type": "field",
                    "is_static": is_static,
                })

    return entries


# ============================================================================
# ProGuard Parser (1.17+)
# ============================================================================

def parse_proguard(content: str) -> List[dict]:
    """
    Parse ProGuard format (1.17+).

    Returns list of entries: { deobf_class, obf_class, obf_name, deobf_name, descriptor, type }
    """
    entries = []

    current_deobf_class = None
    current_obf_class = None

    for line in content.splitlines():
        if not line.strip() or line.startswith("#"):
            continue

        # Check indentation
        if line.startswith(" ") or line.startswith("\t"):
            # Member line
            stripped = line.strip()

            if "(" in stripped:
                # Method: [line:]returnType name(params) -> obfName
                # Parse the method signature
                arrow_pos = stripped.rfind("->")
                if arrow_pos == -1:
                    continue

                method_part = stripped[:arrow_pos].strip()
                obf_name = stripped[arrow_pos + 2:].strip()

                # Extract method name and descriptor
                # Format: returnType name(params)
                paren_start = method_part.find("(")
                if paren_start == -1:
                    continue

                # Get return type and method name
                before_paren = method_part[:paren_start].strip()
                parts = before_paren.split()
                if len(parts) < 2:
                    continue

                return_type = parts[0]
                method_name = parts[1]

                # Build descriptor (simplified - full descriptor building is complex)
                # For now, we'll use the method name as deobf_name
                entries.append({
                    "deobf_class": current_deobf_class,
                    "obf_class": current_obf_class,
                    "obf_name": obf_name,
                    "deobf_name": method_name,
                    "descriptor": "",  # Would need complex parsing for full descriptor
                    "type": "method",
                })
            else:
                # Field: type name -> obfName
                arrow_pos = stripped.rfind("->")
                if arrow_pos == -1:
                    continue

                field_part = stripped[:arrow_pos].strip()
                obf_name = stripped[arrow_pos + 2:].strip()

                parts = field_part.split()
                if len(parts) >= 2:
                    field_type = parts[0]
                    field_name = parts[1]
                    entries.append({
                        "deobf_class": current_deobf_class,
                        "obf_class": current_obf_class,
                        "obf_name": obf_name,
                        "deobf_name": field_name,
                        "descriptor": "",
                        "type": "field",
                    })
        else:
            # Class line: <MojangName> -> <ObfName>:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[1] == "->":
                current_deobf_class = parts[0].replace(".", "/")
                current_obf_class = parts[2].rstrip(":")

    return entries


# ============================================================================
# CSV Parser (MCP fields.csv / methods.csv)
# ============================================================================

def parse_mcp_csv(content: str) -> List[dict]:
    """
    Parse MCP CSV format (fields.csv or methods.csv).

    Returns list of entries: { searge, name, side, desc }
    """
    entries = []

    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        entries.append({
            "searge": row.get("searge", ""),
            "name": row.get("name", ""),
            "side": row.get("side", ""),
            "desc": row.get("desc", ""),
        })

    return entries


# ============================================================================
# static_methods.txt Parser
# ============================================================================

def parse_static_methods(content: str) -> Set[str]:
    """Parse static_methods.txt - one SRG method name per line."""
    result = set()
    for line in content.splitlines():
        name = line.strip()
        if name:
            # Strip trailing underscore for matching
            result.add(name.rstrip("_"))
    return result


# ============================================================================
# constructors Parser
# ============================================================================

def parse_constructors(content: str) -> List[dict]:
    """
    Parse constructors file.
    Format: <srg_id> <class_path> <descriptor>
    """
    entries = []
    for line in content.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3:
            entries.append({
                "srg_id": parts[0],
                "class_path": parts[1],
                "descriptor": parts[2],
            })
    return entries


# ============================================================================
# Shared Helpers for Merge Builders
# ============================================================================

def check_static(srg_name: str, static_methods: Set[str]) -> bool:
    """Check if a method is static by looking up its SRG name."""
    return srg_name.rstrip("_") in static_methods


def fetch_mcp_csv_pair(mcp_stable_url: str) -> Tuple[List[dict], List[dict]]:
    """Download MCP stable ZIP and extract fields.csv + methods.csv."""
    print("  Downloading MCP stable CSV...")
    mcp_zip = fetch_bytes(mcp_stable_url)
    fields_csv = extract_from_zip(mcp_zip, "fields.csv")
    methods_csv = extract_from_zip(mcp_zip, "methods.csv")
    return parse_mcp_csv(fields_csv), parse_mcp_csv(methods_csv)


def build_class_map(methods: Dict[str, dict], fields) -> Dict[str, str]:
    """Build obf_class -> deobf_class lookup from parsed mapping data.

    Accepts both SRG fields (keyed by srg_name) and TSRGv1 fields (keyed by (obf_class, mojang_name)).
    """
    class_map: Dict[str, str] = {}
    for info in methods.values():
        if info["obf_class"] and info["deobf_class"]:
            class_map[info["obf_class"]] = info["deobf_class"]
    for key, info in fields.items():
        if info["obf_class"]:
            if isinstance(key, tuple):
                # TSRGv1 fields: key = (obf_class, mojang_name)
                class_map[info["obf_class"]] = key[0]
            else:
                # SRG fields: key = srg_name
                class_map[info["obf_class"]] = info["deobf_class"]
    return class_map


def merge_csv_methods(
    csv_methods: List[dict],
    mapping_methods: Dict[str, dict],
    static_methods: Set[str],
    method_key: str = "srg_name",
) -> List[MappingEntry]:
    """Merge CSV method entries with SRG/TSRG method mappings.

    Args:
        csv_methods: Parsed MCP CSV method rows.
        mapping_methods: SRG or TSRGv1 method dict (srg_name -> info).
        static_methods: Set of static SRG method names.
        method_key: Key name for the SRG method name in mapping_methods values
                    ("srg_name" for SRG, unused for TSRGv1 which keys by srg_name directly).
    """
    entries = []
    for csv_method in csv_methods:
        srg_name = csv_method["searge"]
        deobf_name = csv_method["name"]
        sideonly = SIDE_MAP.get(csv_method.get("side", "0"), "common")
        info = mapping_methods.get(srg_name)

        if info:
            entries.append(MappingEntry(
                obf_class=info["obf_class"],
                deobf_class=info["deobf_class"],
                type="method",
                obf_name=info["obf_name"],
                deobf_name=deobf_name,
                srg_name=srg_name,
                desc=info["descriptor"],
                is_static=check_static(srg_name, static_methods),
                sideonly=sideonly,
            ))
        else:
            entries.append(MappingEntry(
                obf_class="",
                deobf_class="",
                type="method",
                obf_name="",
                deobf_name=deobf_name,
                srg_name=srg_name,
                desc="",
                is_static=False,
                sideonly=sideonly,
            ))
    return entries


def merge_csv_fields_srg(
    csv_fields: List[dict],
    srg_fields: Dict[str, dict],
) -> List[MappingEntry]:
    """Merge CSV field entries with SRG field mappings (legacy_srg workflow)."""
    entries = []
    for csv_field in csv_fields:
        srg_name = csv_field["searge"]
        deobf_name = csv_field["name"]
        sideonly = SIDE_MAP.get(csv_field.get("side", "0"), "common")
        info = srg_fields.get(srg_name)

        if info:
            entries.append(MappingEntry(
                obf_class=info["obf_class"],
                deobf_class=info["deobf_class"],
                type="field",
                obf_name=info["obf_name"],
                deobf_name=deobf_name,
                srg_name=srg_name,
                desc="",
                is_static=False,
                sideonly=sideonly,
            ))
        else:
            entries.append(MappingEntry(
                obf_class="",
                deobf_class="",
                type="field",
                obf_name="",
                deobf_name=deobf_name,
                srg_name=srg_name,
                desc="",
                is_static=False,
                sideonly=sideonly,
            ))
    return entries


def merge_csv_fields_tsrg(
    csv_fields: List[dict],
    tsrg_fields: Dict[Tuple[str, str], dict],
) -> List[MappingEntry]:
    """Merge CSV field entries with TSRGv1 field mappings (legacy workflow).

    TSRGv1 fields are keyed by (obf_class, second_column) where second_column is:
      - An SRG name (field_xxxx) for most fields
      - A Mojang name (camelCase) for officially mapped fields

    Matching strategy:
      1. For SRG-named TSRG entries: match CSV searge == TSRG second column
      2. For Mojang-named TSRG entries: match CSV name == TSRG second column
    """
    # Build SRG name lookup: srg_name -> (obf_class, tsrg_info)
    srg_lookup: Dict[str, Tuple[str, dict]] = {}
    for (obf_class, col2), tsrg_info in tsrg_fields.items():
        if col2.startswith("field_"):
            srg_lookup[col2] = (obf_class, tsrg_info)

    # Build Mojang name lookup: mojang_name -> (obf_class, tsrg_info)
    mojang_lookup: Dict[str, Tuple[str, dict]] = {}
    for (obf_class, col2), tsrg_info in tsrg_fields.items():
        if not col2.startswith("field_"):
            mojang_lookup[col2] = (obf_class, tsrg_info)

    entries = []
    for csv_field in csv_fields:
        srg_name = csv_field["searge"]
        deobf_name = csv_field["name"]
        sideonly = SIDE_MAP.get(csv_field.get("side", "0"), "common")

        # Try SRG name match first
        match = srg_lookup.get(srg_name)
        if match:
            obf_class, tsrg_info = match
            entries.append(MappingEntry(
                obf_class=tsrg_info["obf_class"],
                deobf_class=obf_class,
                type="field",
                obf_name=tsrg_info["obf_name"],
                deobf_name=deobf_name,
                srg_name=srg_name,
                desc="",
                is_static=False,
                sideonly=sideonly,
            ))
            continue

        # Try Mojang name match
        match = mojang_lookup.get(deobf_name)
        if match:
            obf_class, tsrg_info = match
            entries.append(MappingEntry(
                obf_class=tsrg_info["obf_class"],
                deobf_class=obf_class,
                type="field",
                obf_name=tsrg_info["obf_name"],
                deobf_name=deobf_name,
                srg_name=srg_name,
                desc="",
                is_static=False,
                sideonly=sideonly,
            ))
            continue

        # No match
        entries.append(MappingEntry(
            obf_class="",
            deobf_class="",
            type="field",
            obf_name="",
            deobf_name=deobf_name,
            srg_name=srg_name,
            desc="",
            is_static=False,
            sideonly=sideonly,
        ))
    return entries


def add_constructor_entries(
    constructors: List[dict],
    class_map: Dict[str, str],
) -> List[MappingEntry]:
    """Build MappingEntry list for constructors, using class_map for obf_class lookup."""
    entries = []
    for ctor in constructors:
        obf_class = class_map.get(ctor["class_path"], "")
        entries.append(MappingEntry(
            obf_class=obf_class,
            deobf_class=ctor["class_path"],
            type="method",
            obf_name="<init>",
            deobf_name="<init>",
            srg_name="<init>",
            desc=ctor["descriptor"],
            is_static=False,
            sideonly="common",
        ))
    return entries


# ============================================================================
# Merge Logic for 1.7.10 - 1.11.2 (Legacy with SRG + CSV)
# ============================================================================

def build_merged_table_legacy_srg(mc_version: str, version_config: dict) -> List[MappingEntry]:
    """
    Build merged mapping table for MC 1.7.10 - 1.11.2.
    Uses SRG + MCP stable CSV + static_methods.txt
    """
    print("")
    print("=== Building cache for MC " + mc_version + " (legacy SRG workflow) ===")

    # Step 1: Download and parse SRG
    print("")
    print("[1/3] Downloading SRG mappings...")
    srg_zip = fetch_bytes(version_config["srg_url"])
    srg_content = extract_from_zip(srg_zip, "joined.srg")
    static_content = extract_optional_from_zip(srg_zip, "static_methods.txt", "static_methods.txt")

    srg_methods, srg_fields = parse_srg(srg_content)
    static_methods = parse_static_methods(static_content) if static_content else set()

    # Step 2: Download and parse MCP CSV
    print("[2/3] Downloading MCP stable CSV...")
    csv_fields, csv_methods = fetch_mcp_csv_pair(version_config["mcp_stable_url"])

    # Step 3: Merge
    print("[3/3] Merging data...")
    entries = merge_csv_methods(csv_methods, srg_methods, static_methods)
    entries.extend(merge_csv_fields_srg(csv_fields, srg_fields))

    return entries


# ============================================================================
# Merge Logic for 1.12.2 - 1.15.2 (Legacy with CSV)
# ============================================================================

def build_merged_table_legacy(mc_version: str, version_config: dict) -> List[MappingEntry]:
    """
    Build merged mapping table for MC 1.12.2 - 1.15.2.
    Uses TSRGv1 + MCP stable CSV + static_methods.txt + constructors
    """
    print("")
    print("=== Building cache for MC " + mc_version + " (legacy workflow) ===")

    # Step 1: Download and parse TSRG
    print("")
    print("[1/3] Downloading MCPConfig TSRG...")
    tsrg_zip = fetch_bytes(version_config["tsrg_url"])
    tsrg_content = extract_from_zip(tsrg_zip, "config/joined.tsrg")
    static_content = extract_optional_from_zip(tsrg_zip, "config/static_methods.txt", "static_methods.txt")
    ctor_content = extract_optional_from_zip(tsrg_zip, "config/constructors", "constructors file")

    tsrg_methods, tsrg_fields = parse_tsrgv1(tsrg_content)
    static_methods = parse_static_methods(static_content) if static_content else set()
    constructors = parse_constructors(ctor_content) if ctor_content else []

    # Step 2: Download and parse MCP CSV
    print("[2/3] Downloading MCP stable CSV...")
    csv_fields, csv_methods = fetch_mcp_csv_pair(version_config["mcp_stable_url"])

    # Step 3: Merge
    print("[3/3] Merging data...")
    entries = merge_csv_methods(csv_methods, tsrg_methods, static_methods)
    entries.extend(merge_csv_fields_tsrg(csv_fields, tsrg_fields))

    # Add constructor entries using class_map for efficient lookup
    class_map = build_class_map(tsrg_methods, tsrg_fields)
    entries.extend(add_constructor_entries(constructors, class_map))

    return entries


# ============================================================================
# Merge Logic for 1.16.x (Legacy TSRGv1 + ProGuard)
# ============================================================================

def build_merged_table_legacy_proguard(mc_version: str, version_config: dict) -> List[MappingEntry]:
    """
    Build merged mapping table for MC 1.16.x.
    Uses TSRGv1 + Mojang ProGuard (MCP was abandoned).
    
    TSRGv1 format:
        <obf_class> <mojang_class_path>
            <obf_field> <mojang_field_name>
            <obf_method> <descriptor> <srg_method_name>
    
    ProGuard format:
        <MojangName> -> <ObfName>:
            returnType name(params) -> obfName
            type name -> obfName
    
    Join key: obf_class + obf_name
    """
    print("")
    print("=== Building cache for MC " + mc_version + " (legacy TSRGv1 + ProGuard) ===")

    # Step 1: Download and parse TSRG
    print("")
    print("[1/3] Downloading MCPConfig TSRG...")
    tsrg_zip = fetch_bytes(version_config["tsrg_url"])
    tsrg_content = extract_from_zip(tsrg_zip, "config/joined.tsrg")
    static_content = extract_optional_from_zip(tsrg_zip, "config/static_methods.txt", "static_methods.txt")

    tsrg_methods, tsrg_fields = parse_tsrgv1(tsrg_content)
    static_methods = parse_static_methods(static_content) if static_content else set()

    # Step 2: Download and parse ProGuard
    print("[2/3] Downloading Mojang ProGuard mappings...")
    proguard_content = fetch_text(version_config["proguard_url"])
    proguard_entries = parse_proguard(proguard_content)

    # Step 3: Merge
    print("[3/3] Merging data...")

    # Build ProGuard lookup: (obf_class, obf_name, type) -> entry
    proguard_map = {}
    for entry in proguard_entries:
        key = (entry["obf_class"], entry["obf_name"], entry["type"])
        proguard_map[key] = entry

    entries = []

    # Merge methods from TSRG with ProGuard
    for srg_name, tsrg_info in tsrg_methods.items():
        obf_class = tsrg_info["obf_class"]
        obf_name = tsrg_info["obf_name"]

        proguard_match = proguard_map.get((obf_class, obf_name, "method"))

        if proguard_match:
            entries.append(MappingEntry(
                obf_class=obf_class,
                deobf_class=proguard_match["deobf_class"],
                type="method",
                obf_name=obf_name,
                deobf_name=proguard_match["deobf_name"],
                srg_name=srg_name,
                desc=tsrg_info["descriptor"],
                is_static=check_static(srg_name, static_methods),
                sideonly="common",
            ))
        else:
            entries.append(MappingEntry(
                obf_class=obf_class,
                deobf_class=tsrg_info["deobf_class"],
                type="method",
                obf_name=obf_name,
                deobf_name=srg_name,
                srg_name=srg_name,
                desc=tsrg_info["descriptor"],
                is_static=check_static(srg_name, static_methods),
                sideonly="common",
            ))

    # Merge fields from TSRG with ProGuard
    for (obf_class, mojang_name), tsrg_info in tsrg_fields.items():
        obf_name = tsrg_info["obf_name"]

        proguard_match = proguard_map.get((obf_class, obf_name, "field"))

        if proguard_match:
            entries.append(MappingEntry(
                obf_class=obf_class,
                deobf_class=proguard_match["deobf_class"],
                type="field",
                obf_name=obf_name,
                deobf_name=proguard_match["deobf_name"],
                srg_name="",
                desc="",
                is_static=False,
                sideonly="common",
            ))
        else:
            entries.append(MappingEntry(
                obf_class=obf_class,
                deobf_class=obf_class,
                type="field",
                obf_name=obf_name,
                deobf_name=mojang_name,
                srg_name="",
                desc="",
                is_static=False,
                sideonly="common",
            ))

    return entries


# ============================================================================
# Merge Logic for 1.17+ (Modern)
# ============================================================================

def build_merged_table_modern(mc_version: str, version_config: dict) -> List[MappingEntry]:
    """
    Build merged mapping table for MC 1.17+.
    Uses TSRGv2 + Mojang ProGuard
    """
    print("")
    print("=== Building cache for MC " + mc_version + " (modern workflow) ===")

    # Step 1: Download and parse TSRG
    print("")
    print("[1/3] Downloading MCPConfig TSRG...")
    tsrg_zip = fetch_bytes(version_config["tsrg_url"])
    tsrg_content = extract_from_zip(tsrg_zip, "config/joined.tsrg")

    # Step 2: Download and parse ProGuard
    print("[2/3] Downloading Mojang ProGuard mappings...")
    proguard_content = fetch_text(version_config["proguard_url"])

    tsrg_entries = parse_tsrgv2(tsrg_content)
    proguard_entries = parse_proguard(proguard_content)

    # Step 3: Merge
    print("[3/3] Merging data...")

    # Build lookup maps: (obf_class, obf_name, type) -> entry
    tsrg_map = {}
    for entry in tsrg_entries:
        key = (entry["obf_class"], entry["obf_name"], entry["type"])
        tsrg_map[key] = entry

    proguard_map = {}
    for entry in proguard_entries:
        key = (entry["obf_class"], entry["obf_name"], entry["type"])
        proguard_map[key] = entry

    entries = []

    # Start with all TSRG entries and join with ProGuard
    for tsrg_key, tsrg_entry in tsrg_map.items():
        proguard_match = proguard_map.get(tsrg_key)

        if proguard_match:
            entries.append(MappingEntry(
                obf_class=tsrg_entry["obf_class"],
                deobf_class=proguard_match["deobf_class"],
                type=tsrg_entry["type"],
                obf_name=tsrg_entry["obf_name"],
                deobf_name=proguard_match["deobf_name"],
                srg_name=tsrg_entry["srg_name"],
                desc=tsrg_entry["descriptor"],
                is_static=tsrg_entry["is_static"],
                sideonly="common",
            ))
        else:
            entries.append(MappingEntry(
                obf_class=tsrg_entry["obf_class"],
                deobf_class="",
                type=tsrg_entry["type"],
                obf_name=tsrg_entry["obf_name"],
                deobf_name="",
                srg_name=tsrg_entry["srg_name"],
                desc=tsrg_entry["descriptor"],
                is_static=tsrg_entry["is_static"],
                sideonly="common",
            ))

    # Add ProGuard entries that have no TSRG match
    for proguard_key, proguard_entry in proguard_map.items():
        if proguard_key not in tsrg_map:
            entries.append(MappingEntry(
                obf_class=proguard_entry["obf_class"],
                deobf_class=proguard_entry["deobf_class"],
                type=proguard_entry["type"],
                obf_name=proguard_entry["obf_name"],
                deobf_name=proguard_entry["deobf_name"],
                srg_name="",
                desc=proguard_entry["descriptor"],
                is_static=False,
                sideonly="common",
            ))

    return entries


# ============================================================================
# Cache Output
# ============================================================================

def write_cache(entries: List[MappingEntry], mc_version: str, cache_dir: str = ".mapping-caches"):
    """Write merged entries to CSV cache file."""
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    output_file = cache_path / (mc_version + ".csv")

    # Write to a temp file first, then replace (robust on Windows)
    fd, tmp_path = tempfile.mkstemp(suffix=".csv.tmp", dir=str(cache_path))
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(["obf_class", "deobf_class", "type", "obf_name", "deobf_name", "srg_name", "desc", "is_static", "sideonly"])

            # Write entries
            for entry in entries:
                writer.writerow([
                    entry.obf_class,
                    entry.deobf_class,
                    entry.type,
                    entry.obf_name,
                    entry.deobf_name,
                    entry.srg_name,
                    entry.desc,
                    "true" if entry.is_static else "false",
                    entry.sideonly,
                ])

        # Atomic replace
        os.replace(tmp_path, str(output_file))
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    # Update mapping-info.json
    update_mapping_info(mc_version, cache_dir)

    print("")
    print("[OK] Cache written to: " + str(output_file))
    print("  Total entries: " + str(len(entries)))

    # Count by type
    methods = sum(1 for e in entries if e.type == "method")
    fields = sum(1 for e in entries if e.type == "field")
    print("  Methods: " + str(methods))
    print("  Fields: " + str(fields))


def update_mapping_info(mc_version: str, cache_dir: str = ".mapping-caches"):
    """Update mapping-info.json with the current version's cache-version stamp."""
    cache_path = Path(cache_dir)
    info_path = Path("info.json")
    mapping_info_path = cache_path / "mapping-info.json"

    # Read current mapping-caches-version from info.json
    caches_version = "unknown"
    if info_path.exists():
        with open(info_path, "r", encoding="utf-8") as f:
            root_info = json.load(f)
        caches_version = root_info.get("mapping-caches-version", "unknown")

    # Read existing mapping-info.json or create new
    mapping_info = {}
    if mapping_info_path.exists():
        with open(mapping_info_path, "r", encoding="utf-8") as f:
            mapping_info = json.load(f)

    mapping_info[mc_version] = caches_version

    with open(mapping_info_path, "w", encoding="utf-8") as f:
        json.dump(mapping_info, f, indent="\t", ensure_ascii=False)
        f.write("\n")


# ============================================================================
# Main Entry Point
# ============================================================================

def build_mapping_cache(mc_version: str, cache_dir: str = ".mapping-caches", force: bool = False):
    """
    Build mapping cache for a given MC version.

    Args:
        mc_version: Minecraft version (e.g., "1.12.2", "1.20.1")
        cache_dir: Directory to store cache files
        force: Force rebuild even if cache exists
    """
    cache_path = Path(cache_dir) / (mc_version + ".csv")

    if cache_path.exists() and not force:
        print("Cache already exists: " + str(cache_path))
        print("Use --force to rebuild")
        return

    # Check if version is supported
    if mc_version not in VERSION_TABLE:
        print("[ERROR] MC version " + mc_version + " is not supported.")
        print("Supported versions: " + ", ".join(sorted(VERSION_TABLE.keys())))
        return

    version_config = VERSION_TABLE[mc_version]
    workflow = version_config["workflow"]

    if workflow == "legacy_srg":
        entries = build_merged_table_legacy_srg(mc_version, version_config)
    elif workflow == "legacy":
        entries = build_merged_table_legacy(mc_version, version_config)
    elif workflow == "legacy_proguard":
        entries = build_merged_table_legacy_proguard(mc_version, version_config)
    elif workflow == "modern":
        entries = build_merged_table_modern(mc_version, version_config)
    else:
        print("[ERROR] Unknown workflow: " + workflow)
        return

    write_cache(entries, mc_version, cache_dir)


def list_supported_versions():
    """List all supported MC versions."""
    print("")
    print("=== Supported Minecraft Versions ===")
    print("")
    print("Legacy (SRG + MCP Stable CSV, 1.7.10-1.11.2):")
    for version in sorted(VERSION_TABLE.keys()):
        config = VERSION_TABLE[version]
        if config["workflow"] == "legacy_srg":
            print("  " + version)

    print("")
    print("Legacy (TSRGv1 + MCP Stable CSV, 1.12.2-1.15.2):")
    for version in sorted(VERSION_TABLE.keys()):
        config = VERSION_TABLE[version]
        if config["workflow"] == "legacy":
            print("  " + version)

    print("")
    print("Legacy (TSRGv1 + ProGuard, 1.16.x):")
    for version in sorted(VERSION_TABLE.keys()):
        config = VERSION_TABLE[version]
        if config["workflow"] == "legacy_proguard":
            print("  " + version)

    print("")
    print("Modern (TSRGv2 + ProGuard, 1.17+):")
    for version in sorted(VERSION_TABLE.keys()):
        config = VERSION_TABLE[version]
        if config["workflow"] == "modern":
            print("  " + version)

    print("")
    print("Not available (missing from NeoForge repo):")
    print("  1.21+ (no MCPConfig)")


def print_version_urls(mc_version: str):
    """Print the URLs for a specific MC version."""
    if mc_version not in VERSION_TABLE:
        print("[ERROR] MC version " + mc_version + " is not supported.")
        return

    config = VERSION_TABLE[mc_version]
    print("")
    print("=== URLs for MC " + mc_version + " ===")
    print("  Workflow: " + config["workflow"])
    # legacy_srg versions use "srg_url", others use "tsrg_url"
    mapping_url = config.get("tsrg_url") or config.get("srg_url", "")
    url_label = "SRG URL" if config["workflow"] == "legacy_srg" else "TSRG URL"
    print("  " + url_label + ": " + mapping_url)
    if config.get("mcp_stable_url"):
        print("  MCP Stable URL: " + config["mcp_stable_url"])
    if config.get("proguard_url"):
        print("  ProGuard URL: " + config["proguard_url"])


def main():
    import argparse

    # Ensure working directory is the script's own directory
    os.chdir(Path(__file__).resolve().parent)

    parser = argparse.ArgumentParser(
        description="Build Minecraft mapping cache from MCP/Mojang sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1.12.2          # Build cache for MC 1.12.2
  %(prog)s 1.20.1          # Build cache for MC 1.20.1
  %(prog)s --list           # List all supported versions
  %(prog)s --urls 1.12.2   # Show URLs for a specific version
  %(prog)s --all            # Build caches for all supported versions
  %(prog)s --force 1.12.2  # Force rebuild cache
        """
    )

    parser.add_argument("version", nargs="?", help="Minecraft version to build cache for")
    parser.add_argument("--list", action="store_true", help="List all supported versions")
    parser.add_argument("--urls", metavar="VERSION", help="Show URLs for a specific version")
    parser.add_argument("--all", action="store_true", help="Build caches for all supported versions")
    parser.add_argument("--force", action="store_true", help="Force rebuild even if cache exists")
    parser.add_argument("--cache-dir", default=".mapping-caches", help="Cache directory (default: .mapping-caches)")

    args = parser.parse_args()

    if args.list:
        list_supported_versions()
        return

    if args.urls:
        print_version_urls(args.urls)
        return

    if args.all:
        print("Building caches for " + str(len(VERSION_TABLE)) + " versions...")
        for version in sorted(VERSION_TABLE.keys()):
            try:
                build_mapping_cache(version, args.cache_dir, args.force)
            except Exception as e:
                print("")
                print("[ERROR] Error building cache for " + version + ": " + str(e))
        return

    if not args.version:
        parser.print_help()
        return

    try:
        build_mapping_cache(args.version, args.cache_dir, args.force)
    except Exception as e:
        print("")
        print("[ERROR] " + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

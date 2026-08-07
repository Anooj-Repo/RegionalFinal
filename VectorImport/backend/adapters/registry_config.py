"""
adapters/registry_config.py
----------------------------
Mapping from integer project_id to synthetic dataset folder name.

This is the single place to register new projects.
Adapters consult this registry to resolve file paths.

    project_id=1 → data/projects/alpha/
    project_id=2 → data/projects/beta/
    project_id=3 → data/projects/gamma/
"""

from __future__ import annotations

# project_id (int) → folder name under data/projects/
PROJECT_REGISTRY: dict[int, str] = {
    1: "alpha",   # Digital Transformation Programme
    2: "beta",    # ERP System Upgrade (SAP S/4HANA)
    3: "gamma",   # Zero-Trust Cybersecurity Overhaul
}

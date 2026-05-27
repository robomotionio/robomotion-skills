"""CLI package for vmware-aiops.

Re-exports `app` so the pyproject.toml entry point
``vmware-aiops = "vmware_aiops.cli:app"`` continues to work unchanged.
"""

from vmware_aiops.cli._root import app

__all__ = ["app"]

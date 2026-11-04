"""
Stop-gap shim so `mkfigs` can be imported from the access-model-mkfigs git
submodule (default) or an external worktree (via MKFIGS_SRC), for both
interactive notebooks (ARE/JupyterHub, conda/analysis3) and Papermill batch
runs (mkfigs.sh) -- without a central package install.

Remove this file, and the `import mkfigs_bootstrap` line in each notebook's
second cell, if/when access-model-mkfigs is installed centrally in access3-26.0x.
"""
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent

_DEFAULT_MKFIGS_SRC = _REPO_ROOT / "external" / "access-model-mkfigs" / "src"

_MKFIGS_SRC = Path(
    os.environ.get("MKFIGS_SRC") or _DEFAULT_MKFIGS_SRC
).expanduser().resolve()

if not (_MKFIGS_SRC / "mkfigs" / "__init__.py").is_file():
    raise ImportError(
        f"mkfigs package not found at {_MKFIGS_SRC}.\n"
        "Set MKFIGS_SRC to a valid mkfigs src directory, "
        "or initialise the submodule with:\n"
        "    git submodule update --init --recursive"
    )

# Ensure the selected source takes precedence over other installations.
_src = str(_MKFIGS_SRC)

# Remove the source from sys.path if it is already present, to avoid duplicates.
if _src in sys.path:
    sys.path.remove(_src)

# Add the source to the front of sys.path so it takes precedence over other installations.
sys.path.insert(0, _src)

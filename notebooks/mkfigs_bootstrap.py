"""
Stop-gap shim so `mkfigs` can be imported from the access-model-mkfigs git
submodule, for both interactive notebooks (ARE/JupyterHub, conda/analysis3)
and papermill batch runs (mkfigs.sh) -- without a central package install.

Remove this file, and the `import mkfigs_bootstrap` line in each notebook's
second cell, if/when access-model-mkfigs is installed centrally in access3-26.0x.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_MKFIGS_SRC = _REPO_ROOT / "external" / "access-model-mkfigs" / "src"

if not (_MKFIGS_SRC / "mkfigs").is_dir():
    raise ImportError(
        f"access-model-mkfigs submodule not found at {_MKFIGS_SRC}.\n"
        "Git clone was probably done without submodules. Run:\n"
        "    git submodule update --init --recursive"
    )

if str(_MKFIGS_SRC) not in sys.path:
    sys.path.insert(0, str(_MKFIGS_SRC))

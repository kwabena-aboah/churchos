# Cell Group model lives in apps.core.models (CellGroup, Zone).
# This module re-exports for convenience.
from apps.core.models import CellGroup, Zone
__all__ = ["CellGroup", "Zone"]

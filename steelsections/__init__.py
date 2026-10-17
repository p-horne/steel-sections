import importlib.resources
from .catalogue import SectionCatalogue
from .analysis import SectionProperties
from . import data

# Automatically load the standard bundled catalogues
with importlib.resources.as_file(importlib.resources.files(data) / "nz_sections.csv") as nz_csv:
    nz = SectionCatalogue(nz_csv)
with importlib.resources.as_file(importlib.resources.files(data) / "uk_sections.csv") as uk_csv:
    uk = SectionCatalogue(uk_csv)

__all__ = ["SectionCatalogue", "SectionProperties", "nz", "uk"]
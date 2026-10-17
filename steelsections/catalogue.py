import pandas as pd
import importlib.resources
from pathlib import Path
from typing import Dict, List, Union
from sectionproperties.analysis.section import Section

from . import data
from .analysis import build_section, create_sp_section, SectionProperties


class SectionCatalogue:
    """A catalogue of section geometry properties created from from a CSV file or DataFrame.

    Source dimensions must be in millimetres. Section names are matched
    without spaces and are case-insensitive.
    """
    def __init__(self, data_source: Union[str, Path, pd.DataFrame]):
        """Initialise the catalogue from a CSV path or pandas DataFrame."""
        if isinstance(data_source, pd.DataFrame):
            self.df = self._sanitize_df(data_source.copy())
        else:
            self.df = self._load_and_sanitize_csv(data_source)

    def _sanitize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Index the DataFrame by lowercase section names with spaces removed."""
        df['lookup_key'] = df['name'].astype(str).str.replace(" ", "").str.lower()
        df.set_index('lookup_key', inplace=True)
        return df

    def _load_and_sanitize_csv(self, csv_path: Union[str, Path]) -> pd.DataFrame:
        """Read a CSV file and prepare its section-name lookup index."""
        df = pd.read_csv(csv_path)
        return self._sanitize_df(df)

    def _get_scaled_geometry(self, name: str, units: str, include_radius: bool) -> dict:
        """Look up section geometry and convert dimensions to 'm' or 'mm'.

        Missing values are omitted, except corner_radius, which defaults
        to zero. Set include_radius=False to use a zero corner radius."""
        if units not in ["m", "mm"]:
            raise ValueError("Units must be 'm' or 'mm'.")

        lookup_key = name.replace(" ", "").lower()
        if lookup_key not in self.df.index:
            raise KeyError(f"Section '{name}' not found in catalogue.")

        row = self.df.loc[lookup_key]
        geom_dict = row.dropna().to_dict()

        if not include_radius and "corner_radius" in geom_dict:
            geom_dict["corner_radius"] = 0.0

        if "corner_radius" not in geom_dict:
            geom_dict["corner_radius"] = 0.0

        if units == "m":
            for key in ["depth", "breadth", "web_thickness", "flange_thickness", "corner_radius"]:
                if key in geom_dict and isinstance(geom_dict[key], (int, float)):
                    geom_dict[key] *= 0.001

        return geom_dict

    def get_section(self, name: str, units: str = "m", include_radius: bool = True) -> SectionProperties:
        """
        Build and return a SectionProperties object for the named section.

        Use units='m' or 'mm'. Set include_radius=False to ignore corner radii.
        """
        geom = self._get_scaled_geometry(name, units, include_radius)
        return build_section(geom['name'], geom['shape'], geom)

    def get_geometry(self, name: str, units: str = "m", include_radius: bool = True) -> dict:
        """
        Return the section name, shape, and geometry as a dictionary.

        Use units='m' or 'mm'. Set include_radius=False to ignore corner radii.
        """
        geom = self._get_scaled_geometry(name, units, include_radius)
        geom.pop("lookup_key", None)
        return geom

    def get_sp_section(self, name: str, units: str = "m", include_radius: bool = True) -> Section:
        """
        Build and return a sectionproperties Section for the named section.

        Use units='m' or 'mm'. Set include_radius=False to ignore corner radii.
        """
        geom = self._get_scaled_geometry(name, units, include_radius)
        return create_sp_section(geom['shape'], geom)

    def get_section_list(self, shapes=['I', 'RHS']):
        """
        Return section names matching the supplied list of shape codes.
        Supported codes are 'I', 'C', 'RHS', and 'CHS'. Defaults to I and RHS sections and preserves catalogue order.
        """
        return self.df.loc[self.df["shape"].isin(shapes), "name"].tolist()

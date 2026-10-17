# My Steel Sections

A simple Python package for structural steel section properties.

Rather than using static databasess of section properties from different countries, section properties are calculated from the section geometry using the finite element method via `sectionproperties`. 

Supported shapes are I-sections (UB, UC, etc), Parallel Flange Channels (PFC), Square/Rectangular Hollow Sections (SHS/RHS), Circular Hollow Sections (CHS). Elliptical, crtuciform and other more unusual and compex shapes are not currently supported.

The package includes in-built databases for UB and UC sections available in New Zealand and the United Kingdom.
Note SHS-HF and RHS-HF mean hot formed. The corner radius differs for cold and hot formed sections.


## Usage

The package has three main functions. For each region group of steel sections:

get_section(name, units="m", include_radius=True) - Dynamically calculates structural properties (geometric, warping, plastic) using finite element analysis and returns a typed SteelSection Dataclass.

get_geometry(name, units="m", include_radius=True) - Returns the explicit manufacturing dimensions from the underlying CSV database as a clean dictionary, dropping any non-applicable fields.

get_sp_section(name, units="m", include_radius=True) - Returns a fully meshed Section object from the sectionproperties library, ready for plotting or advanced stress analysis workflows.

Additionally, all API functions accept an optional `include_radius` parameter (defaults to `True`). When set to `False`, the package overrides any value in the `corner_radius` column to `0.0`, forcing the finite element mesher to generate sharp corners. This is useful for simplified calculations or when comparing against older published tables that ignored radii.


### 1. Get section geomertry from a section code

```python
import my_steel_sections as ss

# Fetch a New Zealand UB in meters (default)
beam1 = ss.nz.get_geometry("UB 610x229x140")

# Fetch a UK beam in millimeters (no root radius or corner rounding sections)
beam2 = ss.uk.get_geometry("UB 457x191x98", units="mm")

# List of available sections of certain shape
ss.nz.get_section_list(['I', 'RHS'])
```


### 2. Get section properties from a section code

```python
import my_steel_sections as ss

# Fetch a New Zealand UB in meters (default)
beam1 = ss.nz.get_section("UB 610x229x140")
print(f"Ix: {beam.Ix} m^4")


# Fetch a UK beam in millimeters (no root radius or corner rounding sections)
beam2 = ss.uk.get_section("UB 457x191x98", units="mm")
```


### 3. Get a 'Section` object that can be used further for other tasks
Refer to the `sectionproperties` package for more information:

```python
import my_steel_sections as ss

sp_section = ss.uk.get_sp_section("UB 457x191x98", units="m")
sp_section.plot_mesh()
```


### 4. Load a catalogue of custom sections from your own csv of project specific section geometry
```python
import my_steel_sections as ss

ss.custom = ss.SectionCatalogue("my_custom_beams.csv")
girder = ss.custom.get_section("PG 1200x400")
```


## Data Schema
Section geometry is read from a CSV files. All dimensions must be provided in **millimeters (mm)**. The CSV must include the following columns:

| Column | Description | Required? |
| :--- | :--- | :--- |
| `name` | The section designation (e.g., `UB 610x229x140`). Used as the lookup key. | All sections |
| `shape` | The section shape (see below). Accepted values: `I`, `C`, `RHS`, `CHS`. | All sections |
| `depth` | Overall vertical dimension. For CHS, this is the outer diameter. | All sections |
| `breadth` | Overall horizontal dimension (width). | I, C, RHS. Leave blank for CHS |
| `web_thickness` | Web thickness for I and C sections. For RHS and CHS, this is the uniform wall thickness. | All sections |
| `flange_thickness` | Flange thickness. | I, C. Leave blank for other section types |
| `corner_radius` | See the radius rules below. | I, C, RHS. Leave blank for other section types |

The header row is required: `name,shape,depth,breadth,web_thickness,flange_thickness,corner_radius`

### Valid Shape Types
- **`I`** — I-sections (Universal Beams, Universal Columns, I, H etc). Requires: `depth`, `breadth`, `web_thickness`, `flange_thickness`, `corner_radius`.
- **`C`** — Channels (Parallel Flange Channels). Requires: `depth`, `breadth`, `web_thickness`, `flange_thickness`, `corner_radius`.
- **`RHS`** — Rectangular and Square Hollow Sections. Requires: `depth`, `breadth`, `web_thickness`, `corner_radius`. The `flange_thickness` column is ignored.
- **`CHS`** — Circular Hollow Sections. Requires: `depth` (outer diameter), `web_thickness` (wall thickness). The `breadth`, `flange_thickness`, and `corner_radius` columns are ignored.

### How `corner_radius` is used
The `corner_radius` column has a dual meaning depending on the section shape, and can be left blank for sections where it does not apply:
- **For `I` and `C` sections:** This is the **root radius** (the fillet between the web and flange).
- **For `RHS` sections:** This is the **outer corner radius**.
- **For `CHS` sections:** This column is ignored.


### Example CSV
```csv
name,shape,depth,breadth,web_thickness,flange_thickness,corner_radius
UB 610x229x140,I,617.0,230.0,13.1,22.1,14.0
UC 310x97,I,308.0,305.0,9.9,15.4,16.5
PFC 300x90,C,300.0,90.0,8.0,15.5,14.0
RHS 200x100x5.0,RHS,200.0,100.0,5.0,,10.0
SHS 150x150x6.0,RHS,150.0,150.0,6.0,,12.0
CHS 114.3x4.5,CHS,114.3,,4.5,,
```

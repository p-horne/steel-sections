import sectionproperties.pre.library.steel_sections as sp_steel
from sectionproperties.analysis.section import Section
from dataclasses import dataclass

@dataclass(frozen=True)
class SectionProperties:
    """Read-only container for section properties."""
    name: str
    shape: str
    Area: float
    Ix: float
    Iy: float
    Zx: float
    Zy: float
    Sx: float
    Sy: float
    rx: float
    ry: float
    J: float
    Iw: float


def create_sp_section(shape: str, geom: dict) -> Section:
    """
    Builds and meshes a `sectionproperties` Section object from a dictionary
    of geometric dimensions. Assumes all dimensions are already scaled
    to the desired units.
    
    Args:
        shape: Section type identifier ('I', 'C', 'RHS', 'CHS').
        geom: Dictionary of geometric dimensions (depth, breadth, 
             web_thickness, flange_thickness, corner_radius).
             
    Returns:
        A fully meshed Section object ready for analysis.
    """

    # n_r = Number of points discretising the root radius

    if shape == "I":
        sp_geom = sp_steel.i_section(
            d=geom['depth'], b=geom['breadth'], 
            t_f=geom['flange_thickness'], t_w=geom['web_thickness'], 
            r=geom['corner_radius'], n_r=8
        )
        mesh_size = (geom['depth'] * geom['breadth']) / 100.0

    elif shape == "C":
        sp_geom = sp_steel.channel_section(
            d=geom['depth'], b=geom['breadth'], 
            t_f=geom['flange_thickness'], t_w=geom['web_thickness'], 
            r=geom['corner_radius'], n_r=8
        )
        mesh_size = (geom['depth'] * geom['breadth']) / 100.0

    elif shape == "RHS":
        sp_geom = sp_steel.rectangular_hollow_section(
            d=geom['depth'], b=geom['breadth'], 
            t=geom['web_thickness'], r_out=geom['corner_radius'], n_r=8
        )
        mesh_size = (geom['depth'] * geom['breadth']) / 100.0

    elif shape == "CHS":
        sp_geom = sp_steel.circular_hollow_section(
            d=geom['depth'], t=geom['web_thickness'], n=32
        )
        mesh_size = (geom['depth'] * geom['depth']) / 100.0

    else:
        raise ValueError(f"Shape type '{shape}' is not supported.")

    sp_geom.create_mesh(mesh_sizes=[mesh_size])
    return Section(sp_geom)

def build_section(name: str, shape: str, geom: dict) -> SectionProperties:
    """
    Calculates section properties (geometric, warping, and plastic) via
    finite element analysis (using `sectionproperties`).
    
    Args:
        name: The section designation (e.g., 'UB 610x229x140').
        shape: Section type identifier ('I', 'C', 'RHS', 'CHS').
        geom: Dictionary of geometric dimensions, already scaled to
              the desired units.
              
    Returns:
        A SectionProperties dataclass containing the computed properties.
    """
    sec = create_sp_section(shape, geom)

    sec.calculate_geometric_properties()
    sec.calculate_warping_properties()
    sec.calculate_plastic_properties()

    z = sec.get_z()        
    s = sec.get_s()        
    rc = sec.get_rc()      
    ic = sec.get_ic()

    return SectionProperties(
        name=name,
        shape=shape,
        Area=sec.get_area(),
        Ix=ic[0],
        Iy=ic[1],
        Zx=min(z[0], z[1]), 
        Zy=min(z[2], z[3]),
        Sx=s[0],
        Sy=s[1],
        rx=rc[0],
        ry=rc[1],
        J=sec.get_j(),
        Iw=sec.get_gamma()
    )

#!/usr/bin/env python3
"""
Automated Validation Suite - Sample Model Generator
Creates realistic simulation model files for demonstration

Author: Ryan Hendrix - SOARZ Automation
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
import random

def create_sample_models(base_path):
    """
    Create realistic sample simulation models with both valid and invalid examples
    """
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating sample simulation models in: {base_path}")
    
    # Create valid model
    create_valid_fluid_model(base_path / "valid_fluid_model")
    
    # Create invalid model with errors
    create_invalid_thermal_model(base_path / "invalid_thermal_model")
    
    # Create model with warnings
    create_warning_structural_model(base_path / "warning_structural_model")
    
    # Create configuration file
    create_validation_config(base_path / "validation_config.json")
    
    # Create README
    create_sample_readme(base_path / "README_SAMPLE_MODELS.md")
    
    print("\nSample models created successfully!")
    print("Models available:")
    print("  • valid_fluid_model/ - Clean model that passes all validations")
    print("  • invalid_thermal_model/ - Model with critical errors")
    print("  • warning_structural_model/ - Model with warnings but no errors")
    print("  • validation_config.json - Configuration file for validation rules")

def create_valid_fluid_model(model_path):
    """Create a valid fluid dynamics simulation model"""
    model_path.mkdir(parents=True, exist_ok=True)
    
    # Main input file
    input_content = """# Fluid Dynamics Simulation Input
# Model: Pipe Flow Analysis
# Created: 2024-01-15

SIMULATION_TYPE = FLUID_DYNAMICS
SOLVER = NAVIER_STOKES

# Fluid Properties
temperature = 293.15
pressure = 101325
density = 1.225
viscosity = 1.81e-5
velocity = 25.0

# Geometry
pipe_diameter = 0.1
pipe_length = 2.0
inlet_area = 0.00785
outlet_area = 0.00785

# Solver Settings
max_iterations = 1000
convergence_tolerance = 1e-6
time_step = 0.001
total_time = 10.0

# Output Settings
output_frequency = 100
save_pressure = true
save_velocity = true
save_temperature = true
"""
    
    with open(model_path / "input.dat", 'w') as f:
        f.write(input_content)
    
    # Boundary conditions
    boundary_content = """# Boundary Conditions
# Inlet: Fixed velocity
# Outlet: Fixed pressure
# Walls: No-slip

INLET
  type = velocity_inlet
  velocity = 25.0
  temperature = 293.15
  
OUTLET
  type = pressure_outlet
  pressure = 101325
  
WALLS
  type = no_slip
  temperature = 293.15
"""
    
    with open(model_path / "boundary_conditions.txt", 'w') as f:
        f.write(boundary_content)
    
    # Material properties CSV
    material_data = [
        ['property', 'value', 'units'],
        ['density', '1.225', 'kg/m3'],
        ['viscosity', '1.81e-5', 'Pa·s'],
        ['specific_heat', '1005', 'J/kg·K'],
        ['thermal_conductivity', '0.026', 'W/m·K']
    ]
    
    with open(model_path / "material_properties.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(material_data)
    
    # Mesh information
    mesh_content = """# Mesh Configuration
# Generated automatically

MESH_TYPE = structured
ELEMENTS = 50000
NODES = 52500

# Element Quality
min_angle = 45.2
max_angle = 134.8
aspect_ratio_max = 2.1
skewness_max = 0.25

# Boundary Layers
boundary_layer_thickness = 0.001
boundary_layer_growth_rate = 1.2
boundary_layer_count = 5
"""
    
    with open(model_path / "mesh_info.txt", 'w') as f:
        f.write(mesh_content)

def create_invalid_thermal_model(model_path):
    """Create a thermal model with critical errors"""
    model_path.mkdir(parents=True, exist_ok=True)
    
    # Main input file with errors
    input_content = """# Thermal Analysis - Heat Transfer
# Model: Electronic Component Cooling
# Created: 2024-02-10

SIMULATION_TYPE = THERMAL
SOLVER = HEAT_TRANSFER

# Thermal Properties - ERRORS INTENTIONALLY INCLUDED
temperature = 50.0        # ERROR: Too low for Kelvin, probably Celsius
pressure = 1000000000     # ERROR: Extreme pressure value
density = -2.5           # ERROR: Negative density (impossible)
thermal_conductivity = 0.025
specific_heat = 1200

# Component Properties  
power_dissipation = 150
component_area = 0.001
heat_flux = power_dissipation / component_area

# Boundary Conditions
ambient_temperature = 25.0  # ERROR: Mixed units with temperature above
convection_coefficient = 50
surface_emissivity = 0.8

# Solver Settings
max_iterations = 2000
convergence_tolerance = 1e-8
"""
    
    with open(model_path / "input.dat", 'w') as f:
        f.write(input_content)
    
    # Missing required boundary conditions file - ERROR
    # (Intentionally not creating boundary_conditions.txt)
    
    # Material properties with formatting errors
    material_content = """property,value,units
density,-2.5,kg/m3
specific_heat,1200,J/kg·K
thermal_conductivity,0.025,W/m·K
# ERROR: Missing important properties
"""
    
    with open(model_path / "material_properties.csv", 'w') as f:
        f.write(material_content)
    
    # Empty mesh file - ERROR
    with open(model_path / "mesh_info.txt", 'w') as f:
        f.write("")  # Empty file

def create_warning_structural_model(model_path):
    """Create a structural model with warnings but no critical errors"""
    model_path.mkdir(parents=True, exist_ok=True)
    
    # Main input file
    input_content = """# Structural Analysis
# Model: Beam Deflection Study
# Created: 2024-03-05

SIMULATION_TYPE = STRUCTURAL
SOLVER = LINEAR_STATIC

# Material Properties
youngs_modulus = 200000000000  # Pa (Steel)
poisson_ratio = 0.3
density = 7850
yield_strength = 250000000

# Geometry
beam_length = 2.0
beam_width = 0.1
beam_height = 0.05
cross_sectional_area = beam_width * beam_height

# Loading Conditions
distributed_load = 5000     # N/m
point_load = 10000         # N
load_position = 1.0        # m from left end

# WARNING: High load for given geometry
# load_safety_factor = distributed_load / yield_strength * beam_length  

# Boundary Conditions
left_support = FIXED
right_support = PINNED

# Analysis Settings
max_iterations = 500
convergence_tolerance = 1e-5
"""
    
    with open(model_path / "input.dat", 'w') as f:
        f.write(input_content)
    
    # Boundary conditions
    boundary_content = """# Structural Boundary Conditions

LEFT_END
  type = fixed_support
  displacement_x = 0
  displacement_y = 0
  rotation_z = 0
  
RIGHT_END
  type = pinned_support  
  displacement_x = FREE
  displacement_y = 0
  rotation_z = FREE

LOADING
  distributed_load = 5000 N/m
  point_load = 10000 N at x=1.0m
"""
    
    with open(model_path / "boundary_conditions.txt", 'w') as f:
        f.write(boundary_content)
    
    # Material properties
    material_data = [
        ['property', 'value', 'units'],
        ['youngs_modulus', '200000000000', 'Pa'],
        ['poisson_ratio', '0.3', 'dimensionless'],
        ['density', '7850', 'kg/m3'],
        ['yield_strength', '250000000', 'Pa']
    ]
    
    with open(model_path / "material_properties.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(material_data)

def create_validation_config(config_path):
    """Create validation configuration file"""
    config = {
        "file_types": [".dat", ".inp", ".txt", ".csv", ".json"],
        "parameter_ranges": {
            "temperature": [200, 800],
            "pressure": [0, 500000],
            "velocity": [0, 100],
            "density": [0.1, 10000],
            "youngs_modulus": [1000000000, 500000000000],
            "poisson_ratio": [0.1, 0.5]
        },
        "required_files": [
            "input.dat",
            "boundary_conditions.txt", 
            "material_properties.csv"
        ],
        "validation_rules": [
            "file_existence",
            "file_format", 
            "parameter_ranges",
            "cross_file_consistency",
            "physics_validation"
        ],
        "physics_constraints": {
            "density_positive": True,
            "temperature_reasonable": True,
            "pressure_limits": True
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def create_sample_readme(readme_path):
    """Create README for sample models"""
    readme_content = """# Sample Simulation Models

This directory contains sample simulation models for demonstrating the automated validation system.

## Models Included

### valid_fluid_model/
A properly configured fluid dynamics simulation with:
- Correct parameter ranges and units
- All required files present
- Consistent cross-file relationships
- Physically realistic values

**Expected Result**: Passes all validation checks

### invalid_thermal_model/
A thermal analysis model with intentional errors:
- Temperature in wrong units (Celsius vs Kelvin)
- Impossible negative density value
- Extreme pressure value outside reasonable range
- Missing required boundary conditions file
- Empty mesh information file

**Expected Result**: Multiple critical errors detected

### warning_structural_model/
A structural analysis model with warnings but no critical errors:
- High loading conditions that generate warnings
- All required files present and properly formatted
- Parameters within acceptable ranges but near limits

**Expected Result**: Passes with warnings about loading conditions

## Validation Configuration

The `validation_config.json` file defines:
- Acceptable parameter ranges for different simulation types
- Required file lists for complete model validation
- Physics-based constraints and checks
- File format requirements

## Usage

Run validation on any model:
```bash
python validation_engine.py valid_fluid_model/
python validation_engine.py invalid_thermal_model/ --verbose
python validation_engine.py warning_structural_model/ --config validation_config.json
```

## Error Examples Demonstrated

1. **Unit Consistency Errors**: Mixed Celsius/Kelvin temperatures
2. **Physical Impossibilities**: Negative density values
3. **Extreme Values**: Pressures outside reasonable engineering ranges
4. **Missing Files**: Required input files not present
5. **Format Issues**: Empty or malformed configuration files
6. **Cross-File Inconsistencies**: Parameter values that don't match between files

This sample data demonstrates the types of errors commonly found in real simulation workflows and how automated validation catches them systematically.
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create sample simulation models for validation demo')
    parser.add_argument('output_path', nargs='?', default='sample_models', 
                       help='Path where sample models will be created')
    
    args = parser.parse_args()
    
    create_sample_models(args.output_path)
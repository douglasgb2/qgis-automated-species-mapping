# qgis-automated-species-mapping
Automated species mapping system using Python/PyQGIS. Processes Excel data, creates symbolized layers, and batch exports PDF maps. Reduces manual work from 15-20 min/map to 30 seconds. Perfect for environmental licensing and biodiversity research projects.

# QGIS Automated Species Mapping

An automated cartographic production system that transforms manual species distribution mapping from hours to minutes using Python/PyQGIS integration.

## Overview

This automation system processes biodiversity datasets and generates professional-quality species distribution maps at scale. Originally developed for environmental licensing projects, it handles hundreds of species records and produces customized PDF maps with consistent styling and layout.

**Key Benefits:**
- 95% time reduction: From 15-20 minutes to 30 seconds per map
- Batch processing: Handle 800+ specimens generating 100+ unique maps
- Consistent styling: Automated symbology for herbarium vs field records
- Professional layouts: Custom legends, titles, and reference layers
- Reproducible workflow: Reusable for multiple projects

## Features

### Data Processing (species_data_loader.py)
- **Excel Integration**: Automatic loading and filtering of species coordinate data
- **Smart Grouping**: Organizes records by source type (Common, Herbarium Only, Field Only)
- **Coordinate Validation**: Filters out records with missing or invalid coordinates
- **Dynamic Symbolization**: 
  - Herbarium records: Colored circles with white borders
  - Field records: Colored triangles with black center dots
- **Layer Organization**: Hierarchical legend structure for easy navigation

### Map Export (batch_map_exporter.py)
- **Layout Automation**: Dynamic title and numbering updates
- **Multi-layer Management**: Handles base layers, species data, and reference maps
- **Custom Legends**: Contextual legend generation excluding unnecessary elements
- **High-Quality Export**: 300 DPI PDF output with vector graphics
- **Batch Processing**: Sequential export with sanitized filenames

## Prerequisites

### Software Requirements
- **QGIS 3.x** with Python console enabled
- **Python Libraries**:
  - pandas - Data manipulation
  - PyQt5 - GUI components
  - qgis.core - QGIS API access

### Data Requirements
- **Excel file** with the following columns:
  - Longitude (numeric)
  - Latitude (numeric)
  - Match (text: "Comum", "Só no Herbário", "Só no Campo")
  - Espécie (text: species name)
  - Fonte (text: "Herbário" or "Campo")
  - Mapa (numeric: map reference number)

### QGIS Setup
- **Layout Template**: Create a layout named "Atlas_Layout_LTs" with:
  - Title label item
  - Notes label item (for map numbering)
  - Map 1 (main species map)
  - Map 2 (reference/context map)
  - Legend item
- **Base Layers**: The default configuration includes Brazilian administrative layers, but you can customize these for any region:
  - AU_2022_AreasUrbanizadas2019_Brasil (Urban areas) - Replace with your local urban boundaries
  - BR_Municipios_2023 (Municipal boundaries) - Replace with your administrative divisions
  - Google Satellite (Satellite imagery) - Any satellite/aerial imagery layer
  - complexo_toropi (Study area) - Your specific study area boundary
  - BR_UF_2023 (State boundaries) - Replace with your regional boundaries

**Note**: Layer names are configurable in the script. Update the `base_layers_names` and `map2_layers_names` variables to match your local layers.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/qgis-automated-species-mapping.git
   cd qgis-automated-species-mapping
   ```

2. **Prepare your data**:
   - Place your Excel file in the project directory
   - Update the file path in species_data_loader.py:
     ```python
     path = "your_path_to_excel_file.xlsx"
     ```

3. **Configure layers for your region**:
   - Update base layer names in batch_map_exporter.py:
     ```python
     base_layers_names = [
         "your_urban_areas_layer",
         "your_admin_boundaries_layer", 
         "your_satellite_layer"
     ]
     ```
4. **Configure output directory**:
   - Update the output folder in batch_map_exporter.py:
     ```python
     output_folder = "C:/your/output/directory"
     ```

## Usage

### Step 1: Load and Process Species Data

1. Open QGIS and load your base layers
2. Open the Python Console (Plugins > Python Console)
3. Run the data loading script:
   ```python
   exec(open('species_data_loader.py').read())
   ```

This will:
- Load your Excel data
- Create memory layers grouped by match type
- Apply appropriate symbology
- Organize layers in the legend tree

### Step 2: Batch Export Maps

1. Ensure your layout template is properly configured
2. Run the export script:
   ```python
   exec(open('batch_map_exporter.py').read())
   ```

This will:
- Process each species layer sequentially
- Update layout elements dynamically
- Export individual PDF maps
- Generate numbered filenames

### Step 3: Review Output

Maps will be exported as:
```
01_Species_name_one.pdf
02_Species_name_two.pdf
03_Species_name_three.pdf
...
```

## Configuration

### Adapting for Different Regions

This system was originally developed for Brazilian biodiversity mapping but can be adapted for any geographic region:

1. **Update layer names** in batch_map_exporter.py to match your local data:
   ```python
   # Replace Brazilian layers with your regional equivalents
   base_layers_names = [
       "your_urban_areas_layer",      # Urban/developed areas
       "your_admin_boundaries_layer", # Administrative boundaries
       "your_satellite_imagery"       # Satellite or aerial imagery
   ]
   
   map2_layers_names = [
       "your_study_area_boundary",    # Project study area
       "your_regional_context_layer"  # Regional reference layer
   ]
   ```

2. **Customize legend labels** for your region:
   ```python
   base_layer_custom_names = {
       "your_urban_areas_layer": "Urban Areas",
       "your_admin_boundaries_layer": "Administrative Boundaries"
   }
   ```

### Customizing Symbology

Edit the symbol creation section in species_data_loader.py:

```python
# Herbarium records (circles)
if valor == "Registro de Herbário":
    circle.setColor(QColor(your_r, your_g, your_b))
    circle.setSize(your_size)

# Field records (triangles)
else:
    triangle.setColor(QColor(your_r, your_g, your_b))
    triangle.setSize(your_size)
```

### Layout Customization

Modify text templates in batch_map_exporter.py:

```python
title_item.setText(f"Your custom title: {species_name}")
notes_item.setText(f"Map #{idx} of {len(species_layers)}")
```

### Export Settings

Adjust PDF quality and format:

```python
export_settings.dpi = 300  # Change resolution
export_settings.forceVectorOutput = True  # Vector vs raster
```

## Performance Metrics

| Metric | Manual Process | Automated Process | Improvement |
|--------|---------------|------------------|-------------|
| Time per map | 15-20 minutes | 30 seconds | 95% reduction |
| Maps per hour | 3-4 maps | 100+ maps | 25x increase |
| Error rate | ~10% styling errors | <1% errors | 90% reduction |
| Consistency | Variable | 100% consistent | Perfect standardization |

## Troubleshooting

### Common Issues

**"Layout not found" error**:
- Verify layout name matches exactly: "Atlas_Layout_LTs"
- Check layout items have correct IDs

**"Layer not found" warnings**:
- Ensure all base layers are loaded in QGIS
- Check layer names match exactly (case-sensitive)
- Update layer names in the script to match your local data

**Empty maps**:
- Verify coordinate data is in correct format (decimal degrees)
- Check CRS settings (should be EPSG:4326)

**Export failures**:
- Ensure output directory exists and is writable
- Check for special characters in species names

### Debug Mode

Add debug prints to track progress:

```python
print(f"Processing species: {species_name}")
print(f"Features found: {len(list(layer.getFeatures()))}")
```

## Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Developed for environmental consulting and biodiversity research
- QGIS community for excellent Python API documentation
- Environmental licensing teams for workflow requirements

## Contact

For questions, suggestions, or collaboration opportunities, please open an issue or contact the development team.

---

**Note**: This automation saved over 30 hours per week in a real environmental licensing project, processing 800+ specimens to generate 106 unique species distribution maps.

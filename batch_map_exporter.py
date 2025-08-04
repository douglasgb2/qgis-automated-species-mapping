import os
from qgis.core import (
    QgsProject,
    QgsLayoutExporter,
    QgsLayoutItemMap,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayerTreeLayer,
    QgsLayerTreeGroup
)
from qgis.utils import iface

# === CONFIGURATION ===
layout_name = "Atlas_Layout_LTs"
output_folder = "C:/Users/Douglas/Desktop/Celtes/LTs combinado"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

project = QgsProject.instance()
layout = project.layoutManager().layoutByName(layout_name)
if not layout:
    raise Exception(f"❌ Layout '{layout_name}' not found.")

# Find layout items
title_item = None
notes_item = None
map1_item = None
map2_item = None
legend_item = None

for item in layout.items():
    if isinstance(item, QgsLayoutItemLabel):
        if "Mapa de registros de campo" in item.text() or "Mapa de distribuição" in item.text():
            title_item = item
        elif "Mapa nº" in item.text():
            notes_item = item
    elif isinstance(item, QgsLayoutItemMap):
        if item.id() == "Map 1":
            map1_item = item
        elif item.id() == "Map 2":
            map2_item = item
    elif isinstance(item, QgsLayoutItemLegend):
        legend_item = item

if not all([title_item, notes_item, map1_item, legend_item]):
    raise Exception("❌ Required layout items (title, notes, Map 1, legend) not found.")

# === Prepare base layers ===
base_layers_names = [
    "AU_2022_AreasUrbanizadas2019_Brasil",
    "BR_Municipios_2023",
    "Google Satellite"
]
base_layers = []
for name in base_layers_names:
    layers = project.mapLayersByName(name)
    if layers:
        base_layers.append(layers[0])
    else:
        print(f"⚠️ Base layer '{name}' not found.")

# === Map 2 layers (must remain untouched) ===
map2_layers_names = ["complexo_toropi", "BR_UF_2023"]
map2_layers = []
for name in map2_layers_names:
    layers = project.mapLayersByName(name)
    if layers:
        map2_layers.append(layers[0])
    else:
        print(f"⚠️ Map 2 layer '{name}' not found.")

# Ensure Map 2 layers are always set and visible
if map2_item and map2_layers:
    map2_item.setLayers(map2_layers)
    for layer in map2_layers:
        layer.setCustomProperty("identify/disable", False)

# === Species groups to process ===
species_group_names = ["Comum", "Só no Herbário", "Só no Campo"]

# Make sure species groups and their layers are visible in the Layer Panel
root = project.layerTreeRoot()
for group_name in species_group_names:
    group = root.findGroup(group_name)
    if group:
        group.setItemVisibilityChecked(True)
        for child in group.children():
            if hasattr(child, 'setItemVisibilityChecked'):
                child.setItemVisibilityChecked(True)

# Collect all species layers from these groups
species_layers = []
for group_name in species_group_names:
    group = root.findGroup(group_name)
    if group:
        def collect_layers_from_group(group_node):
            for child in group_node.children():
                if isinstance(child, QgsLayerTreeLayer):
                    species_layers.append(child.layer())
                elif isinstance(child, QgsLayerTreeGroup):
                    # Recursively collect from nested groups
                    collect_layers_from_group(child)
        
        collect_layers_from_group(group)

if not species_layers:
    raise Exception("❌ No species layers found under expected groups.")

# Remove duplicates and sort alphabetically
species_layers = list(set(species_layers))
species_layers.sort(key=lambda l: l.name().lower())

print(f"📊 Found {len(species_layers)} species layers to process")

# === Legend customization function ===
def customize_legend_for_species(species_layer):
    """Customize legend to show only relevant layers for current species"""
    legend_model = legend_item.model()
    legend_root = legend_model.rootGroup()

    # Clear existing legend entries
    legend_root.clear()

    # Add species layer to legend first (will appear on top)
    legend_root.addLayer(species_layer)
    
    # Find the species layer node and customize it
    for child in legend_root.children():
        if isinstance(child, QgsLayerTreeLayer) and child.layer() == species_layer:
            # Keep original layer name for species
            child.setName(species_layer.name())
            
            # The legend will automatically show the symbology for 
            # "Registro de Campo" and "Registro de Herbário" features
            # since they are part of the same shapefile with categorized styling
            break

    # Add base layers with custom names (excluding Google Satellite)
    base_layer_custom_names = {
        "AU_2022_AreasUrbanizadas2019_Brasil": "Áreas Urbanizadas",
        "BR_Municipios_2023": "Limites Municipais"
    }
    
    for layer in base_layers:
        if layer.name() != "Google Satellite":  # Exclude Google Satellite from legend
            legend_root.addLayer(layer)
            # Find the added layer node and rename it
            for child in legend_root.children():
                if isinstance(child, QgsLayerTreeLayer) and child.layer() == layer:
                    custom_name = base_layer_custom_names.get(layer.name(), layer.name())
                    child.setName(custom_name)
                    break

    # Hide all group names in legend by setting them to empty string
    def hide_group_names(node):
        if isinstance(node, QgsLayerTreeGroup):
            node.setName("")
            for child in node.children():
                hide_group_names(child)

    hide_group_names(legend_root)

    # Refresh legend
    legend_item.setAutoUpdateModel(True)
    legend_item.refresh()

# === Main export loop ===
print("📤 Starting PDF export process...")

for idx, species_layer in enumerate(species_layers, start=1):
    species_name = species_layer.name()

    print(f"🔄 Exporting map {idx}/{len(species_layers)}: {species_name}")

    # Update title and notes text
    title_item.setText(f"Mapa de distribuição de {species_name}")
    notes_item.setText(f"Mapa nº {idx}")

    # Map 1 layers: species layer first (on top), then base layers
    layers_for_map1 = [species_layer] + base_layers  # Species layer first for proper visibility

    # Set layers for Map 1
    map1_item.setLayers(layers_for_map1)

    # Ensure Map 2 layers remain unchanged
    if map2_item and map2_layers:
        map2_item.setLayers(map2_layers)

    # Customize legend for current species (excludes Google Satellite)
    customize_legend_for_species(species_layer)

    # Refresh all components
    iface.mapCanvas().refresh()
    iface.mapCanvas().refreshAllLayers()
    map1_item.refresh()
    if map2_item:
        map2_item.refresh()
    legend_item.refresh()
    layout.refresh()

    # Export PDF with sanitized filename
    safe_name = "".join(c for c in species_name if c.isalnum() or c in " ()-_")
    pdf_path = os.path.join(output_folder, f"{idx:02d}_{safe_name}.pdf")

    # Configure export settings
    exporter = QgsLayoutExporter(layout)
    export_settings = QgsLayoutExporter.PdfExportSettings()
    export_settings.dpi = 300  # High quality export
    export_settings.forceVectorOutput = True
    export_settings.exportMetadata = True

    # Export to PDF
    result = exporter.exportToPdf(pdf_path, export_settings)

    if result == QgsLayoutExporter.Success:
        print(f"✅ Successfully exported: {pdf_path}")
    else:
        print(f"❌ Failed to export: {pdf_path} (Error code: {result})")

print("🏁 All maps exported successfully.")
print(f"📁 Output folder: {output_folder}")
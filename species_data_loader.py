import pandas as pd
import random
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFields, QgsField, QgsPointXY,
    QgsFeature, QgsGeometry, QgsSymbol, QgsSimpleMarkerSymbolLayer,
    QgsRendererCategory, QgsCategorizedSymbolRenderer
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPointF
from qgis.PyQt.QtCore import QVariant

# === 1. Load Excel File ===
path = "C:/Users/Douglas/Desktop/Celtes/Registros_Combinados.xlsx"
df = pd.read_excel(path)

# Filter out records without coordinates
df = df[df['Longitude'].notna() & df['Latitude'].notna()]

# === 2. Access Project and Layer Tree ===
project = QgsProject.instance()
root = project.layerTreeRoot()

# === 3. Group records by "Match" (Comum, Só no Herbário, Só no Campo) ===
for group_key, group_df in df.groupby("Match"):
    # Create main group in legend
    match_group = root.findGroup(group_key)
    if not match_group:
        match_group = root.addGroup(group_key)

    # === 4. Group species within each match category ===
    for especie, especie_df in group_df.groupby("Espécie"):
        layer_name = f"{especie}"

        # Create memory layer
        fields = QgsFields()
        fields.append(QgsField("Espécie", QVariant.String))
        fields.append(QgsField("Latitude", QVariant.Double))
        fields.append(QgsField("Longitude", QVariant.Double))
        fields.append(QgsField("Fonte", QVariant.String))
        fields.append(QgsField("Mapa", QVariant.Int))

        layer = QgsVectorLayer("Point?crs=EPSG:4326", layer_name, "memory")
        prov = layer.dataProvider()
        prov.addAttributes(fields)
        layer.updateFields()

        # Add features
        features = []
        for _, row in especie_df.iterrows():
            point = QgsPointXY(float(row['Longitude']), float(row['Latitude']))
            feature = QgsFeature()
            geometry = QgsGeometry.fromPointXY(point)

            # Rename species based on Fonte
            especie_nome = "Registro de Herbário" if row['Fonte'] == "Herbário" else "Registro de Campo"

            feature.setGeometry(geometry)
            feature.setAttributes([
                especie_nome,
                row['Latitude'],
                row['Longitude'],
                row['Fonte'],
                int(row['Mapa']) if not pd.isna(row['Mapa']) else None
            ])
            features.append(feature)

        prov.addFeatures(features)
        layer.updateExtents()

        # === 5. Symbolize by Renamed "Espécie" field ===
        categorias = []
        valores = list({f["Espécie"] for f in layer.getFeatures()})

        for valor in valores:
            if valor == "Registro de Herbário":
                simbolo = QgsSymbol.defaultSymbol(layer.geometryType())
                circle = QgsSimpleMarkerSymbolLayer()
                circle.setShape(QgsSimpleMarkerSymbolLayer.Circle)
                circle.setColor(QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                circle.setStrokeColor(QColor("#ffffff"))
                circle.setStrokeWidth(0.3)
                circle.setSize(2)
                circle.setRenderingPass(1)  # Draw this after Campo

                simbolo.deleteSymbolLayer(0)
                simbolo.appendSymbolLayer(circle)

            else:  # Registro de Campo
                simbolo = QgsSymbol.defaultSymbol(layer.geometryType())

                # Triangle
                triangle = QgsSimpleMarkerSymbolLayer()
                triangle.setShape(QgsSimpleMarkerSymbolLayer.Triangle)
                triangle.setColor(QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                triangle.setSize(3)
                triangle.setRenderingPass(0)

                # Black dot
                black_dot = QgsSimpleMarkerSymbolLayer()
                black_dot.setShape(QgsSimpleMarkerSymbolLayer.Circle)
                black_dot.setColor(QColor("black"))
                black_dot.setSize(1)
                black_dot.setOffset(QPointF(0, 0.5))
                black_dot.setRenderingPass(0)

                simbolo.deleteSymbolLayer(0)
                simbolo.appendSymbolLayer(triangle)
                simbolo.appendSymbolLayer(black_dot)

            categoria = QgsRendererCategory(valor, simbolo, valor)
            categorias.append(categoria)

        renderer = QgsCategorizedSymbolRenderer("Espécie", categorias)
        layer.setRenderer(renderer)
        layer.renderer().setUsingSymbolLevels(True)  # Ensures draw order

        # === 6. Add to project under correct legend group ===
        project.addMapLayer(layer, False)
        match_group.addLayer(layer)

print("✅ Camadas carregadas com simbologia e ordem de desenho correta.")

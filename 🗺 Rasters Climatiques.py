import streamlit as st
from streamlit_folium import folium_static
import folium
import rasterio
import numpy as np
import branca.colormap as cm
import pandas as pd

st.set_page_config(
    page_title="Morocco Clima\u2013MAPS",
    page_icon="🗺️",
)
# Set Page Header   
st.markdown(
    """
    <div style="text-align:center">
        <h2>🌍 Exploration temporelle des Rasters Climatiques</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
        # Set custom CSS for hr element
        # Set custom CSS for hr element
st.markdown("""
        <style>
            hr {
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
                height: 3px;
                background-color: #333;
                border: none;
            }
        </style>
    """, unsafe_allow_html=True)

        # Add horizontal line
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

def load_tif_image(column_type, day_offset):
    column_mapping = {
        "🌧  Précipitation": "prec",
        "🌡️ Température": "temp",
        "💧 Humidité": "hum"
    }
    
    if column_type not in column_mapping:
        raise ValueError(f"Le type de colonne {column_type} n'est pas pris en charge.")

    tif_path = f"cliptemp/{column_mapping[column_type]}{day_offset}.tif"
    basemap = rasterio.open(tif_path)

    # Utilise la méthode read pour récupérer l'image
    img = basemap.read(1)
    
    return img, basemap.bounds

def create_heatmap(column_type, day_offset=0):
    day = f'Jour {day_offset}' if day_offset >= 0 else f'Jour {abs(day_offset)} avant'

    # Create a folium map
    m = folium.Map(location=[29.985782, -8.668263], zoom_start=4.5)  # Coordonnées centrées sur le Maroc

    # Ajouter le plugin Fullscreen
    folium.plugins.Fullscreen().add_to(m)

    # Ajouter le plugin MousePosition
    folium.plugins.MousePosition().add_to(m)

    # Ajouter le plugin Draw avec le mode rectangle activé
    folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(m)
    folium.plugins.MiniMap().add_to(m)
    

    # Load the TIF image for the selected column type and day
    basemap_image, bounds = load_tif_image(column_type, day_offset)

    # Ajuste les coordonnées pour encadrer la région du Maroc
    bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

    # Ajoute l'image GeoTIFF à la carte Folium en utilisant la colormap viridis
    image_overlay = folium.raster_layers.ImageOverlay(image=basemap_image, bounds=bounds, opacity=1, colormap=lambda x: (0, 0, 1, x))
    image_overlay.add_to(m)

    # Create a colormap legend with custom min and max values
    if column_type == "🌧  Précipitation":
        colormap = cm.LinearColormap(colors=['white', 'blue'], vmin=0, vmax=100)
        colormap.caption = f'Legend - Min: 0, Max: 100 ({column_type})'
    elif column_type == "🌡️ Température":
        colormap = cm.LinearColormap(colors=['white', 'blue'], vmin=0, vmax=20)
        colormap.caption = f'Legend - Min: 0, Max: 20 ({column_type})'
    elif column_type == "💧 Humidité":
        colormap = cm.LinearColormap(colors=['white', 'blue'], vmin=0, vmax=50)
        colormap.caption = f'Legend - Min: 0, Max: 50 ({column_type})'
    else:
        colormap = cm.LinearColormap(colors=['white', 'blue'], vmin=basemap_image.min(), vmax=basemap_image.max())
        colormap.caption = 'Legend'
    
    # Add the legend to the map (positioned at the bottom-left)
    colormap.add_to(m)
    

    # Manually adjust the HTML to position the legend at the bottom-left
    html = f'<div style="position: fixed; bottom: 10px; left: 10px; z-index:1000;">{colormap._repr_html_()}</div>'
    m.get_root().html.add_child(folium.Element(html))

    # Affiche la carte utilisant Streamlit et folium_static
    folium_static(m)
   

def main():
  
    df = pd.read_parquet(r"finalfinaaaaaaaaaal.parquet")
    st.sidebar.header('🗺  Rasters Climatiques ')
    # Display a dropdown to select the column type (Précipitation, Temperature, Humidité)
    selected_column_type = st.sidebar.selectbox("Choisir l'attribut :", ["🌧  Précipitation", "🌡️ Température", "💧 Humidité"])

        # Utiliser la première date dans la colonne "DATE" comme date fixe
    selected_date = df["DATE"].min()
    # Sidebar
    
    # Utiliser st.date_input avec min_value et max_value pour bloquer la sélection
    st.sidebar.date_input("🗓️ La date disponible :", value=selected_date, min_value=selected_date, max_value=selected_date)
    # Display the slider for choosing the day offset
    day_offset = st.sidebar.slider("Choisir le jour: J-6 au J0", min_value=-6, max_value=0, step=1, value=0, key="day_slider")

    create_heatmap(selected_column_type, day_offset)

if __name__ == "__main__":
    main()
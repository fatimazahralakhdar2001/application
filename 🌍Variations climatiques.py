import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
import rasterio
import branca.colormap as cm

st.set_page_config(
    page_title="Morocco Clima\u2013MAPS",
    page_icon="🗺️",
)

# Set Page Header   
st.markdown(
    """
    <div style="text-align:center">
        <h2>🌍 Variations climatiques</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
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
file_container = st.container()
with file_container:
         st.markdown("<br>", unsafe_allow_html=True)
         st.markdown(
    """
         <div style="text-align:">
        <h6>Cette onglet vous permet de comparer deux jours et d'explorer les variations climatiques sur la carte. :</h6>
    </div>
    """,
    unsafe_allow_html=True,
)

def load_tif_image(column_type, day_offset):
    column_mapping = {
        "🌧 Précipitation": "prec",
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

def create_split_map(column_type, day_offset_1=0, day_offset_2=-1):
    day_1 = f'Jour {day_offset_1}' if day_offset_1 >= 0 else f'Jour {(day_offset_1)} '
    day_2 = f'Jour {day_offset_2}' if day_offset_2 >= 0 else f'Jour {(day_offset_2)} '
    # Load the TIF image for the selected column type and day
    basemap_image, bounds = load_tif_image(column_type, day_offset_2)
    # Create two folium maps side by side
    m1 = folium.Map(location=[31.7917, -7.0926], zoom_start=4.5, width='100%', height='80%')  
    m2 = folium.Map(location=[31.7917, -7.0926], zoom_start=4.5, width='100%', height='80%')
    folium.plugins.MousePosition().add_to(m2)
    folium.plugins.MousePosition().add_to(m1)
    # Load the TIF images for the selected column type and days
    basemap_image_1, bounds_1 = load_tif_image(column_type, day_offset_1)
    basemap_image_2, bounds_2 = load_tif_image(column_type, day_offset_2)

    # Ajuste les coordonnées pour encadrer la région du Maroc
    bounds_1 = [[bounds_1.bottom, bounds_1.left], [bounds_1.top, bounds_1.right]]
    bounds_2 = [[bounds_2.bottom, bounds_2.left], [bounds_2.top, bounds_2.right]]

    # Ajoute les images GeoTIFF à chaque carte Folium
    image_overlay_1 = folium.raster_layers.ImageOverlay(image=basemap_image_1, bounds=bounds_1, opacity=1, colormap=lambda x: (0, 0, 1, x))
    image_overlay_2 = folium.raster_layers.ImageOverlay(image=basemap_image_2, bounds=bounds_2, opacity=1, colormap=lambda x: (0, 0, 1, x))

    # Ajoute les images aux cartes
    image_overlay_1.add_to(m1)
    image_overlay_2.add_to(m2)
    
    # Affiche les cartes utilisant Streamlit et folium_static
    col1, col2 = st.columns(2)
    with col1:
        st.header(day_1)
        folium_static(m1)

    with col2:
        st.header(day_2)
        folium_static(m2)
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
        colormap.add_to(m2)
        # Manually adjust the HTML to position the legend at the bottom-left
        html = f'<div style="position: fixed; bottom: 10px; left: 10px; z-index:1000;">{colormap._repr_html_()}</div>'
        m2.get_root().html.add_child(folium.Element(html))

def main():
    
    # Display a dropdown to select the column type (Précipitation, Temperature, Humidité)
    df = pd.read_parquet(r"finalfinaaaaaaaaaal.parquet")
    st.sidebar.header('🌍 Variations climatiques')
    selected_column_type = st.sidebar.selectbox("Choisir le type de données climatiques", ["🌧 Précipitation", "🌡️ Température", "💧 Humidité"])
    selected_date = df["DATE"].min()
    # Utiliser st.date_input avec min_value et max_value pour bloquer la sélection
    st.sidebar.date_input(" 🗓️ Date disponible", value=selected_date, min_value=selected_date, max_value=selected_date)
    # Display the slider for choosing the day offsets
    day_offset_1 = st.sidebar.slider("Choisir le premier jour", min_value=-6, max_value=0, step=1, value=0, key="day_slider_1")
    day_offset_2 = st.sidebar.slider("Choisir le deuxième jour", min_value=-6, max_value=0, step=1, value=-1, key="day_slider_2")

    create_split_map(selected_column_type, day_offset_1, day_offset_2)
    

if __name__ == "__main__":
    main()
# Variations_climatiques.py
import streamlit as st

def run():
    st.title("Variations climatiques")
    # Votre code Streamlit pour l'application Variations climatiques

if __name__ == "__main__":
    run()

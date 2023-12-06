import streamlit as st
import rasterio
import folium
from streamlit_folium import folium_static
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
        <h2>🌍 Analyse Géospatiale avec COG (Cloud-Optimized GeoTIFF)</h2>
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

# Create tabs
tabs = ["Informations sur les COGS", "Exploration des COGs"]
st.sidebar.header("📂Exploration des COGs")
selected_tab = st.sidebar.radio("Sélectionnez une section", tabs)

# Section: Qu'est-ce qu'un COG?
if selected_tab == "Informations sur les COGS":
    st.markdown(
        """
        ### :blue[▶ Qu'est-ce qu'un COG?]
        
        Un Cloud Optimized GeoTIFF (COG) est un fichier GeoTIFF standard, destiné à être hébergé sur un serveur de fichiers HTTP, avec une organisation interne qui permet des flux de travail plus efficaces sur le cloud. Pour ce faire, il exploite la capacité des clients émettant des requêtes de plage HTTP GET à demander uniquement les parties d'un fichier dont ils ont besoin.
        """
    )
    st.markdown(
        """
        ### :blue[ ▶ Avantages des COG dans l'Analyse Géospatiale:]

        - *Efficacité de Stockage:* Les COG permettent de stocker de grandes quantités de données géospatiales de manière optimisée, réduisant ainsi les besoins de stockage.
        
        - *Accès efficace aux données d'imagerie:* Réduction du temps de traitement et de téléchargement complet du fichier.
       
        - *Réduction de la duplication des données:* Divers logiciels accèdent tous à un seul fichier en ligne et il évite aussi la duplication dans le cache.

        - *Compatibilité Cloud:* Les COG sont conçus pour fonctionner de manière fluide dans des environnements cloud tels que AWS S3, Google Cloud Storage, ou Azure Blob Storage.
        """
    )
    st.markdown(
        """
        ### :blue[▶ Comparaison entre GeoTIFF et COG :]
        
        """
    )

    feature_comparison_data = {
        "Fonctionnalité": ["Type de fichier", "Référence géographique", "Optimisation du cloud", "Soutien à la compression", "Compatibilité SIG"],
        "GeoTIFF": ["raster", "Oui", "Non", "Oui", "Complet"],
        "COG": ["raster", "Oui", "Oui", "Oui", "Complet"]
    }

    # Create a DataFrame
    df_comparison = pd.DataFrame(feature_comparison_data)

    # Display the dataframe
    st.dataframe(df_comparison.set_index("Fonctionnalité"), width=800)

# Section: Exploration des COGs
elif selected_tab == "Exploration des COGs":
    st.markdown(
        """
        ### :blue[▶ Exploration des COGs pour les données climatiques :]
        
        Explorez les données climatiques avec le format COG sur une carte interactive. Utilisez la barre latérale pour personnaliser votre expérience en fonction des données disponibles.🌐
        """
    )

    def load_cog_image(column_type, day_offset):
        column_mapping = {
            "💧 Humidité": "humcog",
        }

        if column_type not in column_mapping:
            raise ValueError(f"Le type de colonne {column_type} n'est pas pris en charge.")

        cog_url = f"https://cog2023.s3.eu-north-1.amazonaws.com/cog//{column_mapping[column_type]}{day_offset}.tif"
        
        with rasterio.Env():
            with rasterio.open(cog_url) as basemap:
                img = basemap.read(1)
                bounds = basemap.bounds

        return img, bounds

    def create_heatmap(column_type, day_offset=0):
        day = f'Jour {day_offset}' if day_offset >= 0 else f'Jour {abs(day_offset)} avant'

        # Create a folium map
        m = folium.Map(location=[29.985782, -8.668263], zoom_start=4.5)  # Coordonnées centrées sur le Maroc

        # Load the COG image for the selected column type and day
        basemap_image, bounds = load_cog_image(column_type, day_offset)

        # Ajuste les coordonnées pour encadrer la région du Maroc
        bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

        # Ajoute l'image GeoTIFF à la carte Folium en utilisant la colormap viridis
        image_overlay = folium.raster_layers.ImageOverlay(image=basemap_image, bounds=bounds, opacity=1, colormap=lambda x: (0, 0, 1, x))
        image_overlay.add_to(m)

        # Create a colormap legend with custom min and max values
        if column_type == "💧 Humidité":
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
        folium.plugins.MiniMap().add_to(m)
        folium.plugins.Fullscreen().add_to(m)
        folium.plugins.MousePosition().add_to(m)
        folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(m)
        
        # Affiche la carte utilisant Streamlit et folium_static
        folium_static(m)

    df = pd.read_parquet(r"finalfinaaaaaaaaaal.parquet")
    
    # Display a dropdown to select the column type (Précipitation, Temperature, Humidité)
    selected_column_type = st.sidebar.selectbox("Choisir la donnée disponible", ["💧 Humidité"])
    selected_date = df["DATE"].min()
        
        # Utiliser st.date_input avec min_value et max_value pour bloquer la sélection
    st.sidebar.date_input(" 🗓️ Date disponible", value=selected_date, min_value=selected_date, max_value=selected_date)
    # Display the slider for choosing the day offset
    day_offset = st.sidebar.slider("Choisir le jour", min_value=-6, max_value=0, step=1, value=0, key="day_slider")

    create_heatmap(selected_column_type, day_offset)

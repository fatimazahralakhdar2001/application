import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
from shapely.geometry import Point
import matplotlib.pyplot as plt
import base64
st.set_page_config(
    page_title="Morocco Clima\u2013MAPS",
    page_icon="🗺️",
)
st.markdown(
    """
    <div style="text-align:center">
        <h2>📈 Graphique Temporel Climatique</h2>
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
        <h6>Cet onglet offre une exploration interactive des variations climatiques à travers des graphiques détaillés.</h6>
    </div>
    """,
    unsafe_allow_html=True,
)
# Définir la fonction pour convertir le graphique Matplotlib en HTML
def mpl_to_html(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return f"<img src='data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}'/>"

# Charger les données avec pandas
df = pd.read_parquet("finalfinaaaaaaaaaal.parquet", engine='pyarrow')

# Afficher la carte avec les points
# Modifier la fonction create_map pour créer un seul graphique pour tempéra-ture, humidité et précipitations
def create_map(gdf):
    carte = folium.Map(location=[29.985782, -8.668263], zoom_start=4.5)
    folium.plugins.Fullscreen().add_to(carte)
    folium.plugins.MousePosition().add_to(carte)
    folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(carte)
    folium.plugins.Geocoder().add_to(carte)
    for index, row in gdf.iterrows():
        try:
            latitude, longitude = row['geometry'].y, row['geometry'].x
            radius = 2
            precip_columns = ["PRECIPITATJ0", "PRECIPITJ_1", "PRECIPITJ_2", "PRECIPITJ_3", "PRECIPITJ_4", "PRECIPITJ_5", "PRECIPITJ_6"]
            temp_columns = ["TEMPERATURJ0", "TEMPERATJ_1", "TEMPERATJ_2", "TEMPERATJ_3", "TEMPERATJ_4", "TEMPERATJ_5", "TEMPERATJ_6"]
            humid_columns = ["HUMIDITEJ0", "HUMIDITEJ_1", "HUMIDITEJ_2", "HUMIDITEJ_3", "HUMIDITEJ_4", "HUMIDITEJ_5", "HUMIDITEJ_6"]
            # Créer un seul graphique pour température, humidité et précipita-tions avec Matplotlib
            fig, ax = plt.subplots(figsize=(6, 4))
            jours = ['J-6', 'J-5', 'J-4', 'J-3', 'J-2', 'J-1', 'J0']

            # Tracer les lignes pour température, humidité et précipitations
            temp_values = [row[col] for col in temp_columns]
            humid_values = [row[col] for col in humid_columns]
            precip_values = [row[col] for col in precip_columns]

            ax.plot(jours, temp_values, marker='o', label='Température (°c)')
            ax.plot(jours, humid_values, marker='o', label='Humidité (%)')
            ax.plot(jours, precip_values, marker='o', label='Précipitations (mm)')

            ax.set_xlabel('Jours')
            ax.set_ylabel('Valeurs')
            ax.set_title("Évolution Temporelle de Température,Humidité et Précipitation")
            
            ax.legend(loc='upper right', bbox_to_anchor=(1, 1), ncol=1)

            # Convertir le graphique en HTML et l'ajouter au popup
            popup_content = f"""
            <div id='chart_{index}_popup'>
                {mpl_to_html(fig)}
            </div>
            """
            popup = folium.Popup(popup_content, max_width=300)
            
            folium.CircleMarker(
                location=[latitude, longitude],
                radius=radius,
                color='blue',
                weight=0.5,
                fill=True,
                fill_opacity=0.7,
                tooltip="Coordonnées: ({:.5f}, {:.5f})".format(latitude, longitude),
                popup=popup_content
            ).add_to(carte)

        except Exception as e:
            st.warning(f"Erreur lors de l'extraction des coordonnées : {e}")

    folium_static(carte)

# Convertir la colonne de géométrie en format Shapely
df['geometry'] = df['geometry'].apply(lambda x: loads(x))

# Créer un GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')
selected_date = df["DATE"].min()
        
        # Utiliser st.date_input avec min_value et max_value pour bloquer la sélection
st.date_input(" 🗓️ Date disponible", value=selected_date, min_value=selected_date, max_value=selected_date)
# Afficher la carte
create_map(gdf)

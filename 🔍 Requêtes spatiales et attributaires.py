import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
from shapely.geometry import Point

st.set_page_config(
    page_title="Morocco Clima\u2013MAPS",
    page_icon="🗺️",
)
# Set Page Header   
st.markdown(
    """
    <div style="text-align:center">
        <h2>🌍 Requêtes spatiales et attributaires</h2>
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
        <h6>Cette onglet vous permet de filtrer et visualiser les points d'intérêt sur une carte interactive 🗺️ :</h6>
    </div>
    """,
    unsafe_allow_html=True,
)


def create_map(gdf, buffer_radius):
    # Création d'une carte centrée sur le Maroc
    carte = folium.Map(location=[29.985782, -8.668263], zoom_start=4.5)  # Augmentez le zoom_start
    # Ajouter le plugin Fullscreen
    folium.plugins.Fullscreen().add_to(carte)

    # Ajouter le plugin MousePosition
    folium.plugins.MousePosition().add_to(carte)

    # Ajouter le plugin Draw avec le mode rectangle activé
    folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(carte)

    folium.plugins.Geocoder().add_to(carte)

    # Ajout des points sous forme de marqueurs
    for idx, row in gdf.iterrows():
        latitude, longitude = row['geometry'].y, row['geometry'].x

        
        # Créer le popup avec les valeurs de TEMP, HUMIDITE et DATE
        popup_text = f" Date: {row['DATE']}\n Région: {row['Nom_Region']}\nTempératureMoyenne: {row['TEMPMOY']}\n Humidité Moyenne: {row['HUMIDITEMO']}"



        # Ajouter le marqueur avec le popup
        folium.Marker(location=[latitude, longitude], popup=folium.Popup(popup_text, parse_html=True)).add_to(carte)

        # Calculer la distance en kilomètres pour le rayon du buffer
        buffer_radius_km = buffer_radius
        buffer_point = row['geometry'].buffer(buffer_radius_km / 111.32)  # 1 degré de latitude ~ 111.32 km

        # Ajouter le buffer à la carte
        folium.GeoJson(buffer_point.__geo_interface__, style_function=lambda x: {'fillColor': 'green', 'color': 'green'}).add_to(carte)
   
    # Affichage de la carte dans Streamlit
    folium_static(carte)

def main():

    try:
        # Charger le fichier Parquet avec pandas et fastparquet
        df = pd.read_parquet(r"finalfinaaaaaaaaaal.parquet")

        # Convertir les objets bytes en objets GeoPandas
        df['geometry'] = df['geometry'].apply(lambda x: loads(x))
        gdf = gpd.GeoDataFrame(df, geometry='geometry')

       
        # Ajout de la possibilité de choisir une région
        selected_region = st.selectbox(':blue[Choisir une région]', gdf['Nom_Region'].unique())

        # Filtrer les points en fonction de la région choisie
        filtered_gdf = gdf[gdf['Nom_Region'] == selected_region]

        # Ajout d'un texte pour spécifier le rayon du buffer
        buffer_radius = st.text_input(':blue[Entrer le rayon du buffer (en kilomètres)]', 0.0)

        # Show the selectable columns based on the selected attribute
        selectable_columns = {
            "🌧 Précipitation": ["PRECIPITATJ0", "PRECIPITJ_1", "PRECIPITJ_2", "PRECIPITJ_3", "PRECIPITJ_4", "PRECIPITJ_5", "PRECIPITJ_6"],
            "🌡️ Température": ["TEMPERATURJ0", "TEMPERATJ_1", "TEMPERATJ_2", "TEMPERATJ_3", "TEMPERATJ_4", "TEMPERATJ_5", "TEMPERATJ_6"],
            "💧 Humidité": ["HUMIDITEJ0", "HUMIDITEJ_1", "HUMIDITEJ_2", "HUMIDITEJ_3", "HUMIDITEJ_4", "HUMIDITEJ_5", "HUMIDITEJ_6"]
        }
        selected_attribute = st.selectbox(":blue[Sélectionner l'attribut]", list(selectable_columns.keys()))
          # ":blue[Sélectionner le jour pour]"
        # Show the selectable columns based on the selected attribute
        selected_date = df["DATE"].min()
        
        # Utiliser st.date_input avec min_value et max_value pour bloquer la sélection
        st.date_input(" 🗓️ Date disponible", value=selected_date, min_value=selected_date, max_value=selected_date)
        selected_columns = selectable_columns[selected_attribute]
        selected_column = st.selectbox(f":blue[Sélectionner le jour]", selected_columns, key=f"{selected_attribute}_column")

        # Add text input boxes for attribute filters
        attribute_filter = st.text_input(f":blue[Choisir une valeur de {selected_attribute}]", "0.0")

        

        # Vérifier si le bouton a été cliqué pour rechercher un point
        if st.button("Rechercher le point"):
            # Parse the input values
            attribute_value = float(attribute_filter) if attribute_filter else 0.0

            # Filter GeoDataFrame based on user inputs
            if selected_column:
                filtered_gdf = filtered_gdf[filtered_gdf[selected_column].eq(attribute_value)]
            else:
                filtered_gdf = filtered_gdf[filtered_gdf[selected_columns].eq(attribute_value).any(axis=1)]

            # If the filtered GeoDataFrame is not empty, create and display the map
            if not filtered_gdf.empty:
                create_map(filtered_gdf, float(buffer_radius))
            else:
                st.warning("Aucun point ne correspond aux critères de filtre spécifiés.")
        
    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    main()

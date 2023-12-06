import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads

st.set_page_config(
    page_title="Morocco Clima\u2013MAPS",
    page_icon="🗺️",
)
st.markdown(
    """
    <div style="text-align:center">
        <h2> 🌍 Rechercher un point par ses coordonnées</h2>
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
st.markdown("<br>", unsafe_allow_html=True)
def create_map(gdf, search_coordinates=None):
    # Création d'une carte centrée sur le Maroc
    carte = folium.Map(location=[29.985782, -8.668263], zoom_start=4.5)  # Augmentez le zoom_start
    folium.plugins.MiniMap().add_to(carte)
    folium.plugins.Fullscreen().add_to(carte)
    folium.plugins.MousePosition().add_to(carte)
    folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(carte)
    folium.plugins.Geocoder().add_to(carte)
    # Ajout des points sous forme de marqueurs
    for index, row in gdf.iterrows():
        try:
            # Extraction des coordonnées à partir de la colonne 'geometry'
            latitude, longitude = row['geometry'].y, row['geometry'].x

            # Ajouter un point au cluster
            folium.CircleMarker(location=[latitude, longitude], radius=1, color='blue', fill=True, fill_color='blue', fill_opacity=0.7,
                                popup=f"Point {index}").add_to(carte)

        except Exception as e:
            st.warning(f"Une erreur s'est produite lors du traitement du point {index}: {e}")

    # Si des coordonnées de recherche sont spécifiées, ajouter le point recherché avec un grand marqueur rouge
    if search_coordinates:
        try:
            latitude, longitude = map(float, search_coordinates.split(','))
            folium.Marker(location=[latitude, longitude], icon=folium.Icon(color='red', icon_size=(10, 10)),
                          popup="Point recherché").add_to(carte)

            # Zoom sur le point recherché
            carte.fit_bounds([[latitude, longitude], [latitude, longitude]])

        except ValueError:
            st.error("Format de coordonnées invalide. Veuillez utiliser le format 'latitude, longitude'.")

    # Affichage de la carte dans Streamlit
    folium_static(carte)
    # Ajouter le plugin Fullscreen
    folium.plugins.Fullscreen().add_to(carte)

    # Ajouter le plugin MousePosition
    folium.plugins.MousePosition().add_to(carte)

    # Ajouter le plugin Draw avec le mode rectangle activé
    folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(carte)

    folium.plugins.Geocoder().add_to(carte)

def main():
    
    
    
    try:
        # Charger le fichier Parquet avec pandas et fastparquet
        df = pd.read_parquet(r"datafin.parquet")

        # Convertir les objets bytes en objets GeoPandas
        df['geometry'] = df['geometry'].apply(lambda x: loads(x))
        gdf = gpd.GeoDataFrame(df, geometry='geometry')

        # Ajout de la possibilité de chercher un point par ses coordonnées
        coordinates = st.text_input("Entrer les coordonnées du point (format: 'latitude, longitude')")

        if st.button("Rechercher le point"):
            # Création d'une nouvelle carte avec le point recherché
            create_map(gdf, search_coordinates=coordinates)
        else:
            # Création de la carte sans recherche
            create_map(gdf)

    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    main()
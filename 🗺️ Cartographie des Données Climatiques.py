import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.wkb import loads
import plotly.express as px
import folium
from streamlit_folium import folium_static
import datetime
st.set_page_config(
    page_title="Morocco Clima\u2013MAPS",
    page_icon="🗺️",
)

def create_map(gdf, selected_column):
    # Création d'une carte centrée sur le Maroc
    carte = folium.Map(location=[29.985782, -8.668263], zoom_start=4.5)

    for index, row in gdf.iterrows():
        try:
            # Extraction des coordonnées à partir de la colonne 'geometry'
            latitude, longitude = row['geometry'].y, row['geometry'].x

            # Récupération de la valeur de la colonne sélectionnée
            column_value = row[selected_column]

            # Fix indentation for "TEMPMOY"
            if selected_column == "TEMPMOY":  # Classification for TEMPMOY
                radius=5,
                if column_value < 19.4:
                    fill_color = '#fcc5c0'
                elif 19.4 <= column_value < 21.9:
                    fill_color = '#df65b0'
                elif 21.9 <= column_value < 25:
                    fill_color = '#ce1256'
                else:
                    fill_color = 'red'
            if selected_column == "HUMIDITEMO":  # Classification for HUMIDITEMO
                # Define your humidity thresholds and corresponding colors
                radius=5
                if column_value < 21.9:
                    fill_color = '#ffffcc'
                elif 21.9 <= column_value < 31.5:
                    fill_color = '#a1dab4'
                elif 31.5 <= column_value < 35.7:
                    fill_color = '#41b6c4'
                elif 35.7 <= column_value < 40.6:
                    fill_color = '#225ea8'
                else:
                    fill_color = '#e31a1c'
           

            # Ajout d'un marqueur circulaire à la carte
            folium.CircleMarker(
                location=[latitude, longitude],
                radius=radius,
                color='blue',
                weight=0.5,
                fill=True,
                fill_color=fill_color,
                fill_opacity=0.7,
                tooltip=f"{selected_column}: {row[selected_column]}",
            ).add_to(carte)
        except Exception as e:
            st.warning(f"Erreur lors de l'extraction des coordonnées pour {selected_column} {row[selected_column]} : {e}")

    # Ajouter la légende à la carte en tant que plugin
    folium.plugins.MiniMap().add_to(carte)
    
    folium.plugins.Fullscreen().add_to(carte)
    folium.plugins.MousePosition().add_to(carte)
    folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(carte)
    folium.plugins.Geocoder().add_to(carte)
    # Affichage de la carte dans Streamlit
    folium_static(carte)

def create_days_map(gdf, selected_column_type, selected_day):
    """
    Crée une carte basée sur les valeurs quotidiennes d'une colonne de type sélectionné.
    :param gdf: GeoDataFrame contenant les données géospatiales.
    :param selected_column_type: Type de colonne (Précipitation, Température, Humidité).
    :param selected_day: Jour spécifique à afficher sur la carte.
    """
    carte = folium.Map(location=[29.985782, -8.668263], zoom_start=4.5)

    for index, row in gdf.iterrows():
        try:
            latitude, longitude = row['geometry'].y, row['geometry'].x
            column_value = row[selected_day]
            radius, fill_color = get_radius_and_color(selected_day, column_value)

            folium.CircleMarker(
                location=[latitude, longitude],
                radius=radius,
                color='blue',
                weight=0.5,
                fill=True,
                fill_color=fill_color,
                fill_opacity=0.7,
                tooltip=f"{selected_day}: {column_value}",
            ).add_to(carte)
        except Exception as e:
            st.warning(f"Erreur lors de l'extraction des coordonnées pour {selected_day} {column_value}: {e}")

    folium.plugins.MiniMap().add_to(carte)
    folium.plugins.Fullscreen().add_to(carte)
    folium.plugins.MousePosition().add_to(carte)
    folium.plugins.Draw(export=True, draw_options={'rectangle': True}).add_to(carte)
    folium.plugins.Geocoder().add_to(carte)

    folium_static(carte)


def get_radius_and_color(selected_day, column_value):
    """
    Obtient le rayon et la couleur en fonction du jour sélectionné et de la valeur de la colonne.
    :param selected_day: Jour sélectionné.
    :param column_value: Valeur de la colonne pour le jour sélectionné.
    :return: Tuple (rayon, couleur).
    """
    if "PRECIPIT" in selected_day:
        if column_value < 22:
            return 1, 'blue'
        elif 22 <= column_value < 46:
            return 2, 'blue'
        elif 46 <= column_value < 72:
            return 3, 'blue'
        elif 72 <= column_value < 100:
            return 4, 'blue'
        else:
            return 2, 'blue'
    elif "TEMPERAT" in selected_day:
        if column_value < 5:
            return 1, 'red'
        elif 5 <= column_value < 10:
            return 2, 'red'
        elif 10 <= column_value < 15:
            return 3, 'red'
        elif 15 <= column_value < 20:
            return 4, 'red'
        else:
            return 2, 'red'
    elif "HUMIDITE" in selected_day:
        if column_value < 12:
            return 1, 'green'
        elif 12 <= column_value < 25:
            return 2, 'green'
        elif 25 <= column_value < 38:
            return 3, 'green'
        elif 38 <= column_value < 50:
            return 4, 'green'
        else:
            return 2, 'green'
    else:
        return 2, 'blue'



def main():
    # Charger le fichier Parquet avec pandas et fastparquet
    df = pd.read_parquet(r"finalfinaaaaaaaaaal.parquet")

    # Convertir les objets bytes en objets GeoPandas
    df['geometry'] = df['geometry'].apply(lambda x: loads(x))
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    excluded_columns = ['FID_1', 'CID', 'FID_2', 'OBJECTID', 'Nom_Region', 'DATE', 'geometry', 'TEMPMOY', 'HUMIDITEMO']
    selected_columns = [col for col in gdf.columns if col not in excluded_columns]

    # Sidebar
    st.sidebar.header('🗺️ Cartographie ')


    # Onglets
    tabs = st.sidebar.radio('Sélectionner une option', ["Valeurs Moyennes", "Valeurs selon les jours"])

    
    
    # Utiliser la première date dans la colonne "DATE" comme date fixe
    selected_date = df["DATE"].min()

    # Utiliser st.date_input avec min_value et max_value pour bloquer la sélection
    st.sidebar.date_input(" 🗓️ Date disponible", value=selected_date, min_value=selected_date, max_value=selected_date)


    if tabs == "Valeurs Moyennes":
        # Set Page Header   
        st.markdown(
    """
    <div style="text-align:center">
        <h2>🌍 Visualisation Géographique des Moyennes Climatiques</h2>
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

        # Charger le fichier Parquet avec pandas
        df = pd.read_parquet(r"finalfinaaaaaaaaaal.parquet")

        # Convertir les objets bytes en objets GeoPandas
        df['geometry'] = df['geometry'].apply(lambda x: loads(x))
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        excluded_columns = ['FID_1','CID','FID_2','OBJECTID','Nom_Region', 'DATE','geometry','PRECIPITATJ0', 'PRECIPITJ_1', 'PRECIPITJ_2','PRECIPITJ_3', 'PRECIPITJ_4', 'PRECIPITJ_5', 'PRECIPITJ_6','TEMPERATURJ0', 'TEMPERATJ_1', 'TEMPERATJ_2', 'TEMPERATJ_3','TEMPERATJ_4', 'TEMPERATJ_5','TEMPERATJ_6','HUMIDITEJ0','HUMIDITEJ_1', 'HUMIDITEJ_2', 'HUMIDITEJ_3', 'HUMIDITEJ_4', 'HUMIDITEJ_5', 'HUMIDITEJ_6']
        selected_columns = [col for col in gdf.columns if col not in excluded_columns]
      

        # Sélection de la colonne à cartographier
        selected_column_type = st.sidebar.selectbox("Choisir le type de la propriété à cartographier", ["🌡️Température moyenne", "💧 Humidité moyenne "])

        # Propriété fixe
        selected_propriete = "TEMPMOY" if selected_column_type == "🌡️Température moyenne" else "HUMIDITEMO"  # Choisis la propriété en fonction du type sélectionné

        # Création de la carte
        create_map(gdf, selected_propriete)
        st.sidebar.markdown(get_legend_values(selected_propriete), unsafe_allow_html=True)
    elif tabs == "Valeurs selon les jours":
        # Options pour les valeurs selon les jours
        
        st.markdown(
    """
    <div style="text-align:center">
        <h2>🌍 Visualisation Géospatiale des Conditions Climatiques Journalières</h2>
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
        selected_column_type = st.sidebar.selectbox("Choisir l'attribut à cartographier", ["Précipitation", "Température", "Humidité"])

        if selected_column_type == "Précipitation":
            days = ["PRECIPITATJ0", "PRECIPITJ_1", "PRECIPITJ_2", "PRECIPITJ_3", "PRECIPITJ_4", "PRECIPITJ_5", "PRECIPITJ_6"]
        elif selected_column_type == "Température":
            days = ["TEMPERATURJ0", "TEMPERATJ_1", "TEMPERATJ_2", "TEMPERATJ_3", "TEMPERATJ_4", "TEMPERATJ_5", "TEMPERATJ_6"]
        else:
            days = ["HUMIDITEJ0", "HUMIDITEJ_1", "HUMIDITEJ_2", "HUMIDITEJ_3", "HUMIDITEJ_4", "HUMIDITEJ_5", "HUMIDITEJ_6"]

        selected_day = st.sidebar.selectbox("Choisir le jour", days)
        create_days_map(gdf, selected_column_type, selected_day)
        st.sidebar.markdown(get_legend_valuess(selected_column_type), unsafe_allow_html=True)

def get_legend_valuess(selected_column_type):
    """
    Obtient les valeurs de légende en HTML en fonction du type de colonne sélectionné.
    :param selected_column_type: Type de colonne (Précipitation, Température, Humidité).
    :return: Chaîne HTML représentant la légende.
    """
    if "Précipitation" in selected_column_type:
        return """
        <div class="legend">
            <p style="margin:5px;">Légende:</p>
            <p style="margin:5px;">Précipitation en mm</p>
            <p style="margin:5px;color:green">22</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="3" fill="blue" /></svg></div>
            <p style="margin:5px;color:green">46</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="5" fill="blue" /></svg></div>
            <p style="margin:5px;color:green">72</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="blue" /></svg></div>
            <p style="margin:5px;color:green">100</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="9" fill="blue" /></svg></div>
        </div>
        """
    elif "Température" in selected_column_type:
        return """
        <div class="legend">
            <p style="margin:5px;">Légende:</p>
            <p style="margin:5px;">Température en C° </p>
            <p style="margin:5px;color:green">5</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="3" fill="red" /></svg></div>
            <p style="margin:5px;color:green">10</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="5" fill="red" /></svg></div>
            <p style="margin:5px;color:green">15</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="red" /></svg></div>
            <p style="margin:5px;color:green">20</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="9" fill="red" /></svg></div>
        </div>
        """
    elif "Humidité" in selected_column_type:
        return """
        <div class="legend">
            <p style="margin:5px;">Légende:</p>
            <p style="margin:5px;">Humidité en %</p>
            <p style="margin:5px;color:green">12</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="3" fill="green" /></svg></div>
            <p style="margin:5px;color:green">25</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="5" fill="green" /></svg></div>
            <p style="margin:5px;color:green">38</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="green" /></svg></div>
            <p style="margin:5px;color:green">50</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="9" fill="green" /></svg></div>
        </div>
        """
    else:
        return ""
    
def get_legend_values(selected_propriete):
    # Définir dynamiquement les valeurs de légende en fonction de la colonne sélectionnée
    if "TEMPMOY" in selected_propriete:
        return """
        <div class="legend">
            <p style="margin:5px;">Légende:</p>
            <p style="margin:5px;">Temperature moyenne en C°</p>
            <p style="margin:5px;color:black">[17.6-19.4]</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#fcc5c0" /></svg></div>
            <p style="margin:5px;color:black"> [19.4-21.9]</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#df65b0" /></svg></div>
            <p style="margin:5px;color:black">[21.9-25]</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#ce1256" /></svg></div>
        </div>
        """
    elif "HUMIDITEMO" in selected_propriete:
        return """
        <div class="legend">
            <p style="margin:5px;">Légende:</p>
            <p style="margin:5px;">Humidité moyenne en % </p>
            <p style="margin:5px;color:black">[18.7-21.9]</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#ffffcc" /></svg></div>
            <p style="margin:5px;color:black">[21.9-31.5]</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#a1dab4" /></svg></div>
            <p style="margin:5px;color:black">[31.5-35.7]</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#41b6c4" /></svg></div>
            <p style="margin:5px;color:black">[35.7-40.6]</p>
            <div style="margin:5px;"><svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#225ea8" /></svg></div>
        </div>
        """
    
    else:
        return ""
    
if __name__ == "__main__":
    main()

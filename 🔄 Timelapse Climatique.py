import streamlit as st
import os
import imageio
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

st.set_page_config(
    page_title="Dashboard GeoAnalytique",
    page_icon="🗺️",
)
st.markdown(
    """
    <div style="text-align:center">
        <h2> 🌦️🔄Timelapse Climatique</h2>
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

def load_tif_image(column_type, day_offset):
    column_mapping = {
        "Précipitation": "prec",
        "Température": "temp",
        "Humidité": "hum"
    }

    if column_type not in column_mapping:
        raise ValueError(f"Le type de colonne {column_type} n'est pas pris en charge.")

    tif_path = f"cliptemp/{column_mapping[column_type]}{day_offset}.tif"
    basemap = rasterio.open(tif_path)

    # Utilise la méthode read pour récupérer l'image
    img = basemap.read(1)

    return img, basemap.bounds, basemap.crs

def create_timelapse_gif(column_type, output_path):
    # Création d'un fichier temporaire pour stocker les images
    temp_folder = 'temp_images/'

    # Création du dossier temporaire s'il n'existe pas
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    # Création du timelapse
    images = []
    for day_offset in range(-6, 1):
        try:
            # Load the TIF image for the selected column type and day
            print(f"Loading image for {column_type} - Jour {day_offset}")
            basemap_image, bounds, crs = load_tif_image(column_type, day_offset)

            # Ajuste les coordonnées pour encadrer la région du Maroc
            bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

            # Create a Matplotlib plot
            plt.figure(figsize=(10, 10))

            if column_type == "Précipitation":
                # Use LogNorm for better visualization of precipitation data
                plt.imshow(basemap_image, extent=[bounds[0][1], bounds[1][1], bounds[0][0], bounds[1][0]], cmap='Blues', vmin=1, vmax=100)
                plt.colorbar(label="Précipitation (mm)")
            elif column_type == "Température":
                plt.imshow(basemap_image, extent=[bounds[0][1], bounds[1][1], bounds[0][0], bounds[1][0]], cmap='Reds', vmin=0, vmax=20)
                plt.colorbar(label="Température (°C)")
            elif column_type == "Humidité":
                plt.imshow(basemap_image, extent=[bounds[0][1], bounds[1][1], bounds[0][0], bounds[1][0]], cmap='Greens', vmin=0, vmax=50)
                plt.colorbar(label="Humidité (%)")

            plt.title(f"{column_type} - Jour {day_offset}")
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")

            # Save the Matplotlib plot as an image
            temp_image_path = os.path.join(temp_folder, f'temp_image_{day_offset}.png')
            plt.savefig(temp_image_path)
            plt.close()
            images.append(imageio.imread(temp_image_path))

        except Exception as e:
            st.warning(f"Une erreur s'est produite lors de la création de l'image pour le jour {day_offset}: {e}")

    # Création du GIF avec imageio
    imageio.mimsave(output_path, images, fps=1)

    # Affichage du GIF
    st.image(output_path, use_column_width=True)

def main():
    # Titre de l'application
    st.title("Cartography")

    try:
        # Sélectionner le type de timelapse
        selected_timelapse = st.selectbox("Choisir le type de timelapse", ["Précipitation", "Température", "Humidité"])

        if selected_timelapse in ["Précipitation", "Température", "Humidité"]:
            create_timelapse_gif(selected_timelapse, output_path=f'{selected_timelapse.lower()}_timelapse.gif')

    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    main()

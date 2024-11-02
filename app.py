import io
import streamlit as st
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Draw
from cairosvg import svg2png


def create_png_from_smiles(smiles, size=(600, 600)):
    """
    Create a PNG image from a SMILES string using RDKit.

    Args:
    smiles (str): The SMILES string representation of the molecule.
    size (tuple): The size of the image (width, height).

    Returns:
    Image: PIL Image object of the molecule.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    # Create an RDKit drawing object
    img = Draw.MolToImage(mol, size=size)

    # Convert the image to PNG format
    png_image = Image.new("RGB", size, (255, 255, 255))
    png_image.paste(img)
    
    # Resize the image
    png_image = png_image.resize(size, Image.LANCZOS)
    
    # Convert to PNG
    png_buffer = io.BytesIO()
    png_image.save(png_buffer, format='PNG')
    png_buffer.seek(0)
    
    return Image.open(png_buffer)


def create_acs_png_from_smiles(smiles, size=(600, 600)):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    drawer = Draw.rdMolDraw2D.MolDraw2DSVG(-1,-1)
    Draw.rdDepictor.Compute2DCoords(mol)
    Draw.rdMolDraw2D.DrawMoleculeACS1996(drawer, mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    
    # Convert SVG to PNG using cairosvg
    png_data = svg2png(bytestring=svg.encode('utf-8'), output_width=size[0], output_height=size[1])
    
    # Create a PIL Image from the PNG data
    img = Image.open(io.BytesIO(png_data))
    
    # Ensure the image is in RGB mode
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize the image if necessary
    if img.size != size:
        img = img.resize(size, Image.LANCZOS)
    return img


st.title("Smiles to GIF")

# Create input for image size
image_size = st.number_input("Enter image size (pixels)", min_value=100, max_value=1200, value=600, step=100)

# Create radio button for format selection
format_type = st.radio("Select format", ["Standard", "ACS Style"])

# Create a text area for multiple SMILES strings
smiles_input = st.text_area(
    "Enter SMILES strings (one per line)",
    height=200,
    help="Enter each SMILES string on a new line"
)

# Add submit button
submit_button = st.button("Generate GIF")

if submit_button and smiles_input:
    png_images = []
    errored = False
    for smiles in smiles_input.split('\n'):
        if smiles.strip():
            try:
                if format_type == "Standard":
                    png_images.append(create_png_from_smiles(smiles, size=(image_size, image_size)))
                else:
                    png_images.append(create_acs_png_from_smiles(smiles, size=(image_size, image_size)))
            except Exception as e:
                st.error(f"Failed to process SMILES string: '{smiles}'\nError: {str(e)}")
                errored = True

    if errored:
        st.stop()

    # Create a BytesIO object to store the GIF
    gif_buffer = io.BytesIO()
    
    # Save the images as an animated GIF
    png_images[0].save(
        gif_buffer,
        format='GIF',
        save_all=True,
        append_images=png_images[1:],
        duration=500,  # Display each image for 500ms
        loop=0  # Loop infinitely
    )

    # Add download button for GIF
    gif_buffer.seek(0)
    st.download_button(
        label="Download GIF",
        data=gif_buffer,
        file_name="molecule_sequence.gif",
        mime="image/gif"
    )

    # Display the GIF
    gif_buffer.seek(0)
    st.image(gif_buffer, caption="Animated molecule sequence")


import streamlit as st
from PIL import Image
import zipfile
import io
import tempfile
import os

def process_images(uploaded_files, target_size, maintain_aspect_ratio):
    temp_dir = tempfile.TemporaryDirectory()
    processed_files = []
    
    for uploaded_file in uploaded_files:
        try:
            image = Image.open(uploaded_file)
            original_format = image.format

            if maintain_aspect_ratio:
                image.thumbnail(target_size, Image.Resampling.LANCZOS)
            else:
                image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save processed image
            file_path = os.path.join(temp_dir.name, uploaded_file.name)
            image.save(file_path, format=original_format)
            processed_files.append(file_path)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    return temp_dir, processed_files

def create_zip(files):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in files:
            with open(file_path, "rb") as f:
                zip_file.writestr(os.path.basename(file_path), f.read())
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit UI
st.title("📸 Bulk Image Resizer")
st.markdown("Upload multiple images and resize them to your desired dimensions!")

with st.sidebar:
    st.header("Settings")
    width = st.number_input("Target Width (px)", min_value=1, value=800)
    height = st.number_input("Target Height (px)", min_value=1, value=600)
    maintain_aspect_ratio = st.checkbox("Maintain Aspect Ratio", value=True)
    st.markdown("---")
    st.markdown("ℹ️ When maintaining aspect ratio, images will be scaled to fit within the target dimensions while preserving their original proportions.")

uploaded_files = st.file_uploader(
    "Upload Images", 
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) > 0:
    if st.button("Process Images"):
        with st.spinner("Processing images..."):
            target_size = (width, height)
            temp_dir, processed_files = process_images(
                uploaded_files, 
                target_size, 
                maintain_aspect_ratio
            )
            
            if processed_files:
                st.success(f"Successfully processed {len(processed_files)} images!")
                zip_buffer = create_zip(processed_files)
                
                st.download_button(
                    label="Download Processed Images",
                    data=zip_buffer,
                    file_name="processed_images.zip",
                    mime="application/zip",
                )
                
                # Clean up temporary directory
                temp_dir.cleanup()
            else:
                st.error("No images were processed successfully.")

import fitz
import os
import zipfile
import tempfile
import shutil

def pdf_to_images(pdf_path, output_zip_path, mode="pages", callback=None):
    """
    Convierte un PDF a imágenes y las guarda en un archivo ZIP.
    
    :param pdf_path: Ruta del PDF original.
    :param output_zip_path: Ruta del archivo ZIP de salida.
    :param mode: "pages" para convertir cada página en una imagen, 
                 "extract" para extraer las imágenes incrustadas en el PDF.
    :param callback: Función callback(current, total) para actualizar progreso.
    """
    temp_dir = tempfile.mkdtemp()
    image_paths = []
    
    try:
        doc = fitz.open(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        total_pages = len(doc)
        
        if mode == "pages":
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                # Escalar para mejor resolución (opcional, p.ej. 2x)
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                img_name = f"{base_name}_page_{page_num + 1}.png"
                img_path = os.path.join(temp_dir, img_name)
                pix.save(img_path)
                image_paths.append(img_path)
                
                if callback:
                    callback(page_num + 1, total_pages)
                    
        elif mode == "extract":
            img_index = 0
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                images = page.get_images(full=True)
                for img in images:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    img_name = f"{base_name}_img_{img_index + 1}.{image_ext}"
                    img_path = os.path.join(temp_dir, img_name)
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)
                    image_paths.append(img_path)
                    img_index += 1
                
                if callback:
                    callback(page_num + 1, total_pages)
        
        doc.close()
        
        if not image_paths:
            raise Exception("No se encontraron imágenes o no se pudo convertir el PDF.")
            
        # Create ZIP file
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for img_path in image_paths:
                zipf.write(img_path, os.path.basename(img_path))
                
        return True
        
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

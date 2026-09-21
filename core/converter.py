"""
Lógica para convertir PDF a Word usando pdf2docx.
"""
import os
from typing import List, Callable, Optional
from pdf2docx import Converter

def convert_to_docx(input_path: str, output_path: str, callback: Optional[Callable[[int, int], None]] = None) -> str:
    """
    Convierte un archivo PDF a formato .docx.
    
    Args:
        input_path (str): Ruta del archivo PDF original.
        output_path (str): Ruta del archivo Word a generar.
        callback (callable, opcional): Callback(actual, total) para reportar progreso.
            
    Returns:
        str: Ruta del archivo generado.
    """
    if not os.path.isfile(input_path):
        raise ValueError(f"El archivo PDF no existe: {input_path}")
        
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()
    
    if callback:
        callback(1, 1)
        
    return output_path

def convert_batch(file_list: List[str], output_dir: str, callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
    """
    Convierte múltiples archivos PDF a Word.
    
    Args:
        file_list (List[str]): Lista de rutas de los PDFs.
        output_dir (str): Directorio donde se guardarán los archivos Word.
        callback (callable, opcional): Función de progreso global (actual, total).
        
    Returns:
        List[str]: Lista de rutas de los archivos Word generados.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    output_files = []
    total_files = len(file_list)
    
    for i, input_path in enumerate(file_list):
        if not os.path.isfile(input_path):
            continue
            
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        out_path = os.path.join(output_dir, f"{base_name}.docx")
        
        convert_to_docx(input_path, out_path)
        output_files.append(out_path)
        
        if callback:
            callback(i + 1, total_files)
            
    return output_files

"""
Lógica para unir archivos PDF.
"""
import os
from typing import List, Callable, Optional
from pypdf import PdfWriter

def merge_pdfs(file_list: List[str], output_path: str, callback: Optional[Callable[[int, int], None]] = None) -> str:
    """
    Une una lista de archivos PDF en un solo archivo.
    
    Args:
        file_list (List[str]): Lista de rutas de los archivos PDF a unir.
        output_path (str): Ruta del archivo resultante.
        callback (callable, opcional): Función de progreso (actual, total).
        
    Returns:
        str: Ruta del archivo unido.
        
    Raises:
        ValueError: Si la lista de archivos está vacía o un archivo no existe.
    """
    if not file_list:
        raise ValueError("La lista de archivos está vacía.")
        
    for f in file_list:
        if not os.path.isfile(f):
            raise ValueError(f"El archivo no existe: {f}")
            
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    writer = PdfWriter()
    total_files = len(file_list)
    
    for i, path in enumerate(file_list):
        writer.append(path)
        if callback:
            callback(i + 1, total_files)
            
    with open(output_path, 'wb') as f:
        writer.write(f)
        
    return output_path

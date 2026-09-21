"""
Lógica para dividir archivos PDF.
"""
import os
import re
from typing import List, Callable, Optional
from pypdf import PdfReader, PdfWriter

def parse_ranges(range_str: str) -> List[int]:
    """
    Parsea una cadena de rangos (ej. '1-3, 5, 7-10') a una lista de números de página (índice 0).
    
    Args:
        range_str (str): Cadena con los rangos.
        
    Returns:
        List[int]: Lista de índices de páginas base 0.
        
    Raises:
        ValueError: Si la cadena de rangos tiene un formato inválido.
    """
    if not range_str.strip():
        raise ValueError("La cadena de rangos está vacía.")
    
    pages = set()
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if '-' in part:
            match = re.match(r'^(\d+)\s*-\s*(\d+)$', part)
            if not match:
                raise ValueError(f"Formato de rango inválido: {part}")
            start, end = map(int, match.groups())
            if start > end or start < 1:
                raise ValueError(f"Rango de páginas inválido: {part}")
            # Convertir a índice 0 e incluir el fin
            pages.update(range(start - 1, end))
        else:
            if not part.isdigit():
                raise ValueError(f"Número de página inválido: {part}")
            val = int(part)
            if val < 1:
                raise ValueError(f"El número de página debe ser mayor a 0: {part}")
            pages.add(val - 1)
            
    return sorted(list(pages))

def split_by_ranges(input_path: str, range_str: str, output_dir: str, callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
    """
    Divide un PDF según los rangos de páginas especificados. Cada rango se guarda en un archivo.
    
    Args:
        input_path (str): Ruta del PDF original.
        range_str (str): Cadena de rangos (ej. '1-3, 5, 7-10').
        output_dir (str): Directorio donde guardar los archivos.
        callback (callable, opcional): Función de callback(actual, total) para el progreso.
        
    Returns:
        List[str]: Lista de rutas de los archivos generados.
    """
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    parts = [p.strip() for p in range_str.split(',') if p.strip()]
    output_files = []
    
    total_steps = len(parts)
    
    for i, part in enumerate(parts):
        writer = PdfWriter()
        # Para cada parte individual, extraer el rango o página
        try:
            pages_to_extract = parse_ranges(part)
        except ValueError as e:
            continue
            
        for p in pages_to_extract:
            if 0 <= p < total_pages:
                writer.add_page(reader.pages[p])
                
        if len(writer.pages) > 0:
            if '-' in part:
                clean_part = part.replace(' ', '')
                out_name = f"{base_name}_paginas_{clean_part}.pdf"
            else:
                out_name = f"{base_name}_pagina_{part}.pdf"
                
            out_path = os.path.join(output_dir, out_name)
            with open(out_path, 'wb') as f:
                writer.write(f)
            output_files.append(out_path)
            
        if callback:
            callback(i + 1, total_steps)
            
    return output_files

def split_every_n(input_path: str, n: int, output_dir: str, callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
    """
    Divide un PDF agrupando cada N páginas.
    
    Args:
        input_path (str): Ruta del PDF original.
        n (int): Número de páginas por grupo.
        output_dir (str): Directorio donde guardar los archivos.
        callback (callable, opcional): Función de callback para progreso.
        
    Returns:
        List[str]: Lista de rutas generadas.
    """
    if n < 1:
        raise ValueError("N debe ser mayor o igual a 1.")
        
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    output_files = []
    num_parts = (total_pages + n - 1) // n
    
    for i in range(num_parts):
        writer = PdfWriter()
        start = i * n
        end = min((i + 1) * n, total_pages)
        
        for p in range(start, end):
            writer.add_page(reader.pages[p])
            
        out_name = f"{base_name}_paginas_{start+1}-{end}.pdf"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, 'wb') as f:
            writer.write(f)
        output_files.append(out_path)
        
        if callback:
            callback(i + 1, num_parts)
            
    return output_files

def split_all(input_path: str, output_dir: str, callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
    """
    Extrae cada página del PDF en un archivo individual.
    
    Args:
        input_path (str): Ruta del PDF original.
        output_dir (str): Directorio donde guardar los archivos.
        callback (callable, opcional): Función de progreso.
        
    Returns:
        List[str]: Rutas de los archivos creados.
    """
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    output_files = []
    
    for p in range(total_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[p])
        out_name = f"{base_name}_pagina_{p+1}.pdf"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, 'wb') as f:
            writer.write(f)
        output_files.append(out_path)
        
        if callback:
            callback(p + 1, total_pages)
            
    return output_files

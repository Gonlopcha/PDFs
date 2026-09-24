"""
Lógica para convertir PDF a Word usando pdf2docx.
"""
import os
import logging
import re
from typing import List, Callable, Optional
from pdf2docx import Converter

class _ProgressHandler(logging.Handler):
    def __init__(self, callback: Callable[[float, float], None]):
        super().__init__()
        self.callback = callback
        self.current_step = 0

    def emit(self, record):
        try:
            msg = self.format(record)
            if 'Parsing pages' in msg:
                self.current_step = 3
            elif 'Creating pages' in msg:
                self.current_step = 4
            else:
                match = re.search(r'\((\d+)/(\d+)\) Page', msg)
                if match:
                    i = int(match.group(1))
                    N = int(match.group(2))
                    if N > 0:
                        file_prog = 0.0
                        if self.current_step == 3:
                            file_prog = (i / N) * 0.5
                        elif self.current_step == 4:
                            file_prog = 0.5 + (i / N) * 0.5
                        
                        if self.callback:
                            self.callback(int(file_prog * 100.0), 100)
        except Exception:
            pass

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
        
    handler = None
    if callback:
        handler = _ProgressHandler(callback)
        logging.getLogger().addHandler(handler)
        
    try:
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
    finally:
        if handler:
            logging.getLogger().removeHandler(handler)
    
    if callback:
        callback(100, 100)
        
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
        
        def file_progress(current_file_prog, total_file_prog):
            if callback:
                overall_current = int((i * 100) + current_file_prog)
                overall_total = int(total_files * 100)
                callback(overall_current, overall_total)
                
        convert_to_docx(input_path, out_path, callback=file_progress)
        output_files.append(out_path)
            
    return output_files

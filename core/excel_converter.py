import os
import sys
from typing import List, Callable, Optional

def convert_excel_to_pdf(input_path: str, output_path: str, orientation: str = "Vertical", paper_size: str = "Carta", margin_size: str = "Sin márgenes (0cm)", alignment: str = "Arriba - Izquierda (Por defecto)", sheet_callback: Optional[Callable[[int, int], None]] = None):
    """
    Convierte un archivo Excel a PDF. Cada hoja en una página, ajustado sin espacio blanco.
    """
    import pythoncom
    import win32com.client
    
    pythoncom.CoInitialize()
    excel = None
    wb = None
    try:
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        abs_input = os.path.abspath(input_path)
        abs_output = os.path.abspath(output_path)
        
        wb = excel.Workbooks.Open(abs_input)
        
        xlPortrait = 1
        xlLandscape = 2
        orientation_val = xlPortrait if orientation == "Vertical" else xlLandscape
        
        paper_map = {
            "Carta": 1,
            "Legal (Oficio)": 5,
            "A4": 9,
            "A3": 8,
            "Ejecutivo": 7
        }
        paper_val = paper_map.get(paper_size, 1)

        margin_map = {
            "Sin márgenes (0cm)": 0,
            "Estrechos (1.27cm)": 36,
            "Normales (1.91cm)": 54,
            "Anchos (2.54cm)": 72
        }
        margin_val = margin_map.get(margin_size, 0)
        
        align_horiz = False
        align_vert = False
        if alignment == "Centrado Horizontal (Arriba)":
            align_horiz = True
        elif alignment == "Centrado Vertical (Izquierda)":
            align_vert = True
        elif alignment == "Centrado Total (Medio)":
            align_horiz = True
            align_vert = True
        
        sheets_count = wb.Worksheets.Count
        
        for idx, sheet in enumerate(wb.Worksheets):
            try:
                sheet.PageSetup.Zoom = False
                sheet.PageSetup.FitToPagesWide = 1
                sheet.PageSetup.FitToPagesTall = 1
                sheet.PageSetup.Orientation = orientation_val
                
                sheet.PageSetup.PaperSize = paper_val
                
                sheet.PageSetup.LeftMargin = margin_val
                sheet.PageSetup.RightMargin = margin_val
                sheet.PageSetup.TopMargin = margin_val
                sheet.PageSetup.BottomMargin = margin_val
                sheet.PageSetup.HeaderMargin = 0
                sheet.PageSetup.FooterMargin = 0
                
                sheet.PageSetup.CenterHorizontally = align_horiz
                sheet.PageSetup.CenterVertically = align_vert
                
            except Exception as e:
                print(f"No se pudo configurar la hoja {sheet.Name}: {e}")
                
            if sheet_callback:
                sheet_callback(idx + 1, sheets_count)
        
        wb.ExportAsFixedFormat(0, abs_output)
        
    finally:
        # Explicitly delete COM objects to release them from memory
        # before CoUninitialize is called. Otherwise, they hang around
        # and keep the Excel process alive.
        if 'sheet' in locals():
            del sheet
            
        if wb:
            try:
                wb.Close(False)
            except:
                pass
            del wb
            
        if excel:
            try:
                excel.Quit()
            except:
                pass
            del excel
            
        # Force garbage collection to ensure COM objects are destroyed
        import gc
        gc.collect()
        
        pythoncom.CoUninitialize()

def convert_excel_batch(file_list: List[str], output_dir: str, orientation: str = "Vertical", paper_size: str = "Carta", margin_size: str = "Sin márgenes (0cm)", alignment: str = "Arriba - Izquierda (Por defecto)", callback: Optional[Callable[[float, int], None]] = None) -> List[str]:
    """
    Convierte múltiples archivos Excel a PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    output_files = []
    total_files = len(file_list)
    
    for i, input_path in enumerate(file_list):
        if not os.path.isfile(input_path):
            continue
            
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        out_path = os.path.join(output_dir, f"{base_name}.pdf")
        
        def sheet_callback(curr_sheet, total_sheets):
            if callback:
                # El progreso es el número de archivos ya completados (i) 
                # más la fracción del archivo actual basado en hojas completadas.
                fraction = curr_sheet / float(total_sheets)
                # Max a 0.9 para guardar 10% para la exportación final
                fraction = min(fraction, 0.9)
                callback(i + fraction, total_files)
                
        convert_excel_to_pdf(input_path, out_path, orientation, paper_size, margin_size, alignment, sheet_callback=sheet_callback)
        output_files.append(out_path)
        
        if callback:
            callback(i + 1, total_files)
            
    return output_files

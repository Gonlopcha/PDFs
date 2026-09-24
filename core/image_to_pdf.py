import fitz

def images_to_pdf(image_list, output_path, callback=None):
    doc = fitz.open()
    total = len(image_list)
    for i, img_path in enumerate(image_list):
        img_doc = fitz.open(img_path)
        pdfbytes = img_doc.convert_to_pdf()
        img_doc.close()
        
        pdf_page = fitz.open("pdf", pdfbytes)
        doc.insert_pdf(pdf_page)
        pdf_page.close()
        
        if callback:
            callback(i + 1, total)
            
    doc.save(output_path)
    doc.close()

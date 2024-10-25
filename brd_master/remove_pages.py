import fitz
import os


def remove_preceding_pages(pdf_path, start_page, output_path):
    document = fitz.open(pdf_path)
    new_document = fitz.open()

    if start_page < 1 or start_page > len(document):
        raise ValueError("Invalid start page number.")

    for page_num in range(start_page - 1, len(document)):
        new_document.insert_pdf(document, from_page=page_num, to_page=page_num)

    temp_output_path = output_path + ".temp"
    new_document.save(temp_output_path)
    new_document.close()
    document.close()

    os.replace(temp_output_path, output_path)

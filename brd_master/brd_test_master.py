import asyncio
import os
from remove_pages import remove_preceding_pages
from analyze_pdf import analyze_pdf


async def main(pdf_bytes, start_page, output_path):
    temp_pdf_path = "temp_pdf.pdf"
    with open(temp_pdf_path, "wb") as temp_pdf_file:
        temp_pdf_file.write(pdf_bytes)

    remove_preceding_pages(temp_pdf_path, start_page, output_path)

    with open(output_path, "rb") as modified_pdf_file:
        modified_pdf_bytes = modified_pdf_file.read()

    results = await analyze_pdf(modified_pdf_bytes)

    os.remove(temp_pdf_path)

    return results

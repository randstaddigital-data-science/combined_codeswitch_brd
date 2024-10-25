import fitz
import asyncio
import aiohttp
from brd_master.analyze_image import analyze_image
from brd_master.metrics import metrics, AsyncTimer

async def analyze_pdf(pdf_bytes):
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    metrics.processed_pdfs.inc()

    async with AsyncTimer(metrics.request_time):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                tasks.append(analyze_image(session, model_id, img_data, page_num + 1))

            results = await asyncio.gather(*tasks)

    pdf_document.close()
    return dict(results)
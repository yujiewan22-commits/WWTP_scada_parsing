from pathlib import Path
import base64, io
from PIL import Image
import fitz

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

def _image_to_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img.save(buf, format="JPEG", quality=88)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"

def load_document_images(path: str, max_pdf_pages: int = 8) -> list[dict]:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in IMAGE_EXTS:
        return [{"page": 1, "data_url": _image_to_data_url(Image.open(p))}]
    if suffix == ".pdf":
        doc = fitz.open(p)
        result = []
        for i in range(min(len(doc), max_pdf_pages)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes("jpeg")))
            result.append({"page": i + 1, "data_url": _image_to_data_url(img)})
        return result
    return []

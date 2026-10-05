from pathlib import Path
import base64
import io

from PIL import Image


SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def image_file_to_data_url(file_path: str) -> str:
    path = Path(file_path)
    if path.suffix.lower() not in SUPPORTED_EXTS:
        raise ValueError(
            "当前正式版只支持SCADA截图图片：PNG/JPG/JPEG/WEBP/BMP；"
            "不再处理PDF/DWG设计图。"
        )

    with Image.open(path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"

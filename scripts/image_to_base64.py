import base64
import io
from PIL import Image

def image_to_base64(image_path: str) -> str:
    # 讀圖後統一轉成 RGB，再以 PNG 編碼後 base64
    img = Image.open(image_path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

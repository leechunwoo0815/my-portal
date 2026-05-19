import os
import uuid
import re
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.exceptions import FileError
from app.models import User

router = APIRouter(tags=["上传"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def sanitize_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r"[^\w\-.]", "_", name)
    return name or "file"


def ensure_module_dir(module: str) -> str:
    module_safe = module.strip().lower()
    safe_modules = {"news", "blog", "products", "solutions", "portfolio", "moment", "avatar"}
    if module_safe not in safe_modules:
        module_safe = "misc"
    dir_path = os.path.join(settings.UPLOAD_DIR, module_safe)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def save_upload(file: UploadFile, module: str, custom_name: str | None = None) -> tuple[str, str]:
    if not file.content_type or file.content_type not in ALLOWED_IMAGE_TYPES:
        raise FileError("仅支持 JPG/PNG/GIF/WebP 格式图片")

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise FileError(f"图片大小不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB")

    ext = os.path.splitext(sanitize_filename(file.filename))[1] or ".jpg"
    if not ext.startswith("."):
        ext = "." + ext

    if custom_name:
        safe_name = re.sub(r"[^\w\-]", "_", custom_name)
        filename = f"{safe_name}{ext}"
    else:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        uid = uuid.uuid4().hex[:8]
        filename = f"{timestamp}_{uid}{ext}"

    module_dir = ensure_module_dir(module)
    file_path = os.path.join(module_dir, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    module_safe = module.strip().lower()
    safe_modules = {"news", "blog", "products", "solutions", "portfolio", "moment", "avatar"}
    if module_safe not in safe_modules:
        module_safe = "misc"
    relative_path = f"/uploads/{module_safe}/{filename}"
    return relative_path, filename


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    module: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    relative_url, filename = save_upload(file, module)
    return {"url": relative_url, "filename": filename}


@router.post("/cover")
async def upload_cover(
    file: UploadFile = File(...),
    module: str = Form(...),
    record_id: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    safe_name = re.sub(r"[^\w\-]", "_", record_id)
    relative_url, filename = save_upload(file, module, custom_name=safe_name)
    return {"url": relative_url, "filename": filename}
from squeezy.forms.file import FileForm
from squeezy.models.file import File
from werkzeug.utils import secure_filename
from hashlib import sha256
from datetime import datetime
from config import ENVIRONMENT
from database import db
from pathlib import Path
import os

class SqueezyServiceFileFormatError(Exception):
    pass



class SqueezyService:
    def handle_file_upload(self, form: FileForm):
        data = form.file.data
        if not data.content_type.startswith("text/"):
            raise SqueezyServiceFileFormatError("Plain Text files only")
        filename = secure_filename(data.filename)
        file_db = File()
        on_disk_name = sha256(bytes(filename + str(datetime.now()), encoding="utf-8")).hexdigest()
        file_db.label = form.label.data
        file_db.original_filename = filename
        storage_path = ENVIRONMENT.get("SQUEEZY_FILE_STORAGE_PATH")
        filepath = os.path.join(ENVIRONMENT.get("INSTANCE_PATH"), storage_path, f"file_{on_disk_name}")
        normalized_path = Path(filepath)
        file_db.filepath = str(normalized_path.absolute())
        with open(normalized_path.absolute(), "w+b") as f:
            data.save(f)
            f.seek(0)
            file_db.sha256 = sha256(f.read()).hexdigest()
        db.session.add(file_db)
        db.session.commit()

    def handle_file_read(self, file: File):
        with open(file.filepath, "rt", encoding="utf-8") as f:
            return f.read()

    def handle_file_delete(self, file: File):
        os.unlink(file.filepath)
        db.session.delete(file)
        db.session.commit()
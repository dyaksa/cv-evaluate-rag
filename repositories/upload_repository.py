from internal.db import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from model.model import Upload
import uuid

class UploadRepository:
    def __init__(self):
        pass

    def find_by_id(self, upload_id: str) -> Upload:
        db = SessionLocal()
        try:
            upload = db.query(Upload).filter(Upload.id == upload_id).first()
            return upload
        except SQLAlchemyError as e:
            raise e
        finally:
            db.close()

    def create(self, title: str, file_path: str, job_context: str, rubric_context: str) -> Upload:
        db = SessionLocal()
        try:
            new_upload = Upload(
                id=str(uuid.uuid4()),
                title=title,
                file_path=file_path,
                job_context=job_context,
                rubric_context=rubric_context
            )
            db.add(new_upload)
            db.commit()
            db.refresh(new_upload)
            return new_upload
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

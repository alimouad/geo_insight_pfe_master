from sqlalchemy.orm import Session

from app.models.system_log import SystemLog


def log_action(db: Session, *, user_id: int | None, action: str, details: str | None = None) -> None:
    db.add(SystemLog(user_id=user_id, action=action, details=details))
    db.commit()

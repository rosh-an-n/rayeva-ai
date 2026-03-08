from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AILog


def log_ai_call(
    db: Session,
    module: str,
    prompt: str,
    response: str,
    success: bool = True,
    error_message: str = None,
    tokens_used: int = None,
):
    entry = AILog(
        module=module,
        prompt_sent=prompt,
        response_received=response,
        tokens_used=tokens_used,
        success=success,
        error_message=error_message,
    )
    db.add(entry)
    db.commit()

    status = "✓" if success else "✗"
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{ts} | {module} | {status}")

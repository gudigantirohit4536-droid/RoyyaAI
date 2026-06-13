# Import all models here so Alembic can detect them
from app.core.database import Base  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.farm import Farm  # noqa: F401
from app.models.pond import Pond, Stocking, PondStatus  # noqa: F401
from app.models.daily_log import DailyLog  # noqa: F401
from app.models.conversation import AIConversation  # noqa: F401

import yaml
from pathlib import Path
from sqlmodel import Session
from app.core.security import get_password_hash
from app.models.user import User, UserCreate
from app.models.item import Item

class Seeder:
    def __init__(self, session: Session):
        self.session = session
        self.seed_data = self._load_seed_data()

    def _load_seed_data(self) -> dict:
        # Get the absolute path to the seed_data.yaml file
        current_dir = Path(__file__).parent
        seed_file = current_dir / "seed_data.yaml"
        
        if not seed_file.exists():
            raise FileNotFoundError(f"Seed file not found at {seed_file}")
            
        with open(seed_file, "r") as file:
            return yaml.safe_load(file)

    def _get_user_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def seed_users(self) -> None:
        for user_data in self.seed_data.get("users", []):
            if not self._get_user_by_email(user_data["email"]):
                user = UserCreate(**user_data)
                db_user = User(
                    email=user.email,
                    hashed_password=get_password_hash(user.password),
                    full_name=user.full_name,
                    is_active=user_data.get("is_active", True),
                    is_superuser=user_data.get("is_superuser", False)
                )
                self.session.add(db_user)
        self.session.commit()

    def seed_items(self) -> None:
        for item_data in self.seed_data.get("items", []):
            owner = self._get_user_by_email(item_data.pop("owner_email"))
            if owner:
                item = Item(**item_data, owner_id=owner.id)
                self.session.add(item)
        self.session.commit()

    def seed_all(self) -> None:
        self.seed_users()
        self.seed_items()
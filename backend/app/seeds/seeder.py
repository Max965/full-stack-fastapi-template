from sqlmodel import Session, select
from typing import Any, Dict, List, Type
import yaml
from app.models.user import User
from app.models.role import Role
from app.models.organisation import Organisation, Department, Employee

class Seeder:
    def __init__(self, session: Session):
        self.session = session
        self.model_map = {
            'roles': Role,
            'organisations': Organisation,
            'departments': Department,
            'users': User,
            'employees': Employee
        }
        self.seeded_ids = {}  # Store IDs of seeded records for references

    def _load_yaml(self) -> Dict[str, List[Dict[str, Any]]]:
        with open('app/seeds/seed.yaml', 'r') as file:
            return yaml.safe_load(file)

    def _exists(self, model: Type, unique_fields: Dict[str, Any]) -> bool:
        query = select(model)
        for field, value in unique_fields.items():
            query = query.where(getattr(model, field) == value)
        return self.session.exec(query).first() is not None

    def _resolve_reference(self, value: str) -> Any:
        """Resolve references like ${model[index].id} in the seed file"""
        if not isinstance(value, str) or not value.startswith('${'):
            return value
        
        path = value[2:-1].split('.')  # Remove ${} and split by .
        collection = path[0].split('[')
        model_name = collection[0]
        index = int(collection[1][:-1])
        field = path[-1]
        
        return self.seeded_ids[model_name][index][field]

    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data to resolve references"""
        processed = {}
        for key, value in data.items():
            processed[key] = self._resolve_reference(value)
        return processed

    def seed_all(self) -> None:
        data = self._load_yaml()
        
        # Seed in order of dependencies
        seeding_order = ['roles', 'organisations', 'departments', 'users', 'employees']
        
        for model_name in seeding_order:
            if model_name in data:
                self.seeded_ids[model_name] = []
                for item_data in data[model_name]:
                    processed_data = self._process_data(item_data)
                    model_class = self.model_map[model_name]
                    
                    # Check unique constraints based on model
                    unique_fields = {
                        'roles': {'name'},
                        'organisations': {'domain'},
                        'users': {'email'},
                        'employees': {'user_id', 'organisation_id'},
                        'departments': {'name', 'organisation_id'}
                    }[model_name]
                    
                    unique_data = {f: processed_data[f] for f in unique_fields}
                    if not self._exists(model_class, unique_data):
                        instance = model_class(**processed_data)
                        self.session.add(instance)
                        self.session.flush()  # Get ID before commit
                        self.seeded_ids[model_name].append({
                            'id': instance.id,
                            **processed_data
                        })
                
                self.session.commit()
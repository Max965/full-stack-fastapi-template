from typing import Any, Dict, List, Type, Optional
from sqlmodel import SQLModel, Session, select
import inspect
from datetime import datetime
from uuid import UUID, uuid4
import random
import string
from faker import Faker
import logging

logger = logging.getLogger(__name__)
fake = Faker()

class AutoSeeder:
    """Automatically generates seed data based on model structure"""
    
    def __init__(self, models: List[Type[SQLModel]], session: Session):
        self.models = models
        self.session = session
        self.generated_data: Dict[str, List[Dict[str, Any]]] = {}
        
    def _generate_value_for_type(self, field_type: Type, field_name: str, model_name: str) -> Any:
        """Generate appropriate test data based on field type and name"""
        if field_type == str:
            if "email" in field_name.lower():
                return f"test_{model_name.lower()}_{fake.user_name()}@example.com"
            elif "name" in field_name.lower():
                return f"Test {model_name} {fake.last_name()}"
            elif "description" in field_name.lower():
                return f"Test description for {model_name}: {fake.text(max_nb_chars=50)}"
            elif "password" in field_name.lower():
                return "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # test password
            elif "domain" in field_name.lower():
                return f"test-{fake.domain_word()}.example.com"
            else:
                return f"Test_{model_name}_{fake.word()}"
        elif field_type == int:
            if "level" in field_name.lower():
                return random.randint(1, 5)
            return random.randint(1, 100)
        elif field_type == float:
            return round(random.uniform(0, 100), 2)
        elif field_type == bool:
            return random.choice([True, False])
        elif field_type == datetime:
            return datetime.utcnow()
        elif field_type == UUID:
            return uuid4()
        return None

    def _get_model_dependencies(self) -> List[Type[SQLModel]]:
        """Sort models by their dependencies"""
        dependency_graph = {}
        
        for model in self.models:
            dependencies = set()
            for field in model.__fields__.values():
                if field.type_ in self.models:
                    dependencies.add(field.type_)
            dependency_graph[model] = dependencies
        
        # Topological sort
        sorted_models = []
        visited = set()
        
        def visit(model):
            if model in visited:
                return
            visited.add(model)
            for dep in dependency_graph[model]:
                visit(dep)
            sorted_models.append(model)
            
        for model in self.models:
            visit(model)
            
        return sorted_models

    def _check_existing_data(self, model: Type[SQLModel]) -> bool:
        """Check if test data already exists for this model"""
        try:
            result = self.session.exec(select(model)).first()
            return result is not None
        except Exception as e:
            logger.warning(f"Error checking existing data for {model.__name__}: {e}")
            return False

    def generate_seed_data(self, num_records: int = 3, force: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Generate seed data for all models"""
        sorted_models = self._get_model_dependencies()
        
        for model in sorted_models:
            model_name = model.__name__
            
            # Check if test data already exists
            if not force and self._check_existing_data(model):
                logger.info(f"Skipping {model_name} - test data already exists")
                continue
                
            logger.info(f"Generating test data for {model_name}")
            self.generated_data[model_name.lower()] = []
            
            for i in range(num_records):
                record = {}
                
                for field_name, field in model.__fields__.items():
                    if field_name == "id":
                        continue  # Skip ID fields as they're usually auto-generated
                        
                    if field.type_ in self.models:
                        # Handle foreign key
                        related_model_name = field.type_.__name__.lower()
                        if related_model_name in self.generated_data and self.generated_data[related_model_name]:
                            record[field_name] = random.choice(self.generated_data[related_model_name])["id"]
                    else:
                        # Generate value based on field type
                        value = self._generate_value_for_type(field.type_, field_name, f"{model_name}_{i+1}")
                        if value is not None:
                            record[field_name] = value
                
                self.generated_data[model_name.lower()].append(record)
        
        return self.generated_data

    def generate_yaml(self) -> str:
        """Generate YAML representation of the seed data"""
        import yaml
        return yaml.dump(self.generated_data, default_flow_style=False)

    def seed_database(self, num_records: int = 3, force: bool = False) -> None:
        """Generate and seed the database"""
        try:
            self.generate_seed_data(num_records, force)
            
            for model in self._get_model_dependencies():
                model_name = model.__name__.lower()
                if model_name in self.generated_data:
                    for record_data in self.generated_data[model_name]:
                        record = model(**record_data)
                        self.session.add(record)
            
            self.session.commit()
            logger.info("Test data seeding completed successfully")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error seeding database: {e}")
            raise

# Example usage:
if __name__ == "__main__":
    from app.models.user import User
    from app.models.role import Role
    from app.models.organisation import Organisation, Department, Employee
    from app.core.db import db
    
    models = [Role, User, Organisation, Department, Employee]
    
    with Session(db.engine) as session:
        seeder = AutoSeeder(models, session)
        
        # Generate and seed test data
        seeder.seed_database(num_records=3, force=False)
        
        # Optionally save to YAML
        with open('app/seeds/auto_generated_seed.yaml', 'w') as f:
            f.write(seeder.generate_yaml()) 
from abc import ABC, abstractmethod

class BaseModelInterface(ABC):
    @abstractmethod
    def save(self):
        """Save the model instance to the database."""
        pass

    @abstractmethod
    def delete(self):
        """Delete the model instance from the database."""
        pass
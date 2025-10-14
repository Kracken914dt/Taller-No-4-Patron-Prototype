"""
Patrón Prototype - Interfaces y clases base para clonación de objetos.

El patrón Prototype permite la clonación de objetos sin acoplar el código
a las clases específicas de esos objetos. Es útil para crear nuevas instancias
basadas en configuraciones existentes.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import copy
import uuid
from datetime import datetime


class Prototype(ABC):
    """
    Interfaz base del patrón Prototype.
    
    Define el método clone() que debe ser implementado por todas las clases
    que quieran ser clonables.
    """
    
    @abstractmethod
    def clone(self) -> Prototype:
        """
        Crea una copia del objeto actual.
        
        Returns:
            Una nueva instancia con los mismos datos que el objeto actual
        """
        pass
    
    @abstractmethod
    def get_prototype_info(self) -> Dict[str, Any]:
        """
        Obtiene información del prototipo para identificación y gestión.
        
        Returns:
            Diccionario con información del prototipo
        """
        pass


class CloneableResource(Prototype):
    """
    Clase base para recursos que pueden ser clonados.
    
    Proporciona funcionalidad común para la clonación de recursos de infraestructura,
    incluyendo metadatos de clonación y gestión de identificadores únicos.
    """
    
    def __init__(self):
        self.prototype_id: str = f"proto-{uuid.uuid4().hex[:8]}"
        self.is_prototype: bool = False
        self.cloned_from: Optional[str] = None
        self.clone_count: int = 0
        self.created_at: datetime = datetime.now()
        self.last_cloned_at: Optional[datetime] = None
        
    def clone(self) -> CloneableResource:
        """
        Implementación por defecto del clonado profundo.
        
        Crea una copia completa del objeto, actualizando los metadatos
        de clonación apropiadamente.
        """
        # Realizar copia profunda del objeto
        cloned = copy.deepcopy(self)
        
        # Actualizar metadatos del clon
        cloned.resource_id = f"{self.resource_id.split('-')[0]}-{uuid.uuid4().hex[:8]}"
        cloned.prototype_id = f"proto-{uuid.uuid4().hex[:8]}"
        cloned.is_prototype = False
        cloned.cloned_from = self.prototype_id
        cloned.clone_count = 0
        cloned.created_at = datetime.now()
        cloned.last_cloned_at = None
        
        # Actualizar contador del objeto original
        self.clone_count += 1
        self.last_cloned_at = datetime.now()
        
        return cloned
    
    def get_prototype_info(self) -> Dict[str, Any]:
        """
        Obtiene información detallada del prototipo.
        """
        return {
            "prototype_id": self.prototype_id,
            "resource_id": getattr(self, 'resource_id', 'unknown'),
            "resource_type": getattr(self, 'get_resource_type', lambda: 'unknown')(),
            "name": getattr(self, 'name', 'unnamed'),
            "is_prototype": self.is_prototype,
            "cloned_from": self.cloned_from,
            "clone_count": self.clone_count,
            "created_at": self.created_at.isoformat(),
            "last_cloned_at": self.last_cloned_at.isoformat() if self.last_cloned_at else None
        }
    
    def mark_as_prototype(self, prototype_name: Optional[str] = None) -> None:
        """
        Marca este recurso como un prototipo reutilizable.
        
        Args:
            prototype_name: Nombre descriptivo para el prototipo
        """
        self.is_prototype = True
        if prototype_name:
            self.name = prototype_name
    
    def can_be_cloned(self) -> bool:
        """
        Verifica si el recurso puede ser clonado.
        
        Returns:
            True si el recurso está en un estado que permite clonación
        """
        # Verificar que el recurso esté en un estado estable
        valid_statuses = ['running', 'stopped', 'creating']
        current_status = getattr(self, 'status', None)
        
        return current_status in valid_statuses if current_status else True


class PrototypeMetadata:
    """
    Clase para almacenar metadatos adicionales de prototipos.
    
    Facilita la gestión y búsqueda de prototipos en el PrototypeManager.
    """
    
    def __init__(self, 
                 name: str,
                 description: str = "",
                 category: str = "general",
                 tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.description = description
        self.category = category
        self.tags = tags or {}
        self.created_at = datetime.now()
        self.usage_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte los metadatos a diccionario."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count
        }
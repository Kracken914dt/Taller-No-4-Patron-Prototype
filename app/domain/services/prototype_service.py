"""
Prototype Manager - Gestiona la colección de prototipos disponibles.

El PrototypeManager actúa como un registro centralizado de prototipos,
permitiendo almacenar, buscar, clonar y gestionar prototipos de recursos
de infraestructura.
"""
from typing import Dict, List, Optional, Any, Type
import uuid
from datetime import datetime
import logging

from ..abstractions.prototype import CloneableResource, PrototypeMetadata
from ..abstractions.products import VirtualMachine, Database, LoadBalancer


logger = logging.getLogger(__name__)


class PrototypeManager:
    """
    Gestor centralizado de prototipos.
    
    Implementa el patrón Singleton para garantizar una única instancia
    y mantiene un registro de todos los prototipos disponibles en el sistema.
    """
    
    _instance: Optional['PrototypeManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'PrototypeManager':
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el manager solo una vez."""
        if not self._initialized:
            self._prototypes: Dict[str, CloneableResource] = {}
            self._metadata: Dict[str, PrototypeMetadata] = {}
            self._categories: Dict[str, List[str]] = {}
            self._initialize_default_prototypes()
            PrototypeManager._initialized = True
            logger.info("PrototypeManager initialized")
    
    def _initialize_default_prototypes(self) -> None:
        """Inicializa prototipos predeterminados del sistema."""
        logger.info("Initializing default prototypes...")
        # Los prototipos por defecto se pueden cargar aquí
        # Por ahora, el manager comienza vacío y se puebla dinámicamente
    
    def register_prototype(self, 
                          prototype: CloneableResource,
                          name: str,
                          description: str = "",
                          category: str = "general",
                          tags: Optional[Dict[str, str]] = None) -> str:
        """
        Registra un nuevo prototipo en el manager.
        
        Args:
            prototype: El objeto que actuará como prototipo
            name: Nombre descriptivo del prototipo
            description: Descripción detallada
            category: Categoría del prototipo (vm, database, loadbalancer, etc.)
            tags: Tags adicionales para búsqueda y clasificación
            
        Returns:
            ID único del prototipo registrado
        """
        prototype_id = f"proto-{uuid.uuid4().hex[:8]}"
        
        # Marcar el objeto como prototipo
        prototype.mark_as_prototype(name)
        
        # Crear metadatos
        metadata = PrototypeMetadata(name, description, category, tags)
        
        # Registrar en las colecciones
        self._prototypes[prototype_id] = prototype
        self._metadata[prototype_id] = metadata
        
        # Agregar a la categoría correspondiente
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(prototype_id)
        
        logger.info(f"Prototype registered: {name} (ID: {prototype_id}, Category: {category})")
        return prototype_id
    
    def get_prototype(self, prototype_id: str) -> Optional[CloneableResource]:
        """
        Obtiene un prototipo por su ID.
        
        Args:
            prototype_id: ID único del prototipo
            
        Returns:
            El prototipo si existe, None en caso contrario
        """
        return self._prototypes.get(prototype_id)
    
    def clone_prototype(self, prototype_id: str, new_name: Optional[str] = None) -> Optional[CloneableResource]:
        """
        Clona un prototipo existente.
        
        Args:
            prototype_id: ID del prototipo a clonar
            new_name: Nombre para la nueva instancia (opcional)
            
        Returns:
            Nueva instancia clonada o None si el prototipo no existe
        """
        prototype = self.get_prototype(prototype_id)
        if not prototype:
            logger.warning(f"Prototype not found: {prototype_id}")
            return None
        
        if not prototype.can_be_cloned():
            logger.warning(f"Prototype cannot be cloned in current state: {prototype_id}")
            return None
        
        # Clonar el prototipo
        cloned = prototype.clone()
        
        # Actualizar el nombre si se proporcionó
        if new_name:
            cloned.name = new_name
        
        # Incrementar contador de uso en metadatos
        if prototype_id in self._metadata:
            self._metadata[prototype_id].usage_count += 1
        
        logger.info(f"Prototype cloned: {prototype_id} -> {cloned.prototype_id}")
        return cloned
    
    def list_prototypes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista todos los prototipos disponibles.
        
        Args:
            category: Filtrar por categoría específica (opcional)
            
        Returns:
            Lista de información de prototipos
        """
        if category:
            prototype_ids = self._categories.get(category, [])
        else:
            prototype_ids = list(self._prototypes.keys())
        
        result = []
        for pid in prototype_ids:
            if pid in self._prototypes and pid in self._metadata:
                prototype = self._prototypes[pid]
                metadata = self._metadata[pid]
                
                info = {
                    "prototype_id": pid,
                    "prototype_info": prototype.get_prototype_info(),
                    "metadata": metadata.to_dict()
                }
                result.append(info)
        
        return result
    
    def search_prototypes(self, 
                         query: str = "",
                         category: Optional[str] = None,
                         tags: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Busca prototipos basado en diferentes criterios.
        
        Args:
            query: Texto a buscar en nombre y descripción
            category: Filtrar por categoría
            tags: Filtrar por tags específicos
            
        Returns:
            Lista de prototipos que coinciden con los criterios
        """
        results = []
        
        for pid, metadata in self._metadata.items():
            prototype = self._prototypes.get(pid)
            if not prototype:
                continue
            
            # Filtrar por categoría si se especifica
            if category and metadata.category != category:
                continue
            
            # Filtrar por query en nombre y descripción
            if query:
                query_lower = query.lower()
                if (query_lower not in metadata.name.lower() and 
                    query_lower not in metadata.description.lower()):
                    continue
            
            # Filtrar por tags si se especifican
            if tags:
                metadata_tags = metadata.tags
                if not all(metadata_tags.get(k) == v for k, v in tags.items()):
                    continue
            
            # Si pasa todos los filtros, agregarlo a resultados
            info = {
                "prototype_id": pid,
                "prototype_info": prototype.get_prototype_info(),
                "metadata": metadata.to_dict()
            }
            results.append(info)
        
        return results
    
    def remove_prototype(self, prototype_id: str) -> bool:
        """
        Remueve un prototipo del manager.
        
        Args:
            prototype_id: ID del prototipo a remover
            
        Returns:
            True si se removió exitosamente, False si no se encontró
        """
        if prototype_id not in self._prototypes:
            return False
        
        # Obtener categoría para limpieza
        metadata = self._metadata.get(prototype_id)
        if metadata:
            category = metadata.category
            if category in self._categories:
                self._categories[category] = [
                    pid for pid in self._categories[category] 
                    if pid != prototype_id
                ]
        
        # Remover de las colecciones
        del self._prototypes[prototype_id]
        if prototype_id in self._metadata:
            del self._metadata[prototype_id]
        
        logger.info(f"Prototype removed: {prototype_id}")
        return True
    
    def get_categories(self) -> List[str]:
        """
        Obtiene todas las categorías disponibles.
        
        Returns:
            Lista de nombres de categorías
        """
        return list(self._categories.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del uso de prototipos.
        
        Returns:
            Diccionario con estadísticas generales
        """
        total_prototypes = len(self._prototypes)
        total_clones = sum(p.clone_count for p in self._prototypes.values())
        
        categories_stats = {}
        for category, prototype_ids in self._categories.items():
            categories_stats[category] = {
                "count": len(prototype_ids),
                "total_clones": sum(
                    self._prototypes[pid].clone_count 
                    for pid in prototype_ids 
                    if pid in self._prototypes
                )
            }
        
        most_used = None
        max_usage = 0
        for pid, metadata in self._metadata.items():
            if metadata.usage_count > max_usage:
                max_usage = metadata.usage_count
                most_used = {
                    "prototype_id": pid,
                    "name": metadata.name,
                    "usage_count": metadata.usage_count
                }
        
        return {
            "total_prototypes": total_prototypes,
            "total_clones_created": total_clones,
            "categories": categories_stats,
            "most_used_prototype": most_used
        }
    
    def clear_all(self) -> None:
        """Limpia todos los prototipos (útil para testing)."""
        self._prototypes.clear()
        self._metadata.clear()
        self._categories.clear()
        logger.info("All prototypes cleared")


# Instancia global del manager (Singleton)
prototype_manager = PrototypeManager()
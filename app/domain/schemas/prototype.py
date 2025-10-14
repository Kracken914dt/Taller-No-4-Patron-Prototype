"""
Esquemas Pydantic para el patrón Prototype.

Define las estructuras de datos para requests y responses
relacionadas con la funcionalidad de clonación de prototipos.
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PrototypeCategory(str, Enum):
    """Categorías disponibles para prototipos"""
    VM = "vm"
    DATABASE = "database"
    LOADBALANCER = "loadbalancer"
    STORAGE = "storage"
    NETWORK = "network"
    GENERAL = "general"


class CreatePrototypeRequest(BaseModel):
    """Request para crear un prototipo desde un recurso existente"""
    
    resource_id: str = Field(..., description="ID del recurso existente a convertir en prototipo")
    name: str = Field(..., description="Nombre descriptivo para el prototipo")
    description: str = Field(default="", description="Descripción detallada del prototipo")
    category: PrototypeCategory = Field(default=PrototypeCategory.GENERAL, description="Categoría del prototipo")
    tags: Optional[Dict[str, str]] = Field(default=None, description="Tags adicionales para clasificación")
    
    class Config:
        schema_extra = {
            "example": {
                "resource_id": "i-1234567890abcdef0",
                "name": "web-server-template",
                "description": "Plantilla de servidor web con configuración optimizada",
                "category": "vm",
                "tags": {
                    "environment": "production",
                    "team": "devops",
                    "purpose": "web-server"
                }
            }
        }


class ClonePrototypeRequest(BaseModel):
    """Request para clonar un prototipo existente"""
    
    prototype_id: str = Field(..., description="ID del prototipo a clonar")
    new_name: Optional[str] = Field(default=None, description="Nombre para la nueva instancia clonada")
    custom_tags: Optional[Dict[str, str]] = Field(default=None, description="Tags adicionales para la instancia clonada")
    
    class Config:
        schema_extra = {
            "example": {
                "prototype_id": "proto-12345678",
                "new_name": "web-server-prod-01",
                "custom_tags": {
                    "environment": "production",
                    "instance_number": "01"
                }
            }
        }


class PrototypeSearchRequest(BaseModel):
    """Request para buscar prototipos"""
    
    query: Optional[str] = Field(default="", description="Texto a buscar en nombre y descripción")
    category: Optional[PrototypeCategory] = Field(default=None, description="Filtrar por categoría específica")
    tags: Optional[Dict[str, str]] = Field(default=None, description="Filtrar por tags específicos")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "web server",
                "category": "vm",
                "tags": {
                    "environment": "production"
                }
            }
        }


class PrototypeInfo(BaseModel):
    """Información básica de un prototipo"""
    
    prototype_id: str
    resource_id: str
    resource_type: str
    name: str
    is_prototype: bool
    cloned_from: Optional[str]
    clone_count: int
    created_at: str
    last_cloned_at: Optional[str]


class PrototypeMetadata(BaseModel):
    """Metadatos de un prototipo"""
    
    name: str
    description: str
    category: str
    tags: Dict[str, str]
    created_at: str
    usage_count: int


class PrototypeDetails(BaseModel):
    """Información completa de un prototipo"""
    
    prototype_id: str
    prototype_info: PrototypeInfo
    metadata: PrototypeMetadata


class PrototypeResponse(BaseModel):
    """Response base para operaciones con prototipos"""
    
    success: bool
    message: str
    prototype_id: Optional[str] = None
    prototype_details: Optional[PrototypeDetails] = None


class CloneResponse(BaseModel):
    """Response para operaciones de clonación"""
    
    success: bool
    message: str
    original_prototype_id: str
    cloned_resource: Optional[Dict[str, Any]] = None
    clone_info: Optional[PrototypeInfo] = None


class PrototypeListResponse(BaseModel):
    """Response para listado de prototipos"""
    
    success: bool
    total_count: int
    category_filter: Optional[str] = None
    prototypes: List[PrototypeDetails]


class PrototypeSearchResponse(BaseModel):
    """Response para búsqueda de prototipos"""
    
    success: bool
    query: str
    results_count: int
    prototypes: List[PrototypeDetails]


class PrototypeStatistics(BaseModel):
    """Estadísticas de uso de prototipos"""
    
    total_prototypes: int
    total_clones_created: int
    categories: Dict[str, Dict[str, int]]
    most_used_prototype: Optional[Dict[str, Any]]


class PrototypeStatsResponse(BaseModel):
    """Response para estadísticas de prototipos"""
    
    success: bool
    statistics: PrototypeStatistics


class PrototypeCategoriesResponse(BaseModel):
    """Response para listado de categorías"""
    
    success: bool
    categories: List[str]


# Esquemas para integración con recursos existentes
class ResourceToPrototypeRequest(BaseModel):
    """Request para convertir un recurso existente en prototipo"""
    
    provider: str = Field(..., description="Proveedor del recurso (aws, azure, gcp, etc.)")
    resource_type: str = Field(..., description="Tipo de recurso (vm, database, loadbalancer, etc.)")
    resource_id: str = Field(..., description="ID único del recurso")
    prototype_name: str = Field(..., description="Nombre para el prototipo")
    prototype_description: str = Field(default="", description="Descripción del prototipo")
    prototype_category: PrototypeCategory = Field(default=PrototypeCategory.GENERAL)
    prototype_tags: Optional[Dict[str, str]] = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "aws",
                "resource_type": "vm",
                "resource_id": "i-1234567890abcdef0",
                "prototype_name": "optimized-web-server",
                "prototype_description": "Servidor web optimizado para alta concurrencia",
                "prototype_category": "vm",
                "prototype_tags": {
                    "performance": "high",
                    "use_case": "web"
                }
            }
        }
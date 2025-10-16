"""
Controlador para el patrón Prototype.

Proporciona endpoints REST para gestionar prototipos de recursos de infraestructura,
incluyendo creación, clonación, búsqueda y estadísticas.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
import logging

from ..domain.services.prototype_service import prototype_manager
from ..domain.schemas.prototype import (
    CreatePrototypeRequest, ClonePrototypeRequest, PrototypeSearchRequest,
    PrototypeResponse, CloneResponse, PrototypeListResponse, PrototypeSearchResponse,
    PrototypeStatsResponse, PrototypeCategoriesResponse, ResourceToPrototypeRequest,
    PrototypeCategory
)
from ..infrastructure.repository import repository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/prototype/create", 
            response_model=PrototypeResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Crear prototipo desde recurso existente",
            description="Convierte un recurso existente en un prototipo reutilizable")
async def create_prototype(request: CreatePrototypeRequest):
    """
    Crea un prototipo a partir de un recurso existente en el sistema.
    
    El recurso debe existir en el repositorio y estar en un estado válido
    para ser convertido en prototipo.
    """
    try:
        # Buscar el recurso en el repositorio
        resource = None
        try:
            resource = repository.get(request.resource_id)
        except Exception:
            resource = None
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource with ID {request.resource_id} not found"
            )
        # Verificar que el recurso puede ser clonado
        if not hasattr(resource, 'can_be_cloned') or not resource.can_be_cloned():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resource {request.resource_id} cannot be used as prototype in its current state"
            )
        # Registrar el prototipo
        prototype_id = prototype_manager.register_prototype(
            prototype=resource,
            name=request.name,
            description=request.description,
            category=request.category.value,
            tags=request.tags or {}
        )
        # Obtener detalles del prototipo creado
        prototype = prototype_manager.get_prototype(prototype_id)
        prototype_details = {
            "prototype_id": prototype_id,
            "prototype_info": prototype.get_prototype_info(),
            "metadata": prototype_manager._metadata[prototype_id].to_dict()
        }
        logger.info(f"Prototype created successfully: {prototype_id}")
        return PrototypeResponse(
            success=True,
            message=f"Prototype '{request.name}' created successfully",
            prototype_id=prototype_id,
            prototype_details=prototype_details
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prototype: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prototype: {str(e)}"
        )


@router.post("/prototype/clone/{prototype_id}",
            response_model=CloneResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Clonar prototipo existente",
            description="Crea una nueva instancia basada en un prototipo existente")
async def clone_prototype(prototype_id: str, request: ClonePrototypeRequest):
    """
    Clona un prototipo existente, creando una nueva instancia con las mismas configuraciones.
    
    La nueva instancia será independiente del prototipo original y podrá ser
    modificada sin afectar al prototipo.
    """
    try:
        # Verificar que el prototype_id en la URL coincide con el del request
        if prototype_id != request.prototype_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prototype ID in URL does not match request body"
            )
        
        # Clonar el prototipo
        cloned_resource = prototype_manager.clone_prototype(
            prototype_id=prototype_id,
            new_name=request.new_name
        )
        
        if not cloned_resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prototype with ID {prototype_id} not found or cannot be cloned"
            )
        
        # Agregar tags personalizados si se proporcionaron
        if request.custom_tags:
            cloned_resource.tags.update(request.custom_tags)
        
        # Almacenar el recurso clonado en el repositorio
        repository.store_resource(cloned_resource.resource_id, cloned_resource)
        
        logger.info(f"Prototype cloned successfully: {prototype_id} -> {cloned_resource.resource_id}")
        
        return CloneResponse(
            success=True,
            message=f"Prototype cloned successfully as '{cloned_resource.name}'",
            original_prototype_id=prototype_id,
            cloned_resource={
                "resource_id": cloned_resource.resource_id,
                "name": cloned_resource.name,
                "resource_type": cloned_resource.get_resource_type(),
                "specs": cloned_resource.get_specs()
            },
            clone_info=cloned_resource.get_prototype_info()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cloning prototype {prototype_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clone prototype: {str(e)}"
        )
@router.get("/prototype/list",
            response_model=PrototypeListResponse,
            summary="Listar prototipos disponibles",
            description="Obtiene la lista de todos los prototipos disponibles, opcionalmente filtrados por categoría")
async def list_prototypes(category: Optional[PrototypeCategory] = Query(None, description="Filtrar por categoría")):
    """
    Lista todos los prototipos disponibles en el sistema.
    
    Permite filtrar por categoría para obtener solo prototipos específicos.
    """
    try:
        category_filter = category.value if category else None
        prototypes = prototype_manager.list_prototypes(category=category_filter)
        
        logger.info(f"Listed {len(prototypes)} prototypes (category: {category_filter})")
        
        return PrototypeListResponse(
            success=True,
            total_count=len(prototypes),
            category_filter=category_filter,
            prototypes=prototypes
        )
        
    except Exception as e:
        logger.error(f"Error listing prototypes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list prototypes: {str(e)}"
        )


# @router.post("/prototype/search",
#             response_model=PrototypeSearchResponse,
#             summary="Buscar prototipos",
#             description="Busca prototipos basado en criterios específicos como texto, categoría y tags")
# async def search_prototypes(request: PrototypeSearchRequest):
#     """
#     Busca prototipos basándose en diferentes criterios de búsqueda.
#     
#     Permite combinar búsqueda por texto libre, categoría específica y tags.
#     """
#     try:
#         category_filter = request.category.value if request.category else None
#         
#         results = prototype_manager.search_prototypes(
#             query=request.query,
#             category=category_filter,
#             tags=request.tags
#         )
#         
#         logger.info(f"Search completed: {len(results)} results for query '{request.query}'")
#         
#         return PrototypeSearchResponse(
#             success=True,
#             query=request.query,
#             results_count=len(results),
#             prototypes=results
#         )
#         
#     except Exception as e:
#         logger.error(f"Error searching prototypes: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to search prototypes: {str(e)}"
#         )


@router.get("/prototype/{prototype_id}",
           response_model=PrototypeResponse,
           summary="Obtener detalles de prototipo",
           description="Obtiene información detallada de un prototipo específico")
async def get_prototype_details(prototype_id: str):
    """
    Obtiene información detallada de un prototipo específico.
    """
    try:
        prototype = prototype_manager.get_prototype(prototype_id)
        if not prototype:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prototype with ID {prototype_id} not found"
            )
        
        metadata = prototype_manager._metadata.get(prototype_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata for prototype {prototype_id} not found"
            )
        
        prototype_details = {
            "prototype_id": prototype_id,
            "prototype_info": prototype.get_prototype_info(),
            "metadata": metadata.to_dict()
        }
        
        return PrototypeResponse(
            success=True,
            message="Prototype details retrieved successfully",
            prototype_id=prototype_id,
            prototype_details=prototype_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prototype details {prototype_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prototype details: {str(e)}"
        )


@router.delete("/prototype/{prototype_id}",
              response_model=PrototypeResponse,
              summary="Eliminar prototipo",
              description="Elimina un prototipo del sistema")
async def delete_prototype(prototype_id: str):
    """
    Elimina un prototipo del sistema.
    
    Esta operación no afecta a las instancias que fueron clonadas desde este prototipo.
    """
    try:
        success = prototype_manager.remove_prototype(prototype_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prototype with ID {prototype_id} not found"
            )
        
        logger.info(f"Prototype deleted: {prototype_id}")
        
        return PrototypeResponse(
            success=True,
            message=f"Prototype {prototype_id} deleted successfully",
            prototype_id=prototype_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prototype {prototype_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete prototype: {str(e)}"
        )



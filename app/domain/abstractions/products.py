"""
Abstract products for the Abstract Factory pattern.
These define the interfaces for the different types of cloud resources.

Ahora integrado con el patrón Prototype para permitir clonación de recursos.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from .prototype import CloneableResource


class ResourceStatus(str, Enum):
    """Estados posibles de los recursos"""
    CREATING = "creating"
    RUNNING = "running" 
    STOPPED = "stopped"
    DELETING = "deleting"
    ERROR = "error"


class CloudResource(CloneableResource, ABC):
    """
    Producto abstracto base para todos los recursos en la nube.
    
    Ahora hereda de CloneableResource para soportar el patrón Prototype,
    permitiendo que todos los recursos de infraestructura puedan ser clonados.
    """
    
    def __init__(self, resource_id: str, name: str, region: str):
        # Inicializar CloneableResource (patrón Prototype)
        super().__init__()
        
        # Propiedades específicas del recurso cloud
        self.resource_id = resource_id
        self.name = name
        self.region = region
        self.status = ResourceStatus.CREATING
        self.tags: Dict[str, str] = {}
    
    @abstractmethod
    def get_resource_type(self) -> str:
        """Retorna el tipo de recurso"""
        pass
    
    @abstractmethod
    def get_specs(self) -> Dict[str, Any]:
        """Retorna las especificaciones del recurso"""
        pass
    
    def can_be_cloned(self) -> bool:
        """
        Override del método base para verificar estado específico de recursos cloud.
        
        Los recursos cloud pueden ser clonados cuando están en estados estables.
        """
        valid_statuses = [ResourceStatus.RUNNING, ResourceStatus.STOPPED, ResourceStatus.CREATING]
        return self.status in valid_statuses


class VirtualMachine(CloudResource):
    """Producto abstracto para máquinas virtuales"""
    
    @abstractmethod
    def start(self) -> None:
        """Inicia la máquina virtual"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Detiene la máquina virtual"""
        pass
    
    @abstractmethod
    def restart(self) -> None:
        """Reinicia la máquina virtual"""
        pass
    
    @abstractmethod
    def resize(self, new_size: str) -> None:
        """Cambia el tamaño de la VM"""
        pass


class Database(CloudResource):
    """Producto abstracto para bases de datos"""
    
    @abstractmethod
    def backup(self) -> str:
        """Crea un backup de la base de datos"""
        pass
    
    @abstractmethod
    def restore(self, backup_id: str) -> None:
        """Restaura desde un backup"""
        pass
    
    @abstractmethod
    def scale(self, new_tier: str) -> None:
        """Escala la base de datos"""
        pass


class LoadBalancer(CloudResource):
    """Producto abstracto para balanceadores de carga"""
    
    @abstractmethod
    def add_target(self, target_id: str) -> None:
        """Añade un target al balanceador"""
        pass
    
    @abstractmethod
    def remove_target(self, target_id: str) -> None:
        """Remueve un target del balanceador"""
        pass
    
    @abstractmethod
    def configure_health_check(self, config: Dict[str, Any]) -> None:
        """Configura los health checks"""
        pass


class Storage(CloudResource):
    """Producto abstracto para almacenamiento"""
    
    @abstractmethod
    def create_bucket(self, bucket_name: str) -> None:
        """Crea un bucket/contenedor"""
        pass
    
    @abstractmethod
    def upload_file(self, file_path: str, key: str) -> None:
        """Sube un archivo"""
        pass
    
    @abstractmethod
    def download_file(self, key: str, local_path: str) -> None:
        """Descarga un archivo"""
        pass


class NetworkInterface(CloudResource):
    """Producto abstracto para interfaces de red (ahora heredando de CloudResource para clonación)"""
    
    @abstractmethod
    def configure_security_group(self, rules: Dict[str, Any]) -> None:
        """Configura las reglas de seguridad"""
        pass
    
    @abstractmethod
    def assign_public_ip(self) -> str:
        """Asigna una IP pública"""
        pass
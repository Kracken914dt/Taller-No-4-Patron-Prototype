"""
Productos concretos de OnPremise para el patrón Abstract Factory.
Estos implementan las interfaces abstractas para infraestructura on-premise (VMware, Hyper-V, KVM, etc.).
"""
from __future__ import annotations
from typing import Dict, Any, List
import uuid
import copy
import random
from ..abstractions.products import VirtualMachine, Database, LoadBalancer, Storage, ResourceStatus, NetworkInterface


class OnPremiseVirtualMachine(VirtualMachine):
    """Implementación concreta de VM para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "datacenter-1")
        super().__init__(
            resource_id=f"onprem-vm-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-vm-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.cpu_cores = config.get("cpu", 2)
        self.ram_gb = config.get("ram_gb", 4)
        self.disk_gb = config.get("disk_gb", 50)
        self.hypervisor = config.get("hypervisor", "vmware")  # vmware, hyperv, kvm, xen
        self.network_interface = config.get("nic", "eth0")
        self.host_server = config.get("host_server", "esxi-01.company.local")
        self.datastore = config.get("datastore", "datastore1")
        
    def start(self) -> None:
        print(f"🟢 OnPrem: Iniciando VM {self.name} en {self.hypervisor} host {self.host_server}")
        self.status = ResourceStatus.RUNNING

    def stop(self) -> None:
        print(f"🔴 OnPrem: Deteniendo VM {self.name} en {self.hypervisor}")
        self.status = ResourceStatus.STOPPED

    def restart(self) -> None:
        print(f"🔁 OnPrem: Reiniciando VM {self.name} en {self.hypervisor}")
        self.status = ResourceStatus.RUNNING

    def resize(self, new_size: str) -> None:
        print(f"🔄 OnPrem: Redimensionando VM {self.name} a tamaño {new_size}")
        # Aquí podrías mapear new_size a cpu/ram/disk si lo deseas

    def get_resource_type(self) -> str:
        return "onprem.virtual_machine"

    def get_specs(self) -> Dict[str, Any]:
        return {
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "disk_gb": self.disk_gb,
            "hypervisor": self.hypervisor,
            "network_interface": self.network_interface,
            "host_server": self.host_server,
            "datastore": self.datastore
        }
    
    def clone(self) -> 'OnPremVirtualMachine':
        """Clona la VM On-Premise con nueva configuración"""
        
        if not self._prepare_for_cloning():
            raise ValueError(f"OnPrem VM {self.id} no puede clonarse en estado {self.status}")
        
        # Crear copia profunda
        cloned_vm = copy.deepcopy(self)
        
        # Generar nuevos identificadores únicos
        original_id = self.id
        cloned_vm.id = self._generate_clone_id()
        
        # Generar nueva IP en el mismo rango de red
        if hasattr(self, 'network_interface') and isinstance(self.network_interface, dict):
            if 'ip_address' in self.network_interface:
                base_ip = ".".join(self.network_interface['ip_address'].split('.')[:-1])
                new_last_octet = random.randint(10, 254)
                cloned_vm.network_interface['ip_address'] = f"{base_ip}.{new_last_octet}"
        
        # Asignar nuevo datastore/host (simulado - distribuir carga)
        if hasattr(self, 'host_server'):
            host_num = random.randint(1, 10)
            cloned_vm.host_server = f"esxi-host-{host_num:02d}.local"
        
        # Actualizar metadatos de clonación
        cloned_vm._update_clone_metadata(original_id)
        cloned_vm.status = ResourceStatus.CREATING
        
        # Incrementar contador en original
        self._prototype_metadata["clone_count"] += 1
        
        return cloned_vm
        
    def get_status(self) -> ResourceStatus:
        return self.status
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "disk_gb": self.disk_gb,
            "hypervisor": self.hypervisor,
            "network_interface": self.network_interface,
            "host_server": self.host_server,
            "datastore": self.datastore,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OnPremiseDatabase(Database):
    """Implementación concreta de base de datos para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "datacenter-1")
        super().__init__(
            resource_id=f"onprem-db-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-db-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.engine = config.get("engine", "postgresql")  # postgresql, mysql, oracle, sqlserver
        self.version = config.get("version", "13.0")
        self.port = config.get("port", 5432)
        self.host_server = config.get("host_server", "db-server-01.company.local")
        self.data_directory = config.get("data_directory", "/var/lib/postgresql/data")
        self.max_connections = config.get("max_connections", 100)
        
    def backup(self) -> str:
        backup_id = f"backup-{uuid.uuid4().hex[:8]}"
        backup_path = f"/backups/{self.name}/{backup_id}.sql"
        print(f"💾 OnPrem: Creando backup {backup_id} de base de datos {self.name} → {backup_path}")
        return backup_id
        
    def restore(self, backup_id: str) -> None:
        backup_path = f"/backups/{self.name}/{backup_id}.sql"
        print(f"♻️ OnPrem: Restaurando base de datos {self.name} desde {backup_path}")
        
    def scale(self, new_tier: str) -> None:
        print(f"📈 OnPrem: Escalando base de datos {self.name} a tier {new_tier}")
        
    def get_resource_type(self) -> str:
        return "onprem.database"
        
    def get_specs(self) -> Dict[str, Any]:
        return {
            "engine": self.engine,
            "version": self.version,
            "port": self.port,
            "host_server": self.host_server,
            "data_directory": self.data_directory,
            "max_connections": self.max_connections
        }
    
    def clone(self) -> 'OnPremiseDatabase':
        """Clona la base de datos On-Premise con nueva configuración"""
        
        if not self._prepare_for_cloning():
            raise ValueError(f"OnPrem DB {self.id} no puede clonarse en estado {self.status}")
        
        # Crear copia profunda
        cloned_db = copy.deepcopy(self)
        
        # Generar nuevos identificadores únicos
        original_id = self.id
        cloned_db.id = self._generate_clone_id()
        
        # Asignar nuevo puerto (incrementar desde el original)
        cloned_db.port = self.port + random.randint(1, 100)
        
        # Generar nuevo directorio de datos
        timestamp = uuid.uuid4().hex[:6]
        cloned_db.data_directory = f"{self.data_directory}-clone-{timestamp}"
        
        # Asignar nuevo host server (simulado - distribuir carga)
        db_server_num = random.randint(1, 5)
        cloned_db.host_server = f"db-server-{db_server_num:02d}.company.local"
        
        # Actualizar metadatos de clonación
        cloned_db._update_clone_metadata(original_id)
        cloned_db.status = ResourceStatus.CREATING
        
        # Incrementar contador en original
        self._prototype_metadata["clone_count"] += 1
        
        return cloned_db
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "engine": self.engine,
            "version": self.version,
            "port": self.port,
            "host_server": self.host_server,
            "data_directory": self.data_directory,
            "max_connections": self.max_connections,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OnPremiseLoadBalancer(LoadBalancer):
    """Implementación concreta de Load Balancer para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "datacenter-1")
        super().__init__(
            resource_id=f"onprem-lb-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-lb-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.load_balancer_type = config.get("type", "nginx")  # nginx, haproxy, f5, citrix
        self.listen_port = config.get("listen_port", 80)
        self.algorithm = config.get("algorithm", "round_robin")  # round_robin, least_conn, ip_hash
        self.host_server = config.get("host_server", "lb-server-01.company.local")
        self.backend_servers = []
        
    def add_target(self, target_id: str) -> None:
        target_info = {"id": target_id}
        self.backend_servers.append(target_info)
        print(f"➕ OnPrem: Añadiendo backend {target_id} al Load Balancer {self.name}")
        
    def remove_target(self, target_id: str) -> None:
        self.backend_servers = [t for t in self.backend_servers if t["id"] != target_id]
        print(f"➖ OnPrem: Removiendo backend {target_id} del Load Balancer {self.name}")
        
    def configure_health_check(self, config: Dict[str, Any]) -> None:
        check_path = config.get("path", "/health")
        check_interval = config.get("interval", 30)
        print(f"🔍 OnPrem: Configurando health check para Load Balancer {self.name}: {check_path} cada {check_interval}s")
        
    def get_resource_type(self) -> str:
        return "onprem.loadbalancer"
        
    def get_specs(self) -> Dict[str, Any]:
        return {
            "type": self.load_balancer_type,
            "listen_port": self.listen_port,
            "algorithm": self.algorithm,
            "host_server": self.host_server,
            "backend_servers": self.backend_servers
        }
    
    def clone(self) -> 'OnPremiseLoadBalancer':
        """Clona el Load Balancer On-Premise con nueva configuración"""
        
        if not self._prepare_for_cloning():
            raise ValueError(f"OnPrem Load Balancer {self.id} no puede clonarse en estado {self.status}")
        
        # Crear copia profunda
        cloned_lb = copy.deepcopy(self)
        
        # Generar nuevos identificadores únicos
        original_id = self.id
        cloned_lb.id = self._generate_clone_id()
        
        # Limpiar backend servers (se configurarán después del clon)
        cloned_lb.backend_servers = []
        
        # Asignar nuevo puerto de escucha
        cloned_lb.listen_port = self.listen_port + random.randint(1, 1000)
        
        # Asignar nuevo host server
        lb_server_num = random.randint(1, 5)
        cloned_lb.host_server = f"lb-server-{lb_server_num:02d}.company.local"
        
        # Actualizar metadatos de clonación
        cloned_lb._update_clone_metadata(original_id)
        cloned_lb.status = ResourceStatus.CREATING
        
        # Incrementar contador en original
        self._prototype_metadata["clone_count"] += 1
        
        return cloned_lb
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "type": self.load_balancer_type,
            "listen_port": self.listen_port,
            "algorithm": self.algorithm,
            "host_server": self.host_server,
            "backend_servers": self.backend_servers,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class OnPremiseStorage(Storage):
    """Implementación concreta de almacenamiento para infraestructura on-premise"""
    
    def __init__(self, config: Dict[str, Any]):
        region = config.get("region", "datacenter-1")
        super().__init__(
            resource_id=f"onprem-storage-{uuid.uuid4().hex[:8]}",
            name=config.get("name", f"onprem-share-{uuid.uuid4().hex[:6]}"),
            region=region
        )
        self.storage_type = config.get("storage_type", "nfs")  # nfs, smb, iscsi, fc
        self.mount_point = config.get("mount_point", f"/mnt/{self.name}")
        self.capacity_gb = config.get("capacity_gb", 1000)
        self.host_server = config.get("host_server", "storage-server-01.company.local")
        self.protocol_version = config.get("protocol_version", "4.1")
        self.access_permissions = config.get("permissions", "rw")
        
    def create_bucket(self, bucket_name: str) -> None:
        print(f"🪣 OnPrem: Creando share adicional {bucket_name} en {self.storage_type}")
        
    def upload_file(self, file_path: str, key: str) -> None:
        destination_path = f"{self.mount_point}/{key}"
        print(f"⬆️ OnPrem: Copiando {file_path} a {self.storage_type} share → {destination_path}")
        
    def download_file(self, key: str, local_path: str) -> None:
        source_path = f"{self.mount_point}/{key}"
        print(f"⬇️ OnPrem: Descargando {source_path} desde {self.storage_type} share {self.name}")
        
    def get_resource_type(self) -> str:
        return "onprem.storage"
        
    def get_specs(self) -> Dict[str, Any]:
        return {
            "storage_type": self.storage_type,
            "mount_point": self.mount_point,
            "capacity_gb": self.capacity_gb,
            "host_server": self.host_server,
            "protocol_version": self.protocol_version,
            "access_permissions": self.access_permissions
        }
    
    def clone(self) -> 'OnPremiseStorage':
        """Clona el almacenamiento On-Premise con nueva configuración"""
        
        if not self._prepare_for_cloning():
            raise ValueError(f"OnPrem Storage {self.id} no puede clonarse en estado {self.status}")
        
        # Crear copia profunda
        cloned_storage = copy.deepcopy(self)
        
        # Generar nuevos identificadores únicos
        original_id = self.id
        cloned_storage.id = self._generate_clone_id()
        
        # Generar nuevo mount point único
        timestamp = uuid.uuid4().hex[:6]
        cloned_storage.mount_point = f"/mnt/{cloned_storage.name}-clone-{timestamp}"
        
        # Asignar nuevo host server
        storage_server_num = random.randint(1, 5)
        cloned_storage.host_server = f"storage-server-{storage_server_num:02d}.company.local"
        
        # Actualizar metadatos de clonación
        cloned_storage._update_clone_metadata(original_id)
        cloned_storage.status = ResourceStatus.CREATING
        
        # Incrementar contador en original
        self._prototype_metadata["clone_count"] += 1
        
        return cloned_storage
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "storage_type": self.storage_type,
            "mount_point": self.mount_point,
            "capacity_gb": self.capacity_gb,
            "host_server": self.host_server,
            "protocol_version": self.protocol_version,
            "access_permissions": self.access_permissions,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }
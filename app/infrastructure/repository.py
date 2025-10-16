from __future__ import annotations
from typing import List, Dict, Any
from app.domain.schemas import VMDTO
from app.domain.ports import VMRepositoryPort


class VMRepository(VMRepositoryPort):
    """Repositorio en memoria (dict) para simular persistencia sin BD."""

    def __init__(self):
        self._store: Dict[str, VMDTO] = {}
        # Almacén adicional para objetos de productos originales (para Prototype Pattern)
        self._products_store: Dict[str, Any] = {}

    def save(self, vm: VMDTO) -> None:
        # Soportar tanto 'id' como 'resource_id' para compatibilidad con productos de Abstract Factory
        vm_id = getattr(vm, 'id', None) or getattr(vm, 'resource_id', None)
        if not vm_id:
            raise ValueError("El recurso debe tener 'id' o 'resource_id'")
        self._store[vm_id] = vm
    
    def save_product(self, product: Any) -> None:
        """
        Guarda el objeto de producto original (EC2Instance, AzureVM, etc.)
        para permitir la clonación con el patrón Prototype.
        """
        product_id = getattr(product, 'resource_id', None)
        if not product_id:
            raise ValueError("El producto debe tener 'resource_id'")
        self._products_store[product_id] = product

    # Alias explícito usado por prototype_controller para almacenar recursos clonados
    def store_resource(self, resource_id: str, resource: Any) -> None:
        """Guarda cualquier recurso clonable directamente en el almacén de productos."""
        if not resource_id:
            raise ValueError("resource_id es requerido")
        self._products_store[resource_id] = resource

    def get(self, vm_id: str) -> VMDTO:
        # Primero intentar obtener del almacén de productos (objetos originales)
        if vm_id in self._products_store:
            return self._products_store[vm_id]
        # Si no, obtener del almacén de DTOs
        vm = self._store.get(vm_id)
        if not vm:
            raise KeyError("VM not found")
        return vm

    def delete(self, vm_id: str) -> None:
        # Borrar tanto del almacén de DTOs como del de productos
        removed = False
        if vm_id in self._store:
            del self._store[vm_id]
            removed = True
        if vm_id in self._products_store:
            del self._products_store[vm_id]
            removed = True
        if not removed:
            raise KeyError("VM not found")


    def list(self) -> List[VMDTO]:
        return list(self._store.values())

# Instancia global para acceso desde controladores
repository = VMRepository()

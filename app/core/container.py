from app.domain.services import VMService
from app.infrastructure.repository import repository

# Contenedor simple para inyección de dependencias (DIP)
# Usamos la MISMA instancia global de repositorio que utilizan los controladores
_service = VMService(repo=repository)


def get_vm_service() -> VMService:
    return _service

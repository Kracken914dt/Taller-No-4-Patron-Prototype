from fastapi import FastAPI
from app.api.vm_controller import router as vm_router
from app.api.logs_controller import router as logs_router
from app.api.abstract_factory_controller import router as abstract_factory_router
from app.api.prototype_controller import router as prototype_router

app = FastAPI(
    title="VM Infrastructure API - Abstract Factory + Prototype + Builder", 
    version="3.0.0",
    description="""
    API completa de infraestructura cloud que implementa múltiples patrones de diseño:
    
    **🏭 Abstract Factory Pattern**: Creación de familias de recursos por proveedor (AWS, Azure, GCP, Oracle, OnPremise)
    
    **🔨 Builder + Director Pattern**: Construcción parametrizada de VMs por tier (small, medium, large, xlarge)
    
    **📋 Prototype Pattern**: Clonación de recursos existentes para crear nuevas instancias basadas en plantillas
    
    ### Funcionalidades principales:
    - Gestión completa de VMs, Databases, Load Balancers y Storage
    - Soporte para 5 proveedores cloud diferentes
    - Clonación y gestión de prototipos de infraestructura
    - Logs de auditoría y persistencia simulada
    - Validación tipada por proveedor con Pydantic
    """
)

# Rutas principales - Abstract Factory Pattern
app.include_router(abstract_factory_router, prefix="/cloud", tags=["abstract-factory"])

# Rutas de VM (Abstract Factory + Builder Pattern)
app.include_router(vm_router, prefix="/vm", tags=["virtual-machines"])

# Rutas de Prototype Pattern - NUEVA FUNCIONALIDAD
app.include_router(prototype_router, prefix="/api", tags=["prototype-pattern"])

# Rutas de logs
app.include_router(logs_router, prefix="/api", tags=["logs"])

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "version": "3.0.0", 
        "patterns": ["Abstract Factory", "Builder + Director", "Prototype"],
        "features": [
            "Multi-provider cloud resource management",
            "VM building by tiers",
            "Resource prototyping and cloning",
            "Audit logging",
            "Type-safe validation"
        ]
    }
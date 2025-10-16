# 🚀 Guía Rápida - Patrón Prototype

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ **Iniciar el Servidor**
```bash
# Activar entorno virtual (si existe)
.\.venv\Scripts\Activate.ps1

# Instalar dependencias (primera vez)
pip install -r requirements.txt

# Iniciar servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


### 3️⃣ **Acceder a Documentación Interactiva**
Abrir en navegador: http://localhost:8000/docs

---

## 📝 **Ejemplos de Uso Rápido**

### **Escenario 1: Crear y Clonar una VM**

```python
from app.infrastructure.repository import InMemoryRepository
from app.domain.services.prototype_service import PrototypeManager
from app.domain.factory_provider import get_cloud_factory

# 1. Crear VM con Abstract Factory
repository = InMemoryRepository()
aws_factory = get_cloud_factory("aws")

vm_config = {
    "name": "web-server-base",
    "instance_type": "t3.medium",
    "region": "us-east-1"
}

vm = aws_factory.create_virtual_machine("web-server-base", vm_config)
repository.save(vm)

# 2. Registrar como prototipo
prototype_manager = PrototypeManager()
prototype_id = prototype_manager.register_prototype(
    resource=vm,
    name="optimized-web-server",
    description="VM optimizada para servidores web",
    category="vm",
    tags={"environment": "production", "type": "web"}
)

print(f"✅ Prototipo creado: {prototype_id}")

# 3. Clonar el prototipo
cloned_vm = prototype_manager.clone_prototype(
    prototype_id=prototype_id,
    new_name="web-server-prod-01",
    custom_tags={"instance": "01", "deployment": "production"}
)

# 4. Guardar el clon
repository.save(cloned_vm)
print(f"✅ Clon creado: {cloned_vm.id}")
```

---

### **Escenario 2: Scaling Horizontal (Crear 5 instancias)**

```python
# Asumiendo que ya tienes un prototipo registrado
prototype_id = "proto-12345678"

for i in range(1, 6):
    clone = prototype_manager.clone_prototype(
        prototype_id=prototype_id,
        new_name=f"web-server-{i:02d}",
        custom_tags={
            "instance_number": str(i),
            "cluster": "web-tier",
            "auto_scaled": "true"
        }
    )
    repository.save(clone)
    print(f"✅ Instancia {i} creada: {clone.id}")
```

---

### **Escenario 3: Búsqueda de Prototipos**

```python
# Buscar prototipos de VMs de producción
results = prototype_manager.search_prototypes(
    query="web server",
    category="vm",
    tags={"environment": "production"}
)

for proto in results:
    print(f"""
    📋 {proto['name']}
       ID: {proto['id']}
       Tipo: {proto['resource_type']}
       Uso: {proto['usage_count']} veces
       Tags: {proto['tags']}
    """)
```

---

## 🌐 **Uso con API REST**

# 1. Crear infraestructura AWS
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "aws",
       "name": "mi-infraestructura-aws",
       "region": "us-east-1",
       "vm_config": {
         "instance_type": "t3.medium",
         "ami": "ami-0abcdef1234567890",
         "vpc_id": "vpc-12345678"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'

# 2. Usar el resource_id de la VM (por ejemplo: i-3c2f9485) para crear prototipo
curl -X POST "http://localhost:8000/api/prototype/create" \
     -H "Content-Type: application/json" \
     -d '{
       "resource_id": "i-3c2f9485",
       "name": "web-server-optimizado",
       "description": "VM configurada para alto rendimiento",
       "category": "vm",
       "tags": {
         "environment": "production",
         "type": "web-server"
       }
     }'

### **Crear Prototipo**
```bash
curl -X POST "http://localhost:8000/api/prototype/create" \
     -H "Content-Type: application/json" \
     -d '{
       "resource_id": "i-1234567890abcdef0",
       "name": "web-server-optimizado",
       "description": "VM configurada para alto rendimiento",
       "category": "vm",
       "tags": {
         "environment": "production",
         "type": "web-server"
       }
     }'
```

### **Clonar Prototipo**
```bash
curl -X POST "http://localhost:8000/api/prototype/clone/proto-12345678" \
     -H "Content-Type: application/json" \
     -d '{
        "prototype_id": "proto-6ee7b92e" = del prototypo
       "new_name": "web-server-prod-03",
       "custom_tags": {
         "instance": "03",
         "deployment": "production"
       }
     }'
```

### **Buscar Prototipos**
```bash
curl -X POST "http://localhost:8000/api/prototype/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "web",
       "category": "vm",
       "tags": {"environment": "production"}
     }'
```

### **Listar Todos los Prototipos**
```bash
curl "http://localhost:8000/api/prototype/list"
```

### **Obtener Estadísticas**
```bash
curl "http://localhost:8000/api/prototype/stats"
```

### **Ver Categorías Disponibles**
```bash
curl "http://localhost:8000/api/prototype/categories"
```

---

## 🎯 **Flujos de Trabajo Comunes**

### **Workflow 1: Desarrollo → Staging → Producción**

```python
# 1. Crear VM de desarrollo
dev_vm = aws_factory.create_virtual_machine("dev-server", dev_config)
repository.save(dev_vm)

# 2. Probar y optimizar en dev
# ... configuraciones, testing ...

# 3. Registrar como prototipo
proto_id = prototype_manager.register_prototype(
    resource=dev_vm,
    name="app-server-v1.0",
    description="Servidor de aplicación versión 1.0",
    category="vm",
    tags={"version": "1.0", "tested": "true"}
)

# 4. Clonar para staging
staging_vm = prototype_manager.clone_prototype(
    proto_id,
    new_name="staging-server",
    custom_tags={"environment": "staging"}
)
repository.save(staging_vm)

# 5. Clonar para producción (múltiples instancias)
for i in range(1, 4):
    prod_vm = prototype_manager.clone_prototype(
        proto_id,
        new_name=f"prod-server-{i}",
        custom_tags={"environment": "production", "instance": str(i)}
    )
    repository.save(prod_vm)
```

### **Workflow 2: Disaster Recovery**

```python
# 1. Identificar recursos críticos
critical_resources = repository.find_by_tags({"critical": "true"})

# 2. Crear prototipos de DR
for resource in critical_resources:
    dr_proto_id = prototype_manager.register_prototype(
        resource=resource,
        name=f"DR-{resource.name}",
        description=f"DR backup de {resource.name}",
        category=resource.get_resource_type().split('.')[-1],
        tags={"disaster_recovery": "true", "original_id": resource.id}
    )
    print(f"✅ DR Prototype creado: {dr_proto_id}")

# 3. En caso de desastre, clonar rápidamente
def restore_from_dr(prototype_id, region="us-west-2"):
    restored = prototype_manager.clone_prototype(
        prototype_id,
        new_name=f"restored-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        custom_tags={
            "restored_from_dr": "true",
            "restore_date": datetime.now().isoformat(),
            "dr_region": region
        }
    )
    repository.save(restored)
    return restored
```

### **Workflow 3: A/B Testing**

```python
# 1. Crear configuración base
base_vm = aws_factory.create_virtual_machine("app-base", base_config)
repository.save(base_vm)

# 2. Registrar como prototipo
proto_id = prototype_manager.register_prototype(
    resource=base_vm,
    name="app-ab-test-base",
    description="Base para A/B testing",
    category="vm",
    tags={"ab_test": "true"}
)

# 3. Crear variante A
variant_a = prototype_manager.clone_prototype(
    proto_id,
    new_name="app-variant-a",
    custom_tags={
        "variant": "a",
        "feature_flag": "new_ui",
        "traffic_split": "50"
    }
)
repository.save(variant_a)

# 4. Crear variante B
variant_b = prototype_manager.clone_prototype(
    proto_id,
    new_name="app-variant-b",
    custom_tags={
        "variant": "b",
        "feature_flag": "old_ui",
        "traffic_split": "50"
    }
)
repository.save(variant_b)
```

---

## 🔍 **Comandos de Debug**

### **Ver todos los prototipos registrados**
```python
all_protos = prototype_manager.list_prototypes()
for proto in all_protos:
    print(f"- {proto.name} ({proto.category}): {proto.usage_count} usos")
```

### **Ver detalles de un prototipo específico**
```python
proto_info = prototype_manager.get_prototype("proto-12345678")
print(f"""
Prototipo: {proto_info.name}
Categoría: {proto_info.category}
Proveedor: {proto_info.provider}
Tipo: {proto_info.resource_type}
Creado: {proto_info.created_at}
Usos: {proto_info.usage_count}
Tags: {proto_info.tags}
""")
```

### **Ver estadísticas globales**
```python
stats = prototype_manager.get_statistics()
print(f"""
Total de prototipos: {stats['total_prototypes']}
Total de clonaciones: {stats['total_clones']}
Más usado: {stats['most_used']['name']} ({stats['most_used']['count']} veces)

Por categoría:
{json.dumps(stats['by_category'], indent=2)}

Por proveedor:
{json.dumps(stats['by_provider'], indent=2)}
""")
```

### **Verificar logs de auditoría**
```bash
# Ver últimas operaciones de Prototype
cat logs/audit.log | grep prototype | tail -n 20

# Contar clonaciones por día
cat logs/audit.log | grep "clone_prototype" | wc -l
```

---

## 🚨 **Solución de Problemas Comunes**

### **Error: "Recurso no puede clonarse en estado X"**
```python
# Solución: Verificar y cambiar estado
resource.status = ResourceStatus.RUNNING  # o STOPPED, AVAILABLE
clone = resource.clone()
```

### **Error: "Prototipo no encontrado"**
```python
# Solución: Listar prototipos disponibles
available = prototype_manager.list_prototypes()
print([p.id for p in available])
```

### **Error: "ID duplicado"**
```python
# Solución: Los IDs se generan automáticamente de forma única
# No necesitas intervenir, pero puedes verificar:
clone = resource.clone()
print(f"Original ID: {resource.id}")
print(f"Clone ID: {clone.id}")  # Siempre será diferente
```

---

## 📊 **Métricas y Monitoreo**

```python
# Dashboard simple de métricas
def print_prototype_dashboard():
    stats = prototype_manager.get_statistics()
    
    print("=" * 60)
    print("📊 DASHBOARD DE PROTOTIPOS")
    print("=" * 60)
    
    print(f"\n📋 Total de prototipos: {stats['total_prototypes']}")
    print(f"🔄 Total de clonaciones: {stats['total_clones']}")
    
    if stats.get('most_used'):
        print(f"\n🏆 Prototipo más usado:")
        print(f"   {stats['most_used']['name']}")
        print(f"   {stats['most_used']['count']} clonaciones")
    
    print(f"\n📂 Por categoría:")
    for cat, count in stats['by_category'].items():
        print(f"   {cat}: {count}")
    
    print(f"\n☁️ Por proveedor:")
    for prov, count in stats['by_provider'].items():
        print(f"   {prov}: {count}")
    
    print("=" * 60)

# Ejecutar dashboard
print_prototype_dashboard()
```

---

## ⚙️ **Configuración Avanzada**

### **Personalizar comportamiento de clonación**

```python
# En tu clase de producto, puedes personalizar el clone():
class CustomEC2Instance(EC2Instance):
    def clone(self) -> 'CustomEC2Instance':
        # Llamar al clone original
        cloned = super().clone()
        
        # Personalizaciones adicionales
        cloned.custom_property = self.custom_property
        cloned.advanced_config = self.advanced_config.copy()
        
        return cloned
```

### **Agregar validaciones personalizadas**

```python
# Extender CloneableResource con validaciones
class ValidatedResource(CloneableResource):
    def _prepare_for_cloning(self) -> bool:
        # Validación base
        if not super()._prepare_for_cloning():
            return False
        
        # Validaciones personalizadas
        if hasattr(self, 'license_count'):
            if self.license_count >= self.max_licenses:
                print("⚠️ No hay licencias disponibles para clonar")
                return False
        
        return True
```

---

## 🎓 **Recursos Adicionales**

- 📖 **Documentación completa**: `README.md`
- 🔧 **Código fuente**: `app/domain/`
- 🧪 **Ejemplos**: `demo_prototype.py`
- 📊 **Resumen técnico**: `IMPLEMENTATION_SUMMARY.md`
- 🌐 **API Docs**: http://localhost:8000/docs

---

## ✅ **Checklist de Implementación**

- [ ] Servidor FastAPI iniciado
- [ ] Demo ejecutado correctamente
- [ ] API docs accesible
- [ ] Prototipo creado exitosamente
- [ ] Clone funcionando
- [ ] Búsqueda operativa
- [ ] Estadísticas correctas
- [ ] Logs de auditoría generados

¡Todo listo para usar el Patrón Prototype! 🚀

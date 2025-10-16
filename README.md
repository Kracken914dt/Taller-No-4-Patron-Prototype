# VM Infrastructure API - Múltiples Patrones de Diseño (FastAPI)

API completa de infraestructura cloud que implementa **tres patrones de diseño fundamentales** siguiendo principios **SOLID** para gestión integral de infraestructura cloud (VMs, Databases, Load Balancers, Storage) en **5 proveedores** (AWS, Azure, GCP, Oracle, On-Premise), con validación tipada, persistencia simulada y funcionalidades avanzadas de clonación.

## 🏭 **Abstract Factory Pattern** (Base)
Gestión de familias de recursos cloud por proveedor, permitiendo crear recursos compatibles sin acoplar el código a implementaciones específicas.

## 🔨 **Builder + Director Pattern** (Segundo Corte) 
Construcción parametrizada de VMs por "tier" con lógica de negocio centralizada en el Director.

## 📋 **🆕 PROTOTYPE PATTERN (Cuarto Taller)**

### Funcionalidades del Patrón Prototype

El patrón Prototype permite **clonar recursos de infraestructura existentes** para crear nuevas instancias basadas en configuraciones probadas, sin necesidad de recrear desde cero.

#### **Características principales:**

✅ **Clonación inteligente**: Copia completa de recursos con IDs únicos automáticos
✅ **Gestión de prototipos**: Registro, búsqueda y categorización de plantillas
✅ **Metadatos avanzados**: Tracking de clonaciones, uso y procedencia  
✅ **Validación de estados**: Solo clona recursos en estados estables
✅ **Integración completa**: Compatible con Abstract Factory y Builder
✅ **Persistencia**: Los clones se almacenan automáticamente en el repositorio

#### **Clases del Patrón Prototype:**

- `app/domain/abstractions/prototype.py`: Interfaces `Prototype` y `CloneableResource`
- `app/domain/services/prototype_service.py`: `PrototypeManager` (Singleton)
- `app/domain/schemas/prototype.py`: Esquemas Pydantic para requests/responses
- `app/api/prototype_controller.py`: Endpoints REST para gestión de prototipos

#### **Nuevos Endpoints del Patrón Prototype:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/prototype/create` | Crear prototipo desde recurso existente |
| POST | `/api/prototype/clone/{prototype_id}` | Clonar prototipo específico |
| POST | `/api/prototype/search` | Buscar prototipos por criterios |
| GET | `/api/prototype/list` | Listar todos los prototipos |
| GET | `/api/prototype/{prototype_id}` | Obtener detalles de prototipo |
| DELETE | `/api/prototype/{prototype_id}` | Eliminar prototipo |
| GET | `/api/prototype/stats` | Estadísticas de uso |
| GET | `/api/prototype/categories` | Categorías disponibles |
| POST | `/api/prototype/from-resource` | Crear prototipo por tipo de recurso |

#### **Ejemplos de Uso del Patrón Prototype:**

**1. Crear prototipo desde VM existente:**
```json
POST /api/prototype/create
{
  "resource_id": "i-1234567890abcdef0",
  "name": "web-server-optimizado", 
  "description": "VM configurada para servidores web de alto rendimiento",
  "category": "vm",
  "tags": {
    "environment": "production",
    "type": "web-server", 
    "performance": "high"
  }
}
```

**2. Clonar prototipo existente:**
```json
POST /api/prototype/clone/proto-12345678
{
  "prototype_id": "proto-12345678",
  "new_name": "web-server-prod-03",
  "custom_tags": {
    "instance_number": "03",
    "deployment": "production"
  }
}
```

**3. Buscar prototipos por criterios:**
```json
POST /api/prototype/search
{
  "query": "web server",
  "category": "vm", 
  "tags": {
    "environment": "production"
  }
}
```

**4. Listar prototipos por categoría:**
```bash
GET /api/prototype/list?category=vm
```

#### **Flujo típico del Patrón Prototype:**

1. **Crear recurso base** (VM, DB, LB) usando Abstract Factory o Builder
2. **Configurar y optimizar** el recurso según necesidades
3. **Registrar como prototipo** con metadatos descriptivos  
4. **Clonar cuando necesites** instancias similares
5. **Personalizar clones** con nombres y tags específicos
6. **Gestionar prototipos** con búsqueda, estadísticas y categorización

#### **Categorías de Prototipos disponibles:**
- `vm`: Máquinas virtuales
- `database`: Bases de datos  
- `loadbalancer`: Balanceadores de carga
- `storage`: Almacenamiento
- `network`: Componentes de red
- `general`: Uso general

---

## 🔧 **Builder + Director Pattern** (Segundo Corte)

Se añadió el patrón **Builder** con **Director** para parametrizar la construcción de VMs por “tier” (small, medium, large, xlarge) y delegar la creación final al Abstract Factory.

- Builder: parametriza paso a paso la configuración de VM según el proveedor.
- Director: aplica la lógica de negocio (qué CPU/RAM/tamaño asignar) según el tipo de VM (tier).

Clases clave:
- `app/domain/builders/vm_builder.py`: interfaz `VMBuilder` y `Director`.
- `app/domain/builders/vm_builders_concrete.py`: builders por proveedor
  - `AWSVMBuilder`, `AzureVMBuilder`, `GCPVMBuilder`, `OnPremVMBuilder`, `OracleVMBuilder`.
- `app/domain/builders/director.py`: `VMTierDirector` orquesta el flujo (reset → set_name → set_region → set_cpu_ram_by_tier → set_image_defaults → set_network_defaults → build).

Nuevo endpoint:
- POST `/vm/build` → construye una VM usando Builder + Director y la crea con el Abstract Factory.

Request (VMBuildRequest):
```json
{
  "name": "web-01",
  "provider": "aws|azure|gcp|onpremise|oracle",
  "region": "<region>",
  "tier": "small|medium|large|xlarge",
  "profile": "general|memory|compute",               // opcional, default: general
  "key_pair_name": "default-key",                    // opcional
  "firewall_rules": ["HTTP", "SSH"],                 // opcional
  "public_ip": true,                                   // opcional
  "memory_optimization": true,                         // opcional
  "disk_optimization": false,                          // opcional
  "storage_iops": 3000                                 // opcional (didáctico)
}
```

Notas importantes:
- Para este endpoint el proveedor on-premise se expresa como `onpremise` (coincide con `ProviderEnum`).
- El Director decide el “tier” y opcionalmente el “profile” (general/memory/compute), y cada Builder lo traduce al campo/tamaño del proveedor:
  - AWS → `instance_type` (p. ej., t3.micro)
  - Azure → `vm_size` (p. ej., Standard_B1s)
  - GCP → `machine_type` (p. ej., e2-micro)
  - OnPrem → `cpu`, `ram_gb` numéricos
  - Oracle → `compute_shape` (p. ej., VM.Standard2.1)
  Además, el Director agrega al config `vcpus` y `memory_gb` como anotaciones didácticas para reflejar los obligatorios del PDF.



Ejemplos rápidos (PowerShell/curl):

AWS (small, con opcionales)
```powershell
curl -X POST "http://localhost:8000/vm/build" `
     -H "Content-Type: application/json" `
     -d '{
           "name": "aws-web-01",
           "provider": "aws",
           "region": "us-east-1",
           "tier": "small",
           "key_pair_name": "default-key",
           "firewall_rules": ["HTTP", "SSH"],
           "public_ip": true,
           "memory_optimization": true,
           "disk_optimization": false
         }'
```

Azure (medium)
```powershell
curl -X POST "http://localhost:8000/vm/build" `
     -H "Content-Type: application/json" `
     -d '{
           "name": "az-app-01",
           "provider": "azure",
           "region": "eastus",
           "tier": "medium",
           "profile": "general",
           "firewall_rules": ["HTTP", "SSH"],
           "public_ip": true
         }'
```

On-Premise (large)
```powershell
curl -X POST "http://localhost:8000/vm/build" `
     -H "Content-Type: application/json" `
     -d '{
           "name": "onprem-01",
           "provider": "onpremise",
           "region": "datacenter-1",
           "tier": "large"
         }'
```

GCP (xlarge)
```powershell
curl -X POST "http://localhost:8000/vm/build" `
     -H "Content-Type: application/json" `
     -d '{
           "name": "gcp-svc-01",
           "provider": "gcp",
           "region": "us-central1",
           "tier": "xlarge",
           "profile": "compute"
         }'
```

Oracle (medium)
```powershell
curl -X POST "http://localhost:8000/vm/build" `
     -H "Content-Type: application/json" `
     -d '{
           "name": "oci-app-01",
           "provider": "oracle",
           "region": "us-ashburn-1",
           "tier": "medium",
           "profile": "general",
           "public_ip": true
         }'
```

Respuesta esperada (`VMResponse`):
```json
{
  "success": true,
  "vm": {
    "id": "<resource_id>",
    "name": "...",
    "provider": "aws|azure|gcp|onpremise|oracle",
    "status": "creating|running|...",
    "specs": { "...config generada por el builder..." }
  }
}
```

Logs de auditoría: `logs/audit.log` (JSON por línea).

#### Cumplimiento del PDF (obligatorios/opcionales)

- Obligatorios (Builder/Director):
  - provider, region, tier → requeridos en `VMBuildRequest`.
  - vcpus, memoryGB → anotados en el config como `vcpus` y `memory_gb` según el tier.
- Opcionales soportados por `VMBuildRequest` y propagados a factories/productos:
  - `key_pair_name` (AWS → `key_pair`), `firewall_rules` (AWS → `security_groups`, Azure → `network_security_group` simbólico), `public_ip` (marca y simula asignación), `memory_optimization`, `disk_optimization`, `storage_iops` (didáctico).
  - `profile` (general|memory|compute) para reflejar familias del PDF.

## ✅ **IMPLEMENTACIÓN COMPLETA - ABSTRACT FACTORY**

### 🏭 **5 Proveedores Completamente Implementados**

- ☁️ **AWS**: EC2, RDS, ALB, S3
- ☁️ **Azure**: VMs, SQL Database, Load Balancer, Blob Storage
- ☁️ **GCP**: Compute Engine, Cloud SQL, Load Balancing, Cloud Storage
- ☁️ **Oracle**: Compute, Autonomous Database, Load Balancer, Object Storage
- 🏢 **OnPremise**: VMware/Hyper-V, PostgreSQL/MySQL, Nginx/HAProxy, NFS/SMB

## 🏗️ Patrón Abstract Factory Implementado

Esta API implementa el patrón **Abstract Factory** que permite crear familias de productos relacionados (infraestructura cloud) sin especificar sus clases concretas. Cada proveedor cloud tiene su propia factory que crea productos compatibles entre sí.

## 🚀 Endpoints principales

### 🔥 **Abstract Factory Pattern** (Implementación Principal)

- **POST** `/cloud/infrastructure/create` - Crea infraestructura completa por proveedor
- **GET** `/cloud/providers` - Lista proveedores cloud disponibles
- **GET** `/health` - Estado del servicio y patrón implementado

### 🧱 Builder + Director (Nuevo)

- **POST** `/vm/build` - Construye una VM con Builder+Director (tier) y la crea con Abstract Factory

### 🏗️ **Legacy - Factory Method Pattern** (VMs únicamente)

- **POST** `/vm/create` - Crea una VM usando Factory Method
- **PUT** `/vm/{id}` - Actualiza especificaciones de VM
- **DELETE** `/vm/{id}` - Elimina una VM
- **POST** `/vm/{id}/action` - Ejecuta acción: start|stop|restart
- **GET** `/vm/{id}` - Consulta una VM específica
- **GET** `/vm` - Lista todas las VMs
- **GET** `/api/logs` - Consulta logs de auditoría

## 🏛️ Arquitectura del Proyecto

### 🏭 **Abstract Factory Pattern** (Implementación Principal)

- **`app/domain/abstractions/`**: Interfaces abstractas para productos y factories
  - `factory.py`: CloudAbstractFactory, CloudResourceManager
  - `products.py`: VirtualMachine, Database, LoadBalancer, Storage
- **`app/domain/products/`**: Implementaciones concretas de productos cloud
  - `aws_products.py`: EC2Instance, RDSDatabase, ApplicationLoadBalancer, S3Storage
  - `azure_products.py`: AzureVM, SQLDatabase, AzureLoadBalancer, BlobStorage
  - `gcp_products.py`: ComputeEngine, CloudSQL, GCPLoadBalancer, CloudStorage
  - `oracle_products.py`: OracleCompute, AutonomousDatabase, OracleLoadBalancer, ObjectStorage
  - `onprem_products.py`: OnPremVM, OnPremDatabase, OnPremLoadBalancer, OnPremStorage
- **`app/domain/factories_concrete/`**: Factories concretas por proveedor
  - `aws_factory.py`, `azure_factory.py`, `gcp_factory.py`, `oracle_factory.py`, `onprem_factory.py`
- **`app/domain/factory_provider.py`**: Provider pattern para obtener Abstract Factories
- **`app/api/abstract_factory_controller.py`**: Controlador REST para Abstract Factory

### 🔧 **Legacy Factory Method** (Mantenido para compatibilidad)

- **`app/domain/factories/`**: Implementación original del patrón Factory Method para VMs
- **`app/api/vm_controller.py`**: Controlador REST para Factory Method

### 🏗️ **Infraestructura Core**

- **`app/main.py`**: FastAPI app con endpoints para ambos patrones
- **`app/domain/schemas/`**: Validación tipada con Pydantic por proveedor
- **`app/domain/services/`**: Lógica de negocio (VM service, Log service)
- **`app/infrastructure/`**: Repositorio en memoria y logger de auditoría
- **`app/core/`**: Inyección de dependencias

## 🚀 Ejecutar

1. Instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Iniciar servidor

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Documentación interactiva

http://localhost:8000/docs

```

### 🌐 Documentación interactiva:

Una vez iniciado el servidor, visita:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### ✅ **Resultados esperados**:

- ✅ 5 proveedores funcionando: AWS, Azure, GCP, Oracle, OnPremise
- ✅ 4 tipos de recursos por proveedor: VM, Database, LoadBalancer, Storage
- ✅ Principios SOLID completamente implementados
- ✅ Patrón Abstract Factory completamente extensible
- ✅ Validación tipada por proveedor con Pydantic
- ✅ Logs de auditoría en formato JSON
- ✅ Persistencia simulada en memoria

### 🧪 Probar rápidamente el Builder + Director

1) Arranca el servidor (ver pasos arriba).
2) Llama al endpoint `/vm/build` con uno de los ejemplos de arriba.
3) Verifica el resultado en `/vm` (lista de VMs) y revisa los logs en `logs/audit.log`.

## 🔥 Ejemplos de Uso - Abstract Factory

## 📘 Referencia Completa de Payload /cloud/infrastructure/create

El endpoint `POST /cloud/infrastructure/create` acepta este modelo base:

```json
{
  "provider": "aws|azure|gcp|oracle|onprem",
  "name": "nombre-base-infra",
  "region": "<region principal>",
  "vm_config": {
    /* requerido siempre (el controlador rellena defaults si faltan) */
  },
  "database_config": {
    /* requerido si include_database=true (defaults por proveedor) */
  },
  "load_balancer_config": {
    /* requerido si include_load_balancer=true (defaults por proveedor) */
  },
  "storage_config": {
    /* requerido si include_storage=true (defaults por proveedor) */
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "usuario"
}
```

El controlador agrega automáticamente parámetros mínimos cuando no se envían, pero si quieres control total o evitar validaciones 400, usa las tablas siguientes.

### ✅ Campos por Proveedor y Recurso

| Proveedor | Recurso                               | Campos Obligatorios                                                               | Campos Opcionales / Defaults Inyectados                             |
| --------- | ------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| AWS       | VM (`vm_config`)                      | `instance_type`, `ami`, `vpc_id`, `region`                                        | `security_groups`, `key_pair`                                       |
| AWS       | Database (`database_config`)          | `engine`, `instance_class`, `allocated_storage`, `region`                         | —                                                                   |
| AWS       | LoadBalancer (`load_balancer_config`) | `vpc_id`, `region`                                                                | `scheme` (por defecto `internet-facing`), `listeners`               |
| AWS       | Storage (`storage_config`)            | `region`                                                                          | `storage_class` (STANDARD), `versioning_enabled`                    |
| Azure     | VM                                    | `vm_size`, `image`, `resource_group`, `region`                                    | `virtual_network`, `network_security_group`                         |
| Azure     | Database                              | `tier`, `server_name`, `resource_group`, `region`                                 | `max_size_gb`                                                       |
| Azure     | LoadBalancer                          | `resource_group`, `region`                                                        | `sku` (Standard), `frontend_ip_configs`                             |
| Azure     | Storage                               | `region`                                                                          | `account_type` (Standard_LRS), `access_tier` (Hot)                  |
| GCP       | VM                                    | `machine_type`                                                                    | `zone`, `project` (el controlador agrega defaults), otros metadatos |
| GCP       | Database                              | `engine`                                                                          | `tier`, `storage_size`, `region` (si aplica)                        |
| GCP       | LoadBalancer                          | _(ninguno estricto)_                                                              | `type` (HTTP(S)), `region`/`global`                                 |
| GCP       | Storage                               | _(ninguno estricto)_                                                              | `storage_class` (STANDARD), `location` (US)                         |
| Oracle    | VM                                    | `compute_shape`, `compartment_id`, `availability_domain`, `subnet_id`, `image_id` | —                                                                   |
| Oracle    | Database                              | `workload_type`, `compartment_id`                                                 | `cpu_count`, `storage_tb`                                           |
| Oracle    | LoadBalancer                          | `compartment_id`                                                                  | `shape` (100Mbps)                                                   |
| Oracle    | Storage                               | `namespace`, `compartment_id`                                                     | `storage_tier` (Standard)                                           |
| OnPrem    | VM                                    | `cpu`, `ram_gb`, `disk_gb`, `nic`                                                 | `hypervisor` (vmware), `host_server`, `datastore`                   |
| OnPrem    | Database                              | `engine`                                                                          | `version`, `port`, `data_directory`                                 |
| OnPrem    | LoadBalancer                          | _(ninguno estricto)_                                                              | `type` (nginx), `algorithm` (round_robin), `listen_port`            |
| OnPrem    | Storage                               | `storage_type`                                                                    | `capacity_gb` (100), `protocol`, `mount_point`                      |

Notas:

1. Para **Azure**, si envías regiones abreviadas como `East`, el controlador intentará normalizar a `eastus`.
2. Para **GCP**, la validación estricta recae en `machine_type` y `engine` / `storage_class` según recurso.
3. Para **Oracle**, si falta cualquiera de los campos obligatorios en VM se retorna 400.
4. Para **OnPrem**, se validan mínimos de recursos (cpu>=1, ram_gb>=1, disk_gb>=10).

### 🔄 Defaults que el controlador rellena si faltan

| Proveedor          | Campo                   | Valor por Defecto                  |
| ------------------ | ----------------------- | ---------------------------------- |
| AWS                | `instance_type`         | `t2.micro`                         |
| AWS                | `ami`                   | `ami-0abcdef1234567890`            |
| AWS                | `vpc_id`                | `vpc-12345678`                     |
| Azure              | `vm_size`               | `Standard_B1s`                     |
| Azure              | `resource_group`        | `rg-default`                       |
| Azure              | `image`                 | `Ubuntu 20.04 LTS`                 |
| GCP                | `machine_type`          | `e2-micro` (si no enviado)         |
| GCP                | `zone`                  | `us-central1-a`                    |
| GCP                | `project`               | `demo-project`                     |
| Oracle             | `compute_shape`         | `VM.Standard2.1`                   |
| Oracle             | `compartment_id`        | `ocid.compartment.demo`            |
| Oracle             | `availability_domain`   | `AD-1`                             |
| OnPrem             | `cpu`                   | `2`                                |
| OnPrem             | `ram_gb`                | `4`                                |
| OnPrem             | `disk_gb`               | `50`                               |
| Storage (genérico) | `storage_type` (onprem) | `gp3` o `standard` según proveedor |

---

### 🧩 Ejemplos de payload COMPLETO por proveedor (todos los recursos)

#### AWS (completo)

```json
{
  "provider": "aws",
  "name": "infra-aws",
  "region": "us-east-1",
  "vm_config": {
    "instance_type": "t3.medium",
    "ami": "ami-0abcdef1234567890",
    "vpc_id": "vpc-12345678",
    "security_groups": ["sg-web"],
    "key_pair": "my-key"
  },
  "database_config": {
    "engine": "mysql",
    "instance_class": "db.t3.micro",
    "allocated_storage": 20,
    "region": "us-east-1"
  },
  "load_balancer_config": {
    "vpc_id": "vpc-12345678",
    "region": "us-east-1",
    "scheme": "internet-facing"
  },
  "storage_config": {
    "region": "us-east-1",
    "storage_class": "STANDARD",
    "versioning_enabled": true
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### Azure (completo)

```json
{
  "provider": "azure",
  "name": "infra-azure",
  "region": "westus",
  "vm_config": {
    "vm_size": "Standard_B2s",
    "image": "Ubuntu 20.04 LTS",
    "resource_group": "rg-apps",
    "virtual_network": "vnet-apps",
    "network_security_group": "nsg-web"
  },
  "database_config": {
    "tier": "Basic",
    "server_name": "app-sqlsrv",
    "resource_group": "rg-apps",
    "region": "westus",
    "max_size_gb": 32
  },
  "load_balancer_config": {
    "resource_group": "rg-apps",
    "region": "westus",
    "sku": "Standard"
  },
  "storage_config": {
    "region": "westus",
    "account_type": "Standard_LRS",
    "access_tier": "Hot"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### GCP (completo)

```json
{
  "provider": "gcp",
  "name": "infra-gcp",
  "region": "us-central1",
  "vm_config": {
    "machine_type": "e2-medium",
    "zone": "us-central1-a",
    "project": "demo-project"
  },
  "database_config": {
    "engine": "postgres",
    "tier": "db-f1-micro",
    "region": "us-central1"
  },
  "load_balancer_config": {
    "type": "HTTP(S)",
    "region": "us-central1"
  },
  "storage_config": {
    "storage_class": "STANDARD",
    "location": "US"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### Oracle Cloud (completo)

```json
{
  "provider": "oracle",
  "name": "infra-oracle",
  "region": "us-ashburn-1",
  "vm_config": {
    "compute_shape": "VM.Standard2.1",
    "compartment_id": "ocid1.compartment.oc1..xxxxx",
    "availability_domain": "AD-1",
    "subnet_id": "ocid1.subnet.oc1..xxxxx",
    "image_id": "ocid1.image.oc1..xxxxx"
  },
  "database_config": {
    "workload_type": "OLTP",
    "compartment_id": "ocid1.compartment.oc1..xxxxx"
  },
  "load_balancer_config": {
    "compartment_id": "ocid1.compartment.oc1..xxxxx",
    "shape": "100Mbps"
  },
  "storage_config": {
    "namespace": "mytenantns",
    "compartment_id": "ocid1.compartment.oc1..xxxxx",
    "storage_tier": "Standard"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

#### On-Premise (completo)

```json
{
  "provider": "onprem",
  "name": "infra-onprem",
  "region": "datacenter-1",
  "vm_config": {
    "cpu": 4,
    "ram_gb": 8,
    "disk_gb": 120,
    "nic": "eth0",
    "hypervisor": "vmware",
    "host_server": "esxi-01",
    "datastore": "ds-main"
  },
  "database_config": {
    "engine": "postgresql",
    "version": "14",
    "port": 5432,
    "data_directory": "/data/postgres"
  },
  "load_balancer_config": {
    "type": "nginx",
    "algorithm": "round_robin",
    "listen_port": 80
  },
  "storage_config": {
    "storage_type": "nfs",
    "capacity_gb": 500,
    "protocol": "nfs",
    "mount_point": "/mnt/files"
  },
  "include_database": true,
  "include_load_balancer": true,
  "include_storage": true,
  "requested_by": "admin"
}
```

---

### 🩺 1. Verificar estado del servicio

```bash
curl -X GET "http://localhost:8000/health"
```

**Respuesta esperada:**

```json
{
  "status": "ok",
  "version": "2.0.0",
  "pattern": "Abstract Factory"
}
```

### 🏭 2. Listar proveedores disponibles

```bash
curl -X GET "http://localhost:8000/cloud/providers"
```

**Respuesta esperada:**

```json
{
  "supported_providers": ["aws", "azure", "gcp", "oracle", "onprem"],
  "total": 5,
  "description": "List of cloud providers supported by the Abstract Factory"
}
```

### ☁️ 3. Crear infraestructura AWS completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "aws",
       "name": "mi-infraestructura-aws",
       "region": "us-east-1",
       "vm_config": {
         "instance_type": "t3.medium",
         "ami": "ami-0abcdef123456",
         "key_pair": "my-key"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

**Respuesta esperada:**

```json
{
  "success": true,
  "message": "Infraestructura 'mi-infraestructura-aws' creada exitosamente usando AWS",
  "provider": "aws",
  "resources_created": 4,
  "infrastructure": {
    "virtual_machine": {
      "name": "mi-infraestructura-aws-vm",
      "resource_id": "i-1234567890abcdef0",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::EC2::Instance"
    },
    "database": {
      "name": "mi-infraestructura-aws-db",
      "resource_id": "db-abcdef123456789",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::RDS::DBInstance"
    },
    "load_balancer": {
      "name": "mi-infraestructura-aws-lb",
      "resource_id": "alb-123456789abcdef0",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::ElasticLoadBalancingV2::LoadBalancer"
    },
    "storage": {
      "name": "mi-infraestructura-aws-storage",
      "resource_id": "s3-bucket-789abcdef",
      "region": "us-east-1",
      "status": "creating",
      "type": "AWS::S3::Bucket"
    }
  }
}
```

### 🔷 4. Crear infraestructura Azure completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "azure",
       "name": "mi-infraestructura-azure",
       "region": "westus",
       "vm_config": {
         "vm_size": "Standard_B2s",
         "image": "Ubuntu 20.04 LTS",
         "admin_username": "azureuser"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

### 🟡 5. Crear infraestructura GCP completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
        "provider": "onprem",
        "name": "mi-infraestructura-onprem",
        "region": "datacenter-1",
        "vm_config": {
          "cpu": 4,
          "ram_gb": 8,
          "disk_gb": 100,
          "nic": "eth0",
          "hypervisor": "vmware"
        },
        "include_database": true,
        "include_load_balancer": true,
        "include_storage": true
      }'
```

### 🔴 6. Crear infraestructura Oracle Cloud completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "oracle",
       "name": "mi-infraestructura-oracle",
       "region": "us-ashburn-1",
       "vm_config": {
         "compute_shape": "VM.Standard2.1",
         "compartment_id": "ocid1.compartment.demo",
         "availability_domain": "AD-1"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

### 🏢 7. Crear infraestructura On-Premise completa

```bash
curl -X POST "http://localhost:8000/cloud/infrastructure/create" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "onprem",
       "name": "mi-infraestructura-onprem",
       "region": "datacenter-1",
       "vm_config": {
         "cpu": 4,
         "ram_gb": 8,
         "disk_gb": 100,
         "nic": "eth0"
       },
       "include_database": true,
       "include_load_balancer": true,
       "include_storage": true
     }'
```

### 📊 8. Consultar logs de auditoría

```bash
curl -X GET "http://localhost:8000/api/logs"
```

## 🏗️ Requests de creación tipados por proveedor (Legacy VM Factory)

La validación es estricta según `provider`. El campo `params` cambia de forma y es validado automáticamente por Pydantic.

- AWS

```json
curl -X POST "http://localhost:8000/vm/create" `
     -H "accept: application/json" `
     -H "Content-Type: application/json" `
     -d '{
           "name": "test-vm-01",
           "requested_by": "system",
           "provider": "aws",
           "params": {
             "instance_type": "t2.micro",
             "region": "us-east-1",
             "vpc_id": "vpc-12345678",
             "ami": "ami-0abcdef1234567890"
           }
         }'
```

- Azure

```json
{
  "name": "mi-vm-azure",
  "requested_by": "alumno",
  "provider": "azure",
  "params": {
    "vm_size": "Standard_B1s",
    "resource_group": "rg1",
    "image": "UbuntuLTS",
    "region": "eastus"
  }
}
```

- GCP

```json
{
  "provider": "gcp",
  "name": "mi-vm-gcp",
  "params": {
    "machine_type": "e2-micro",
    "zone": "us-central1-a",
    "base_disk": "pd-standard",
    "project": "demo-proj"
  },
  "requested_by": "alumno"
}
```

- On-Premise

```json
{
  "provider": "onpremise",
  "name": "mi-vm-onprem",
  "params": { "cpu": 4, "ram_gb": 8, "disk_gb": 50, "nic": "eth0" },
  "requested_by": "alumno"
}
```

```json
{
  "provider": "oracle",
  "name": "mi-vm-oracle",
  "params": {
    "compute_shape": "VM.Standard2.1",
    "compartment_id": "ocid1.compartment...",
    "availability_domain": "AD-1",
    "subnet_id": "ocid1.subnet...",
    "image_id": "ocid1.image..."
  },
  "requested_by": "alumno"
}
```

## Diseño y arquitectura

- Patrón: Factory Method
  - Abstracción: `app/domain/factories/base.py` (`VirtualMachineFactory`)
  - Implementaciones: `aws.py`, `azure.py`, `gcp.py`, `onprem.py`
  - Resolución: `app/domain/factories/__init__.py#get_factory(provider)`
- Validación de entrada (DTOs):
  - `app/domain/schemas/common.py`: tipos comunes (ProviderEnum, VMDTO, etc.)
  - `app/domain/schemas/{aws,azure,gcp,onpremise}.py`: params por proveedor
  - `app/domain/schemas/create_requests.py`: `VMCreateRequest` (Union discriminado por `provider`)
- Servicios y puertos:
  - Servicio: `app/domain/services.py` (orquesta casos de uso)
  - Puerto de repo (DIP): `app/domain/ports.py` (`VMRepositoryPort`)
  - Implementación repo in-memory: `app/infrastructure/repository.py`
- API/Controller: `app/api/vm_controller.py`
- App FastAPI: `app/main.py`
- Logs: `app/infrastructure/logger.py` → `Backend/logs/audit.log`

## 🎯 Principios SOLID Implementados

### 🔸 **S - Single Responsibility Principle (SRP)**

- Cada clase tiene una única responsabilidad:
  - **Productos**: Solo conocen sus propias operaciones (EC2Instance, RDSDatabase, etc.)
  - **Factories**: Solo crean productos de su proveedor específico
  - **Controllers**: Solo manejan HTTP requests/responses
  - **Services**: Solo lógica de negocio

### 🔸 **O - Open/Closed Principle (OCP)**

- **Abierto para extensión**: Agregar nuevos proveedores solo requiere:
  1. Crear nuevos productos en `app/domain/products/{nuevo}_products.py`
  2. Crear nueva factory en `app/domain/factories_concrete/{nuevo}_factory.py`
  3. Registrar en `factory_provider.py`
- **Cerrado para modificación**: No se modifica código existente

### 🔸 **L - Liskov Substitution Principle (LSP)**

- Todas las factories implementan `CloudAbstractFactory` y son intercambiables
- Todos los productos del mismo tipo (VM, Database, etc.) son intercambiables
- El cliente puede usar cualquier proveedor sin cambiar código

### 🔸 **I - Interface Segregation Principle (ISP)**

- Interfaces específicas y cohesivas:
  - `VirtualMachine`: solo operaciones de VM (start, stop, get_specs)
  - `Database`: solo operaciones de DB (backup, restore, get_connection)
  - `LoadBalancer`: solo operaciones de LB (add_target, remove_target)
  - `Storage`: solo operaciones de Storage (upload, download, list_objects)

### 🔸 **D - Dependency Inversion Principle (DIP)**

- **Abstract Factory** depende de abstracciones (`CloudAbstractFactory`)
- **Controllers** dependen de servicios (abstracción), no implementaciones
- **Services** dependen de puertos/interfaces, no de repositorios concretos
- **Productos** no dependen de implementaciones específicas de otros productos

## Persistencia y estado

- Sin BD: persistencia simulada en memoria (dict) en `app/infrastructure/repository.py`.
- Stateless: la API no guarda estado de sesión; el repositorio in-memory simula almacenamiento volátil.

## Acciones y estados de VM

- `POST /vm/{id}/action` admite `start | stop | restart` y actualiza `status` a `running` o `stopped`.

## Logging de auditoría

- Formato JSON por línea con: timestamp, actor, acción, vm_id, provider, success, details.
- No se registran credenciales ni parámetros sensibles.
- Archivo: `Backend/logs/audit.log`.

## 🔧 Extender con un nuevo proveedor

### Para Abstract Factory (Recomendado):

1. **Crear productos concretos**: `app/domain/products/{nuevo}_products.py`

   ```python
   class NuevoVM(VirtualMachine):
       def start(self): # implementar
       def stop(self): # implementar
       def get_specs(self): # implementar
   ```

2. **Crear factory concreta**: `app/domain/factories_concrete/{nuevo}_factory.py`

   ```python
   class NuevoCloudFactory(CloudAbstractFactory):
       def create_virtual_machine(self, name, config): # implementar
       def create_database(self, name, config): # implementar
   ```

3. **Registrar en provider**: `app/domain/factory_provider.py`

   ```python
   class CloudProvider(str, Enum):
       NUEVO = "nuevo"

   FACTORY_REGISTRY = {
       CloudProvider.NUEVO: NuevoCloudFactory,
   }
   ```

### Para Factory Method (Legacy - solo VMs):

1. Crear `app/domain/schemas/<nuevo>.py` con los params del proveedor.
2. Añadir su variante en `create_requests.py`.
3. Implementar `VirtualMachineFactory` en `app/domain/factories/<nuevo>.py`.
4. Registrar en `get_factory` (`app/domain/factories/__init__.py`).

## 📈 Beneficios del Abstract Factory vs Factory Method

| Aspecto           | Factory Method (Legacy)           | Abstract Factory (Actual)                     |
| ----------------- | --------------------------------- | --------------------------------------------- |
| **Productos**     | Solo VMs                          | VMs + Databases + Load Balancers + Storage    |
| **Consistencia**  | N/A                               | Productos del mismo proveedor trabajan juntos |
| **Escalabilidad** | Limitada                          | Alta - fácil añadir productos y proveedores   |
| **Mantenimiento** | Complejo para múltiples productos | Simple y organizado                           |
| **Testing**       | Difícil mockear                   | Fácil mockear factories completas             |

---

## 🧬 **IMPLEMENTACIÓN TÉCNICA - PATRÓN PROTOTYPE**

### 🏗️ **Arquitectura del Patrón Prototype**

El patrón Prototype permite **clonar objetos existentes** sin acoplar el código a sus clases concretas. En nuestra implementación, cualquier recurso cloud puede convertirse en **prototipo reutilizable** para crear nuevas instancias.

### 📁 **Estructura de Archivos del Prototype**

```
app/domain/
├── abstractions/
│   └── prototype.py          # Interfaces Prototype y CloneableResource
├── services/
│   └── prototype_service.py  # PrototypeManager (Singleton)
├── schemas/
│   └── prototype.py          # Pydantic schemas para requests/responses
└── products/
    ├── aws_products.py       # Clone methods para productos AWS
    ├── azure_products.py     # Clone methods para productos Azure
    ├── gcp_products.py       # Clone methods para productos GCP (pendiente)
    ├── oracle_products.py    # Clone methods para productos Oracle (pendiente)
    └── onprem_products.py    # Clone methods para productos OnPrem (pendiente)

app/api/
└── prototype_controller.py   # REST endpoints para Prototype

demo_prototype.py             # Script de demostración completa
```

### 🔧 **Implementación Detallada**

#### **1. Interface Prototype (`app/domain/abstractions/prototype.py`)**

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime

class Prototype(ABC):
    """Interface del patrón Prototype"""
    
    @abstractmethod
    def clone(self) -> 'Prototype':
        """Crea una copia exacta del objeto actual"""
        pass

class CloneableResource(Prototype):
    """Base class que todos los recursos cloneables deben heredar"""
    
    def __init__(self):
        super().__init__()
        self._prototype_metadata = {
            "original_id": None,
            "clone_count": 0,
            "created_at": datetime.now(),
            "cloned_at": None,
            "is_prototype": False,
            "prototype_name": None,
            "clone_history": []
        }
    
    def _prepare_for_cloning(self) -> bool:
        """Valida si el recurso puede ser clonado"""
        return hasattr(self, 'status') and self.status in ['running', 'stopped', 'available']
    
    def _generate_clone_id(self) -> str:
        """Genera un nuevo ID único para el clon"""
        return str(uuid4())
    
    def _update_clone_metadata(self, original_id: str, clone_name: Optional[str] = None):
        """Actualiza metadatos de clonación"""
        self._prototype_metadata.update({
            "original_id": original_id,
            "cloned_at": datetime.now(),
            "clone_history": [original_id]
        })
        if clone_name:
            self.name = clone_name
```

#### **2. PrototypeManager - Singleton (`app/domain/services/prototype_service.py`)**

```python
class PrototypeManager:
    """Gestor centralizado de prototipos (Singleton pattern)"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._prototypes: Dict[str, PrototypeInfo] = {}
        self._categories: Dict[str, List[str]] = {
            "vm": [], "database": [], "loadbalancer": [], 
            "storage": [], "network": [], "general": []
        }
        self._initialized = True
    
    def register_prototype(self, resource: CloneableResource, 
                          name: str, description: str = "", 
                          category: str = "general", 
                          tags: Dict[str, Any] = None) -> str:
        """Registra un recurso como prototipo"""
        
        if not resource._prepare_for_cloning():
            raise ValueError(f"Recurso {resource.id} no está en estado válido para clonación")
        
        prototype_id = f"proto-{uuid4().hex[:8]}"
        
        prototype_info = PrototypeInfo(
            id=prototype_id,
            name=name,
            description=description,
            category=category,
            resource_type=type(resource).__name__,
            provider=getattr(resource, 'provider', 'unknown'),
            original_resource=resource,
            tags=tags or {},
            created_at=datetime.now(),
            usage_count=0,
            last_used=None
        )
        
        self._prototypes[prototype_id] = prototype_info
        self._categories[category].append(prototype_id)
        
        # Marcar recurso como prototipo
        resource._prototype_metadata.update({
            "is_prototype": True,
            "prototype_name": name,
            "prototype_id": prototype_id
        })
        
        return prototype_id
```

#### **3. Implementación de Clone en Productos**

**Ejemplo AWS EC2Instance:**

```python
class EC2Instance(CloudResource):
    def clone(self) -> 'EC2Instance':
        """Clona la instancia EC2 con nueva configuración"""
        
        if not self._prepare_for_cloning():
            raise ValueError(f"EC2 {self.id} no puede clonarse en estado {self.status}")
        
        # Crear copia profunda
        cloned_instance = copy.deepcopy(self)
        
        # Generar nuevos identificadores únicos
        original_id = self.id
        cloned_instance.id = self._generate_clone_id()
        cloned_instance.instance_id = f"i-{uuid4().hex[:17]}"
        
        # Generar nueva IP privada en el mismo rango
        if hasattr(self, 'private_ip') and self.private_ip:
            base_ip = ".".join(self.private_ip.split('.')[:-1])
            new_last_octet = random.randint(10, 254)
            cloned_instance.private_ip = f"{base_ip}.{new_last_octet}"
        
        # Limpiar IP pública (se asignará nueva si es necesaria)
        cloned_instance.public_ip = None
        
        # Actualizar metadatos de clonación
        cloned_instance._update_clone_metadata(original_id)
        cloned_instance.status = "creating"
        
        # Incrementar contador en original
        self._prototype_metadata["clone_count"] += 1
        
        return cloned_instance
```

### 🔄 **Flujo de Clonación Completo**

#### **1. Creación de Prototipo:**
```python
# 1. Usuario crea VM normal con Abstract Factory
vm = await cloud_service.create_vm("aws", "web-server-base", vm_config)

# 2. Registra VM como prototipo
prototype_id = prototype_manager.register_prototype(
    resource=vm,
    name="web-server-optimizado",
    description="VM configurada para servidores web de alto rendimiento",
    category="vm",
    tags={"environment": "production", "type": "web-server"}
)
```

#### **2. Clonación de Prototipo:**
```python
# 1. Obtener prototipo
prototype_info = prototype_manager.get_prototype(prototype_id)

# 2. Clonar recurso
cloned_vm = prototype_info.original_resource.clone()

# 3. Personalizar clon
cloned_vm.name = "web-server-prod-03"
cloned_vm.tags.update({"instance": "03", "deployment": "production"})

# 4. Persistir en repositorio
repository.save(cloned_vm)

# 5. Actualizar estadísticas de uso
prototype_manager.increment_usage(prototype_id)
```

### 📊 **Integración con Patrones Existentes**

#### **Compatibilidad con Abstract Factory:**
- Los productos creados por Abstract Factory automáticamente heredan capacidades de clonación
- PrototypeManager puede registrar cualquier producto cloud como prototipo
- Los clones se integran seamlessly con el sistema de repositorio existente

#### **Compatibilidad con Builder + Director:**
- Las VMs construidas con Builder pueden convertirse en prototipos
- Los prototipos mantienen la configuración del tier original
- Los clones heredan las optimizaciones aplicadas por el Director

### 🎯 **Beneficios del Patrón Prototype Implementado**

| Beneficio | Descripción | Implementación |
|-----------|-------------|----------------|
| **Performance** | Evita recreación costosa desde cero | Clone via `copy.deepcopy()` + metadatos |
| **Consistencia** | Garantiza configuraciones probadas | Validación de estados antes de clonación |
| **Reutilización** | Templates para casos de uso comunes | Sistema de categorías y tags |
| **Trazabilidad** | Historial de clonaciones y uso | Metadatos completos en cada recurso |
| **Flexibilidad** | Personalización post-clonación | Tags personalizados, nombres únicos |
| **Escalabilidad** | Creación masiva de instancias similares | API RESTful + PrototypeManager |

### 🧪 **Casos de Uso Reales**

#### **1. Scaling Horizontal:**
```bash
# Crear 5 instancias idénticas de web server
for i in {1..5}; do
  curl -X POST "/api/prototype/clone/proto-webserver" \
       -d '{"new_name": "web-'$i'", "custom_tags": {"instance": "'$i'"}}'
done
```

#### **2. Ambientes por Stages:**
```bash
# Clonar configuración de producción para staging
curl -X POST "/api/prototype/clone/proto-prod-config" \
     -d '{"new_name": "staging-env", "custom_tags": {"environment": "staging"}}'
```

#### **3. Disaster Recovery:**
```bash
# Clonar infraestructura crítica como backup
curl -X POST "/api/prototype/clone/proto-critical-db" \
     -d '{"new_name": "dr-backup", "custom_tags": {"purpose": "disaster-recovery"}}'
```

### 🔍 **Demo Script Completo**

Ejecuta `python demo_prototype.py` para ver una demostración completa que incluye:

1. ✅ Creación de recursos con Abstract Factory
2. ✅ Registro como prototipos con metadatos
3. ✅ Clonación con personalización
4. ✅ Búsqueda y filtrado de prototipos
5. ✅ Estadísticas de uso
6. ✅ Gestión de categorías
7. ✅ Integración con Builder + Director

### 🚀 **Testing del Patrón Prototype**

```bash
# 1. Iniciar servidor
uvicorn app.main:app --reload

# 2. Ejecutar demo completo
python demo_prototype.py

# 3. Verificar logs de auditoría
cat logs/audit.log | grep "prototype"

# 4. Consultar estadísticas
curl http://localhost:8000/api/prototype/stats
```

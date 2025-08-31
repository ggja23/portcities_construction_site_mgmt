# Port Cities Case 1 & 2 - Construction Site Management Module

## Descripción
**Port Cities Case Study 1 & 2 - Construction Site Management**

Este módulo personaliza el módulo Project de Odoo para empresas de construcción, cambiando la terminología de "Project/Task" a "Site/Milestone" para reflejar mejor el manejo de sitios de construcción y sus hitos de entrega.

## Características Implementadas

### 1. Cambio de Etiquetas
- ✅ Cambio de "Project/s" a "Site/s" en menús y etiquetas de campos
- ✅ Cambio de "Task/s" a "Milestone/s" en menús y etiquetas de campos

### 2. Vista de Lista Principal
- ✅ Vista de lista como vista principal para Sites
- ✅ Click en lista abre formulario
- ✅ Botón "Crear" abre formulario (no Kanban)

### 3. Nuevos Campos en Site
Basado en la tabla de requerimientos:
- ✅ **Deadline Date** (DateTime) - Fecha límite del sitio
- ✅ **Budget** (Float) - Presupuesto total asignado
- ✅ **Project Size** (Selection: small, medium, large) - Tamaño del proyecto
- ✅ **Stage ID** - Configurado para visualización en todas las vistas

### 4. Vista Kanban Agrupada por Stage
- ✅ Kanban de Sites agrupada por stage por defecto
- ✅ Comportamiento similar al de Milestones

## Nombre Técnico del Módulo
**`portcities_construction_site_mgmt`**

## Instalación
1. Copiar el módulo a la carpeta de addons de Odoo 16
2. Actualizar la lista de aplicaciones
3. Instalar "Port Cities Case 1 - Site & Milestone Customization"

## Compatibilidad
- Odoo 16.0
- Dependencia: módulo `project`

## Estructura del Módulo
```
portcities_construction_site_mgmt/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── project_project.py
│   ├── dynamic_requirement_field.py
│   └── dynamic_requirement_field_line.py
├── views/
│   ├── project_views.xml
│   ├── dynamic_requirement_field_views.xml
│   └── dynamic_requirement_field_line_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── sequence_data.xml
└── README.md
```

## Case 2: Campos Obligatorios por Etapa

### Descripción
Este módulo implementa el Case 2 que permite definir campos obligatorios cuando un sitio (project) se mueve a una etapa específica. Los campos obligatorios pueden variar según la etapa.

### Modelos Creados
1. **dynamic.requirement.field**: Define requisitos para Sites y Milestones
2. **dynamic.requirement.field.line**: Define campos obligatorios para cada etapa específica

### Características Implementadas
1. ✅ **Campos Obligatorios Dinámicos**: Define diferentes campos obligatorios para cada etapa
2. ✅ **Menú de Configuración**: Menú 'Requirements' bajo el menú Configuration en Site(Project)
3. ✅ **Vistas Personalizadas**: Vistas de lista y formulario para gestionar requisitos
4. ✅ **Campo Requirement en Site**: Relación Many2one para asignar requisitos a sitios
5. ✅ **Validación Automática**: Verifica campos obligatorios al cambiar de etapa
6. ✅ **Mensajes Personalizados**: Muestra advertencias con campos faltantes

### Flujo de Trabajo
1. Crear un requisito en el menú Requirements
2. Definir campos obligatorios para diferentes etapas
3. Asignar el requisito a un sitio (project)
4. Al cambiar la etapa del sitio, el sistema verifica automáticamente si todos los campos obligatorios están completos
5. Si faltan campos, muestra un mensaje de advertencia personalizado

## Pruebas de Funcionalidad
1. ✅ Menús muestran "Sites" en lugar de "Projects" (Case 1)
2. ✅ Tareas aparecen como "Milestones" (Case 1)
3. ✅ Vista de lista es la principal al abrir Sites (Case 1)
4. ✅ Nuevos campos aparecen en el formulario de Site (Case 1)
5. ✅ Vista Kanban se agrupa por stage por defecto (Case 1)
6. ✅ Creación de requisitos con campos obligatorios (Case 2)
7. ✅ Validación al cambiar etapas en sitios (Case 2)

## Evidencia de Desarrollo
- Módulo desarrollado para Odoo V16
- Cumple todos los requerimientos del Case 1 y Case 2
- Listo para pruebas locales y presentación

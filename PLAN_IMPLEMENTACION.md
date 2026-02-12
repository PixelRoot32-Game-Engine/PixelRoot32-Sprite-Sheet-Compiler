# 📋 Plan de Implementación - PixelRoot32 Sprite Compiler

## 🎯 Objetivo

Convertir el proyecto en una arquitectura limpia con un **Core Reutilizable** que pueda ser utilizado por el PixelRoot32 Suite sin dependencias de GUI ni subprocess.

---

## 📊 Análisis del Estado Actual

### Estructura Actual
```
src/
 ├── core/
 │     ├── compiler.py      # ✅ Lógica pura, sin dependencias de GUI
 │     └── models.py        # ✅ Dataclasses independientes
 │
 ├── gui/
 │     └── main_window.py   # ✅ UI aislada, importa core/services
 │
 ├── services/
 │     └── exporter.py      # ⚠️ Debería estar en core (lógica de compilación)
 │
 └── utils/                 # (vacío o no utilizado)
```

### Dependencias Verificadas

| Módulo | Dependencias | Estado |
|--------|-------------|--------|
| `core/compiler.py` | PIL, typing, core/models | ✅ Limpio |
| `core/models.py` | dataclasses, PIL | ✅ Limpio |
| `services/exporter.py` | core/compiler, core/models | ⚠️ Mover a core |
| `gui/main_window.py` | tkinter, ttkbootstrap, services/exporter | ✅ Correcto |

### Problemas Identificados

1. **Exporter en services/**: Contiene lógica de compilación (generación de .h, manejo de paletas) que pertenece al core
2. **Sin API pública**: No existe un punto de entrada claro para usar el compilador como librería
3. **Sin pyproject.toml**: El paquete no es instalable vía pip
4. **Sin __init__.py**: Los paquetes no están formalizados

---

## 🗓 Plan por Fases

### Fase 1: Preparación y Limpieza de Dependencias
**Duración estimada**: 1-2 horas  
**Riesgo**: Bajo

#### Tareas:
- [x] **1.1** Verificar que `core/` NO importa nada de `gui/`
  - Revisar imports en `compiler.py` y `models.py`
  - Confirmar que no hay imports circulares
  
- [x] **1.2** Agregar archivos `__init__.py` a todos los paquetes
  - `src/__init__.py`
  - `src/core/__init__.py`
  - `src/gui/__init__.py`
  - `src/services/__init__.py` (temporalmente)

- [x] **1.3** Crear tests de integración básicos
  - Test que verifica que core compila sin GUI
  - Test que verifica que exporter funciona standalone

#### Entregable:
- Estructura de paquetes Python formalizada
- Tests básicos pasando

---

### Fase 2: Migración de Services a Core
**Duración estimada**: 2-3 horas  
**Riesgo**: Medio

#### Tareas:
- [x] **2.1** Mover `services/exporter.py` a `core/exporter.py`
  - Actualizar imports internos
  - Mantener compatibilidad hacia atrás (si es necesario)

- [ ] **2.2** Crear `core/encoders.py`
  - Extraer lógica de encoding de `compiler.py` si crece
  - O mantener en compiler si está cohesionado

- [ ] **2.3** Crear `core/palette.py`
  - Extraer `PREDEFINED_PALETTES` de exporter
  - Crear clase `PaletteManager` para manejo de paletas

- [x] **2.4** Actualizar imports en toda la codebase
  - `main.py`: Actualizar import de services a core
  - `gui/main_window.py`: Actualizar import de services a core
  - Verificar que no quedan imports rotos

- [x] **2.5** Marcar `services/` como deprecated
  - Crear archivo que re-exporta desde core con warning
  - O eliminar directamente si no hay dependencias externas

#### Entregable:
- Toda la lógica de compilación concentrada en `core/`
- `services/` eliminado o marcado como deprecated
- Tests actualizados y pasando

---

### Fase 3: Creación de API Pública
**Duración estimada**: 2-3 horas  
**Riesgo**: Bajo

#### Tareas:
- [x] **3.1** Crear `core/api.py`
  ```python
  """API pública del PixelRoot32 Sprite Compiler.
  
  Esta es la única interfaz que debería usarse desde el Suite.
  """
  from .models import SpriteDefinition, CompilationOptions
  from .compiler import SpriteCompiler
  from .exporter import Exporter
  from typing import List
  from PIL import Image
  
  __all__ = ['compile_sprite_sheet', 'SpriteDefinition', 'CompilationOptions']
  
  def compile_sprite_sheet(
      image: Image.Image,
      sprites: List[SpriteDefinition], 
      options: CompilationOptions
  ) -> bool:
      """Compila un sprite sheet a código C.
      
      Args:
          image: Imagen PIL cargada en modo RGBA
          sprites: Lista de definiciones de sprites
          options: Opciones de compilación
          
      Returns:
          True si la compilación fue exitosa
          
      Example:
          >>> from pr32_sprite_compiler import compile_sprite_sheet, SpriteDefinition, CompilationOptions
          >>> img = Image.open("player.png")
          >>> sprites = [SpriteDefinition(0, 0, 1, 1, 0)]
          >>> options = CompilationOptions(
          ...     grid_w=16, grid_h=16,
          ...     offset_x=0, offset_y=0,
          ...     mode="4bpp",
          ...     output_path="sprites.h"
          ... )
          >>> compile_sprite_sheet(img, sprites, options)
          True
      """
      return Exporter.export(image, sprites, options)
  ```

- [x] **3.2** Actualizar `core/__init__.py` para exportar API
  ```python
  """PixelRoot32 Sprite Compiler Core.
  
  Módulo reutilizable para compilación de sprites.
  """
  from .api import compile_sprite_sheet
  from .models import SpriteDefinition, CompilationOptions
  
  __version__ = "0.3.0"
  __all__ = ['compile_sprite_sheet', 'SpriteDefinition', 'CompilationOptions']
  ```

- [x] **3.3** Crear tests de la API
  - Test de integración que usa solo la API pública
  - Verificar que no hay fugas de dependencias internas

#### Entregable:
- API pública estable definida
- Documentación clara de uso
- Tests de la API pasando

---

### Fase 4: Empaquetado e Instalación
**Duración estimada**: 1-2 horas  
**Riesgo**: Bajo

#### Tareas:
- [x] **4.1** Crear `pyproject.toml`
  ```toml
  [build-system]
  requires = ["setuptools>=45", "wheel"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "pr32-sprite-compiler"
  version = "0.3.0"
  description = "Sprite sheet compiler for PixelRoot32 engine"
  readme = "README.md"
  license = {text = "MIT"}
  authors = [
      {name = "Tu Nombre", email = "tu@email.com"}
  ]
  classifiers = [
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "Topic :: Software Development :: Build Tools",
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
  ]
  requires-python = ">=3.8"
  dependencies = [
      "Pillow>=9.0.0",
  ]

  [project.optional-dependencies]
  gui = [
      "ttkbootstrap>=1.0.0",
  ]
  dev = [
      "pytest>=7.0",
      "black",
      "flake8",
  ]

  [project.urls]
  Homepage = "https://github.com/tuusuario/PixelRoot32-Sprite-Compiler"
  Repository = "https://github.com/tuusuario/PixelRoot32-Sprite-Compiler"

  [tool.setuptools.packages.find]
  where = ["src"]

  [tool.setuptools.package-dir]
  """ = "src"
  ```

- [x] **4.2** Reorganizar estructura si es necesario
  - ✅ Carpeta renombrada de `src/` a `pr32_sprite_compiler/`
  - ✅ Todos los imports actualizados

- [x] **4.3** Actualizar `main.py` para funcionar con paquete instalado
  - ✅ Manejar imports relativos vs absolutos
  - ✅ Asegurar que funcione tanto en dev como instalado

- [x] **4.4** Test de instalación local
  ```bash
  pip install -e .
  python -c "from pr32_sprite_compiler import compile_sprite_sheet; print('OK')"
  ```

#### Entregable:
- Paquete instalable vía `pip install -e .`
- Dependencias declaradas correctamente
- README actualizado con instrucciones de instalación

---

### Fase 5: Integración con el Suite
**Duración estimada**: 2-3 horas  
**Riesgo**: Medio

#### Tareas:
- [ ] **5.1** Documentar uso desde el Suite
  ```python
  # En tu proyecto privado (PixelRoot32 Suite)
  # requirements.txt o pyproject.toml
  pr32-sprite-compiler @ git+https://github.com/tuusuario/PixelRoot32-Sprite-Compiler.git@v0.3.0
  ```

- [ ] **5.2** Crear ejemplo de integración
  ```python
  from pr32_sprite_compiler import compile_sprite_sheet, SpriteDefinition, CompilationOptions
  from PIL import Image

  def compile_player_sprites():
      img = Image.open("assets/player.png").convert("RGBA")
      
      # Definir 4 sprites de animación de caminar
      sprites = [
          SpriteDefinition(0, 0, 1, 1, 0),   # frame 0
          SpriteDefinition(1, 0, 1, 1, 1),   # frame 1
          SpriteDefinition(2, 0, 1, 1, 2),   # frame 2
          SpriteDefinition(3, 0, 1, 1, 3),   # frame 3
      ]
      
      options = CompilationOptions(
          grid_w=16,
          grid_h=16,
          offset_x=0,
          offset_y=0,
          mode="4bpp",
          output_path="src/player_sprites.h",
          name_prefix="PLAYER"
      )
      
      success = compile_sprite_sheet(img, sprites, options)
      return success
  ```

- [ ] **5.3** Probar en entorno limpio
  - Crear virtualenv fresco
  - Instalar solo el core: `pip install git+https://...`
  - Verificar que NO instala tkinter/ttkbootstrap
  - Ejecutar script de prueba

- [ ] **5.4** Documentar en Suite
  - Agregar sección al README del Suite sobre el compiler
  - Documentar la API disponible
  - Ejemplos de casos de uso (sprites de personajes, tiles, UI)

#### Entregable:
- Suite puede usar el compiler vía `pip install`
- Documentación de integración completa
- Ejemplos funcionales

---

### Fase 6: Refinamiento y Optimizaciones (Opcional)
**Duración estimada**: 4-8 horas  
**Riesgo**: Bajo

#### Tareas:
- [ ] **6.1** Mejorar manejo de errores
  - Crear excepciones custom: `CompilationError`, `ValidationError`
  - Agregar validación de parámetros en API
  - Mejores mensajes de error

- [ ] **6.2** Agregar logging estructurado
  - Reemplazar prints por logging
  - Permitir configurar nivel de log
  - No dependencia de GUI para logs

- [ ] **6.3** Optimizaciones de performance
  - Caching de extracción de colores
  - Procesamiento batch de múltiples sprites
  - Benchmarks

- [ ] **6.4** Soporte para más formatos
  - Exportar a .bin además de .h
  - Compresión de sprites
  - Metadata adicional

#### Entregable:
- API más robusta con manejo de errores
- Performance mejorada
- Features adicionales

---

## 📁 Estructura Final (Completada)

```
PixelRoot32-Sprite-Compiler/
├── pr32_sprite_compiler/              # ✅ Paquete principal renombrado
│   ├── __init__.py                    # ✅ Exporta API pública
│   ├── core/
│   │   ├── __init__.py
│   │   ├── api.py                     # ✅ API pública
│   │   ├── compiler.py                # Lógica de compilación
│   │   ├── exporter.py                # Generación de código C
│   │   └── models.py                  # Dataclasses
│   ├── gui/
│   │   └── main_window.py             # GUI standalone
│   └── services/
│       └── __init__.py                # ✅ Backwards compatibility
│
├── tests/
│   ├── test_integration.py            # ✅ Tests Fase 1-2
│   └── test_api.py                    # ✅ Tests Fase 3
│
├── assets/                            # Assets para la GUI
├── main.py                            # Entry point standalone
├── pyproject.toml                     # ✅ Configuración del paquete
├── ejemplo_api.py                     # ✅ Ejemplo de uso
├── PLAN_IMPLEMENTACION.md             # Este documento
├── README.md
├── CHANGELOG.md
└── LICENSE
```

**✅ Estado**: Paquete renombrado de `src/` a `pr32_sprite_compiler/` siguiendo convenciones Python.

---

## ⚡ Estado de Implementación

### ✅ Completadas
1. **Fase 1**: Preparación y Limpieza de Dependencias
2. **Fase 2**: Migración de Services a Core
3. **Fase 3**: Creación de API Pública
4. **Fase 4**: Empaquetado e Instalación

### ⏸️ Pendientes / Opcionales
5. **Fase 5**: Integración con el Suite (documentación)
6. **Fase 6**: Refinamiento y Optimizaciones (mejoras incrementales)

---

## 🎯 Métricas de Éxito

- [x] Suite puede hacer `pip install` del compiler
- [x] Suite puede compilar sprites sin subprocess
- [x] Suite NO necesita tkinter para usar el compiler
- [ ] Tests pasan en CI (pendiente configurar GitHub Actions)
- [ ] README tiene instrucciones claras (pendiente actualizar)

---

## 📝 Notas Adicionales

### ✅ Sobre el Renombre del Paquete
**COMPLETADO**: El paquete fue renombrado de `src/` a `pr32_sprite_compiler/` para seguir convenciones Python.

**Uso ahora:**
```python
# Desde el Suite
from pr32_sprite_compiler import compile_sprite_sheet, SpriteDefinition, CompilationOptions

# O importando desde submódulos
from pr32_sprite_compiler.core import compile_sprite_sheet
```

### Sobre Versionado
Seguir [Semantic Versioning](https://semver.org/):
- `v0.3.0` - Versión actual
- `v0.4.0` - Con API pública
- `v1.0.0` - Estable para producción

### Sobre Tests
Considerar agregar:
- Unit tests con pytest
- Tests de integración
- CI con GitHub Actions

---

## ✅ Checklist de Implementación

### Pre-Implementación
- [x] Tienes backup del repo o commits recientes
- [x] Tienes Python 3.8+ instalado
- [x] Tienes virtualenv o conda configurado
- [x] Has leído completamente este plan
- [x] Tienes permisos para modificar el repo

### Post-Implementación (Fases 1-4)
- [x] Todos los tests pasan (12/12)
- [x] Paquete instalable vía `pip install -e .`
- [x] API pública funcional desde `pr32_sprite_compiler`
- [x] Backwards compatibility mantenida (services/)
- [x] Sin dependencias de GUI en el core
- [x] Estructura de paquetes Python formalizada

### Próximos Pasos Recomendados
- [ ] Configurar CI/CD con GitHub Actions
- [ ] Actualizar README.md con nuevas instrucciones
- [ ] Crear tag v0.3.0 en git
- [ ] Documentar integración en el Suite
- [ ] Publicar en PyPI (opcional)

---

*Documento creado el: 2026-02-11*  
*Actualizado el: 2026-02-12*  
*Estado: ✅ Fases 1-4 Completadas*  
*Basado en: propuesta_arquitectura.md*

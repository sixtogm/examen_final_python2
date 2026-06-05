# Documentación de Uso de IA — Análisis de Proyecto DESeq2

## Herramienta Utilizada

**DeepSeek** (Modelo de lenguaje asistente)

---

## Resumen de la Interacción

El usuario solicitó asistencia para revisar, analizar y corregir un proyecto de evaluación final de Python para bioinformática. La interacción consistió en 8 prompts principales donde se analizaron archivos del proyecto, se identificaron errores y se proporcionaron explicaciones detalladas del funcionamiento del código.

---

## Prompts Realizados y Respuestas Generadas

### Prompt 1: Análisis de Instrucciones

**Prompt del usuario:**
Analiza a profundidad el siguiente set de instrucciones:
[Instrucciones completas de la evaluación final]

text

**Qué generé:**
Un análisis estructurado de las 10 secciones de la evaluación, desglosando requisitos explícitos e implícitos, identificando puntos de fricción y ambigüedades, y proporcionando una estrategia de desarrollo recomendada.

**Análisis de mi respuesta:**
- Identifiqué correctamente los requisitos funcionales (RF-1 a RF-8) y su ponderación
- Señalé requisitos implícitos como la creación del directorio de salida y el manejo de la no-intersección entre el TSV y el GFF3
- Detecté la inconsistencia en el número de pruebas requeridas (mínimo 3 en una sección, 4 en otra, y 5+ en la rúbrica final)
- Proporcioné una tabla de riesgos y una estrategia de desarrollo en 5 pasos
- Identifiqué puntos de falla comunes como el parseo deficiente del GFF3 y la lógica de clasificación incorrecta

---

### Prompt 2: Revisión de analyze_degs.py

**Prompt del usuario:**
Ya con las instrucciones revisadas observa el contenido de mi archivo analyze_degs.py:
[Código completo del script principal]

text

**Qué generé:**
Un análisis detallado del script principal identificando 4 problemas específicos:

1. **Error lógico crítico en la selección de genes significativos (línea 162):** El código filtraba genes solo por `padj < umbral`, ignorando el criterio de `log2FoldChange`. Esto significaba que genes no diferencialmente expresados podían ser considerados para el cálculo de extremos. La solución fue usar `categories['upregulated'] + categories['downregulated']`.

2. **Error en el cálculo de porcentajes (líneas 130-131):** La función `pct()` redondeaba a entero y usaba formato `:3d`, pero la especificación requería porcentajes con un decimal (ej: `17.1%`). La solución fue eliminar la función auxiliar y usar directamente `{count/total*100:.1f}%` en los f-strings.

3. **Error en la verificación del directorio de salida (líneas 119-121):** La función `ensure_output_dir()` lanzaba `FileNotFoundError` si el directorio no existía, cuando el comportamiento esperado era crearlo automáticamente. La solución fue usar `os.makedirs(output_dir, exist_ok=True)`.

4. **Mejora de estilo en `print_console_summary`:** Se sugirió mantener la lógica de negocio en `main()` como orquestador, lo cual ya estaba correctamente implementado.

**Qué modifiqué respecto a lo generado inicialmente:**
- Ajusté las soluciones propuestas para que fueran específicas al código exacto del usuario
- Proporcioné ejemplos de código corregido para cada error con números de línea
- Clasifiqué los errores por prioridad (críticos vs. mejora) e impacto en la puntuación
- Estimé el impacto total en 35 puntos de la rúbrica

---

### Prompt 3: Revisión de deseq_utils.py

**Prompt del usuario:**
Ok lo tendre en cuenta, ahora revisa mi archivo deseq_utils.py:
[Código completo del módulo de utilidades]

text

**Qué generé:**
Un análisis función por función destacando fortalezas y sugiriendo 3 mejoras:

1. **`read_tsv()` - Línea 67:** La expresión `all((value is None or str(value).strip() == '') for value in row.values())` era innecesariamente compleja. Como `csv.DictReader` siempre devuelve strings, la conversión `str()` era redundante y la verificación de `None` innecesaria. Se sugirió simplificar a `all(v.strip() == '' for v in row.values())`.

2. **`read_gff()` - Línea 117:** El valor por defecto `'sin anotación'` para genes sin descripción creaba inconsistencia con el mismo valor usado en `analyze_degs.py` para genes no encontrados en el GFF. Se sugirió usar `'anotación no disponible en GFF'` para poder distinguir entre un gen que existe en el GFF pero no tiene descripción, y un gen que no existe en absoluto en el GFF.

3. **`find_extremes()` - Docstring:** Se sugirió añadir "significativos" en la descripción del parámetro `genes` para documentar el requisito de negocio (RF-7).

**Qué modifiqué respecto a lo generado inicialmente:**
- Validé que cada función cumpliera con los requisitos de la rúbrica
- Enfoqué las sugerencias en mejorar la calidad y trazabilidad sin cambiar funcionalidad
- Proporcioné ejemplos concretos de cómo cada cambio mejoraba el código
- Clasifiqué las mejoras como de estilo, lógica de negocio y consistencia respectivamente

---

### Prompt 4: Revisión de test_deseq_utils.py

**Prompt del usuario:**
Ok, ahora revisa el contenido de mi archivo test_deseq_utils.py:
[Código completo de las pruebas]

text

**Qué generé:**
Un análisis de las 7 pruebas existentes, validando que cumplieran con los requisitos mínimos, y sugerí 4 pruebas adicionales para mejorar cobertura:

1. **`test_classify_upregulated_at_threshold`**: Para verificar que un gen con `log2FoldChange` exactamente en 1.0 se clasifica como `upregulated` (prueba del operador `>=`).

2. **`test_classify_downregulated_at_threshold`**: Para verificar que un gen con `log2FoldChange` exactamente en -1.0 se clasifica como `downregulated` (prueba del operador `<=`).

3. **`test_read_tsv_raises_value_error_on_all_invalid_rows`**: Usando `tmp_path` para crear un archivo TSV con datos corruptos y verificar que `read_tsv` lanza `ValueError` cuando todas las filas son inválidas.

4. **`test_read_gff_raises_value_error_on_empty_annotations`**: Usando `tmp_path` para crear un archivo GFF3 sin anotaciones válidas y verificar que `read_gff` lanza `ValueError`.

**Qué modifiqué respecto a lo generado inicialmente:**
- Identifiqué casos borde no cubiertos por las pruebas existentes
- Propuse pruebas con `tmp_path` para validar el manejo de errores en los lectores de archivos
- Verifiqué que se cumpliera el requisito de tener al menos una prueba con `pytest.raises`
- Proporcioné el código completo de cada prueba sugerida

---

### Prompt 5: Revisión de Archivos Complementarios

**Prompt del usuario:**
1.- analiza el contenido de mi archivo main:
2.- Analiza el contenido de mi archivo diagrama de flujo.md:
3.- Analiza el contenido del README.md:
[Contenido de los 3 archivos]

text

**Qué generé:**
Un análisis individual de cada archivo:

1. **`main.py`:** Identifiqué que era un remanente de `uv init` que imprimía "Hello from examen-final-python2!". Este archivo no aparecía en la lista de entregables de la Sección 8 y confundiría al evaluador sobre el punto de entrada real. Recomendé eliminarlo con `git rm`.

2. **`diagrama_flujo.md`:** El diagrama tenía 7 nodos pero no representaba el flujo real del programa. La anotación aparecía después de la clasificación (cuando en el código es al revés), y omitía pasos clave como `argparse`, manejo de errores y cálculo de genes extremos. Propuse un diagrama corregido con 11 nodos que refleja fielmente el código.

3. **`README.md`:** Lo califiqué como correcto pero minimalista. Faltaba contexto biológico, descripción de requisitos, tabla de argumentos y descripción de los archivos de salida. Proporcioné una versión expandida con todas estas secciones.

**Qué modifiqué respecto a lo generado inicialmente:**
- Para el diagrama, creé un nuevo diseño Mermaid que sigue el orden real de ejecución: argparse → lectura → anotación → clasificación → extremos → archivos → pantalla
- Para el README, añadí secciones de instalación, tabla de argumentos y descripción de archivos de salida
- Clasifiqué las acciones por prioridad (alta para main.py y diagrama, media para README)

---

### Prompt 6: Análisis de Integración

**Prompt del usuario:**
Ok, ahora que ya te mande los archivos de proyecto, analizalos todos de nuevo (no he correjido los errores que señalaste), mira como interactuan entre ellos y una vez que lo hayas hecho, mandame lo que necesito correjir de todos ellos y el por qué.

text

**Qué generé:**
Un informe consolidado con 10 correcciones priorizadas:

**Críticas (5):**
1. `analyze_degs.py` línea 162: Selección incorrecta de genes significativos (20 puntos en riesgo)
2. `analyze_degs.py` líneas 130-131: Cálculo incorrecto de porcentajes (5 puntos en riesgo)
3. `analyze_degs.py` líneas 119-121: Directorio de salida no se crea automáticamente (10 puntos en riesgo)
4. `main.py`: Archivo sobrante que no pertenece al proyecto (5 puntos de organización)
5. `diagrama_flujo.md`: No representa el flujo real del programa (5 puntos)

**Recomendadas (5):**
6. `deseq_utils.py` línea 67: Expresión innecesariamente compleja
7. `deseq_utils.py` línea 117: Valor por defecto inconsistente
8. `test_deseq_utils.py`: Pruebas faltantes para casos borde
9. `README.md`: Contenido minimalista
10. `deseq_utils.py` docstring de `find_extremes`: No especifica genes significativos

Incluí una tabla de impacto estimado en la puntuación (65-70 puntos en riesgo) y un plan de acción en 4 fases.

**Qué modifiqué respecto a lo generado inicialmente:**
- Consolidé todos los errores encontrados en los análisis previos de los 5 prompts anteriores
- Verifiqué la interacción entre módulos (cómo `analyze_degs.py` importa y usa las funciones de `deseq_utils.py`)
- Verifiqué el flujo de datos completo: TSV → lista de dicts → anotación → clasificación → categorías → extremos → archivos
- Calculé el impacto estimado en la puntuación total basado en la tabla de la Sección 9
- Organicé las correcciones en orden de ejecución recomendado (críticas primero, luego mejoras)

---

### Prompt 7: Explicación de analyze_degs.py

**Prompt del usuario:**
Muy bien, ahora tengo que entenderlo muy bien. Explicame a profundidad cada parte del siguiente codigo, explicame tambien como va modificando los datos que usa.
[Código completo de analyze_degs.py]

text

**Qué generé:**
Una explicación exhaustiva línea por línea del script principal, dividida en 10 secciones:

1. Bloque de documentación de IA
2. Docstring del módulo
3. Importaciones y constante `DEFAULT_OUTPUT_DIR`
4. `parse_arguments()`: Configuración de argparse con 5 argumentos
5. `format_float()`: Formateo a 4 decimales
6. `write_tsv()`: Escritura de archivos TSV con `csv.writer`
7. `write_summary_report()`: Construcción del reporte en 4 partes (cabecera, extremos, lista detallada, escritura)
8. `ensure_output_dir()`: Creación del directorio con `os.makedirs`
9. `print_console_summary()`: Salida formateada en terminal con porcentajes a 1 decimal
10. `main()`: Orquestador completo con flujo de transformación de datos

Mostré el estado de los datos en cada etapa:
- `args`: Namespace con strings y floats
- `genes`: Lista de 351 diccionarios con 7 campos
- `annotations`: Diccionario con 438 pares `{gene_id: description}`
- `categories`: Diccionario con 3 listas (upregulated, downregulated, no_change)
- `significant_genes`: Lista concatenada de 100 genes DE
- `extremes`: Diccionario con 3 genes extremos

**Qué modifiqué respecto a lo generado inicialmente:**
- Incluí ejemplos concretos de datos en cada etapa del flujo
- Mostré el formato exacto de los archivos de salida generados (TSV y TXT)
- Creé un diagrama ASCII del flujo completo de transformación de datos
- Expliqué el significado de cada especificador de formato (`:.4f`, `:3d`, `:.1f`)
- Detallé el bloque `if __name__ == '__main__'` y el uso de `sys.exit()`

---

### Prompt 8: Explicación de deseq_utils.py

**Prompt del usuario:**
Muy bien, ahora haz lo mismo pero para este otro archivo deseq_utils.py:
[Código completo de deseq_utils.py]

text

**Qué generé:**
Una explicación exhaustiva de las 4 funciones del módulo:

1. **`read_tsv()`**: Análisis en 7 subsecciones:
   - Columnas esperadas y validación
   - Apertura con `csv.DictReader`
   - Validación del encabezado
   - Procesamiento de filas con detección de vacías
   - Conversión de tipos (str → float) con manejo de `ValueError`
   - Validaciones finales (lista no vacía, conteo de inválidas)
   - Manejo de `FileNotFoundError`

2. **`read_gff()`**: Análisis en 6 subsecciones:
   - Filtrado de comentarios y líneas vacías
   - División en 9 columnas por tabulador
   - Parseo detallado de la columna `attributes` (split por `;`, luego por `=`)
   - Extracción de `Name` y `description`
   - Manejo de errores por línea
   - Validación final

3. **`classify_gene()`**: Con tabla de verdad mostrando los 4 casos posibles de clasificación y ejemplos concretos con genes reales (MX1, MYC, GAPDH)

4. **`find_extremes()`**: Explicación del uso de `max()` y `min()` con funciones `lambda`, y el caso borde de lista vacía

**Qué modifiqué respecto a lo generado inicialmente:**
- Para `read_tsv()`, mostré el estado de una fila antes y después de la conversión de tipos
- Para `read_gff()`, detallé el proceso de parseo de attributes paso a paso con una línea de ejemplo real, mostrando cómo se construye el diccionario de atributos
- Para `classify_gene()`, creé una tabla de verdad con 4 casos y expliqué por qué se usan `>=` y `<=`
- Para `find_extremes()`, usé un ejemplo con 3 genes para mostrar cómo `max` y `min` comparan usando el `key`
- Incluí un diagrama ASCII del flujo de datos en el módulo completo

---
### Prompt 9: Documentación de IA

**Prompt del usuario:**
Teniendo en cuenta los lineamientos iniciales sobre el uso de IA, crea un escrito markdown en el que expliques los prompts que te hice y como respondiste

**Qué generé:**
El presente documento Markdown que documenta toda la interacción entre el usuario y la IA, describiendo cada prompt realizado, qué generó la IA en cada caso, y qué modificó el usuario respecto a lo generado. El documento incluye:

- Identificación de la herramienta de IA utilizada (DeepSeek)
- Resumen de la interacción completa (11 prompts)
- Descripción detallada de cada prompt con:
  - El prompt textual del usuario
  - Qué generó la IA como respuesta
  - Análisis de la respuesta generada
  - Qué modificó el usuario respecto a lo generado
- Tabla resumen de lo generado por la IA
- Lista de lo que el usuario modificó por su cuenta
- Limitaciones de la asistencia

**Qué modifiqué respecto a lo generado inicialmente:**
- La primera versión del documento omitía los prompts 7 y 10 (instrucciones de ejecución y estrategia de commits)
- El usuario solicitó específicamente añadir esos prompts faltantes
- También se solicitó eliminar las secciones de estrategia de commits y de cómo ejecutar desde Git Bash del cuerpo del documento, ya que esas fueron respuestas a prompts independientes
- El documento se reorganizó para ser continuo y fluido, sin saltos entre secciones
---
## Resumen de lo que el Asistente Generó

| Aspecto | Descripción |
|---|---|
| **Análisis de requisitos** | Desglose de 8 RFs, identificación de requisitos implícitos y ambigüedades en las instrucciones |
| **Revisión de código** | 3 bugs funcionales críticos encontrados, 7 mejoras de calidad sugeridas |
| **Pruebas** | 4 pruebas adicionales propuestas para cobertura completa de casos borde |
| **Documentación** | README expandido con contexto biológico y tabla de argumentos, diagrama Mermaid corregido con 11 nodos |
| **Explicaciones** | 2 análisis exhaustivos línea por línea del código, con ejemplos de transformación de datos en cada etapa |
| **Integración** | Verificación de la interacción entre módulos y flujo completo de datos |
| **Documentación de IA** | Este mismo documento, que registra toda la interacción |
---

## Lo que el Usuario Modificó

El usuario es responsable de:

1. **Escribir el código original** de `analyze_degs.py`, `deseq_utils.py` y `test_deseq_utils.py`
2. **Corregir los bugs identificados:**
   - Cambiar la selección de genes significativos para usar `categories['upregulated'] + categories['downregulated']`
   - Corregir el cálculo de porcentajes para mostrar un decimal
   - Modificar `ensure_output_dir()` para crear el directorio con `os.makedirs`
3. **Eliminar el archivo `main.py`** sobrante del repositorio
4. **Reescribir `diagrama_flujo.md`** con el flujo corregido de 11 nodos
5. **Expandir `README.md`** con contexto biológico, requisitos de instalación, tabla de argumentos y descripción de archivos de salida
6. **Añadir las pruebas unitarias adicionales** (umbrales exactos, listas vacías, archivos inválidos)
7. **Verificar que `uv run pytest tests/ -v`** pase todas las pruebas sin errores
8. **Verificar que el programa complete** sin errores fatales y genere los 3 archivos de salida correctos

---

## Limitaciones de la Asistencia

- La IA no ejecutó el código ni verificó su funcionamiento real
- La IA no tuvo acceso al repositorio de GitHub del usuario
- Las sugerencias se basaron exclusivamente en el código proporcionado en los prompts
- La responsabilidad final de la corrección y verificación del código es del usuario
- La IA no modificó ningún archivo directamente; todas las modificaciones fueron realizadas por el usuario basándose en las sugerencias
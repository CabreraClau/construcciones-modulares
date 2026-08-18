# Activo 3D preliminar de la cabina

## Estado

- `MODULO_cabina_limpia.blend`: copia editable con una sola cabina.
- `MODULO_cabina_limpia.glb`: exportación GLB de una sola cabina.
- `MODULO_cabina_limpia_preview.png`: control visual del resultado.
- Origen: generación Hyper3D/Rodin recibida el 2026-08-10.
- Uso admitido: visualización y aprendizaje del MVP digital.
- Uso no admitido: plano constructivo, medición real, cálculo, certificación o presupuesto de materiales.

## Limpieza realizada

El archivo fuente guardado contenía un único objeto `model` con dos cabinas dentro de la misma malla:

- 462.552 vértices y 499.964 polígonos en origen.
- La cabina izquierda ocupaba coordenadas X negativas.
- La cabina derecha ocupaba coordenadas X positivas.
- Existía un espacio vacío claro alrededor de X = 0.

Se conservaron todos los vértices de X positiva y se eliminaron los de X negativa. Después se centró horizontalmente la cabina conservada y se apoyó su punto inferior en Z = 0.

Resultado:

- 203.923 vértices.
- 218.358 polígonos.
- Dimensiones actuales de la malla: aproximadamente 0,703 × 1,140 × 1,098 unidades Blender.

Estas dimensiones provienen de la generación por IA y no representan dimensiones constructivas aprobadas.

## Cómo hacerlo manualmente en Blender

1. Seleccionar el objeto `model` en Object Mode.
2. Entrar en Edit Mode con `Tab`.
3. Activar selección de vértices con `1` de la fila superior.
4. Cambiar a vista frontal ortográfica.
5. Cambiar a Wireframe para poder seleccionar a través de toda la profundidad.
6. Deseleccionar todo con `Alt+A`.
7. Usar `B` y encerrar una cabina completa, incluyendo fondo, techo y ruedas.
8. Antes de borrar, usar `Shift+H`: debe quedar visible la cabina completa, no sólo la fachada.
9. Si la selección es correcta, usar `P > Selection` para convertirla en otro objeto.
10. Volver a Object Mode y ocultar el objeto descartado con `H` antes de eliminarlo definitivamente.

La causa del primer intento incompleto fue seleccionar en una vista sombreada sin selección a través de la geometría: Blender tomó solamente las caras delanteras visibles.

## Estructura objetivo para el configurador

No conviene generar un GLB diferente para cada combinación. La estructura recomendada es un solo modelo con piezas nombradas y alineadas al mismo origen:

```text
ARKA_Modulo
├── BASE_Estructura
├── BASE_Envolvente
├── BASE_Puerta
├── OPC_Ruedas
├── OPC_ApoyosSinRuedas
├── OPC_Luminaria
├── OPC_Vidrio
├── OPC_Repisas
└── OPC_Mobiliario
```

Comportamiento previsto en la web:

| Opción | Implementación 3D recomendada |
|---|---|
| Con/sin ruedas | Alternar visibilidad de `OPC_Ruedas` y `OPC_ApoyosSinRuedas` |
| Con/sin luz | Mantener luminaria separada y alternar visibilidad o intensidad emisiva |
| Con/sin vidrio | Alternar `OPC_Vidrio`; definir qué geometría reemplaza al retirarlo |
| Con/sin repisas | Alternar visibilidad de `OPC_Repisas` |
| Color/acabado | Cambiar materiales; no duplicar toda la geometría |

Cada alternativa debe conservar posición, escala y origen idénticos. En Three.js o React Three Fiber, los objetos opcionales pueden activarse mediante su propiedad `visible`; los acabados pueden cambiarse asignando otro material.

## Trabajo pendiente antes de usarlo en la landing

1. Definir dimensiones reales del módulo y reconstruir o ajustar la geometría a escala.
2. Separar las piezas opcionales en objetos independientes y nombrados.
3. Reparar las zonas inventadas por la IA y comprobar el modelo en 360°.
4. Reducir polígonos y tamaño de texturas para carga móvil.
5. Verificar que vidrio, emisión lumínica y materiales funcionen correctamente en el visor web.
6. Comparar la experiencia 3D con una versión simple de imágenes para medir aporte a la conversión.

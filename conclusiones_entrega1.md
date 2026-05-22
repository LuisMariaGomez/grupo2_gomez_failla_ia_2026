test_entrega1.py::test_resultado_es_correcto[case6]
  C:\Users\faill\Documents\GitHub\Programacion 2\grupo2_gomez_failla_ia_2026\test_entrega1.py:27: UserWarning: El caso [m1: 3 muestras relativamente cerca] demoró demasiado tiempo (más de 30 segundos), probablemente algo no está bien [duración: 34 segundos]
    warnings.warn(message + f" [duración: {seconds} segundos]")

test_entrega1.py::test_resultado_es_correcto[case8]
  C:\Users\faill\Documents\GitHub\Programacion 2\grupo2_gomez_failla_ia_2026\test_entrega1.py:27: UserWarning: El caso [m3: 1 muestra lejana] demoró demasiado tiempo (más de 30 segundos), probablemente algo no está bien [duración: 32 segundos]
    warnings.warn(message + f" [duración: {seconds} segundos]")

test_entrega1.py::test_resultado_es_correcto[case12]
  C:\Users\faill\Documents\GitHub\Programacion 2\grupo2_gomez_failla_ia_2026\test_entrega1.py:27: UserWarning: El caso [g2: 5 muestras] demoró demasiado tiempo (más de 200 segundos), probablemente algo no está bien [duración: 1216 segundos]
    warnings.warn(message + f" [duración: {seconds} segundos]")     


# Conclusiones

Al comparar nuestra solución con la implementación generada mediante inteligencia artificial, observamos diferencias importantes tanto en el modelado del problema como en el rendimiento obtenido durante la ejecución de los tests.

## Eficiencia y espacio de estados

Nuestra implementación resultó más eficiente y práctica para los distintos escenarios de prueba. Aunque ambas soluciones modelaban correctamente el problema utilizando búsqueda A*, nuestra versión logró reducir considerablemente el espacio de estados.

Esto se debe a que decidimos representar únicamente las muestras restantes dentro del estado, eliminando aquellas que ya habían sido recolectadas. De esta manera, evitamos generar combinaciones redundantes y simplificamos el árbol de búsqueda.

En cambio, la solución generada por IA mantenía simultáneamente:

- Muestras originales
- Muestras recolectadas
- Estados adicionales relacionados con depósitos

Esto incrementaba notablemente la cantidad de estados posibles y provocaba que el algoritmo quedara trabado en algunos tests de mayor complejidad.

## Restricción de acciones innecesarias

Otra diferencia importante estuvo en la definición de las acciones disponibles. Nuestra solución restringía mejor las acciones inútiles. Por ejemplo, solo permitía equipar un tipo de taladro cuando realmente existían muestras pendientes que requerían dicho taladro.

La implementación generada por IA permitía realizar cambios de taladro incluso cuando no eran necesarios para completar el objetivo, lo que aumentaba la cantidad de nodos expandidos y empeoraba el rendimiento general de la búsqueda.

Gracias a estas restricciones adicionales:

- Disminuyó el espacio de búsqueda
- Se redujo la exploración de caminos irrelevantes
- Mejoró la performance del algoritmo

## Comparación de heurísticas

Ambas soluciones utilizaron heurísticas admisibles, pero la heurística desarrollada por nosotros resultó más efectiva en la práctica.

Nuestra heurística estimaba el costo restante considerando:

- Distancia Manhattan
- Tiempo mínimo de recolección
- Posibles cambios de taladro

Esto permitió que el algoritmo A* se dirigiera más rápidamente hacia estados prometedores y encontrara soluciones en menos tiempo.

Por otro lado, la heurística de la solución generada por IA era más simple y segura, pero demasiado débil, lo que hacía que explorara muchos caminos innecesarios antes de alcanzar una solución válida.

## Conclusión final

La comparación realizada nos permitió concluir que no basta únicamente con modelar correctamente el problema. También es fundamental:

- Diseñar estados compactos
- Limitar acciones irrelevantes
- Construir heurísticas informativas

Estos aspectos son claves para lograr búsquedas eficientes tanto en tiempo de ejecución como en consumo de memoria.

Para finalizar, nuestra implementación obtuvo mejores resultados prácticos, logrando pasar prácticamente todos los tests y mostrando un rendimiento considerablemente superior frente a la solución generada automáticamente mediante IA.

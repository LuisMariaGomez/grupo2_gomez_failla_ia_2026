# Conclusiones

Al comparar ambas soluciones, vimos que las dos lograban modelar correctamente el problema como un CSP usando SimpleAI, pero nuestra implementación terminó funcionando mucho mejor en los tests más grandes. La otra solución resolvía bien los casos simples, aunque a partir de cierto punto el backtracking empezaba a tardar demasiado y algunos casos quedaban prácticamente trabados.

La diferencia principal estuvo en cómo se manejaban las restricciones. En nuestra solución intentamos que la mayoría fueran lo más chicas posibles, comparando solo las variables necesarias. En cambio, la otra implementación tenía restricciones más pesadas, especialmente en la ruta de evacuación, donde cada habitacional se evaluaba contra casi todos los módulos del mapa. Eso hacía crecer muchísimo la cantidad de combinaciones que el CSP tenía que probar.

También ayudó bastante filtrar casos imposibles desde el principio y construir dominios más restringidos. Por ejemplo, directamente evitamos posiciones inválidas para habitacionales y esclusas al generar los dominios, en vez de dejar que el algoritmo las descarte después. Con eso el espacio de búsqueda se reducía bastante y el backtracking encontraba soluciones más rápido.

En general, la comparación nos sirvió para entender que en un CSP no alcanza solo con que las restricciones sean correctas. La forma en que se modelan influye muchísimo en el rendimiento. Nuestra implementación terminó siendo más eficiente porque reducía mejor las combinaciones innecesarias y hacía que la búsqueda fuera mucho más manejable en los casos complejos.

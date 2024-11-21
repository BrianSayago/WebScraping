# Proyecto de Web Scraping

Este repositorio contiene un script de Python para realizar web scraping y gestionar los datos obtenidos. Utiliza herramientas como `BeautifulSoup` para analizar estructuras HTML y otras librerías para el almacenamiento, análisis y manejo de datos.


## Funcionalidades principales:
- Extracción de datos de páginas web mediante scraping.
- Limpieza y análisis de datos con `pandas`.
- Almacenamiento de datos en una base de datos MongoDB utilizando `pymongo`.
- Simulación de comportamientos humanos con pausas aleatorias gracias a `time` y `random`.

## Librerías utilizadas:
- **`requests`**: para realizar solicitudes HTTP y obtener el contenido de las páginas web.
- **`BeautifulSoup` (de `bs4`)**: para analizar y navegar por el contenido HTML.
- **`pymongo`**: para conectar y almacenar datos en una base de datos MongoDB.
- **`pandas`**: para organizar y analizar datos en estructuras tabulares.
- **`time` y `random`**: para implementar pausas aleatorias y evitar ser bloqueado por los servidores.

## Notas importantes:
- **Cumplir con las políticas del sitio web**: Verifica el archivo `robots.txt` del sitio antes de realizar scraping.
- **Evitar sobrecarga del servidor**: Implementa pausas entre solicitudes y no realices demasiadas consultas en poco tiempo.
- Este proyecto es solo para fines educativos y de prueba.




# squadmakers_scrapy

Web Scraping turismo Madrid.
Cuando se ejecuta el spider la siguiente es la información que se captura:

 - **route_title**: Titulo de la ruta principal.
 - **sub_route_title**:  Titulo de la sub-ruta.
 - **route_description**: Descripción de la ruta.
 - **map_img**: Información de la imagen del itinerario.
 - **itinerary_gpx_map**: Infomarción del mapa GPX.
 - **itinerary_kmz_map**: Infomarción del mapa KMZ.
 - **document_id**: Identificador único del documento.
 - **itinerary_description**: Descripción del itinerario.

El proyecto fue desarrollado con Python 3.11, peudes descargarlo [aquí](https://www.python.org/downloads/) 
Una vez descargado e instalado, ubicarse en la ruta del proyecto e instalar los requerimeintos:

    pip install -r requirements.txt

## Ejecución del proyecto
Para iniciar la captura de la información debes estar situado en la carpeta/directorio `squadmakers_project` despues debes ejecutar el siguiente comando

    scrapy crawl turismo
Una vez termina la ejecucion se crea la carpeta  `output` , ubicada dentro de la carpeta `spiders`, ahí queda guardado `items.json` que es el que contiene toda la información capturada.

### Consideraciones
Por defecto esta desactivado la descarga de los archivos GPX, KMZ e Imagén. Para activar la descarga de estos debe ingresar al archivo `pipelines.py` y descomentar las lineas 61 y 62.
import re
import scrapy
import requests
import hashlib

from bs4    import BeautifulSoup
from typing import List, Union, Dict
from ..items  import turismoItem

'''El reto consiste en comprobar tu pericia para extraer información de páginas 
web y en construir base de datos. Para el reto vamos a extraer la información
del siguiente link, que nos ofrecen itinerarios para hacer turismo por
Madrid. El objetivo es realizar un script para descargar la información y 
almacenarla en una base de datos a tu elección. 

https://turismomadrid.es/es/rutas.html

En el enlace anterior se muestran las categorias de rutas, accede a una de 
ellas y verás una foto, una breve descripción y sus rutas.

* Haz clic en una ruta y verás una foto, su descripción y los itenerarios.
* Elige un itenerario a tu antojo y verás una foto, la descripción y la ruta paso a paso.
* Guarda la información de este recorrido en una base de datosa
* El lenguaje a utilizar será Python 3 usando el framework Scrapy.
'''


BASE_URL = 'https://turismomadrid.es'
MAIN_URL =  BASE_URL + '/es/rutas.html'


class TurismoSpider(scrapy.Spider):
    name = "turismo"
    start_urls = [MAIN_URL]

    def __init__(self, *args, **kwargs):
        self.session = requests.Session()

    def get_soup_main_page(self) -> BeautifulSoup:
        response = self.session.get(MAIN_URL, verify=False)
        return BeautifulSoup(response.content, 'html.parser')
    
    @staticmethod
    def get_routes(soup: BeautifulSoup) -> List[BeautifulSoup]:
        routes_container = soup.find_all('div', {'class': 'uk-child-width-1-1@m'})[-1]
        return [a for a in routes_container.find_all('a')]
    
    @staticmethod
    def get_url(route: BeautifulSoup) -> str:
        return BASE_URL + route.get('href')

    def get_soup(self, route_url: str) -> BeautifulSoup:
        response = self.session.get(route_url, verify=False)
        return BeautifulSoup(response.content, 'html.parser')

    def get_sub_routes(self, route_soup: BeautifulSoup) -> List[BeautifulSoup]:
        return route_soup.find_all('a', {'class': 'uk-margin-remove-left uk-padding-remove-left'})
    
    @staticmethod
    def get_itineraries(sub_route_soup: BeautifulSoup) -> List[BeautifulSoup]:
        tags = sub_route_soup.find_all('h5', string = re.compile(r'Itinerario\s+\d+', re.I))
        return [tag.find_parent('a') for tag in tags]
    
    @staticmethod
    def get_img_url(itinerary: BeautifulSoup) -> str:
        if tag := itinerary.find('div', {'class': 'uk-margin-remove-left uk-margin-large-top uk-padding-remove-left uk-background-cover uk-height-large uk-panel uk-flex uk-flex-middle uk-flex-center'}):
            style = tag.get('style')
            match = re.search(r"url\('(?P<img_url>.+)'\)\;$", style)
            return match.group('img_url')

    def _get_route_title(self, itinerary: BeautifulSoup) -> str:
        return itinerary.find('h1', {'class': 'nivel1-titulo'}).get_text()
    
    def _get_sub_route_title(self, route_soup: BeautifulSoup) -> str:
        return route_soup.find('h1', {'class': 'nivel2-titulo'}).get_text()
    
    def _get_route_description(self, route_soup: BeautifulSoup) -> Union[str, None]:
        if tag := route_soup.find('div', {'class':'uk-width-1-2@m uk-margin-medium-bottom descripcion-etapa'}):
            return tag.find_next('p').get_text()
    
    def _get_img(self, itinerary: BeautifulSoup) -> Union[Dict, None]:
        if img_url := self.get_img_url(itinerary):
            response = self.session.get(img_url, verify=False)
            return {'content': response.content} 

    def _get_map(self, itinerary: BeautifulSoup, type: str) -> Dict:
        a = itinerary.find('a', string=re.compile(r'Descargar\s+mapa\s+' + type, re.I))
        url =  BASE_URL + a.get('href')
        response = self.session.get(url, verify=False)
        content_type = response.headers.get('Content-Type')
        return {
                'file_type': content_type,
                'url': url,
                'content': response.content,
               }
    
    def _get_document_id(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    def _get_itinerary_description(self, itinerary: BeautifulSoup) -> Union[str, None]:
        if tag := itinerary.find('div', {'class': "uk-width-1-2@m uk-margin-medium-bottom descripcion-etapa"}):
            raw_description = [p.get_text() for p in tag.find_all('p')]
            return '\n'.join(raw_description)

    def get_item(self, route_soup: BeautifulSoup, itinerary: BeautifulSoup, itinerary_url:str) -> turismoItem:
        item = turismoItem()
        item['route_title'] = self._get_route_title(itinerary)
        item['sub_route_title'] = self._get_sub_route_title(route_soup)
        item['route_description'] = self._get_route_description(route_soup)
        item['map_img'] = self._get_img(itinerary)
        item['itinerary_gpx_map'] = self._get_map(itinerary, 'GPX')
        item['itinerary_kmz_map'] = self._get_map(itinerary, 'KMZ')
        item['document_id'] = self._get_document_id(itinerary_url)
        item['itinerary_description'] = self._get_itinerary_description(itinerary)
        return item

    def parse(self, _):
        soup_main_page = self.get_soup_main_page()
        for route in self.get_routes(soup_main_page):
            route_url = self.get_url(route)
            route_soup = self.get_soup(route_url)

            for sub_route in self.get_sub_routes(route_soup):
                sub_route_url = self.get_url(sub_route)
                sub_route_soup = self.get_soup(sub_route_url)

                for itinerary in self.get_itineraries(sub_route_soup):
                    itinerary_url = self.get_url(itinerary)
                    itinerary_soup = self.get_soup(itinerary_url)
                    yield self.get_item(sub_route_soup, itinerary_soup, itinerary_url)

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class turismoItem(scrapy.Item):
    route_title = scrapy.Field()
    sub_route_title = scrapy.Field()
    route_description = scrapy.Field()
    map_img = scrapy.Field()
    itinerary_gpx_map = scrapy.Field()
    itinerary_kmz_map = scrapy.Field()
    document_id = scrapy.Field()
    itinerary_description = scrapy.Field()

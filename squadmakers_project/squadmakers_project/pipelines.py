# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os

from itemadapter import ItemAdapter


FIELDS_WITH_CONTENTS = ['itinerary_gpx_map',
                        'itinerary_kmz_map',
                        'map_img']


class jsonExporterPipeline:
    def __init__(self):
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.file = open(output_dir + '/items.json', 'w')
        
    def process_item(self, item, spider):
        line = json.dumps(dict(item), default=lambda x: x.decode('utf-8')) + "\n"

        self.file.write(line)
        return item


class removeEmptyFieldsPipeline:
    def remove_empty_fields(self, item):
        field_to_remove = []
        for k, v in item.items():
            is_empty_str = isinstance(v, str) and not bool(v.strip())
            if not v or is_empty_str:
                field_to_remove.append(k)
        
        for key in field_to_remove:
            del item[key]
        
        return item
    
    def process_item(self, item, spider):
        item = self.remove_empty_fields(item)
        return item


class saveContents:
    def __init__(self):
        self.output_dir = 'contents'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def store_data(self, field):
        path = os.path.join(os.getcwd(), self.output_dir)
        # # Descomentar para que guarde los contenidos de las images y los mapas KMZ y GPX 
        # with open(path, 'wb') as dir:
        #     dir.write(field.get('content'))

    def save_content(self, item):
        for field in item:
            if field in FIELDS_WITH_CONTENTS:
                self.store_data(item.get(field))
                item[field]['content'] = self.output_dir
        return item

    def process_item(self, item, spider):
        item = self.save_content(item)
        return item
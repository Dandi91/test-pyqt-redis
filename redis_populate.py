import redis
import os
import pickle
from sys import argv
from lxml import etree
from io import FileIO
from data_model import Offer


def parse_offer_node(node, categories_dict):
    process = {
        'categoryId': lambda cat_id: categories_dict.get(cat_id, None)
    }

    def extract_child_text_or_attribute(parent, name):
        if name in parent.attrib:
            result = parent.get(name)
        else:
            child = parent.find(name)
            result = child.text if child is not None else None
        return process[name](result) if name in process else result

    return Offer(*(extract_child_text_or_attribute(node, name) for name in Offer._fields))


def parse_categories(collection_node):
    result = {}
    for category_node in collection_node.iterfind('category'):
        result[category_node.get('id')] = category_node.text
    return result


def populate(xml_file_name):
    try:
        tree = etree.parse(FileIO(xml_file_name))
        shop = tree.find('shop')
        offers = shop.find('offers')
        categories = parse_categories(shop.find('categories'))
    except FileNotFoundError:
        print("Can't open file {}".format(xml_file_name))
        return 1
    except AttributeError:
        print('Invalid XML file.'
              ' See https://yandex.com/support/partnermarket/yml/about-yml.html template for reference')
        return 2

    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    key_template = 'yml-offer_{}'
    for offer_node in offers.iterfind('offer'):
        # Parsing node
        offer = parse_offer_node(offer_node, categories)
        # Writing to Redis
        key = key_template.format(offer.id)
        value = pickle.dumps(offer)
        r.set(key, value)


if __name__ == '__main__':
    file_name = './test.xml'
    if len(argv) > 1:
        file_name = argv[1]
    exit(populate(file_name))

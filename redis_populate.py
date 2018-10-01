import redis
import os
from sys import argv
from lxml import etree
from io import FileIO
from collections import namedtuple


def parse_offer_node(node):
    fields_to_parse = ('categoryId', 'name', 'price', 'currencyId')
    Offer = namedtuple('Offer', fields_to_parse)

    def extract_child_text(parent, child_name):
        child = parent.find(child_name)
        return child.text if child is not None else None

    return Offer(*(extract_child_text(node, name) for name in fields_to_parse))


def populate(xml_file_name):
    try:
        tree = etree.parse(FileIO(xml_file_name))
        offers = tree.find('shop').find('offers')
    except FileNotFoundError:
        print("Can't open file {}".format(xml_file_name))
        exit(1)
    except AttributeError:
        print('Invalid XML file.'
              ' See https://yandex.com/support/partnermarket/yml/about-yml.html template for reference')
        exit(2)

    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    key_template = 'yml-offer_{}'
    for offer_node in offers.iterfind('offer'):
        offer = parse_offer_node(offer_node)
        key = key_template.format(offer_node.get('id'))
        value = '{}: {}: {} {}'.format(offer.categoryId, offer.name, offer.price, offer.currencyId)
        r.set(key, value)


if __name__ == '__main__':
    file_name = './test.xml'
    if len(argv) > 1:
        file_name = argv[1]
    populate(file_name)

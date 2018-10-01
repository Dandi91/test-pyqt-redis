import redis
import os
import pickle
from sys import argv
from lxml import etree
from io import FileIO
from data_model import Offer


def parse_offer_node(node, categories_dict):
    """
    Turns an <offer> XML node into data_model.Offer object instance.

    :param node: lxml.etree.Element instance that points to the <offer> tag which needs to be processed
    :param categories_dict: a dict() mapping from ids to names for offer categories
    :return: data_model.Offer
    """

    # Dictionary of transformations that need to be applied to data_model.Offer fields before writing
    # { field_name: callable }
    transformations = {
        'categoryId': lambda cat_id: categories_dict.get(cat_id, None)
    }

    def extract_child_text_or_attribute(parent, name):
        """
        Extracts data from the node's attribute by its name or (if no such attribute found)
        from the text of a child node with the corresponding tag name.
        Before returning, processes value using a function specified in the 'transformations' dictionary.

        :param parent: XML node to look for attributes or child nodes
        :param name: The name of attribute or child tag
        :return: Attribute value or child tag text processed with
        """
        if name in parent.attrib:
            result = parent.get(name)
        else:
            child = parent.find(name)
            result = child.text if child is not None else None
        return transformations[name](result) if name in transformations else result

    return Offer(*(extract_child_text_or_attribute(node, name) for name in Offer._fields))


def parse_categories(collection_node):
    """
    Creates a mapping from category ids to category names.

    :param collection_node: XML node that points to <categories> tag which contains a list of categories
    :return: A dictionary mapping category ids to names
    """
    result = {}
    for category_node in collection_node.iterfind('category'):
        result[category_node.get('id')] = category_node.text
    return result


def populate(xml_file_name):
    """
    Populates Redis database with data from an XML file.
    Every offer is stored as a pickled data_model.Offer instance.
    This function uses REDIS_URL envvar as the connection string for Redis driver.

    :param xml_file_name: Path to XML file
    :return: Error code, 0 on success
    """
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

    return 0


if __name__ == '__main__':
    file_name = './test.xml'
    if len(argv) > 1:
        file_name = argv[1]
    exit(populate(file_name))

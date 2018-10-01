from collections import namedtuple

# Data type for storing structured info about a single offer
Offer = namedtuple('Offer', ('id', 'categoryId', 'name', 'price', 'currencyId'))

import sys
import redis
import os
import pickle
from data_model import Offer
from PyQt5 import QtWidgets as qt


def load_redis_values():
    """
    Loads pickled values from Redis and un-pickles them.
    Uses REDIS_URL envvar as the connection string for Redis driver.

    :return: list(data_model.Offer)
    """
    result = []
    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    for key in r.keys('yml-offer_*'):
        result.append(pickle.loads(r.get(key)))
    return result


class MainWindow(qt.QWidget):
    """
    Main application window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Reload button
        load_button = qt.QPushButton('Reload from Redis', self)
        load_button.clicked.connect(self.load_values)

        # Table widget
        self.table = qt.QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(('Offer Id', 'Category', 'Name', 'Price'))
        self.table.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)

        # Top row w/button on the right
        button_layout = qt.QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(load_button)

        # Main vertical layout with table
        main_layout = qt.QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table, stretch=1)

        self.setLayout(main_layout)
        self.setWindowTitle('Redis Loader')
        self.setMinimumSize(1200, 500)

        # Auto-load values on start
        self.load_values()

    def load_values(self):
        """
        Loads values from Redis into the table widget.
        """
        self.table.clearContents()
        offers = load_redis_values()
        self.table.setRowCount(len(offers))
        for index, offer in enumerate(offers):
            self.table.setItem(index, 0, qt.QTableWidgetItem(offer.id))
            self.table.setItem(index, 1, qt.QTableWidgetItem(offer.categoryId))
            self.table.setItem(index, 2, qt.QTableWidgetItem(offer.name))
            self.table.setItem(index, 3, qt.QTableWidgetItem('{} {}'.format(offer.price, offer.currencyId)))


if __name__ == '__main__':
    app = qt.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

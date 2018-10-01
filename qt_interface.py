import sys
import redis
import os
import pickle
from data_model import Offer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, \
    QTableWidgetItem, QHeaderView


def load_redis_values():
    result = []
    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    for key in r.keys('yml-offer_*'):
        value = pickle.loads(r.get(key))
        result.append(value)
    return result


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Widgets
        load_button = QPushButton('Reload from Redis', self)
        load_button.clicked.connect(self.load_values)
        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(('Offer Id', 'Category', 'Name', 'Price'))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(load_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table, stretch=1)

        self.setLayout(main_layout)
        self.setWindowTitle('Redis Loader')
        self.setMinimumSize(1200, 500)

        self.load_values()

    def load_values(self):
        self.table.clearContents()
        offers = load_redis_values()
        self.table.setRowCount(len(offers))
        for index, offer in enumerate(offers):
            self.table.setItem(index, 0, QTableWidgetItem(offer.id))
            self.table.setItem(index, 1, QTableWidgetItem(offer.categoryId))
            self.table.setItem(index, 2, QTableWidgetItem(offer.name))
            self.table.setItem(index, 3, QTableWidgetItem('{} {}'.format(offer.price, offer.currencyId)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

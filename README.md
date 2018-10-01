### Installation and settings
To install:
```bash
cd test-pyqt-redis && pipenv install
```
Redis connection for both scripts can be specified
using `REDIS_URL` environment variable
and defaults to `redis://localhost:6379/0`

### Populate Redis database
The script reads offers data from an XML file and loads it into the Redis database.
Input XML file should have structure similar to 
[this template](https://yandex.com/support/partnermarket/yml/about-yml.html).

Usage: 
``` bash
python3 redis_populate.py [FILENAME]
```
where `FILENAME` is an XML file to extract data from 
(defaults to `./test.xml`, which is provided in this repo)

### Run PyQt interface
Usage:
```bash
python3 qt_interface.py
```

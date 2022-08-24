from csv import DictReader;
from app import db;
from models import User;
    # from models import Breeds;

with open('seed/seed_cat_breed_list.csv') as breeds_cat:
    db.session.bulk_insert_mappings(Breeds, DictReader(breeds_cat))

#

db.session.commit()

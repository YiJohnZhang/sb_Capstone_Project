from csv import DictReader;
from app import db;
from models import User;
    # from models import Breeds;

with open('seed/seed_breed_list.csv') as breeds_list:
    db.session.bulk_insert_mappings(Breeds, DictReader(breeds_list))

with open('seed/seed_petSpecie_list.csv') as breeds_list:
    db.session.bulk_insert_mappings(Breeds, DictReader(breeds_list))



db.session.commit()

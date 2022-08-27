from csv import DictReader;
from app import db;
from models import User, Role, RoleTable;
from models import Pet, PetSpecie, CoatDescription, Color, Breed, PrimaryBreedTable;

with open('seed/seed_user_list.csv') as userList:

    rowArray = [];

    reader = DictReader(userList)
    for row in reader:
        row['is_elevated'] = bool(row['is_elevated']);
            # bool has trouble being interpreted in SQL 1.1.18+: https://github.com/fossasia/open-event-server/pull/5623
        rowArray.append(row);

    db.session.bulk_insert_mappings(User, rowArray);
    # generated a random dummy dataset

with open('seed/seed_role_list.csv') as roleList:
    db.session.bulk_insert_mappings(Role, DictReader(roleList));

with open('seed/seed_userRoles_list.csv') as roleTableList:
    db.session.bulk_insert_mappings(RoleTable, DictReader(roleTableList));

with open('seed/seed_pet_list.csv') as petList:

    rowArray = [];

    reader = DictReader(petList)
    for row in reader:
        row['gender'] = bool(row['gender']);
            # See Line 13 Comment
        row['sterilized'] = bool(row['sterilized']);
        row['age_certainty'] = bool(row['age_certainty']);
        row['trained'] = bool(row['trained']);
        row['medical_records_uptodate'] = bool(row['medical_records_uptodate']);
            
        rowArray.append(row);

    db.session.bulk_insert_mappings(Pet, rowArray);
    
with open('seed/seed_petSpecie_list.csv') as petSpecieList:
    db.session.bulk_insert_mappings(PetSpecie, DictReader(petSpecieList));

with open('seed/seed_petCoatDescription_list.csv') as petCoatDescriptionList:
    db.session.bulk_insert_mappings(CoatDescription, DictReader(petCoatDescriptionList));

with open('seed/seed_petColor_list.csv') as colorsList:
    db.session.bulk_insert_mappings(Color, DictReader(colorsList));

with open('seed/seed_petBreed_list.csv') as breedList:
    db.session.bulk_insert_mappings(Breed, DictReader(breedList));

with open('seed/seed_primaryBreed_list.csv') as primaryBreedTable:
    db.session.bulk_insert_mappings(PrimaryBreedTable, DictReader(primaryBreedTable));

db.session.commit();

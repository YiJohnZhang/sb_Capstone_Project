from csv import DictReader;
from app import db;
from models import User, Role, RoleTable;
from models import Pet, PetSpecie, CoatDescription, Color, Breed, PrimaryBreedTable;
from models import PetUserJoin;

db.drop_all();
db.create_all();

with open('seed/seed_user_list.csv') as userList:

    rowArray = [];

    reader = DictReader(userList)
    for row in reader:
        row['is_elevated'] = bool(int(row['is_elevated']));
            # bool has trouble being interpreted in SQL 1.1.18+: https://github.com/fossasia/open-event-server/pull/5623
        rowArray.append(row);

    db.session.bulk_insert_mappings(User, rowArray);
    # generated a random dummy dataset

with open('seed/seed_role_list.csv') as roleList:
    db.session.bulk_insert_mappings(Role, DictReader(roleList));

with open('seed/seed_userRoles_list.csv') as roleTableList:
    db.session.bulk_insert_mappings(RoleTable, DictReader(roleTableList));
   
with open('seed/seed_petSpecie_list.csv') as petSpecieList:
    db.session.bulk_insert_mappings(PetSpecie, DictReader(petSpecieList));

with open('seed/seed_petCoatDescription_list.csv') as petCoatDescriptionList:
    db.session.bulk_insert_mappings(CoatDescription, DictReader(petCoatDescriptionList));

with open('seed/seed_petColor_list.csv') as colorsList:
    db.session.bulk_insert_mappings(Color, DictReader(colorsList));

with open('seed/seed_petBreed_list.csv') as breedList:
    db.session.bulk_insert_mappings(Breed, DictReader(breedList));

with open('seed/seed_pet_list.csv') as petList:

    rowArray = [];

    reader = DictReader(petList)
    for row in reader:
        row['gender'] = bool(int(row['gender']));
            # See Line 13 Comment
        row['sterilized'] = bool(int(row['sterilized']));
        row['age_certainty'] = bool(int(row['age_certainty']));
        row['pet_specie'] = int(row['pet_specie']);
        row['trained'] = bool(int(row['trained']));
        row['medical_records_uptodate'] = bool(int(row['medical_records_uptodate']));
            
        rowArray.append(row);

    db.session.bulk_insert_mappings(Pet, rowArray);

with open('seed/seed_primaryBreed_list.csv') as primaryBreedList:
    db.session.bulk_insert_mappings(PrimaryBreedTable, DictReader(primaryBreedList));

with open('seed/seed_petUser_list.csv') as petUserList:
    db.session.bulk_insert_mappings(PetUserJoin, DictReader(petUserList));

db.session.commit();

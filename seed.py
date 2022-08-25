from csv import DictReader;
from app import db;
from models import User, Role, RoleTable;
from models import Pet, PetSpecie, CoatDescription, Color, Breed, PrimaryBreedTable, SecondaryBreedTable;

with open('seed/seed_user_list.csv') as userList:
    db.session.bulk_insert_mappings(User, DictReader(userList));
    # not yet completed

with open('seed/seed_role_list.csv') as roleList:
    db.session.bulk_insert_mappings(Role, DictReader(roleList));

with open('seed/seed_userRoles_list.csv') as roleTableList:
    db.session.bulk_insert_mappings(RoleTable, DictReader(roleTableList));
    # JOIN: not yet completed

with open('seed/seed_pet_list.csv') as petList:
    db.session.bulk_insert_mappings(Pet, DictReader(petList));
    # not yet completed
    
with open('seed/seed_petSpecie_list.csv') as petSpecieList:
    db.session.bulk_insert_mappings(PetSpecie, DictReader(petSpecieList));

with open('seed/seed_petCoatDescription_list.csv') as petCoatDescriptionList:
    db.session.bulk_insert_mappings(CoatDescription, DictReader(petCoatDescriptionList));

with open('seed/seed_petColor_list.csv') as colorsList:
    db.session.bulk_insert_mappings(Color, DictReader(colorsList));

with open('seed/seed_breed_list.csv') as breedList:
    db.session.bulk_insert_mappings(Breed, DictReader(breedList));

with open('seed/seed_primaryBreed_list.csv') as primaryBreedTable:
    db.session.bulk_insert_mappings(PrimaryBreedTable, DictReader(primaryBreedTable));
    # JOIN: not yet completed

with open('seed/seed_secondaryBreed_list.csv') as secondaryBreedTable:
    db.session.bulk_insert_mappings(SecondaryBreedTable, DictReader(secondaryBreedTable));
    # JOIN: not yet completed

db.session.commit();

# based on `../models.py`

role
-
id smallint PK				# double check smallserial?
role_name varchar(16)
	# only place if it is: admin, rescueagency, lister
	# skip out if the role is "user"

users
-
username text pk
encrypted_password text
first_name text
	# limit to 32 in Form
last_name text nullable
	# limit to 32 in Form
email varchar(320)
	# https://www.rfc-editor.org/errata/eid1690; publicly viewable if is_lister
description varchar(512) nullable
	# 512 character description
image_url text				# default='_defaultUser.jpg'
is_elevated boolean			# default false
	# do not show on `forms.py` to register

usersrole_join
	# user_role_join
-
user_username text FK - users.username		# pk, cascade on update, delete
role_id smallint FK - role.id				# pk, cascade on update, delete

coatdescription
	# coat_description
-
id smallint PK
	# 0-10 straight, mixed, curly, bald? defaults to straight; this should be linked to breed but idk maybe conditions change the pet's hair style 
	# 100+: coat patterns?
coat_detail_name varchar(16)	# first 16 charas no more.

petspecie
	# pet_specie
-
id smallint pk
	# 0-100 {common_mammals: dog, cat (0-2), ...}; bird (Aves); reptile (Squamata, Testudines, Crocodilia for FL man, ...); 
	# fish (Actinopterygii & Chondrichthyes); amphibia (axolotl, frog) plants (lol)
pet_name varchar(16)
specie_fa text
	# trollololol: find a FL icon for 'gator

breed
-
id smallint PK
	# All (Search): 0
	# Cat Breeds: 1 - 1000
	# Dog Breeds: 1001 - 2000
	# Plants: 2001 - 3000 (really just: decorative tree, fruit tree, indoor non-tree, outdoor non-tree)
	# Birds, Amphibians, etc. are not given categorization
breed_name text
breed_image text nullable	# default = 'default_pet.png'

color
-
id smallint pk
	#	All (Search): 0
	#	Light Colors: 1 - 100
	#	Dark Colors: 101 - 200
	#	Unknown: 999
color_name varchar(16)
	# colors color available
color_hex varchar(7)
	# corresponding hex

pet
-
id bigserial PK
pet_name varchar(32)
description varchar(512) nullable
image_url text nullable							# default 'default_pet.png'
publish_time timestamp							# default datetime.utcnow()
# 
gender boolean									# T (1) for male, F (0) for female
sterilized boolean								# spayed/neutered
estimated_age smallint							# default = 0
age_certainty boolean							# default F; T (1) for estimate, F (0) for approximate (default); inject tilde if T
weight smallint									# default = 0
# 
pet_specie smallint FK -< petspecie.id			# 1 to 1, pet is parent;
coat_hair smallint fk - coatdescription.id
coat_pattern smallint fk - coatdescription.id
primary_light_shade smallint FK - color.id		# default = 0
primary_dark_shade smallint FK - color.id		# default = 0
# 
trained boolean									# default False
medical_record_uptodate boolean					# default False
special_needs text nullable

primarybreed_join
	# primary_breed_join
-
pet_id bigint FK - pet.id				# pk, CASCADE all
breed_id smallint FK - breed.id			# pk, CASCADE all

petuser_join
	# pet_users_join 
-
user_username text FK -0< users.username    # FK to users.username	# pk, CASCADE all
pet_id bigint FK - pet.id				    # FK to pet.id			# pk, CASCADE all
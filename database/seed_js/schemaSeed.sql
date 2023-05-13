-- DROP TABLE IF EXISTS primarybreed_join CASCADE, petuser_join, pet, breed, color, coatdescription, petspecie, userrole_join, role, users;-- DATABASE RELATIONS
CREATE TABLE "role" (

	"id" SMALLINT NOT NULL PRIMARY KEY,
	"role_name" VARCHAR(16) NOT NULL

);

-- only place if it is: admin, rescueagency, lister
-- skip out if the role is "user"
CREATE TABLE "users" (

	"username" TEXT NOT NULL PRIMARY KEY,
	"encrypted_password" TEXT NOT NULL,
	"first_name" VARCHAR(32) NOT NULL,
	-- limit to 32 in Form
	"last_name" VARCHAR(32),
	-- limit to 32 in Form
	"email" VARCHAR(320) NOT NULL,
	-- https://www.rfc-editor.org/errata/eid1690; publicly viewable if is_lister
	"description" VARCHAR(512),
	-- 512 character description
	-- default='_defaultUser.jpg'
	"image_url" TEXT NOT NULL
		DEFAULT '_defaultUser.jpg',
	-- default false
	"is_elevated" BOOLEAN
		DEFAULT FALSE
	
);

-- do not show on `forms.py` to register
CREATE TABLE "usersrole_join" (
	
	-- pk, cascade on update, delete
	"user_username" TEXT NOT NULL
		REFERENCES users(username) ON DELETE CASCADE,
	-- pk, cascade on update, delete
	"role_id" SMALLINT NOT NULL
		REFERENCES role(id),
	PRIMARY KEY ("user_username", "role_id")

);

CREATE TABLE "coatdescription" (

	"id" SMALLINT NOT NULL PRIMARY KEY,
	-- 0-10 straight, mixed, curly, bald? defaults to straight; this should be linked to breed but idk maybe conditions change the pet's hair style
	-- 100+: coat patterns?
	-- first 16 charas no more.
	"coat_description" TEXT NOT NULL

);

CREATE TABLE "petspecie" (

	"id" SMALLINT NOT NULL PRIMARY KEY,
	-- 0-100 {common_mammals: dog, cat (0-2), ...}; bird (Aves); reptile (Squamata, Testudines, Crocodilia for FL man, ...);
	-- fish (Actinopterygii & Chondrichthyes); amphibia (axolotl, frog) plants (lol)
	"specie_name" VARCHAR(16) NOT NULL,
	"specie_fa" TEXT NOT NULL
		-- trollololol: find a FL icon for 'gator

);

CREATE TABLE "breed" (

	"id" SMALLINT NOT NULL PRIMARY KEY,
	-- All (Search): 0
	-- Cat Breeds: 1 - 1000
	-- Dog Breeds: 1001 - 2000
	-- Plants: 2001 - 3000 (really just: decorative tree, fruit tree, indoor non-tree, outdoor non-tree)
	-- Birds, Amphibians, etc. are not given categorization
	"breed_name" TEXT NOT NULL,
	-- default = 'default_pet.png'
	"breed_image" TEXT DEFAULT 'default_pet.png'

);

CREATE TABLE "color" (
	
	"id" SMALLINT NOT NULL PRIMARY KEY,
	-- All (Search): 0
	-- Light Colors: 1 - 100
	-- Dark Colors: 101 - 200
	-- Unknown: 999
	"color_name" VARCHAR(16) NOT NULL,
	-- colors color available
	"color_hex" VARCHAR(7) NOT NULL
	-- corresponding hex

);

CREATE TABLE "pet" (

	"id" BIGSERIAL NOT NULL PRIMARY KEY,
	"pet_name" VARCHAR(32) NOT NULL,
	"description" VARCHAR(512),
	-- default 'default_pet.png'
	"image_url" TEXT
		DEFAULT 'default_pet.png',
	-- default datetime.utcnow()
	"publish_time" DATE
		DEFAULT CURRENT_DATE,
	-- T (1) for male, F (0) for female
	"gender" BOOLEAN NOT NULL,
	-- spayed/neutered
	"sterilized" BOOLEAN NOT NULL,
	-- default = 0
	"estimated_age" SMALLINT NOT NULL,
	-- default F; T (1) for estimate, F (0) for approximate (default); inject tilde if T
	"age_certainty" BOOLEAN
		DEFAULT FALSE,
	-- default = 0
	"weight" SMALLINT DEFAULT 0,
	-- 1 to 1, pet is parent;
	"pet_specie" SMALLINT NOT NULL
		REFERENCES "petspecie" ("id"),
	"coat_hair" SMALLINT NOT NULL
		REFERENCES "coatdescription" ("id"),
	"coat_pattern" SMALLINT NOT NULL
		REFERENCES "coatdescription" ("id"),
	-- default = 0
	"primary_light_shade" SMALLINT
		DEFAULT 0
		REFERENCES "color" ("id"),
	-- default = 0
	"primary_dark_shade" SMALLINT
		DEFAULT 0
		REFERENCES "color" ("id"),
	-- default False
	"trained" BOOLEAN
		DEFAULT FALSE,
	-- default False
	"medical_records_uptodate" BOOLEAN
		DEFAULT FALSE,
	"special_needs" TEXT

);

CREATE TABLE "primarybreed_join" (

	-- pk, CASCADE all
	"pet_id" BIGINT NOT NULL
		REFERENCES "pet" ("id") ON DELETE CASCADE,
	-- pk, CASCADE all
	"breed_id" SMALLINT NOT NULL
		REFERENCES "breed" ("id"),
	PRIMARY KEY ("pet_id", "breed_id")

);

CREATE TABLE "petuser_join" (

	-- FK to users.username
	"user_username" TEXT NOT NULL
		REFERENCES "users" ("username") ON DELETE CASCADE,
	-- FK to pet.id
	"pet_id" BIGINT NOT NULL
		REFERENCES "pet" ("id") ON DELETE CASCADE,
	PRIMARY KEY ("user_username", "pet_id")

);
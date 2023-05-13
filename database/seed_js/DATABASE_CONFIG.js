/**	Object: CONFIGURATION_OBJ
 *	@param {Object} CONFIGURATION_OBJ A database output configuration object.
 *	@param {Object} CONFIGURATION_OBJ.relationNames arr, names of the relations in the db; sorted from independent to dependent
 *	@param {Object} CONFIGURATION_OBJ.baseSeedFileName str, base seed output file name (contains references to table and seed output files)
 *	@param {Object} CONFIGURATION_OBJ.tableOutputFileName str, table output file name
 *	@param {Object} CONFIGURATION_OBJ.seedOutputFileName str, seed output file name
 */
const CONFIGURATION_OBJ = {

	databaseName: 'testsetststs',
	relationNames: [
		'users',
		'role',
		'userrole_join',
		'petspecie',
		'coatdescription',
		'color',
		'breed',
		'pet',
		'petuser_join',
		'primarybreed_join'
	],
	baseSeedFileName: 'baseSeed.sql',
	tableOutputFileName: 'schemaSeed.sql',
	seedOutputFileName: 'contentSeed.sql'

}

module.exports = {
	CONFIGURATION_OBJ
};
//	CJS T_T

/*
'seed_petBreed_list.csv',
'seed_petCoatDescription_list.csv',
'seed_petColor_list.csv',
'seed_pet_list.csv',
'seed_petSpecie_list.csv',
'seed_petUser_list.csv',
'seed_primaryBreed_list.csv',
'seed_role_list.csv',
'seed_user_list.csv',
'seed_userRoles_list.csv'

	__tablename__ = 'users';
	__tablename__ = 'role';
	__tablename__ = 'userrole_join';
	__tablename__ = 'petspecie';
	__tablename__ = 'coatdescription';
	__tablename__ = 'color';
	__tablename__ = 'breed';  
	__tablename__ = 'pet';
	__tablename__ = 'petuser_join';
	__tablename__ = 'primarybreed_join';
	
	
	'users',
	'role',
	'userrole_join',
	'petspecie',
	'coatdescription',
	'color',
	'breed',
	'pet',
	'petuser_join',
	'primarybreed_join'
*/

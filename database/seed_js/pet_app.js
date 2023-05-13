//	LIBRARIIES & MODULES
const fs = require('fs');
const csvParser = require('csv-parser');

//	CONFIGURATION FILE
const { CONFIGURATION_OBJ } = require('./DATABASE_CONFIG.js');
// const { databaseName, relationNames, baseSeedFileName, tableOutputFileName, seedOutputFileName } = CONFIGURATION_OBJ;
	//	._.; ESM: config as CONFIG..., this CJS: config: CONFIG...

//	GLOBAL VARIABLES
let RELATIONS_HEADER = {};
let RELATIONS_DATA = {};
let FILES_READ = 0;

/**	writeDatabaseSeedFile()
 *	Write the database seed file from global state, impurely.
 *	@type void
 *	@returns undefined
 */
function writeDatabaseSeedFile(){

	// Read all CSVs into state.
	if(FILES_READ !== CONFIGURATION_OBJ.relationNames.length - 1){
		FILES_READ++;
		return;
	}

	/**	Write the base file.	*/
	const writerStreamBaseFile = fs.createWriteStream(`${CONFIGURATION_OBJ.baseSeedFileName}`/*, {flags: 'a'}*/);
	writerStreamBaseFile.write(`--	SETUP\nDROP DATABASE IF EXISTS ${CONFIGURATION_OBJ.databaseName};\nCREATE DATABASE ${CONFIGURATION_OBJ.databaseName};\n\\c ${CONFIGURATION_OBJ.databaseName};\n\n`);
	writerStreamBaseFile.write(`\n\\i ${CONFIGURATION_OBJ.tableOutputFileName}\n\\i ${CONFIGURATION_OBJ.seedOutputFileName}`)	
	writerStreamBaseFile.end();

	/**	Write the table file (database schema).	*/
	const writerStreamTableFile = fs.createWriteStream(`${CONFIGURATION_OBJ.tableOutputFileName}`/*, {flags: 'a'}*/);

	//	DROP EXISITING DB: from most to least dependent (least to most independent)
	let dropRelationsString = CONFIGURATION_OBJ.relationNames.reduceRight((prev, element, index) => {

		if(index !== 0){
			return prev.concat(`${element}, `)
		}

		return prev.concat(`${element};`);

	}, 'DROP TABLE IF EXISTS ');
	writerStreamTableFile.write(dropRelationsString);
	
	//	DATABASE RELATIONS
	writerStreamTableFile.write('-- DATABASE RELATIONS\n');
	for (let relationName of CONFIGURATION_OBJ.relationNames){
	
		writerStreamTableFile.write(`--\t${relationName}\nCREATE TABLE ${relationName} (\n\n\t--properties\n\n);`);
		writerStreamTableFile.write('\n\n');
	
	}

	// writerStreamTableFile.write('\n');
	writerStreamTableFile.end();

	/**	Write the seed file.	*/
	const writerStreamSeedFile = fs.createWriteStream(`${CONFIGURATION_OBJ.seedOutputFileName}`);
	writerStreamSeedFile.write('--	DATABASE SEEDING');
	writerStreamSeedFile.write(`-- understood: \`"\` is for column names, \`'\` is for data\n\t-- boolean: expect: TRUE / FALSE without quotes\n\t-- date: expect with single-quotes to not be parsed as integers\n`);

	for (let relationName of CONFIGURATION_OBJ.relationNames){
		
		const newHeaders = RELATIONS_HEADER[relationName][0];
		// const newHeaders = RELATIONS_HEADER[relationName][0].filter((element) => element !== 'id');
			// remove 'id' attributes that are `SERIAL`sql
	
		writerStreamSeedFile.write(`INSERT INTO ${relationName}(`);
		writerStreamSeedFile.write(`${newHeaders}`)
		// column name(s)
		// for(let __ of .split(','))
		writerStreamSeedFile.write(`)\n\tVALUES`);
		// value(s)
		writerStreamSeedFile.write(`\n\t`);

		for(let i = 0; i < RELATIONS_DATA[relationName].length; i++){
			
			// if(RELATIONS_DATA[relationName][i].id)
				// delete RELATIONS_DATA[relationName][i].id;

			const stringifiedRecord = Object.values(RELATIONS_DATA[relationName][i]).join(',');

			if(i !== RELATIONS_DATA[relationName].length - 1){
				writerStreamSeedFile.write(`(${stringifiedRecord}),\n\t`);
			}else{
				writerStreamSeedFile.write(`(${stringifiedRecord});\n\t`);
			}
			
		}
		
		writerStreamSeedFile.write('\n');

	}

	writerStreamSeedFile.end();

}

/**	readCSVs()
 *	Reads the input CSV files.
 *	@type Promise<void>
 *	@returns undefined
 */
async function readCSVs(){

	for (let relationName of CONFIGURATION_OBJ.relationNames){

		RELATIONS_HEADER[relationName] = [];
		RELATIONS_DATA[relationName] = [];

		fs.createReadStream(`seed_${relationName}.csv`)
			.pipe(csvParser())
			.on('headers', (header) => RELATIONS_HEADER[relationName].push(header))
			.on('data', (data) => RELATIONS_DATA[relationName].push(data))
			.on('close', () => writeDatabaseSeedFile());

	}

}

readCSVs();

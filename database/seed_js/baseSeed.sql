--	SETUP
DROP DATABASE IF EXISTS sb_29_capstone_project_petsearch;
CREATE DATABASE sb_29_capstone_project_petsearch;
\c sb_29_capstone_project_petsearch;


\i schemaSeed.sql
\i contentSeed.sql
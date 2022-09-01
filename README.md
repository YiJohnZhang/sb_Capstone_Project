# 01. Introduction
The project, "PetSearch" is a concept Pet Adoption website that provides a front-end for:
- **Users** to both **search for pets** and contact pet rescue organizations about interest in pets for adoption, and
- **Pet Rescue Organizations**, private or public, to both **manage their database of pets with a GUI** and **allow users to search their listed pets**.

**PetSearch** is a full-stack application with the following features:
- Full-Stack application built using JavaScript, Flask, and PostgreSQL.
- Features public, user, and restricted elevated (Pet Rescue Organization and Admins) routes.
- Features API endpoints for returning JSON.

The motivation for **PetSearch** is that:
1) ~6.3 mn companion animals ("pets", dogs and cats) entered a pet shelter as of 2019<sup>[1]</sup> and at any given time, there are an estimated 70 mn strays roaming on US streets alone<sup>[2]</sup>. 920,000 were euthanized in 2019 alone<sup>[1]</sup>.
2) There are a total of ~3,500 municipal shelters and ~10,500 "animal rescue organizations", consisting mostly of privately- and mixed-funded pet shelters, in the United States<sup>[2]</sup>. In total, it is claimed that U.S. taxpayers directly fund animal shelters ~$1-2 bn/yr (0.03% USA FY2020 Budget, 0.01% USA 2020 GDP)<sup>[2]</sup>.
3) Most of these shelters<sup>[3]</sup>, even if they have an Excel Spreadsheet equivalent or better ("database system"), unlikely has a robust database search system for users to search their database to find a pet within their search parameters. **PetSearch** fulfills that demand so that:
    - **Animal rescue organizaions** may focus on taking care of pets searching for a home and improving adoption rates. Because animal rescue organizations won't have to spend resources to find and/or keep a technical individual, say a software engineer, to setup and/or manage their database that makes it easier for
    - **Users** to easily search for pets listed for adoption.

## Source(s):
[1] Unknown. *Pet Statistics*. **American Society for the Prevention of Cruelty to Animals**. https://www.aspca.org/helping-people-pets/shelter-intake-and-surrender/pet-statistics (retrieved 2022-08-30)

[2] Cvetkovska, L. *44 Shocking Animal Shelter Statistics (2022 Update)*. **petpedia.co**. https://petpedia.co/animal-shelter-statistics/#14,000%20shelters%20and%20rescue%20groups (updated 2022-02-18, retrieved 2022-08-30)

[3] **Dude trust me**.

# 02. User Flow
## 02.01. Public Routes
- Login, Register, Request Rescue Organization Account
> ***insertGIF***
- Search Pets
> ***insertGIF***
- View Pets
> ***insertGIF***

## 02.02. (Non-Elevated) User Route
All of **Public Routes** and additional tasks:
- Edit User Profile
> ***insertGIF***
- *Not Implemented*: Send Messages to other Users and Favorite Pets

## 02.03 (Elevated) User Route
All of **(Non-Elevated) User Routes** and a Database Management System, depending on the elevated user type:
- Pet Rescue Organizations ("rescueAgency") can only manage pets they have listed (edit and delete) or add new pets to the database.
> ***insertGIF***
- Administrators ("admin") can remove any pet(s) from the database and remove any non-admin user(s) from the database.
> ***insertGIF***

## 02.04. Features Teased but **NOT** Implemented
- General
    - Request Rescue Organization Account (i.e. sends a message to an administrator for approval and manual creation of a database account)
	- Toggle Favorite (pet)
	- See Favorite pets
	- Message (user/about pet)
	- Report (pet)
- Elevated User Commands (Rescue Agency)
	- Import Database as CSV
	- Export Database as CSV
	- Toggle "Pet Adopted"
- Elevated User Commands (Admin)
	- Ban (user)

# 03. Future Developments
If I had more time beyond the 2 weeks to both work on and document this project, I would have:
- Database Redesign: A design decision that I made early on in the schema design to reduce space-complexity that introduces one inconvenience to maintain the code base (`app.py: petView:`line `` to ``)
- UI: Made the Elevated User UI more pretty. Ad tooltips to the UI.
- User signup has email verification for non-elevated users and location verification (for rescue organization).
- Change user password.
- Search categories: search by rescue organization and more pet search parameters.
- User interaction, such as `Direct Messagse`, and `Favorites`.
- Administrator QOL improvements, a search feature in the administrator panel:
    - Rescue Organizations
	    - Query and sort their pet listings by pet name, gender, pet specie, pet breed, coat hair type, coat pattern, primary light shade, primary dark shade.
    - Administrators
	    - Query and sort users by rescue organization, `LIKE`sql username, `LIKE`sql last name/first name, account status (not a database attribute, i.e. banned or active), complaints (not a database attribute)
- API key and API routes to support widgets for rescue organizations to display a search method on their website.

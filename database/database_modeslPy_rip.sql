
    __tablename__ = 'users';

    username = db.Column(db.Text, nullable = False, unique = True, primary_key = True);
        # limit to 32 in Form
    encrypted_password = db.Column(db.Text, nullable = False);
    first_name = db.Column(db.Text, nullable = False);
        # if is_elevated, String(128), in `forms.py` make it Length(max=32) 
    last_name = db.Column(db.Text, nullable = True);
        # limit to 32 in Form
        # if is_elevated, it is Null, in `forms.py` make it InputRequired() because normal user cannot get elevated priviledges
    email = db.Column(db.Text, nullable = False);
    description = db.Column(db.Text, nullable = True);
        # limit to 512 in Form
    image_url = db.Column(db.Text, nullable = False, default='_defaultUser.jpg')
    is_elevated = db.Column(db.Boolean, nullable = False, default = False);
        # do not show on `forms.py` to register




    __tablename__ = 'role';

    id = db.Column(db.SmallInteger, primary_key = True);
    role_name = db.Column(db.String(16), nullable = False);



    __tablename__ = 'userrole_join';

    user_username = db.Column(
        db.String(32), 
        db.ForeignKey(User.username, ondelete='CASCADE', onupdate='CASCADE'),
        primary_key = True);
    role_id = db.Column(db.SmallInteger, 
        db.ForeignKey(Role.id, ondelete='CASCADE', onupdate='CASCADE'),
        primary_key = True);

    userReference = db.relationship('User', backref=db.backref('userAlias', cascade='all, delete'));
    roleReference = db.relationship('Role', backref=db.backref('roleJoinAlias', cascade='all, delete'));


    __tablename__ = 'petspecie';

    id = db.Column(db.SmallInteger, primary_key = True);    # not smallserial
    specie_name = db.Column(db.String(16), nullable = False);
    specie_fa = db.Column(db.Text, nullable = False);


    __tablename__ = 'coatdescription';
    
    id = db.Column(db.SmallInteger, primary_key = True);    # smallint
    coat_description = db.Column(db.Text, nullable = False);




    __tablename__ = 'color';

    id = db.Column(db.SmallInteger, primary_key = True);    # not smallserial
        #   All (Search): 0
        #   Light Colors: 1 - 100
        #   Dark Colors: 101 - 200
        #   Unknown: 999
    color_name = db.Column(db.String(16), nullable = False);
    color_hex = db.Column(db.String(7), nullable = False);

-- breed
    __tablename__ = 'breed';

    id = db.Column(db.SmallInteger, primary_key = True);    # not smallserial
        # All (Search): 0
        # Cat Breeds: 1 - 1000
        # Dog Breeds: 1001 - 2000
        # Plants: 2001 - 3000 (really just: decorative tree, fruit tree, indoor non-tree, outdoor non-tree)
        # Birds, Amphibians, etc. are not given categorization
    breed_name = db.Column(db.Text, nullable = False);
    breed_image = db.Column(db.Text, nullable = True, default = 'default_pet.png');



    
    __tablename__ = 'pet';

    id = db.Column(db.BigInteger, autoincrement = True, primary_key = True);
    pet_name = db.Column(db.Text, nullable = False);    # 2022-08-31: probably should've just called this 'name' ._.
        # limit the character in form (32)
    description = db.Column(db.Text, nullable = True);
        # limit the character in form (512)
    image_url = db.Column(db.Text, nullable = True, default = 'default_pet.png');
    publish_time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow());
    gender = db.Column(db.Boolean, nullable = False);
        # F => Female, T => Male,
    sterilized = db.Column(db.Boolean, nullable = False);
    estimated_age = db.Column(db.Integer, nullable = False, default = 0)
    age_certainty = db.Column(db.Boolean, nullable = False, default = False);
        # F => Unsure, T => Sure
    weight = db.Column(db.Integer, nullable = False, default = 0);

    pet_specie = db.Column(db.SmallInteger, 
        db.ForeignKey(PetSpecie.id));
    coat_hair = db.Column(db.SmallInteger, 
        db.ForeignKey(CoatDescription.id));
    coat_pattern = db.Column(db.SmallInteger, 
        db.ForeignKey(CoatDescription.id));
    primary_light_shade = db.Column(db.SmallInteger, 
        db.ForeignKey(Color.id), default = 0);
    primary_dark_shade = db.Column(db.SmallInteger, 
        db.ForeignKey(Color.id), default = 0);

    trained = db.Column(db.Boolean, nullable = False, default = False);
    medical_record_uptodate = db.Column(db.Boolean, nullable = False, default = False);
    special_needs = db.Column(db.Text, nullable = True);

    userPetThrough = db.relationship('User',
        secondary='petuser_join',
        backref='petUserThrough');





    __tablename__ = 'petuser_join';

    user_username = db.Column(db.Text, db.ForeignKey(User.username, ondelete='CASCADE', onupdate='CASCADE'), primary_key = True);
    pet_id = db.Column(db.BigInteger, db.ForeignKey(Pet.id, ondelete='CASCADE', onupdate='CASCADE'), primary_key = True);

    userReference = db.relationship('User', backref=db.backref('userJoinAlias', cascade='all, delete'));
    petReference = db.relationship('Pet', backref=db.backref('petJoinAlias', cascade='all, delete'));
        # Todo: through relationship unnecessary?






    __tablename__ = 'primarybreed_join';
    
    pet_id = db.Column(db.BigInteger, db.ForeignKey(Pet.id, ondelete='CASCADE', onupdate='CASCADE'), primary_key = True);
        # retrosepct: pet_id should be UNIQUE
    breed_id = db.Column(db.SmallInteger, db.ForeignKey(Breed.id), primary_key = True);
        # 0 is unknown.

    petReference = db.relationship('Pet', backref=db.backref('petAlias', cascade='all, delete'));
    breedReference = db.relationship('Breed', backref=db.backref('breedAlias'));

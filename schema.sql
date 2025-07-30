CREATE TABLE LBA_TYPE_VOCABULAIRE (
    id_type SERIAL PRIMARY KEY,
    type VARCHAR(255)
);


CREATE TABLE LBA_LESSON_VOCABULAIRE (
    id_lesson SERIAL PRIMARY KEY,
    lesson VARCHAR(255)
);

/

CREATE TABLE LBA_UNIT_VOCABULAIRE (
    id_unit SERIAL PRIMARY KEY,
    unit VARCHAR(255)
);
/

CREATE TABLE LBA_VOCABULAIRE (
    id_voc SERIAL PRIMARY KEY,
    id_unit INTEGER REFERENCES LBA_UNIT_VOCABULAIRE(id_unit),
    id_lesson INTEGER REFERENCES LBA_LESSON_VOCABULAIRE(id_lesson),
    id_type INTEGER REFERENCES LBA_TYPE_VOCABULAIRE(id_type),
    voc_coreen VARCHAR(255),
    voc_traduction VARCHAR(255),
    exemple_coreen VARCHAR(255),
	exemple_traduit VARCHAR(255),
    date_ajout DATE DEFAULT CURRENT_DATE
);
/

INSERT INTO LBA_VOCABULAIRE (
    id_unit,
    id_lesson,
    id_type,
    voc_coreen,
    voc_traduction,
    exemple_coreen,
	exemple_traduit
) VALUES (
    1,
    1,
    1,
    '한국 ',
    'Corée',
    '한국은 아름다운 나라예요',
	'La Corée est un jolie pays'
);

/

create or replace view LBAV_VOCABULAIRE as
select lu.unit,lvoc.lesson,lt.type, voc.voc_coreen,voc.voc_traduction,voc.exemple_coreen,voc.exemple_traduit from LBA_VOCABULAIRE voc 
inner join LBA_LESSON_VOCABULAIRE lvoc on lvoc.id_lesson = voc.id_lesson
inner join LBA_UNIT_VOCABULAIRE lu on lu.id_unit = voc.id_unit
inner join LBA_TYPE_VOCABULAIRE lt on lt.id_type = voc.id_type
;

/
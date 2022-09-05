import time
import datetime
import sqlite3

con = sqlite3.connect("lovebox")
cursor = con.cursor()

cursor.execute('DROP TABLE IF EXISTS tratamento')

cursor.execute('''
    CREATE TABLE medicamentos(id INTEGER PRIMARY KEY AUTOINCREMENT
    , paciente TEXT
    , medicamento TEXT
    , dosagem NUMERIC
    , um TEXT
    , compartimento NUMERIC
    , statusTratamento NUMERIC);
''')
con.commit()

cursor.execute('''
    CREATE TABLE horarios( idHorario INTEGER PRIMARY KEY AUTOINCREMENT
    , id INTEGER
    , horarioMedicacao TIMESTAMP
    , tempoLimite TIMESTAMP
    , statusIngestao NUMERIC
    , statusSincronizacao NUMERIC);
''')
con.commit()

cursor.execute('''
    INSERT INTO medicamentos (paciente
    , medicamento
    , dosagem
    , um
    , compartimento 
    , statusTratamento) 
    VALUES ('Daniela'
    , 'Vitamina'
    , 1
    , 'ml'
    , 0
    , 1);
''')
con.commit()

cursor.execute('''
    INSERT INTO medicamentos (paciente
    , medicamento
    , dosagem
    , um
    , compartimento 
    , statusTratamento) 
    VALUES ('Daniela'
    , 'Antibiotico'
    , 1
    , 'ml'
    , 1
    , 1);
''')
con.commit()

cursor.execute('''
    INSERT INTO horarios (id
    , horarioMedicacao
    , tempoLimite
    , statusIngestao
    , statusSincronizacao) 
    VALUES ('1'
    , '13:00'
    , '13:30'
    , 0
    , 1);
''')
con.commit()

cursor.execute('''
    INSERT INTO horarios (id
    , horarioMedicacao
    , tempoLimite
    , statusIngestao
    , statusSincronizacao) 
    VALUES ('2'
    , '08:00'
    , '08:20'
    , 0
    , 1);
''')
con.commit()
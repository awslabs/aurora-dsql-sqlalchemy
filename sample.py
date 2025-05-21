from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

import os

envuser = os.getenv('PGUSER', 'admin')
envpwd = os.getenv('PGPASSWORD', '')
envhost = os.getenv('PGHOST', 'localhost')
envdb = os.getenv('PGDATABASE', 'postgres')
envsslmode = os.getenv('PGSSLMODE', 'disable')
envpost = os.getenv('PGPORT', '5432')
envoptions = os.getenv('PGOPTIONS', '')

url = URL.create("aurora_dsql+psycopg2", username=envuser, password=envpwd, host=envhost, database=envdb, 
query={'options': envoptions})
print(f"URL: {url}")
    
options = {}
engine = create_engine(url, **options, connect_args={'sslmode': envsslmode}, echo=True)

with engine.connect() as conn:
    conn.begin()
    result =  conn.execute(text('select * from "information_schema"."tables"'))
    print(result.fetchone())
    conn.commit()





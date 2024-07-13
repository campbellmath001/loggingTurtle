from datetime import datetime, timedelta
from pathlib import Path
import logging
import sqlite3
import pandas as pd
import sys

# entityName is used to name the directories and database where the logged information is stored
entityName = "FFPD"

# Get the current working directory
current_dir = Path.cwd()
home_dir = Path.home()

def verify_Path(test_Path):
    if not test_Path.exists():
        # create the directory
        try:
            test_Path.mkdir(parents=True)
            print(f"Directory created at {test_Path.absolute()}")
        except Exception as e:
            print(f'an error has occured when verifying the file structure: {e}')
            sys.exit(1)


path_List = [
    entityHome := (current_dir / f"{entityName}"),
    log_Path := (entityHome / "Debug_Logs"),
    db_Path := (entityHome / "DataBase"),
    csv_Path := (entityHome / "csv"),
    html_Path := (home_dir / "public_html" / entityName)
]

# verify file system
for p in path_List:
    verify_Path(p)

# --setup logging

# ----format for log file
logfile = log_Path / f"{datetime.today().strftime('%M-%S-%H-%d-%m-%Y')}.log"

logger = logging.getLogger(__name__)

logging.basicConfig(filename=logfile, level=logging.DEBUG)

logger.debug(f'Logging initiated in file {logfile.absolute()}')

logger.debug(f' File System verified.')

#Set url for collecting data
url = 'http://'

#pull the website with tables into a dataframe
try:
    tables = pd.read_html(url)
    logger.debug(f'Url {url} read successful')
except Exception as e:
    logger.error(f'Error when fetching the url: {e}')
    sys.exit(1)

#select the correct table for archiving
try:
    raw_data = tables[1]
    logger.debug(f'desired table # read succesfully')
except Exception as e:
    logger.error(f'Error when choosing desired table for logging: {e}')
    sys.exit(1)

# clean up the data with a custom method chain for your data
# clean data sent to df
logger.debug('beginning data cleanup')
try:
    df = (
        raw_data
        .rename(
            columns = {'Date Time':'Incident_Time', 'inci #':'Incident_ID'}
            )
        .assign(
            Incident_Time = lambda x: pd.to_datetime(x['Incident_Time'], format ='%m/%d/%Y %I:%M:%S %p')
            )
        .sort_values(
            by = 'Incident_Time'
            )
    )
    logger.debug('Data Cleaned Successfuly')
except Exception as e:
    logger.error(f'error when cleaning data with method chain: {e}')

#write the data to the database
# --setup database
# ----set file name
db_File = entityHome / "DataBase" / f"{entityName}.db"
# ----create connection to database
try:
    db = sqlite3.connect(db_File)
    logger.debug(f'Database connected at {db_File.absolute()}')
except Exception as e:
    logger.error(f'an error occured when connecting to database: {e}')

# --write to database
try:
    #this acts as a context handler and will .commit() when succesful
    with db:
        df.to_sql('Data_Log', db, if_exists="append", index=False)
        logger.debug('Database commit successful')
except Exception as e:
    logger.error(f'an error occured when writing to the database: {e}')

# --close the database
try:
    db.close()
    logger.debug('Database Closed')
except Exception as e:
    logger.error(f'An error occured when closing the database: {e}')


# Define yesterday string for file naming
# day,month,year used to place most recent log at top
yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')

# where to write csv file and format of filename
csv_File = csv_Path / f"{yesterday}_{entityName}.csv"

# write the csv file
try:
    df.to_csv(csv_File, index=False)
    logger.debug('csv file successfuly written')
except Exception as e:
    logger.error(f'An error occured when writing csv file: {e}')

# where to write html file and format of filename
html_File = html_Path / f"{yesterday}_{entityName}.html"

# write the html fle
try:
    df.to_html(html_File, index=False)
except Exception as e:
    logger.error(f'An error occured when wirting the html file:{e}')
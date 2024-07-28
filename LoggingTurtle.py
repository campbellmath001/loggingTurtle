from datetime import datetime, timedelta
from pathlib import Path
import sys
import argparse
import logging

import adbc_driver_sqlite.dbapi
import pandas as pd
from tomlkit import dump, load
from tomlkit import datetime as tk_datetime

# -- parse command line arguments
parser = argparse.ArgumentParser()

parser.add_argument("name", type=str, help="Name of the entity to log")

parser.add_argument("-d", "--debug",
    action="store_true", help="run in a clean test environment ..entityName/Debug/")

# ---- store the command line arguments in args
args = parser.parse_args()

# load turtles.toml using tomlkit
# tomlkit represents the file as a tomldocument class which acts like a dict
with open('turtles.toml', encoding="utf-8") as f:
    entityDict = load(f)

# check that name is a valid entity
if args.name not in entityDict:
    print(f"{args.name} not in entitydict")
    # prompt for a url and not exit?
    sys.exit(1)

# -- Begin setup of file system
# entityName is used to name the directories and files where the logged information is stored
entityName = entityDict[args.name]['name']

# url for collecting data
url = entityDict[args.name]['url']

# Get the user home directory
home_dir = Path.home()


def verify_path(test_path):
    if not test_path.exists():
        # create the directory
        try:
            test_path.mkdir(parents=True)
            print(f"Directory created at {test_path.resolve()}")
        except FileExistsError as _e:
            print(f'an error has occurred when verifying the file structure: {_e}')
            sys.exit(1)

# Define the directories where the data will be placed
entityHome = home_dir / "loggingTurtle" / entityName
html_Path = home_dir / "public_html" / entityName

# Check if in debug mode and create a debug environment if needed
if args.debug:
    entityHome = entityHome / "Debug"
    html_Path = html_Path / "Debug"

# verify file system
path_List = [
    entityHome,
    log_Path := (entityHome / "Debug_Logs"),
    db_Path := (entityHome / "DataBase"),
    csv_Path := (entityHome / "csv"),
    html_Path
]

for p in path_List:
    verify_path(p)

# --setup logging
# ----format for log file
logfile = log_Path / f"{datetime.today().strftime('%M-%S-%H-%d-%m-%Y')}.log"

logger = logging.getLogger(__name__)

logging.basicConfig(filename=logfile, level=logging.DEBUG)

logger.debug('Logging initiated in file %s', logfile.resolve())

logger.debug('File System verified.')

# pull the website with tables into a dataframe
try:
    tables = pd.read_html(url, dtype_backend="pyarrow")
    logger.debug('Url %s read successful', url)
except Exception as e:
    logger.error('Error when fetching the url: %s', e)
    sys.exit(1)

# select the correct table for archiving
try:
    raw_data = tables[1]
    logger.debug('desired table # read successfully')
except Exception as e:
    logger.error('Error when choosing desired table for logging: %s', e)
    sys.exit(1)

# clean up the data with a custom method chain for your data
# clean data sent to df
logger.debug('beginning data cleanup')
try:
    df = (
        raw_data
        .rename(
            columns = {'Date Time': 'Incident_Time', 'inci #': 'Incident_ID'}
        )
        .assign(
            Incident_Time = (
                lambda x:
                    pd.to_datetime(x['Incident_Time'], format='%m/%d/%Y %I:%M:%S %p')
            ),
            Block = (
                lambda x:
                    x['Address'].str.split(' Block of ', expand = True)[0]
            ),
            Street = (
                lambda x:
                    x['Address'].str.split(' Block of ', expand = True)[1]
            ),
            Full_Address = (
                lambda x:
                    x['Block'] + ' ' + x['Street'] + ' Fairfield, Ca'
            )
        )
        .sort_values(
            by = 'Incident_Time'
        )
    )
    logger.debug('Data Cleaned Successfully')
except Exception as e:
    logger.error('error when cleaning data with method chain: %s', e)
    # if the data cleanse fails we should exit with an error
    sys.exit(1)

# write the data to the database
# --setup database
# ----set file name
db_File = entityHome / "DataBase" / f"{entityName}.db"
# ----create connection to database
try:
    db = adbc_driver_sqlite.dbapi.connect(str(db_File.resolve()))
    logger.debug('Database connected at %s', str(db_File.resolve()))
except Exception as e:
    logger.error('an error occurred when connecting to database: %s', e)

# --write to database
try:
    # this acts as a context handler and will .commit() when successful
    with db:
        # write clean data to Data_Log table
        df.to_sql('Data_Log', db, if_exists="append", index=False)
        logger.debug('Database commit of clean data successful')
        # write raw data to Raw_Data_Log table
        raw_data.to_sql('Raw_Data_Log', db, if_exists="append", index=False)
        logger.debug('Database commit of raw data successful')
except Exception as e:
    logger.error('an error occurred when writing to the database: %s', e)

# --close the database
try:
    db.close()
    logger.debug('Database Closed')
except Exception as e:
    logger.error('An error occurred when closing the database: %s', e)

# Define yesterday string for file naming
# day,month,year used to place most recent log at top
yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')

# where to write csv file and format of filename
csv_File = csv_Path / f"{yesterday}_{entityName}.csv"

# write the csv file
try:
    df.to_csv(csv_File, index=False)
    logger.debug('csv file successfully written')
except Exception as e:
    logger.error('An error occurred when writing csv file: %s', e)

# where to write html file and format of filename
html_File = html_Path / f"{yesterday}_{entityName}.html"

# write the html fle
try:
    df.to_html(html_File, index=False)
    logger.debug('html file successfully written')
except Exception as e:
    logger.error('An error occurred when writing the html file: %s', e)

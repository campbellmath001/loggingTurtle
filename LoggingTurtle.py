from datetime import datetime, timedelta
import logging
from pathlib import Path
import sqlite3

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

# --setup database
# ----set file name
db_File: Path = entityHome / "DataBase" / f"{entityName}.db"
# ----create connection to database
try:
    db = sqlite3.connect(db_File)
    logger.debug(f'Database connected at {db_File.absolute()}')
except Exception as e:
    logger.error(f'an error occured when connecting to database: {e}')

# Define yesterday string for file naming
# day,month,year used to place most recent log at top
yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')

#pull the data into a dataframe

#clean up the data

#write the data to the database

# where to write csv file and format of filename
csv_File = csv_Path / f"{yesterday}_{entityName}.csv"
#write the csv file

# where to write html file and format of filename
html_File = html_Path / f"{yesterday}_{entityName}.html"

#write the html fle



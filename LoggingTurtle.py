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
        test_Path.mkdir(parents=True)
        print(f"Logging directory created at {test_Path.absolute()}")


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


logfile = log_Path / f"{datetime.today().strftime('%M-%S-%H-%d-%m-%Y')}.log"

logger = logging.getLogger(__name__)

logging.basicConfig(filename=logfile, level=logging.DEBUG)

logger.debug(f'Logging initiated in file {logfile}')



db_File: Path = entityHome / "DataBase" / f"{entityName}.db"

# create connection to database
sqlite3.connect(db_File)

# yesterday sorted by day/month/year for sorting most recent
yesterday = (datetime.today() - timedelta(days=1)).strftime('%d-%m-%Y')

# where to write csv file and format of filename
csv_File = csv_Path / f"{yesterday}_{entityName}.csv"

# where to write html file and format of filename
html_File = html_Path / f"{yesterday}_{entityName}.html"

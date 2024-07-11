
#this will be the folder name where the csv files are stored
#html files stored at '~/public_html/entityName/
entityName = "FFPD"

from datetime import datetime, timedelta
import logging
from pathlib import Path

# Get the current working directory
current_dir = Path.cwd()
home_dir = Path.home()

log_Path = current_dir / "TurtleLogs" / entityName 

#check if log directory exists
if not log_Path.exists():
    #create the directory
    log_Path.mkdir(parents=True)
    print(f"Logging directory created at {log_Path.absolute()}")

logfile = log_Path / f"{datetime.today().strftime('%S-%M-%H-%d-%m-%Y')}.log"

logger = logging.getLogger(__name__)

logging.basicConfig(filename = logfile, level = logging.DEBUG)

logger.debug(f'Logging initiated in file {logfile}')

# Check if the subdirectory exists
csv_Path = current_dir / entityName
if not csv_Path.exists():
    # Create the subdirectory if it doesn't exist
    csv_Path.mkdir(parents=True)
    print(f"Subdirectory '{csv_Path}' created successfully at {csv_Path.absolute()}")
else:
    logger.debug(f'csv path at {csv_Path.absolute()} verified')
html_Path = home_dir / "public_html" / entityName

if not html_Path.exists():
    html_Path.mkdir(parents=True)
    print(f"Subdirectory '{html_Path}' created successfully at {html_Path.absolute()}")
else:
    logger.debug(f'html path at {html_Path.absolute()} verified')

#yesterday sorted by day/month/year for sorting most recent
yesterday = (datetime.today() - timedelta(days = 1)).strftime('%d-%m-%Y')

#where to write csv file and format of filename
csv_File = csv_Path / f"{yesterday}_{entityName}.csv"

#where to write html file and format of filename
html_File = html_Path / f"{yesterday}_{entityName}.html"


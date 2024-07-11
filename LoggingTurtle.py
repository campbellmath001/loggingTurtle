
#this will be the folder name where the csv files are stored
#html files stored at '~/public_html/entityName/
entityName = "FFPD"


from pathlib import Path

# Get the current working directory
current_dir = Path.cwd()
home_dir = Path.home()

# Check if the subdirectory exists
csv_Path = current_dir / entityName
if not csv_Path.exists():
    # Create the subdirectory if it doesn't exist
    csv_Path.mkdir(parents=True)
    print(f"Subdirectory '{csv_Path}' created successfully at {csv_Path.absolute()}")
else:
    print(f"Subdirectory '{csv_Path}' already exists at {csv_Path.absolute()}")

html_Path = home_dir / "public_html" / entityName

if not html_Path.exists():
    html_Path.mkdir(parents=True)
    print(f"Subdirectory '{html_Path}' created successfully at {html_Path.absolute()}")
else:
    print(f"Subdirectory '{html_Path}' already exists at {html_Path.absolute()}")

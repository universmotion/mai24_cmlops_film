
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import shutil


if os.environ["HOME"] == "/home/romain":
    data_path = Path("data")
else:
    data_path = Path("/app/data/to_ingest")
    

def main():
    date = datetime.now()
    print("## Debut de tache")
    try:
        simulation_data_path = os.path.join(data_path, date.strftime("simulation_data/%Y/%m/%d"))
        raw_data_path = os.path.join(data_path,  date.strftime("raw/%Y/%m/%d"))
        os.makedirs(raw_data_path, exist_ok=True)

        list_files_to_copy = list(Path(simulation_data_path).glob("*.csv"))
        print("## Listes des fichiers disponibles:")

        for file in list_files_to_copy:
            filename = file.name
            print("- ", filename)
            shutil.copyfile(file, os.path.join(raw_data_path, filename))

    except Exception:
        return 0
    return 1 


if __name__ == "__main__":
    main()
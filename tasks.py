from invoke import task

import sqlite3
import os
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style


GPLMLIBS = ["ana", "cap", "con", "cpd", "dio", "ics", "ind", "mpu",
            "mcu", "pwr", "rfm", "res", "reg", "xtr", "osc", "opt", "art", "swi"]
DBFILE = './database/parts.sqlite'


@task()
def create(c):
    """
    Create/Update the parts database from CSV files.
    """
    print("Creating the database from CSV files.")
    conn = sqlite3.connect(DBFILE)
    try:
        print("Processing libraries")

        table_data = []
        for lib in GPLMLIBS:
            csv_file = f'./database/g-{lib}.csv'
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                df.columns = df.columns.str.strip()  # Trim whitespaces from columns
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)  # Trim whitespaces from rows
                df.to_sql(lib, conn, if_exists='replace', index=False)
                table_data.append(
                    [lib, Fore.BLUE+str(len(df)), Fore.GREEN+"Ok"+Style.RESET_ALL])
            else:
                table_data.append(
                    [lib, Fore.BLUE+"0", Fore.Red+"Fail"+Style.RESET_ALL])

        print(tabulate(table_data, headers=[
              "Library", "Number of Components", "Status"], tablefmt="simple_outline"))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    print("Database creation process is complete. All libraries processed.")
    
@task()
def release(c, dry_run=True):
    """
    Release/Bump the version using commitizen (cz).
    
    Parameters:
    dry_run (bool): If True, perform a dry run without making any changes. Default is True.
    """
    c.run(f"cz bump {'--dry-run' if dry_run else ''}")

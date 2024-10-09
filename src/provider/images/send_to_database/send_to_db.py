from pathlib import Path
import pandas as pd
import traceback
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Union
import os


class DataSender:
    """
    Class for reading CSV files and sending them to a database.

    Attributes:
    - docs_links_tables: List of dictionaries containing the paths to CSV files and the target tables in the database.
    - dir_path: Path to the directory containing the files to be ingested.
    - dir_bad_data: Path to store CSV files containing data that wasn't injected due to errors.

    Methods:
    - get_df(doc): Retrieves a DataFrame from a file path or an existing DataFrame.
    - send_df_to_database(values, Schema): Sends a row of data to the database using the provided schema.
    - keep_bad_data_df(df, name_df): Saves non-injected data in a CSV file for analysis.
    - __call__(): Main method for ingesting files and sending the data to the database.
    """

    docs_links_tables: list = []
    dir_path: Union[str, Path] = "/app/data/to_ingest"
    dir_bad_data: Union[str, Path] = "no_injected_data"

    def __init__(
        self, docs_links_tables: dict, db_engine: Session,
        data_path: Path, dir_bad_data: Union[None, str, Path] = None
    ) -> None:
        """
        Initializes the DataSender class with the provided parameters.

        Parameters:
        - docs_links_tables: Dictionary containing the CSV files and target tables.
        - db_engine: The database session.
        - data_path: Path to the directory containing the CSV files to ingest.
        - dir_bad_data: (Optional) Path to store files containing erroneous data.
        """
        self.docs_links_tables = docs_links_tables
        self.dir_path = data_path
        self.db = db_engine
        if dir_bad_data:
            self.dir_bad_data = dir_bad_data

    def get_df(self, doc: dict) -> pd.DataFrame:
        """
        Retrieves a DataFrame from a file path or an existing DataFrame.

        Parameters:
        - doc: Dictionary containing a file path or a DataFrame.

        Returns:
        - pd.DataFrame: DataFrame with the data.

        Raises ValueError if the data type is invalid.
        """
        path_or_df = doc["path_or_df"]
        if isinstance(path_or_df, (str, Path)):
            try:
                df = pd.read_csv(os.path.join(self.dir_path, path_or_df))
                df = df.rename(columns={
                    c: c.replace(" ", "_")
                        .replace("(", "")
                        .replace(")", "")
                        .replace("-", "_")
                    for c in df.columns
                })
            except FileNotFoundError as e:
                raise ValueError(f"File not found: {e}")
            except pd.errors.EmptyDataError:
                raise ValueError(f"The file {path_or_df} is empty.")
            except Exception as e:
                raise ValueError(
                    f"Error while reading the file {path_or_df}: {e}"
                )
        elif isinstance(path_or_df, pd.DataFrame):
            df = path_or_df
        else:
            raise ValueError(
                f"Error: path_or_df is not of type DataFrame, Path, or String, found {type(path_or_df)}"
            )
        return df

    def send_df_to_database(self, values: dict, Schema) -> bool:
        """
        Inserts a row of data into the database using the provided schema.

        Parameters:
        - values: Dictionary of values to insert.
        - Schema: SQLAlchemy schema class to use for the insertion.

        Returns:
        - bool: True if the insertion is successful, False in case of error.
        """
        is_insert = True
        try:
            new_obj = Schema(**values)
            self.db.add(new_obj)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e.orig):
                print("Uniqueness error:", str(values))
            elif "foreign key constraint" in str(e.orig):
                print("Foreign key error:", str(values))
            else:
                print(f"Integrity error: {str(e.orig)}")
                is_insert = False
        except SQLAlchemyError as e:
            self.db.rollback()
            print("SQLAlchemy error:", traceback.format_exc(limit=100))
            is_insert = False
        except Exception as e:
            self.db.rollback()
            print(f"Unexpected error while inserting data: {e}")
            traceback.print_exc()
            is_insert = False
        return is_insert

    def keep_bad_data_df(self, df: pd.DataFrame, name_df: str) -> None:
        """
        Saves the non-injected data in a CSV file.

        Parameters:
        - df: DataFrame containing the non-injected rows.
        - name_df: Name of the CSV file to save.
        """
        try:
            bad_data_path = os.path.join(self.dir_path, self.dir_bad_data)
            os.makedirs(bad_data_path, exist_ok=True)
            df.to_csv(os.path.join(bad_data_path,
                      name_df + ".csv"), index=False)
        except Exception as e:
            print(f"Error while saving bad data: {e}")

    def change_type_col(df, col_types: dict):
        """
        Changes the column types according to the dict col_types in a pandas DataFrame.
        """
        for col, type_col in col_types.items():
            if type_col == "timestamp":
                df[col] = pd.to_datetime(df[col], unit="s")
        return df

    def __call__(self) -> None:
        """
        Main method for reading files and sending data to the database.
        For each document in `docs_links_tables`, it tries to ingest the data and handle errors.
        The non-injected data is stored in a separate CSV file.
        """
        for doc in self.docs_links_tables:
            try:
                list_bad_iter = []
                print("## Start injecting table:", doc["path_or_df"])
                df = self.get_df(doc)
                if "change_col_type" in list(doc.keys()):
                    df = DataSender.change_type_col(df, doc["change_col_type"])
                list_dict = df.to_dict(orient="records")
                for iter, row in enumerate(list_dict):
                    is_commit = self.send_df_to_database(row, doc["schema"])
                    if not is_commit:
                        list_bad_iter.append(iter)
                if list_bad_iter:
                    self.keep_bad_data_df(
                        df.iloc[list_bad_iter], doc["schema"].__tablename__)
                print("## Finished injection")
            except ValueError as ve:
                print(f"Error in file {doc['path_or_df']}: {ve}")
            except Exception as e:
                print(
                    f"Unexpected error processing document {doc['path_or_df']}: {e}"
                )
                traceback.print_exc()

from pathlib import Path
import pandas as pd
import traceback
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Union
import os


class DataSender:
    """
    Classe pour lire des fichiers CSV et les envoyer vers une base de données.

    Attributs :
    - docs_links_tables : Liste de dictionnaires contenant les chemins vers les fichiers CSV et les tables cibles dans la base de données.
    - dir_path : Chemin vers le répertoire des fichiers à ingérer.
    - dir_bad_data : Chemin pour stocker les fichiers CSV contenant des données non injectées en raison d'erreurs.

    Méthodes :
    - get_df(doc) : Récupère un DataFrame à partir d'un chemin ou d'un DataFrame existant.
    - send_df_to_database(values, Schema) : Envoie une ligne de données vers la base de données en utilisant le schéma donné.
    - keep_bad_data_df(df, name_df) : Sauvegarde les données non injectées dans un fichier CSV pour analyse.
    - __call__() : Méthode principale pour ingérer les fichiers et envoyer les données à la base de données.
    """

    docs_links_tables: list = []
    dir_path: Union[str, Path] = "/app/data/to_ingest"
    dir_bad_data: Union[str, Path] = "no_injected_data"

    def __init__(
        self, docs_links_tables: dict, db_engine: Session,
        data_path: Path, dir_bad_data: Union[None, str, Path] = None
    ) -> None:
        """
        Initialise la classe DataSender avec les paramètres fournis.

        Paramètres :
        - docs_links_tables : Dictionnaire contenant les fichiers CSV et les tables cibles.
        - db_engine : Session de la base de données.
        - data_path : Chemin vers le répertoire contenant les fichiers CSV à ingérer.
        - dir_bad_data : (Optionnel) Chemin pour stocker les fichiers contenant des données erronées.
        """
        self.docs_links_tables = docs_links_tables
        self.dir_path = data_path
        self.db = db_engine

        if dir_bad_data:
            self.dir_bad_data = dir_bad_data

    def get_df(self, doc: dict) -> pd.DataFrame:
        """
        Récupère un DataFrame à partir d'un chemin de fichier ou d'un DataFrame existant.

        Paramètres :
        - doc : Dictionnaire contenant un chemin vers un fichier ou un DataFrame.

        Retourne :
        - pd.DataFrame : DataFrame correspondant aux données.

        Lève une ValueError si le type de données est invalide.
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
                }
                )
            except FileNotFoundError as e:
                raise ValueError(f"Fichier non trouvé : {e}")
            except pd.errors.EmptyDataError:
                raise ValueError(f"Le fichier {path_or_df} est vide.")
            except Exception as e:
                raise ValueError(
                    f"Erreur lors de la lecture du fichier {path_or_df}: {e}")

        elif isinstance(path_or_df, pd.DataFrame):
            df = path_or_df

        else:
            raise ValueError(
                f"Error: path_or_df is not of type DataFrame, Path, or String, found {type(path_or_df)}"
            )

        return df

    def send_df_to_database(self, values: dict, Schema) -> bool:
        """
        Insère une ligne de données dans la base de données en utilisant le schéma donné.

        Paramètres :
        - values : Dictionnaire des valeurs à insérer.
        - Schema : Classe de schéma SQLAlchemy à utiliser pour l'insertion.

        Retourne :
        - bool : True si l'insertion est réussie, False en cas d'erreur.
        """
        is_insert = True
        try:
            new_obj = Schema(**values)
            self.db.add(new_obj)
            self.db.commit()

        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e.orig):
                print("Erreur unicité :", str(values))
            elif "foreign key constraint" in str(e.orig):
                print("Erreur clé étrangère :", str(values))
            else:
                print(f"Erreur d'intégrité : {str(e.orig)}")
                is_insert = False

        except SQLAlchemyError as e:
            self.db.rollback()
            print("Erreur SQLAlchemy:", traceback.format_exc(limit=100))
            is_insert = False

        except Exception as e:
            self.db.rollback()
            print(f"Erreur inattendue lors de l'insertion des données : {e}")
            traceback.print_exc()
            is_insert = False

        return is_insert

    def keep_bad_data_df(self, df: pd.DataFrame, name_df: str) -> None:
        """
        Sauvegarde les données non injectées dans un fichier CSV.

        Paramètres :
        - df : DataFrame contenant les lignes non injectées.
        - name_df : Nom du fichier CSV à sauvegarder.
        """
        try:
            bad_data_path = os.path.join(self.dir_path, self.dir_bad_data)
            os.makedirs(bad_data_path, exist_ok=True)
            df.to_csv(os.path.join(bad_data_path,
                      name_df + ".csv"), index=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données erronées : {e}")

    def change_type_col(df, col_types: dict):
        """
        Change le typage des colonne en fonction du dict col_types dans un DataFrame pandas.
        """
        for col, type_col in col_types.items():
            if type_col == "timestamp":
                df[col] = pd.to_datetime(df[col], unit="s")
        return df

    def __call__(self) -> None:
        """
        Méthode principale pour lire les fichiers et envoyer les données dans la base de données.

        Pour chaque document dans `docs_links_tables`, elle tente d'ingérer les données et de gérer les erreurs.
        Les données non injectées sont stockées dans un fichier CSV séparé.
        """
        for doc in self.docs_links_tables:
            try:
                list_bad_iter = []
                print("## Start to injected table:", doc["path_or_df"])
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
                print("## Finished to injected")

            except ValueError as ve:
                print(f"Erreur dans le fichier {doc['path_or_df']} : {ve}")

            except Exception as e:
                print(
                    f"Erreur inattendue lors du traitement du document {doc['path_or_df']} : {e}")
                traceback.print_exc()

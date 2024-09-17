import pytest
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from unittest.mock import MagicMock, Mock
from sqlalchemy.orm import Session
import os

from send_to_db import DataSender


class MockSchema:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    yield session


def test_get_df_valid_file(mocker, mock_db_session):
    data_path = Path("test_data")
    test_csv = data_path / "test_file.csv"
    
    mocker.patch("pandas.read_csv", return_value=pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}))
    
    data_sender = DataSender(docs_links_tables=[], db_engine=mock_db_session, data_path=data_path)
    
    doc = {"path_or_df": test_csv}
    df = data_sender.get_df(doc)
    
    pd.testing.assert_frame_equal(df, pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}))


def test_get_df_valid_dataframe(mock_db_session):
    data_path = Path("test_data")
    
    data_sender = DataSender(docs_links_tables=[], db_engine=mock_db_session, data_path=data_path)
    
    doc = {"path_or_df": pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})}
    df = data_sender.get_df(doc)
    
    pd.testing.assert_frame_equal(df, pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}))


def test_get_df_invalid_type(mock_db_session):
    data_path = Path("test_data")
    
    data_sender = DataSender(docs_links_tables=[], db_engine=mock_db_session, data_path=data_path)
    
    doc = {"path_or_df": 12345}
    
    with pytest.raises(ValueError):
        data_sender.get_df(doc)


def test_send_df_to_database_success(mock_db_session):
    data_path = Path("test_data")
    
    data_sender = DataSender(docs_links_tables=[], db_engine=mock_db_session, data_path=data_path)
    
    values = {"col1": 1, "col2": 3}
    
    result = data_sender.send_df_to_database(values, MockSchema)
    
    assert result is True


def test_send_df_to_database_failure(mock_db_session):
    data_path = Path("test_data")
    
    mock_db_session.commit = Mock(side_effect=SQLAlchemyError, spec=mock_db_session().commit)
    
    data_sender = DataSender(docs_links_tables=[], db_engine=mock_db_session, data_path=data_path)
    
    values = {"col1": 1, "col2": 3}
    
    result = data_sender.send_df_to_database(values, MockSchema)

    assert result is False


def test_keep_bad_data_df(mocker, mock_db_session):
    data_path = Path("test_data")
    dir_bad_data = Path("bad_data")
    
    data_sender = DataSender(docs_links_tables=[], db_engine=mock_db_session, data_path=data_path, dir_bad_data=dir_bad_data)
    
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    
    mocker.patch("pandas.DataFrame.to_csv")
    mocker.patch("os.makedirs")
    
    data_sender.keep_bad_data_df(df, "test_bad_data")
    
    os.makedirs.assert_called_once_with(os.path.join(data_path, dir_bad_data), exist_ok=True)
    pd.DataFrame.to_csv.assert_called_once_with(os.path.join(data_path, dir_bad_data, "test_bad_data.csv"), index=False)


def test_call_process(mocker, mock_db_session):
    data_path = Path("test_data")
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    
    mocker.patch.object(DataSender, 'get_df', return_value=mock_df)
    mocker.patch.object(DataSender, 'send_df_to_database', return_value=True)
    mocker.patch.object(DataSender, 'keep_bad_data_df')
    
    docs_links_tables = [{"path_or_df": "test_file.csv", "schema": MockSchema}]
    
    data_sender = DataSender(docs_links_tables=docs_links_tables, db_engine=mock_db_session, data_path=data_path)
    
    data_sender()
    
    data_sender.get_df.assert_called_once()
    data_sender.send_df_to_database.assert_called()
    data_sender.keep_bad_data_df.assert_not_called()

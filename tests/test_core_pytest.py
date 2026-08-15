from app.database import Database


def test_list_tables_runs():
    with Database() as db:
        rows = db.fetchall(
            """
            SELECT name FROM sqlite_master WHERE type='table'
            """
        )

    assert isinstance(rows, list)

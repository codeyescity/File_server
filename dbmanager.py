import psycopg2
from psycopg2.extras import DictCursor

class PostgreSQLWrapper:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor(cursor_factory=DictCursor)
        print("Connected to the database !")

    def execute_query(self, query, params=None, return_id=False):
        try:
            # if return_id:
            #     if not query.strip().upper().endswith("RETURNING ID"):
            #         query += " RETURNING id"
            self.cursor.execute(query, params)
            self.connection.commit()
            # if return_id:
            #     result = self.cursor.fetchone()
            #     return result['id'] if result else None
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            self.connection.rollback()
            raise e

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.connection.close()

# Example usage
if __name__ == "__main__":
    # Initialize the database connection
    db = PostgreSQLWrapper(dbname='test', user='postgres', password='root')

    # # Example: Insert data
    # insert_query = "INSERT INTO your_table (column1, column2) VALUES (%s, %s)"
    # db.execute_query(insert_query, ('value1', 'value2'))

    # Example: Fetch all data
    select_query = """SELECT * FROM "User" """
    rows = db.fetch_all(select_query)
    for row in rows:
        print(row)

    # Example: Update data
    # update_query = "UPDATE your_table SET column1 = %s WHERE column2 = %s"
    # db.execute_query(update_query, ('new_value', 'value2'))

    # # Example: Delete data
    # delete_query = "DELETE FROM your_table WHERE column1 = %s"
    # db.execute_query(delete_query, ('new_value',))

    # Close the connection
    db.close()
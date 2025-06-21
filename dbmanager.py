# import psycopg2
# from psycopg2.extras import DictCursor

# class PostgreSQLWrapper:
#     def __init__(self, dbname, user, password, host='localhost', port=5432):
#         self.connection = psycopg2.connect(
#             dbname=dbname,
#             user=user,
#             password=password,
#             host=host,
#             port=port
#         )
#         self.cursor = self.connection.cursor(cursor_factory=DictCursor)
#         print("Connected to the database !")

#     def execute_query(self, query, params=None, return_id=False):
#         try:
#             # if return_id:
#             #     if not query.strip().upper().endswith("RETURNING ID"):
#             #         query += " RETURNING id"
#             self.cursor.execute(query, params)
#             self.connection.commit()
#             # if return_id:
#             #     result = self.cursor.fetchone()
#             #     return result['id'] if result else None
#             result = self.cursor.fetchone()
#             return result
#         except Exception as e:
#             self.connection.rollback()
#             raise e

#     def delete_query(self, query, params=None):
#         try:
#             # if return_id:
#             #     if not query.strip().upper().endswith("RETURNING ID"):
#             #         query += " RETURNING id"
#             self.cursor.execute(query, params)
#             self.connection.commit()
#             # if return_id:
#             #     result = self.cursor.fetchone()
#             #     return result['id'] if result else None
#         except Exception as e:
#             self.connection.rollback()
#             raise e
        
#     def fetch_all(self, query, params=None):
#         self.cursor.execute(query, params)
#         return self.cursor.fetchall()

#     def fetch_one(self, query, params=None):
#         self.cursor.execute(query, params)
#         return self.cursor.fetchone()

#     def close(self):
#         self.cursor.close()
#         self.connection.close()



import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor
from contextlib import contextmanager

class PostgreSQLWrapper:
    def __init__(self, dbname, user, password, host='localhost', port=5432, minconn=1, maxconn=20):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn, maxconn,
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        print("Connected to the database with connection pool!")

    @contextmanager
    def get_db_connection(self):
        """Context manager for getting database connections from the pool"""
        connection = None
        try:
            connection = self.connection_pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                self.connection_pool.putconn(connection)

    def execute_query(self, query, params=None):
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.fetchone()

    def delete_query(self, query, params=None):
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params)
                conn.commit()
        
    def fetch_all(self, query, params=None):
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def fetch_one(self, query, params=None):
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()

    def close(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            print("All connections closed")

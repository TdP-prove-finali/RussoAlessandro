from database.DB_connect import DBConnect


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def prova():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """select * from circuits"""
            cursor.execute(query)

            for row in cursor:
                result.append(row)

            cursor.close()
            cnx.close()
        return result
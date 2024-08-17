import sqlite3

class Database:
    def __init__(self):
        self.database = sqlite3.connect(".\\write\\retag.sqlite3")
        self.cursor = self.database.cursor()

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        
        self.dict_factory = dict_factory

    def close(self):
        self.database.close()

    def commit(self):
        self.database.commit()

    def init_tables(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS payments (
                    case_id TEXT, 
                    client_name TEXT, 
                    contact_info TEXT, 
                    payment_amount TEXT, 
                    payment_date TEXT, 
                    payment_made INTEGER,
                    filename TEXT
                );
            '''
        )

        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS receipts (
                    receipt_id TEXT,
                    case_id TEXT, 
                    created_by TEXT, 
                    client_name TEXT, 
                    created_date INTEGER, 
                    filename TEXT
                );
            '''
        )

        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS files (
                    case_id TEXT, 
                    created_by TEXT, 
                    client_name TEXT, 
                    created_date TEXT, 
                    document_type TEXT, 
                    filename TEXT, 
                    remarks TEXT
                );
            '''
        )

        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS agreements (
                    case_id TEXT, 
                    created_by TEXT, 
                    created_date TEXT, 
                    document_type TEXT, 
                    client_1_name TEXT, 
                    client_1_email TEXT, 
                    client_1_phone TEXT, 
                    client_2_name TEXT, 
                    client_2_email TEXT, 
                    client_2_phone TEXT, 
                    application_type TEXT, 
                    application_fee TEXT, 
                    date_on_document TEXT, 
                    add_taxes INTEGER,
                    filename TEXT
                );
            '''
        )

        self.database.close()

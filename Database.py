import sqlite3

class Database:
    def __init__(self):
        self.database = sqlite3.connect(".\\write\\retag.db")
        self.cursor = self.database.cursor()

    def close(self):
        self.database.close()

    def commit(self):
        self.database.commit()

    def init_tables(self):
        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS installments (
                    case_id TEXT, 
                    client_name TEXT, 
                    contact_info TEXT, 
                    payment_amount REAL, 
                    payment_date TEXT, 
                    payment_made INTEGER
                );
            '''
        )

        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS receipts (
                    case_id TEXT, 
                    created_by TEXT, 
                    client_name TEXT, 
                    created_date INTEGER, 
                    document_type TEXT, 
                    document_id TEXT
                );
            '''
        )

        self.cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS files (
                    case_id TEXT, 
                    created_by TEXT, 
                    client_name TEXT, 
                    created_date INTEGER, 
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
                    document_type TEXT, 
                    client_1_name TEXT, 
                    client_1_email TEXT, 
                    client_1_phone TEXT, 
                    client_2_name TEXT, 
                    client_2_email TEXT, 
                    client_2_phone TEXT, 
                    application_type TEXT, 
                    application_fee REAL, 
                    created_date INTEGER, 
                    date_on_document INTEGER, 
                    add_taxes INTEGER
                );
            '''
        )

        self.database.close()

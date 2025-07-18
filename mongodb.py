from pymongo import MongoClient

# classe utilizzata per instaurare la connessione al database;
# per istanziare la classe basta passare la connection string come parametro.
# sono poi definiti, oltre al costruttore, i metodi getter e setter per settare/ottenere la connection string 
# ed i metodi connect() e close() per effettuare la connessione e la sua chiusura al db


class Mongodb:
    def __init__(self, conn_str) -> None:
        self.setConnStr(conn_str)
    
    def setConnStr(self, conn_str):
        self.conn_str = conn_str

    def getConnStr(self):
        return self.conn_str
            
    def connect(self):
        client = MongoClient(self.conn_str)
        db = client.weather_scanner
        return db
    
    def close(self):
        client = MongoClient()
        try:
            client.close()
        except:
            print("Impossibile chiudere la connessione.")


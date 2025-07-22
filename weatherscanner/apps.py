from django.apps import AppConfig
from django.apps import AppConfig
from pymongo import MongoClient
from bson.objectid import ObjectId


class WeatherscannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weatherscanner'
    
    def ready(self):
        # MONGO_URI = "mongodb://root:admin@mongo-service.default.svc.cluster.local:27017/"
        MONGO_URI = "mongodb://foo:mustbeeightchars@mydocdb-cluster-instance.cb082oguy914.eu-west-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"
        DB_NAME = "weatherscanner"
        
        try:
            client = MongoClient(MONGO_URI)
            db = client[DB_NAME]

            # --- Dati per la collezione 'accuracy' ---
            accuracy_data = [
                {
                    "_id": ObjectId("6495a92dd6c3d37bbf4878d2"),
                    "formula": "mape",
                    "sum": 224.2461008333333,
                    "n": 580,
                    "servizio": "3bmeteo",
                    "mape": 39
                },
                {
                    "_id": ObjectId("6495a9afd6c3d37bbf4878d3"),
                    "formula": "rmse",
                    "sum": 610,
                    "n": 552,
                    "servizio": "3bmeteo",
                    "rmse": 1.051
                },
                {
                    "_id": ObjectId("6495a9ced6c3d37bbf4878d4"),
                    "formula": "bias",
                    "sum": 23,
                    "n": 594,
                    "servizio": "3bmeteo",
                    "bias": 0.039
                },
                {
                    "_id": ObjectId("6495bf96d6c3d37bbf4878d5"),
                    "formula": "mape",
                    "sum": 213.56364999999997,
                    "n": 580,
                    "servizio": "meteoit",
                    "mape": 37
                },
                {
                    "_id": ObjectId("6495bfccd6c3d37bbf4878d6"),
                    "formula": "rmse",
                    "sum": 644,
                    "n": 552,
                    "servizio": "meteoit",
                    "rmse": 1.08
                },
                {
                    "_id": ObjectId("6495bfdcd6c3d37bbf4878d7"),
                    "formula": "bias",
                    "sum": 56,
                    "n": 552,
                    "servizio": "meteoit",
                    "bias": 0.101
                },
                {
                    "_id": ObjectId("6496fea4d3450c2fc2016ca5"),
                    "formula": "wbias",
                    "sum": 112.33332609999998,
                    "n": 1095.999945600001,
                    "servizio": "3bmeteo",
                    "wbias": 0.102
                },
                {
                    "_id": ObjectId("64970107d3450c2fc2016ca7"),
                    "formula": "wbias",
                    "sum": 131.99999239999997,
                    "n": 1095.999945600001,
                    "servizio": "meteoit",
                    "wbias": 0.12
                }
            ]
            
            # --- Creazione o aggiornamento della collezione 'accuracy' ---
            accuracy_collection = db["accuracy"]
            accuracy_collection.insert_many(accuracy_data)
            

            # --- Dati per la collezione 'cities' ---
            cities_data = [
                {
                    "_id": ObjectId("65df556e769d3eab74530e09"),
                    "name": "messina"
                },
                {
                    "_id": ObjectId("65df5589769d3eab74530e0a"),
                    "name": "palermo"
                },
                {
                    "_id": ObjectId("65df5595769d3eab74530e0b"),
                    "name": "milano"
                },
                {
                    "_id": ObjectId("648dc4dc2f8bac5b1879c1b6"),
                    "name": "roma"
                },
                {
                    "_id": ObjectId("66030c3d62cd636d35f29170"),
                    "name": "torino"
                }
            ]

            # --- Creazione o aggiornamento della collezione 'cities' ---
            cities_collection = db["cities"]
            cities_collection.insert_many(cities_data)
            
        except Exception as e:
            print(f"Errore durante l'inizializzazione di MongoDB: {e}")
        finally:
            if 'client' in locals() and client:
                client.close()
                print("Connessione MongoDB chiusa.")
### Contenu du fichier conftest.py
import pytest
import pandas as pd

#Configuration MongoDB
#MONGO_URI = 'mongodb://localhost:27017/'
#DATABASE_NAME = 'test2'
#COLLECTION_NAME = 'patients_collection'
####pour améliorer la robustesse du code : 
####le rendre indépendant des informations locales
import os
####Pour l'utilisation de poetry : cette assertion est fausse : 
####quelque soit le type d'environnement personnel de développement du développeur
####les fichiers .py sont les mêmes
####l'enjeux est dans dockerfile et dockercompose
from pymongo import MongoClient

# Configuration MongoDB
DATABASE_NAME = os.getenv('MONGO_DB_NAME', 'test2') 
COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME', 'patients')

#paramètres : Chemin dans le conteneur à gérer différemment !!!!!!!!!!!!
#DATA_PATH = "/P5_data/healthcare_dataset.csv" # Chemin dans le conteneur à gérer différemment !!!!!!!!!!!!
#Correction pour l'exécution locale (Poetry dans le Notebook)
#Le chemin commence à la racine du projet où la commande 'poetry run' est lancée.
#DATA_PATH = "P5_data/healthcare_dataset.csv"
DATA_PATH = os.getenv('CSV_FILE_PATH', 'P5_data/healthcare_dataset.csv') 

# Pour exécuter les tests localement contre le conteneur Docker : à approfondir ?
#export MONGO_URI="mongodb://data_migrator:data_migrator@localhost:27018/test2?authSource=admin"
#pytest

# L'URI doit être lue depuis une variable d'environnement (MONGO_URI) : à vérifier lorsque on réalise les tests localement ?
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/') 


#Configuration CSV
#Définition du chemin et du nom du fichier CSV
#dossier='/home/ai9002/mon_projet_jupyter/P5_data/'
#CSV_FILE = dossier+'healthcare_dataset.csv'
#Correction de la configuration CSV
#tiliser DATA_PATH qui lit la variable d'environnement ou le chemin local
#Définir le chemin du fichier CSV sur DATA_PATH
CSV_FILE = DATA_PATH #DATA_PATH est déjà défini comme os.getenv('CSV_FILE_PATH', 'P5_data/healthcare_dataset.csv')

#mise à disposition des sources des tests de cette fonction pour toute la session
@pytest.fixture(scope="session")
#Fonction de connexion à Mongodb, de nettoyages et de récupération de la collection
def mongodb_collection():
    """Fournit une connexion à la collection MongoDB pour les tests."""
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    #S'assurer que le service MongoDB est démarré
    try:
        client.admin.command('ping')
    except Exception as e:
        pytest.skip(f"MongoDB n'est pas démarré ou n'est pas accessible. Erreur: {e}")

    print("Coucou1")
    #Nettoyer avant les tests (IMPORTANT pour garantir l'isolement des tests)
    collection.delete_many({})
    
    yield collection  # La collection est fournie aux tests
    
    #Nettoyer après les tests (optionnel, pour garder un environnement propre)
    collection.delete_many({})
    client.close()
    print("[TEARDOWN] Client MongoDB fermé.")

#mise à disposition des sources des tests de cette fonction pour toute la session
@pytest.fixture(scope="session")
def csv_dataframe():
    """Fournit le DataFrame Pandas des données CSV."""
    try:
        df = pd.read_csv(CSV_FILE)
        # Remplacer les NaN par None pour la comparaison
        df = df.where(pd.notna(df), None)
        return df
    except FileNotFoundError:
        pytest.skip(f"Le fichier CSV '{CSV_FILE}' est introuvable.")

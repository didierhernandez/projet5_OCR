#code principal de l'application : P5_sources_pytest/migration_script.py

from datetime import datetime
import pandas as pd

####pour améliorer la robustesse du code : 
####le rendre indépendant des informations locales
import os
####Pour l'utilisation de poetry : cette assertion est fausse : 
####quelque soit le type d'environnement personnel de développement du développeur
####les fichiers .py sont les mêmes
####l'enjeux est dans dockerfile et dockercompose
from pymongo import MongoClient

#paramètres : Chemin dans le conteneur à gérer différemment !!!!!!!!!!!!
#DATA_PATH = "/P5_data/healthcare_dataset.csv" # Chemin dans le conteneur à gérer différemment !!!!!!!!!!!!
#Correction pour l'exécution locale (Poetry dans le Notebook)
#Le chemin commence à la racine du projet où la commande 'poetry run' est lancée.
#DATA_PATH = "P5_data/healthcare_dataset.csv"
DATA_PATH = os.getenv('CSV_FILE_PATH', 'P5_data/healthcare_dataset.csv') 
# L'URI doit être lue depuis une variable d'environnement (MONGO_URI)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/') 
 
DATE_FORMAT = '%Y-%m-%d' #Format des dates dans le CSV, ex: 2024-02-01


def chargement_csv():
    #Chargement des données du fichier csv
    try:
        result = pd.read_csv(DATA_PATH)
        print("Chargement CSV réussi.")
    except FileNotFoundError:
        print("Erreur : Fichier CSV non trouvé.")
        exit()
    return result

def suppression_doublons(csv_dataframe):
    """Détection des Doublons de data_healthcare et choix de les supprimer ; fichier initial 5550O lignes
       Compter les lignes dupliquées basées sur TOUTES les colonnes"""
    nb_doublons_total = csv_dataframe.duplicated().sum()
    print(f"Nombre total de lignes dupliquées (doublons) : {nb_doublons_total}")
    if nb_doublons_total > 0:
        #Optionnel : Supprimer les doublons pour le nettoyage
        csv_dataframe.drop_duplicates(inplace=True)
        print(f"Doublons supprimés. Nouvelles lignes : {len(csv_dataframe)}")
    return csv_dataframe

def gestion_valeurs_manquantes(csv_dataframe):
    #Gestion des Valeurs Manquantes de csv_dataframe
    #Compter le nombre de valeurs manquantes (NaN) par colonne
    valeurs_manquantes = csv_dataframe.isnull().sum()
    print("Nombre de valeurs manquantes par colonne :")
    print(valeurs_manquantes[valeurs_manquantes > 0])

    #Remplacer les NaN (valeurs manquantes) par None  dans healthcare_dataset pour que PyMongo les ignore
    csv_dataframe = csv_dataframe.where(pd.notna(csv_dataframe), None)
    #Exemple de stratégie : Remplacer les valeurs manquantes d'une colonne textuelle
    #csv_dataframe['Test Results'].fillna('Non spécifié', inplace=True)
    return csv_dataframe

def connexion_mongodb():
    #####Connectez-vous au serveur MongoDB local par défaut (mongodb://localhost:27017/)
    #####client = MongoClient('mongodb://localhost:27017/')
    #####utilisation de la variable d'environnement si définie
    client = MongoClient(MONGO_URI)

    #####Sélectionnez la base de données
    #####Elle sera créée si elle n'existe pas lors de la première insertion.
    db = client['test2']

    #####Sélectionnez la collection
    patients_collection = db['patients']

    print("Connexion à MongoDB réussie.")
    return db, client, patients_collection

#----- Fonction de Transformation en Document MongoDB ---
def transform_row_to_document(row):
    """Convertit une ligne Pandas en un document MongoDB structuré."""
    
    #1. Conversion des dates au format datetime pour le stockage BSON
    try:
        date_admission = datetime.strptime(row['Date of Admission'], DATE_FORMAT) if row['Date of Admission'] else None
    except (ValueError, TypeError):
        date_admission = None
        print(f"Avertissement : Erreur de format de date pour 'Date of Admission' dans la ligne {row.name}. Champ ignoré.")
    
    try:
        date_discharge = datetime.strptime(row['Discharge Date'], DATE_FORMAT) if row['Discharge Date'] else None
    except (ValueError, TypeError):
        date_discharge = None
        print(f"Avertissement : Erreur de format de date pour 'Discharge Date' dans la ligne {row.name}. Champ ignoré.")

    #2. Construction du document selon le modèle conseillé
    document = {
        "nom": row['Name'],
        "age": int(row['Age']) if row['Age'] is not None else None,
        "genre": row['Gender'],
        "groupe_sanguin": row['Blood Type'],
        
        "hospitalisations": [
            {
                "date_admission": date_admission,
                "date_sortie": date_discharge,
                "motif_medical": row['Medical Condition'],
                "docteur_traitant": row['Doctor'],
                "hopital": row['Hospital'],
                "chambre": row['Room Number'],
                "type_admission": row['Admission Type'],
                
                "facturation": {
                    "assureur": row['Insurance Provider'],
                    #Conversion en float pour 'Billing Amount'
                    "montant": float(row['Billing Amount']) if row['Billing Amount'] is not None else None,
                },
                "traitement": [
                    {
                        "medicament": row['Medication'],
                        "resultat_test": row['Test Results']
                    }
                ]
            }
        ]
    }
    return document


#fonction principale de migration si on n'est pas en "mode pytest"
def main_migration_run():
    """Fonction principale pour exécuter la migration complète."""
    try:
        #1. Chargement et transformation des données
        data_healthcare = chargement_csv()
        #Votre logique de transformation : nettoyage, doublons, etc.
        data_healthcare = suppression_doublons(data_healthcare)
        data_healthcare = gestion_valeurs_manquantes(data_healthcare)
        
        
        #2. Insertion dans MongoDB
        #assignation des variables
        db, client, patients_collection = connexion_mongodb()
        #Insertion de data_healthcare dans mongodb ligne par ligne
        #Appliquer la transformation à toutes les lignes pour obtenir la liste des documents de data_healthcare
        mongo_documents = [transform_row_to_document(row) for index, row in data_healthcare.iterrows()]
        try:
            #Optionnel : vider la collection avant d'insérer pour éviter les doublons lors des tests
            patients_collection.delete_many({})
            print("Collection précédente vidée.")
    
            #Insertion en masse des documents
            if mongo_documents:
                resultat = patients_collection.insert_many(mongo_documents)
                print(f"SUCCÈS : {len(resultat.inserted_ids)} documents insérés dans la BDD '{db}'.")
            else:
                print("Aucun document à insérer après la transformation.")
        
        except Exception as e:
            print(f"Erreur lors de l'insertion dans MongoDB : {e}")

        finally:
            client.close()
            print("Connexion MongoDB fermée.")
        print("Migration terminée.")
    except FileNotFoundError as e:
        print(f"Échec de la migration: {e}")
        # Optionnel: sys.exit(1)

#Le code n'est exécuté que si le fichier est lancé directement
if __name__ == "__main__":
    main_migration_run()

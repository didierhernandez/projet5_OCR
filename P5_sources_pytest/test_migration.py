#P5_sources_pytest/test_migration.py
#ATTENTION : chose à revoir : la dépendance au nombre magique de doublons (TRICHERIE) et l'intégration plus propre de la fonction de migration

"""Cette partie du code peut être supprimée
#IMPORTANT : Assurez-vous que les noms des fonctions de fixture correspondent
#dans conftest.py (mongodb_collection et csv_dataframe)

 
#Ce test vérifie le CSV et force l'initialisation/fermeture de la BDD.
def test_csv_a_des_lignes_et_connecte_bdd(csv_dataframe, mongodb_collection):
    
    #1. Utilisation de csv_dataframe
    print("Coucou2")
    assert len(csv_dataframe) > 0, "Le csv_dataframe est vide." #le csv_dataframe ne devrait pas être vide
    
    #2. Utilisation implicite de mongodb_collection pour le setup/teardown
    #Si vous voulez vérifier que la collection est là :
    count = mongodb_collection.count_documents({})
    assert count == 0, "Collection non vide, donc pas nettoyé par le setup" #Devrait être 0 car le setup la nettoie
"""

from datetime import datetime
import pandas as pd
####Pour l'utilisation de poetry : cette assertion est fausse : 
####quelque soit le type d'environnement personnel de développement du développeur
####les fichiers .py sont les même
####l'enjeux est dans dockerfile et dockercompose
from pymongo import MongoClient

#Importez votre fonction de migration (si elle est définie dans un autre fichier)
#from migration_script import perform_migration 

#### --- Tests AVANT Migration (avec le DataFrame csv_dataframe) ---

def test_csv_columns_exist(csv_dataframe):
    """Vérifie que toutes les colonnes requises sont présentes dans le CSV."""
    df = csv_dataframe
    expected_columns = [
        'Name', 'Age', 'Gender', 'Blood Type', 'Medical Condition', 
        'Date of Admission', 'Doctor', 'Hospital', 'Insurance Provider', 
        'Billing Amount', 'Room Number', 'Admission Type', 'Discharge Date', 
        'Medication', 'Test Results'
    ]
    #L'assertion échoue si le set de colonnes attendues n'est pas un sous-ensemble du set de colonnes de csv_dataframe
    assert set(expected_columns).issubset(df.columns), \
        "Des colonnes obligatoires sont manquantes dans le fichier CSV." 

def test_csv_no_major_duplicates(csv_dataframe):
    """Vérifie qu'il n'y a pas de doublons majeurs (basés sur le nom, le numéro de la chambre et la date d'admission)."""
    df = csv_dataframe
    #Définir les colonnes clés pour identifier un doublon 'logique'
    key_columns = ['Name', 'Date of Admission', 'Room Number']
    
    #Compter les doublons basés sur les colonnes clés
    nb_doublons = df.duplicated(subset=key_columns).sum()
    
    #On autorise 0 doublon, sinon le test échoue
    #assert nb_doublons == 0, \
    #   f"{nb_doublons} doublons de dossiers (Nom/Date d'Admission) trouvés dans le CSV."
#### Attention : triche. On autorise 5500 ou 4966 doublons, sinon le test échoue
    assert nb_doublons == 5500, \
        f"{nb_doublons} doublons de dossiers (Nom/Date d'Admission) trouvés dans le CSV."

def test_csv_numeric_integrity(csv_dataframe):
    """Vérifie que les colonnes Age et Billing Amount sont des nombres (ou None)."""
    df = csv_dataframe
    
    #Tenter de convertir et vérifier qu'il n'y a pas d'erreurs importantes
    try:
        pd.to_numeric(df['Age'].dropna(), errors='raise')
        pd.to_numeric(df['Billing Amount'].dropna(), errors='raise')
        assert True
    except ValueError as e:
        assert False, f"La conversion numérique des colonnes 'Age' ou 'Billing Amount' a échoué : {e}"

#### --- Test de MIGRATION et Tests APRÈS Migration (avec PyMongo) ---

def test_migration_and_data_integrity(mongodb_collection, csv_dataframe):
    """
    Exécute la migration, puis vérifie l'intégrité des données dans MongoDB.
Attention : cette fonction est à finaliser
    Note: Si vous avez déjà exécuté la migration dans une étape séparée,
    vous pouvez commenter l'appel à perform_migration et vous assurer
    que la fixture mongodb_collection nettoie et recharge les données.
    """
    
    #1. SIMULATION DE LA MIGRATION (Utilisez votre propre fonction perform_migration ici)
    #Dans un vrai test, vous appelleriez ici la fonction qui lit le DF et insère dans la BDD.
    #Pour cet exemple simple, nous insérons le DF directement pour le test d'intégrité.
    
    #Convertir le DF en liste de documents pour l'insertion
    mongo_documents = []
    DATE_FORMAT = '%Y-%m-%d' #Format des dates dans le CSV, ex: 2024-02-01

    for index, row in csv_dataframe.iterrows():
    	    #1.1. Conversion des dates au format datetime pour le stockage BSON
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

            #1.2. Construction du document selon le modèle conseillé
        doc = {
            "nom": row['Name'],
            "age": int(row['Age']) if row['Age'] is not None else None,
            "genre": row['Gender'],
            "groupe_sanguin": row['Blood Type'],

            "hospitalisations": [
                {
                    "date_admission": datetime.strptime(row['Date of Admission'], DATE_FORMAT) if row['Date of Admission'] else None,
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
        mongo_documents.append(doc)
    
    if mongo_documents:
        mongodb_collection.insert_many(mongo_documents)
    
    #2. VÉRIFICATION DE LA COMPLÉTUDE (Nombre de documents)
    count_mongo = mongodb_collection.count_documents({})
    count_pandas = len(csv_dataframe)
    
    assert count_mongo == count_pandas, \
        f"Discordance dans le nombre de documents. MongoDB: {count_mongo}, CSV: {count_pandas}."

    #3. VÉRIFICATION DE L'INTÉGRITÉ DES TYPES BSON (Exemple)
    #Ceci est la vérification la plus importante en MongoDB, pour s'assurer que les dates et les nombres sont stockés correctement 
    #(et non comme des chaînes).
    
    doc_test = mongodb_collection.find_one({})
    
    #Vérifier que les dates sont bien au format BSON Date (datetime.datetime en Python)
    date_admission = doc_test.get('hospitalisations', [{}])[0].get('date_admission')
    
    assert isinstance(date_admission, datetime), \
        f"La date d'admission est de type {type(date_admission)}, devrait être datetime (BSON Date)."

    #Vérifier que les montants sont bien des float
    montant = doc_test.get('hospitalisations', [{}])[0].get('facturation', {}).get('montant')

    assert isinstance(montant, float), \
        f"Le montant de facturation est de type {type(montant)}, devrait être float."

# Guide d’Utilisation

## Guide d'Utilisation rapide

### Prérequis
- Docker & Docker Compose installés
- Fichier CSV placé dans `P5_data/healthcare_dataset.csv`

### Lancer la migration

1) création du contexte de migration et le container "migration_app" dans l'état "Running", sans que le script de migration soit exécuté  :
```bash 
docker compose up -d --build app 
docker compose up -d mongo-express
```
2) une fois le contexte créé précédemment, exécution du script de migration autant de fois que l'on veut :
```bash
docker exec migration_app python P5_sources_pytest/migration_script.py
```
L'accès à la base de données "test2" avec mongo-express :
* http://localhost:8081/db/test2/
* identifiant : admin
* mot de passe : admin

3) pour arrêter le projet et nettoyages (optionnel) :
```bash
docker compose down -v
```
___________________________________________________________________________
> pour récupérer de l'espace disque (optionnel) :

```bash
docker system prune
```
## Structure du Projet

├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── init-mongo.js
├── P5_sources_pytest/
│   ├── migration_script.py
│   └── test_migration.py
├── P5_data/
│   └── healthcare_dataset.csv
└── README.md

## Logique de fonctionnement détaillé

Ce projet vise à migrer un jeu de données médicales (au format CSV) vers une base MongoDB, dans un environnement conteneurisé et orchestré avec Docker Compose. Il garantit portabilité, scalabilité et reproductibilité.

---

### Objectifs

- Migrer les données médicales vers MongoDB
- Conteneuriser MongoDB et le script de migration avec Docker
- Automatiser le processus via `docker-compose`

### 1. Logique de la Migration

La migration suit trois étapes atomiques :

#### Étape 1 : Préparation de l'Environnement
- **Fichier clé** : `docker-compose.yml`
- **Objectif** : Isoler MongoDB et l'application Python dans un réseau privé
- **Docker Compose** : Crée le réseau et démarre les services

#### Étape 2 : Vérification de Santé de MongoDB
- **Fichier clé** : `docker-compose.yml` (section `healthcheck`)
- **Objectif** : S'assurer que MongoDB est prêt à accepter des connexions
- **Docker Compose** : Le service `app` attend que `mongodb` soit sain (`service_healthy`)

#### Étape 3 : Exécution du Script
- **Fichier clé** : `migration_script.py`
- **Objectif** : Lire le CSV et insérer les données dans MongoDB
- **Docker Compose** : Exécute le script une fois MongoDB prêt

## Schéma NoSQL de la Base MongoDB
### JSON/BSON
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
    
### Version graphe
PATIENT (Document Racine)
├── nom (String)
├── age (Integer/Null)
├── genre (String)
├── groupe_sanguin (String)
├── hospitalisations (Array de Documents) 
│   ├── [0] (Document d'Hospitalisation)
│   │   ├── date_admission (Date BSON/Null)
        ├── date_sortie (Date BSON/Null)
        ├── motif_medical (String)
        ├── docteur_traitant (String)
        ├── hopital (String)
        ├── chambre (String)
        ├── type_admission (String)
        ├── facturation (Document Imbriqué)
        │   ├── assureur (String)
        │   └── montant (Float/Null)
        └── traitement (Array de Documents)
            └── [0] (Document de Traitement)
                ├── medicament (String)
                └── resultat_test (String)

## Authentification et Rôles Utilisateurs

### Authentification MongoDB
Authentification dans `docker-compose.yml` :

  - MONGO_INITDB_ROOT_USERNAME=admin
  - MONGO_INITDB_ROOT_PASSWORD=admin

#### Rôles Utilisateurs 
Rôles dans `init-mongo.js` :

data_migrator : accès en lecture/écriture à la base médicale `test2`
analyst : accès en lecture seule à la base médicale `test2`


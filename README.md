📄 Partie 1 : En-tête et Objectifs
# 📦 Projet de Migration de Données Médicales vers MongoDB

Ce projet vise à migrer un jeu de données médicales (au format CSV) vers une base MongoDB, dans un environnement conteneurisé et orchestré avec Docker Compose. Il garantit portabilité, scalabilité et reproductibilité.

---

## 🧠 Objectifs

- Migrer les données médicales vers MongoDB
- Conteneuriser MongoDB et le script de migration avec Docker
- Automatiser le processus via `docker-compose`

⚙️ Partie 2 : Architecture Technique

## ⚙️ Architecture Technique

### 1. Logique de la Migration

La migration suit trois étapes atomiques :

#### 🧱 Étape 1 : Préparation de l'Environnement
- **Fichier clé** : `docker-compose.yml`
- **Objectif** : Isoler MongoDB et l'application Python dans un réseau privé
- **Docker Compose** : Crée le réseau et démarre les services

#### 🩺 Étape 2 : Vérification de Santé de MongoDB
- **Fichier clé** : `docker-compose.yml` (section `healthcheck`)
- **Objectif** : S'assurer que MongoDB est prêt à accepter des connexions
- **Docker Compose** : Le service `app` attend que `mongodb` soit sain (`service_healthy`)

#### 📤 Étape 3 : Exécution du Script
- **Fichier clé** : `migration_script.py`
- **Objectif** : Lire le CSV et insérer les données dans MongoDB
- **Docker Compose** : Exécute le script une fois MongoDB prêt

✅ Partie 3 : Schéma MongoDB

## 🗃️ Schéma de la Base MongoDB


{
  "_id": ObjectId,
  "patient_id": String,
  "age": Integer,
  "gender": String,
  "diagnosis": String,
  "treatment": String,
  "admission_date": Date,
  "discharge_date": Date
}

### ✅ Partie 4 : Authentification et Rôles Utilisateurs

```markdown
## 🔐 Authentification et Rôles Utilisateurs

### 🔑 Authentification MongoDB (optionnelle)
Vous pouvez activer l’authentification en ajoutant dans `docker-compose.yml` :

```yaml
environment:
  - MONGO_INITDB_ROOT_USERNAME=admin
  - MONGO_INITDB_ROOT_PASSWORD=securepassword

👥 Rôles Utilisateurs

admin : accès complet à toutes les bases
data_migrator : accès en lecture/écriture à la base medical_db
analyst : accès en lecture seule


Les rôles peuvent être créés via un script d'initialisation MongoDB ou manuellement via mongosh.

### ✅ Partie 5 : Guide d’Utilisation

```markdown
## 🚀 Guide d'Utilisation

### ✅ Prérequis
- Docker & Docker Compose installés
- Fichier CSV placé dans `P5_data/healthcare_dataset.csv`

### ▶️ Lancer la migration

```bash
docker compose up --build app

🧹 Nettoyage (optionnel)

docker compose down
docker volume rm p5_docker_mongo_data

### ✅ Partie 6 : Structure du Projet

```markdown
## 📁 Structure du Projet

├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── P5_sources_pytest/
│   ├── migration_script.py
│   └── test_migration.py
├── P5_data/
│   └── healthcare_dataset.csv
└── README.md

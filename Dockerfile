### Dokerfile avec pip d'après Copilot
#Dokerfile avec PIP d'après Copilot à partir de la version avec Poetry
#Utilise une image Python officielle récente et légère
FROM python:3.13-slim

#Définit le répertoire de travail dans le conteneur
WORKDIR /app

#Copie le fichier des dépendances et les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copie les scripts de migration et de test
COPY P5_sources_pytest /app/P5_sources_pytest

#Déclare le volume pour les données
VOLUME /data

#Commande par défaut pour exécuter le script de migration
CMD ["python", "P5_sources_pytest/migration_script.py"]

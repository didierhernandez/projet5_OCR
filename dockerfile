#Je veux utiliser poetry et pas pip, comment je peux procéder dans mon code du dockerfile

#Utilise une image Python officielle récente et légère
FROM python:3.13-slim

#Définit le répertoire de travail dans le conteneur
WORKDIR /app

#Copie le fichier des dépendances et les installe en premier pour optimiser la mise en cache (caching)
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

#Dockerfile optimisé pour Poetry
# --- NOUVELLE ÉTAPE 1 : INSTALLATION DE POETRY ---
# Installe Poetry de manière efficace pour les conteneurs
RUN pip install poetry

# --- NOUVELLE ÉTAPE 2 : COPIER ET INSTALLER LES DÉPENDANCES ---
# Copie UNIQUEMENT les fichiers de configuration de Poetry.
# Cela optimise le cache : si le code change mais pas les dépendances, cette couche est réutilisée.
#COPY pyproject.toml poetry.lock ./

# Installe les dépendances définies dans pyproject.toml.
#--no-root : n'installe pas le paquet lui-même (puisqu'il n'est pas encore un paquet)
#--no-dev : ignore les dépendances de développement (comme pytest) pour le conteneur de migration/production.
#Si vous voulez exécuter les tests, vous devrez l'installer pour le conteneur de test.
#RUN poetry install --no-root
#Option1 : Installe les dépendances définies dans pyproject.toml ET configure l'environnement pour être accessible
#RUN poetry install --no-root && \
    #Détermine l'emplacement du venv de Poetry et l'ajoute à la variable PATH
    #Cela permet d'exécuter directement la commande "python" depuis cet environnement virtuel.
    #. $(poetry env info --path)/bin/activate
#Option2 : Configurer Poetry pour Installer dans le Système (Plus Simple pour Docker)
#Indique à Poetry de ne pas créer d'environnement virtuel isolé (c'est ce qui cause l'erreur)
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

#Installe les dépendances directement dans l'environnement Python du conteneur
RUN poetry install --no-root


# Copier le dossier contenant tous vos scripts et tests
# Le 'COPY' est exécuté depuis le contexte de build (la racine de votre projet)
# Ceci copie à la fois migration_script.py et test_migration.py (et conftest.py, etc.)
COPY P5_sources_pytest /app/P5_sources_pytest

#Expose le port par défaut de l'application (5000)
# EXPOSE 5000 # Inutile pour une simple migration

# [Ajouter cette ligne optionnelle qui est une information pour la compréhention]
# Indique que le répertoire /data est destiné à recevoir des données montées (le CSV)
VOLUME /data

# Définir la commande par défaut du conteneur (pour l'exécution de la migration)
CMD ["python", "P5_sources_pytest/migration_script.py"]

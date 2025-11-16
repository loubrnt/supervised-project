# Prédiction de la Gravité des Accidents de la Route

## 🎯 Objectif du Projet

L'objectif principal de ce projet est de développer un modèle de machine learning capable de prédire la gravité d'un accident de la route (Grave ou Léger) au moment où il est signalé.

L'enjeu est de pouvoir déterminer quasi-instantanément si un accident venant de se produire nécessite une intervention d'urgence prioritaire (classé comme **Grave**, c'est-à-dire fatal ou sérieux) ou s'il est **Léger**.

## 📊 Source des Données

Pour entraîner ce modèle, nous utilisons l'ensemble des données ouvertes sur la sécurité routière (Road Safety Data) fournies par le gouvernement britannique.

* **Source officielle** : [https://www.gov.uk/government/statistics/road-safety-data](https://www.gov.uk/government/statistics/road-safety-data)

Ce jeu de données complet est historiquement divisé en trois fichiers principaux :
* `collision.csv` : Détails sur les circonstances de l'accident (météo, conditions de route, localisation, etc.).
* `vehicle.csv` : Détails sur les véhicules impliqués (type, âge, propulsion, etc.).
* `casualty.csv` : Détails sur les victimes (âge, sexe, gravité de la blessure).

Pour ce projet, nous utilisons uniquement les fichiers **`collision.csv`** et **`vehicle.csv`**. Le fichier `casualty.csv` n'est pas utilisé car il contient des informations sur l'issue de l'accident, ce qui constituerait une fuite de données (data leakage) pour notre objectif de prédiction *à l'avance*.

> **Périmètre Géographique** : Bien que les données couvrent l'ensemble du Royaume-Uni (UK), notre analyse se concentre **exclusivement sur les accidents survenus en Angleterre**. Les données relatives à l'Écosse et au Pays de Galles sont filtrées lors de la préparation des données (basé sur les codes d'autorité locale commençant par "E").

## 🛠️ Préparation des Données

L'ensemble du processus de chargement, de nettoyage, de filtrage, de fusion et d'ingénierie des variables (feature engineering) est documenté en détail dans le fichier suivant :

➡️ **`documentation/DATAPREP.md`**
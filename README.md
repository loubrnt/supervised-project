# Prédiction de la Gravité des Accidents de la Route

## 🎯 Objectif du Projet

L'objectif principal de ce projet est de développer un modèle de machine learning capable de prédire la gravité d'un accident de la route (Grave ou Léger) au moment où il est signalé.

L'enjeu est de pouvoir déterminer quasi-instantanément si un accident venant de se produire nécessite une intervention d'urgence prioritaire (classé comme **Grave**, c'est-à-dire fatal ou sérieux) ou s'il est **Léger**.

## 📊 Source et Périmètre des Données

Pour entraîner ce modèle, nous utilisons l'ensemble des données ouvertes sur la sécurité routière (Road Safety Data) fournies par le gouvernement britannique.

* **Source officielle** : [https://www.gov.uk/government/statistics/road-safety-data](https://www.gov.uk/government/statistics/road-safety-data)

Ce jeu de données complet est historiquement divisé en trois fichiers principaux :
* `collision.csv` : Détails sur les circonstances de l'accident (météo, conditions de route, localisation, heure, etc.).
* `vehicle.csv` : Détails sur les véhicules impliqués (type, âge, propulsion, sexe du conducteur, etc.).
* `casualty.csv` : Détails sur les victimes. Ce fichier n'est pas utilisé pour éviter toute fuite de données (data leakage) concernant l'issue de l'accident.

> **Périmètre de l'Étude** :
> * **Géographie** : Angleterre uniquement (codes district commençant par "E").
> * **Véhicules** : L'analyse se concentre **exclusivement sur les voitures**. Les deux-roues, poids lourds et autres véhicules sont exclus pour homogénéiser les données d'entrée.

## 🛠️ Préparation des Données

Le pipeline de données a été mis à jour pour inclure une extraction temporelle précise (heure) et des filtres stricts sur l'âge des conducteurs et des véhicules.

**➡️ [Documentation de la Préparation des Données](documentation/DATAPREP.md)**

## 📈 Analyse Exploratoire (EDA)

L'analyse inclut désormais une étude croisée de l'heure et du jour de la semaine pour identifier les moments les plus accidentogènes.

**➡️ [Documentation de l'Analyse des Données](documentation/DATALYSIS.md)**
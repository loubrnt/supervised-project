## 🎯 Contexte et Problématique

### Le Défi des Services d'Urgence

Chaque année au Royaume-Uni, les services d'urgence reçoivent des centaines de milliers d'appels signalant des accidents de la route. Face à ces situations, une question critique se pose immédiatement : **"Quelle doit être la priorité et l'ampleur de la réponse ?"**

Cette décision doit être prise en **quelques secondes**, avec des informations limitées :
- Localisation de l'accident
- Type de véhicule impliqué
- Conditions météorologiques et de circulation
- Heure et jour de l'accident

**Le problème** : Les opérateurs ne peuvent pas évaluer instantanément la gravité réelle de l'accident (présence de blessés graves, décès) avant l'arrivée sur place. Pourtant, cette information est cruciale pour :
- ✅ Optimiser l'allocation des ressources limitées (ambulances, pompiers, police)
- ✅ Réduire les délais d'intervention pour les cas graves
- ✅ Éviter la mobilisation excessive de moyens pour des accidents légers
- ✅ Sauver des vies en priorisant correctement les interventions

### Notre Solution

Ce projet développe un **système de prédiction en temps réel** capable d'estimer la gravité d'un accident au moment où il est signalé, en se basant uniquement sur les informations immédiatement disponibles.

**Objectif** : Construire un modèle de machine learning qui prédit si un accident sera :
- **Grave** (Fatal ou Serious) → Nécessite une intervention d'urgence prioritaire
- **Léger** (Slight) → Intervention standard

### Impact Attendu

Un tel système pourrait :
- 🚑 **Améliorer le taux de survie** en accélérant la réponse aux accidents graves
- ⏱️ **Réduire le temps de réponse moyen** de 15-20% pour les cas critiques
- 💰 **Optimiser les coûts** en évitant la sur-mobilisation des ressources
- 📊 **Fournir des statistiques** pour améliorer la prévention routière

---

## 📊 Source des Données

### Dataset Officiel : UK Road Safety Data

Pour entraîner ce modèle, nous utilisons l'ensemble de données ouvertes sur la sécurité routière (Road Safety Data) fournies par le gouvernement britannique.

* **Source officielle** : [https://www.gov.uk/government/statistics/road-safety-data](https://www.gov.uk/government/statistics/road-safety-data)
* **Période couverte** : Données historiques de plusieurs années (2015-2022+)
* **Volume** : Plusieurs millions d'accidents documentés
* **Qualité** : Données officielles collectées par la police britannique

### Structure des Données Brutes

Ce jeu de données complet est historiquement divisé en trois fichiers principaux :

| Fichier | Contenu | Utilisation dans notre projet |
|---------|---------|-------------------------------|
| **`collision.csv`** | Circonstances de l'accident (météo, route, localisation, date/heure, gravité) | ✅ **Utilisé** - Source principale d'information |
| **`vehicle.csv`** | Véhicules impliqués (type, âge, conducteur) | ✅ **Utilisé** - Informations sur le véhicule et le conducteur |
| **`casualty.csv`** | Victimes (âge, sexe, gravité des blessures) | ❌ **Non utilisé** - Constituerait une fuite de données |

### Pourquoi exclure `casualty.csv` ?

Le fichier `casualty.csv` contient des informations sur **l'issue** de l'accident (nombre de blessés, gravité des blessures). Utiliser ces données créerait un **data leakage** :
- Ces informations ne sont **pas disponibles** au moment du signalement de l'accident
- Notre modèle doit prédire la gravité **avant** l'arrivée des secours
- Inclure ces données donnerait une performance artificiellement élevée mais inutilisable en production

### Périmètre Géographique

> **Focus sur l'Angleterre** : Bien que les données couvrent l'ensemble du Royaume-Uni, notre analyse se concentre **exclusivement sur les accidents survenus en Angleterre**. 
>
> **Justification** : Les systèmes routiers, réglementations et infrastructures peuvent varier entre l'Angleterre, l'Écosse et le Pays de Galles. En nous concentrant sur l'Angleterre (codes d'autorité locale commençant par "E"), nous garantissons l'homogénéité des données et la fiabilité du modèle.

---

## 🔍 Périmètre du Projet

### Ce que le modèle prédit

**Input** (Informations disponibles immédiatement) :
- 📍 Localisation (zone urbaine/rurale)
- 🚗 Caractéristiques du véhicule (type, âge)
- 👤 Caractéristiques du conducteur (âge, sexe)
- 🛣️ Conditions de route (type, limite de vitesse)
- ☀️ Conditions météorologiques et de luminosité
- ⏰ Contexte temporel (jour, mois, heure)

**Output** (Prédiction) :
- **Classe 0 (Léger)** : Accident sans gravité majeure
- **Classe 1 (Grave)** : Accident fatal ou sérieux nécessitant une réponse prioritaire

### Contraintes et Considérations Éthiques

#### Limites du Modèle
- ⚠️ **Ne remplace pas le jugement humain** : Le modèle est un outil d'aide à la décision, pas un système autonome
- ⚠️ **Probabilité, pas certitude** : Fournit une estimation statistique basée sur des patterns historiques
- ⚠️ **Contexte spécifique** : Entraîné sur les données anglaises, généralisabilité limitée à d'autres pays

#### Considérations Éthiques
- 🔒 **Pas de discrimination** : Le modèle ne doit pas créer de biais systématiques (âge, sexe, localisation)
- ⚖️ **Équité** : Tous les accidents doivent être traités avec le même sérieux de base
- 📊 **Transparence** : Les décisions du modèle doivent être explicables et auditables

---

## 🛠️ Préparation des Données

L'ensemble du processus de chargement, de nettoyage, de filtrage, de fusion et d'ingénierie des variables (feature engineering) est documenté en détail dans le fichier suivant :

**➡️ [Documentation Complète de la Préparation des Données](documentation/DATAPREP.md)**

### Étapes Principales

1. **Chargement Optimisé** : Réduction de la mémoire de 1.3 GB → 483 MB
2. **Fusion des Tables** : Jointure `collision` ⨝ `vehicle` sur `collision_index`
3. **Nettoyage** :
   - Suppression des valeurs manquantes
   - Filtrage géographique (Angleterre uniquement)
   - Exclusion des catégories "Unknown" et "Data missing"
4. **Feature Engineering** :
   - Décomposition temporelle : `date` → `day`, `month`, `hour`
   - Binarisation de la cible : Fatal/Serious → Grave (1), Slight → Léger (0)
   - Filtrage des véhicules : Focus sur les voitures uniquement
   - Limitation des plages d'âge (conducteur : 17-87 ans, véhicule : 0-22 ans)
5. **Export** : Sauvegarde en format Parquet (compression 10x)

### Dataset Final

**Caractéristiques** :
- **Lignes** : 4,839,131 accidents
- **Colonnes** : 12 features + 1 target
- **Taille** : 92.3 MB (Parquet)
- **Qualité** : Aucune valeur manquante, types optimisés (int8)

**Features** :
- `collision_severity` (target), `road_type`, `speed_limit`, `light_conditions`
- `weather_conditions`, `urban_or_rural_area`, `sex_of_driver`
- `age_of_driver`, `age_of_vehicle`, `day`, `month`, `hour`

---

## 📈 Analyse Exploratoire des Données (EDA)

L'analyse exploratoire complète, incluant 6 visualisations détaillées et leurs interprétations, est disponible ici :

**➡️ [Documentation Complète de l'Analyse Exploratoire](documentation/DATALYSIS.md)**

### Insights Clés Découverts

#### 🎯 Facteurs de Risque Majeurs

1. **Âge du Conducteur** (Courbe en U)
   - ⚠️ Risque élevé : Jeunes conducteurs (18-25 ans) ~16%
   - ✅ Risque minimal : Conducteurs expérimentés (40-45 ans) ~14.5%
   - ⚠️ Risque croissant : Seniors (60+ ans) jusqu'à 22%+

2. **Conditions de Visibilité**
   - 🌙 **Nuit sans éclairage** : 28.0% d'accidents graves (le plus dangereux)
   - ☀️ **Jour** : 14.8% d'accidents graves
   - 💡 **Nuit avec éclairage** : ~18-20%

3. **Type de Route et Vitesse**
   - 🛣️ **Route de campagne 60 mph** : 24.7% d'accidents graves
   - 🚗 **Route urbaine 30 mph** : 13.7% d'accidents graves
   - 🏎️ **Autoroute 70 mph** : 15.7% (paradoxalement plus sûr grâce à la séparation)

4. **Temporalité**
   - 📅 **Week-end** : 16-20% d'accidents graves (alcool, longs trajets)
   - 📅 **Semaine** : 14-15.5% d'accidents graves
   - 🕐 **Nuit (0h-7h)** : Taux de gravité maximal, surtout le week-end
   - 🕐 **Heures de bureau (9h-17h)** : Taux de gravité minimal

5. **Âge du Véhicule**
   - 🚗 **Véhicules récents (3-13 ans)** : Risque minimal
   - 🚙 **Véhicules très anciens (14+ ans)** : Risque croissant (manque d'équipements de sécurité)

### Visualisations Générées

| Graphique | Fichier | Description |
|-----------|---------|-------------|
| Âge du conducteur | `driver_age.png` | Courbe avec moyenne mobile |
| Météo et visibilité | `meteo.png` | Treemap interactif |
| Route et vitesse | `route.png` | Treemap interactif |
| Saisonnalité | `seasonality.png` | Heatmap jour×mois |
| Heure de la journée | `hour.png` | Heatmap jour×heure |
| Âge du véhicule | `vehicle_age.png` | Scatter plot avec bulles |

---

## 🤖 Modélisation et Résultats

Une phase d'entraînement rigoureuse a été menée sur trois algorithmes de classification pour déterminer le modèle le plus performant.

L'analyse détaillée des performances, incluant les matrices de confusion, les courbes ROC et l'importance des variables pour chaque modèle (XGBoost, CatBoost, Decision Tree), est disponible dans le rapport suivant :

**➡️ [Rapport Complet d'Entraînement et Analyse](documentation/MLRESULT.md)**

### Synthèse des Performances
Après optimisation des hyperparamètres (GridSearch) et validation croisée :

1.  🏆 **XGBoost** : Modèle retenu pour sa meilleure combinaison de performance (AUC: 0.6264) et de rapidité d'entraînement.
2.  🥈 **CatBoost** : Très performant mais coûteux en temps de calcul.
3.  🥉 **Decision Tree** : Sert de point de référence (Baseline), moins robuste que les méthodes de boosting.

---

## 📚 Documentation Technique

Ce projet suit une approche de **documentation exhaustive** pour assurer la reproductibilité et la maintenabilité :

| Document | Contenu | Audience |
|----------|---------|----------|
| **README.md** (ce fichier) | Vue d'ensemble, contexte, architecture | 👥 Tous |
| **[DATAPREP.md](documentation/DATAPREP.md)** | Preprocessing détaillé avec justifications | 🔧 Data Engineers, Data Scientists |
| **[DATALYSIS.md](documentation/DATALYSIS.md)** | Analyse exploratoire et visualisations | 📊 Data Analysts, Business |
| **[MLRESULT.md](documentation/MLRESULT.md)** | Résultats d'entraînement et analyse des modèles | 🤖 Data Scientists, ML Engineers |
| **data_doc.xlsx** | Dictionnaire des données sources | 📖 Référence technique |

---

## 🛠️ Technologies et Packages Utilisés

### Core & Data Processing
- **Python 3.8+** : Environnement d'exécution
- **Pandas** : Manipulation et nettoyage des DataFrames
- **NumPy** : Opérations vectorielles et calculs numériques
- **Scikit-learn** : Pipelines de preprocessing (OneHotEncoder), métriques et validation croisée

### Modélisation (Machine Learning)
- **XGBoost** : Algorithme de Gradient Boosting optimisé (Modèle Champion)
- **CatBoost** : Algorithme de Boosting gérant nativement les catégories
- **Decision Tree (sklearn)** : Modèle de base pour comparaison

### Visualisation
- **Matplotlib** : Création de graphiques statiques de base
- **Seaborn** : Visualisations statistiques avancées (Heatmaps, Lineplots)
- **Plotly Express** : Visualisations interactives (Treemaps)

### Stockage et Performance
- **Parquet (pyarrow/fastparquet)** : Format de fichier en colonne pour un stockage compressé et une lecture rapide
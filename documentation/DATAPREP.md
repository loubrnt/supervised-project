## 🏎️ Chargement et Optimisation des Données

La première étape consiste à charger les données en optimisant l'utilisation de la mémoire, en ne sélectionnant que les colonnes utiles (`usecols`) et en spécifiant des types de données plus légers (`dtype`).

### Pourquoi optimiser le chargement ?

L'optimisation de la mémoire est **cruciale** pour plusieurs raisons :
* **Performance** : Réduire l'empreinte mémoire permet un traitement plus rapide et évite les ralentissements
* **Scalabilité** : Permet de travailler sur des machines avec des ressources limitées
* **Coût** : Moins de RAM nécessaire = possibilité de travailler sur des environnements cloud moins coûteux
* **Efficacité** : En ne chargeant que les colonnes nécessaires, on évite de polluer notre environnement de travail avec des données inutiles

### Configuration du Chargement

| Fichier | Colonnes Sélectionnées (`usecols`) | Types Spécifiés (`dtypes`) |
| :--- | :--- | :--- |
| **`vehicle.csv`** | `collision_index`<br>`age_of_driver`<br>`propulsion_code`<br>`vehicle_type`<br>`age_of_vehicle`<br>`sex_of_driver` | `collision_index: object`<br>`vehicle_type: int8`<br>`age_of_driver: int8`<br>`age_of_vehicle: int8`<br>`propulsion_code: int8`<br>`sex_of_driver: int8` |
| **`collision.csv`** | `collision_index`<br>`urban_or_rural_area`<br>`speed_limit`<br>`date`<br>`road_type`<br>`light_conditions`<br>`weather_conditions`<br>`collision_severity`<br>`local_authority_ons_district`<br>`time` | `collision_index: object`<br>`road_type: int8`<br>`light_conditions: int8`<br>`weather_conditions: int8`<br>`collision_severity: int8`<br>`urban_or_rural_area: int8`<br>`speed_limit: float32` |

### Choix des types de données

Le choix des types est stratégique :
* **`int8`** : Pour les variables catégorielles avec peu de modalités (< 127 valeurs). Utilise seulement 1 octet par valeur au lieu de 8 octets pour un `int64` standard
* **`float32`** : Pour `speed_limit` qui nécessite des décimales mais pas une précision extrême. Utilise 4 octets au lieu de 8 pour `float64`
* **`object`** : Pour `collision_index` car c'est un identifiant textuel unique qui ne peut pas être converti en entier

### Impact sur la Mémoire

| Fichier | Mémoire (Avant Optimisation) | Mémoire (Après Optimisation) | Réduction |
| :--- | :--- | :--- | :--- |
| `vehicle.csv` | `737.0+ MB` | `199.6+ MB` | **-73%** |
| `collision.csv` | `619.0+ MB` | `283.7+ MB` | **-54%** |

Au total, nous économisons **environ 873 MB de RAM**, ce qui est considérable !

```python
# Chargement optimisé des véhicules
df_vehicle = pd.read_csv("data/vehicle.csv", usecols=VEHICLE_FIELDS, dtype=DTYPES_VEHICLE)

# Chargement optimisé des collisions
df_collision = pd.read_csv("data/collision.csv", usecols=COLLISION_FIELD, dtype=DTYPES_COLLISION)
```

-----

## 🤝 Fusion des Données

Les deux DataFrames (`df_vehicle` et `df_collision`) sont fusionnés en un seul DataFrame (`df`) en utilisant `collision_index` comme clé de jointure.

  * Une **jointure interne (`how="inner"`)** est utilisée, ce qui signifie que seuls les enregistrements présents dans *les deux* fichiers seront présents dans le DataFrame final.

```python
df = pd.merge(df_collision, df_vehicle, on="collision_index", how="inner")
```

### Pourquoi une jointure interne ?

Le choix d'une jointure **interne** plutôt qu'externe est délibéré :
* **Cohérence des données** : Nous voulons uniquement des accidents où nous avons à la fois les informations sur la collision ET sur le véhicule
* **Prédiction réaliste** : Dans un contexte réel, si nous n'avons pas d'information sur le véhicule impliqué, nous ne pourrions pas faire de prédiction avec notre modèle
* **Qualité > Quantité** : Mieux vaut avoir moins de données mais complètes que beaucoup de données avec des valeurs manquantes

-----

## 🧹 Nettoyage et Filtrage Initial

Un premier ensemble de filtres est appliqué pour nettoyer le jeu de données fusionné.

### Suppression des valeurs manquantes

```python
df = df.dropna()
```

**Justification** : Les valeurs `NaN` posent plusieurs problèmes :
* Incompatibilité avec de nombreux algorithmes de ML
* Source potentielle de biais si les données manquantes ne sont pas aléatoires
* Complexité accrue si imputation nécessaire
* Dans notre cas, nous avons suffisamment de données pour nous permettre de supprimer les lignes incomplètes

### Filtrage géographique

```python
df = df[df.local_authority_ons_district != -1]
df = df[df.local_authority_ons_district.apply(lambda x: x[0] == "E")]
```

**Justification** : 
* **Exclusion des codes invalides (-1)** : Données de localisation manquantes ou corrompues
* **Focus sur l'Angleterre (codes "E")** : Les systèmes routiers, réglementations et infrastructures peuvent varier entre l'Angleterre, l'Écosse et le Pays de Galles. En se concentrant sur l'Angleterre, nous évitons d'introduire de la variance géographique non désirée
* **Homogénéité** : Un modèle entraîné sur des données homogènes généralisera mieux

### Filtrage des zones urbaines/rurales

```python
df = df[df.urban_or_rural_area.isin([1, 2])]
```

**Justification** : 
* **1** = Urbain, **2** = Rural : Ce sont des catégories claires et bien définies
* **3** = "Unallocated" : Catégorie ambiguë qui pourrait introduire du bruit
* La distinction urbain/rural est un prédicteur potentiellement important (vitesses différentes, types de routes différents)

-----

## 🔬 Ingénierie des Variables (Feature Engineering)

Plusieurs colonnes sont transformées pour les rendre exploitables par un modèle.

### `vehicle_type` (Type de véhicule)

L'objectif est de binariser cette variable en **Voiture (1)** ou **Moto (0)**. Les véhicules non listés ci-dessous sont exclus.

| Catégorie | Codes Bruts | Valeur Finale |
| :--- | :--- | :--- |
| **Moto** | `[2, 3, 4, 5, 23, 97, 103, 104, 105, 106]` | **`0`** |
| **Voiture** | `[8, 9, 19, 108, 109, 110]` | **`1`** |

```python
df = df[df.vehicle_type.isin(TARGETED_CARS + TARGETED_MOTORCYCLES)]
df['vehicle_type'] = df['vehicle_type'].replace(TARGETED_CARS, 1)
df['vehicle_type'] = df['vehicle_type'].replace(TARGETED_MOTORCYCLES, 0)
```

**Pourquoi se limiter aux voitures et motos ?**
* **Volume de données** : Ces deux catégories représentent la grande majorité des accidents
* **Comparabilité** : Les voitures et motos ont des profils de risque différents mais comparables
* **Exclusion du bruit** : Véhicules spéciaux (bus, camions, véhicules agricoles) ont des dynamiques d'accident très différentes
* **Simplicité** : Facilite l'interprétation du modèle

**Note finale** : Seules les **voitures** (`vehicle_type == 1`) sont conservées pour l'analyse finale, et la colonne `vehicle_type` est ensuite supprimée.

**Pourquoi ne garder que les voitures ?**
* **Homogénéité** : Les motos ont un profil de risque radicalement différent (gravité beaucoup plus élevée, facteurs de risque différents)
* **Objectif du modèle** : Prédire la gravité pour les voitures, le cas d'usage le plus courant
* **Performance** : Un modèle spécialisé sur les voitures sera plus performant qu'un modèle généraliste

### `propulsion_code` (Type de propulsion)

Cette variable est filtrée mais finalement **supprimée** du dataset.

```python
df = df[df.propulsion_code.isin(PROPULSION_THERMIQUE + PROPULSTION_ECTRIQUE_HYBRIDE)]
df = df.drop(columns=["propulsion_code"])
```

**Pourquoi filtrer puis supprimer ?**
* **Filtrage** : On exclut les types de propulsion rares ou non définis (ex: propulsion à hydrogène, données manquantes) pour garder la cohérence
* **Suppression** : Après analyse exploratoire, cette variable s'est avérée peu prédictive de la gravité. Les véhicules électriques/hybrides sont encore relativement récents et leur effet est probablement déjà capturé par `age_of_vehicle`

### `date` et `time` (Date et heure de l'accident)

Les colonnes `date` et `time` sont utilisées pour extraire de nouvelles caractéristiques temporelles.

```python
df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
df['day'] = df['date'].dt.day_name()
df['month'] = df['date'].dt.month
df['hour'] = df['time'].str.split(':').str[0].astype("int8")
df.day = df.day.map(DAY_MAPPING).astype("int8")  # Lundi=0, Dimanche=6
```

**Justification de la décomposition temporelle** :

1. **`day` (Jour de la semaine)** :
   * **Hypothèse** : Les accidents de week-end sont différents (loisirs, alcool) des accidents en semaine (trajet travail)
   * **Encodage numérique** : 0-6 permet aux modèles de ML de capturer une relation ordinale

2. **`month` (Mois de l'année)** :
   * **Saisonnalité** : Conditions météo, luminosité, vacances scolaires varient selon les mois
   * **Trafic** : Pics de circulation en été (vacances) vs hiver

3. **`hour` (Heure de la journée)** :
   * **Très prédictif** : La nuit (fatigue, alcool, visibilité) vs le jour
   * **Heures de pointe** : Comportements de conduite différents
   * **Granularité** : 24 valeurs permettent de capturer des patterns fins

**Pourquoi supprimer la date originale ?**
* Évite le surapprentissage sur des dates spécifiques (ex: "le 15/08/2019 est dangereux")
* Les features dérivées (`day`, `month`, `hour`) capturent l'information utile de manière généralisable

### `sex_of_driver` (Sexe du conducteur)

```python
df = df[~df.sex_of_driver.isin([3, -1])]
```

**Justification** : 
* **1** = Masculin, **2** = Féminin : Catégories claires
* **3** = "Not known" / "Autre" : Données ambiguës ou manquantes
* **-1** = Données manquantes
* Cette variable peut capturer des différences de comportement au volant documentées dans la littérature

### `speed_limit` (Limite de vitesse)

```python
df = df[df.speed_limit.isin([30, 60, 40, 70, 50, 20])]
df.speed_limit = df.speed_limit.astype("int8")
```

**Justification** :
* **Limites standard** : Ce sont les limites de vitesse officielles au Royaume-Uni
* **Exclusion des valeurs aberrantes** : Élimine les erreurs de saisie (ex: 999, 0)
* **Prédicteur clé** : La vitesse est fortement corrélée à la gravité des accidents
* **Conversion int8** : Après validation, on peut économiser de la mémoire

### `collision_severity` (Variable Cible)

C'est la variable cible (Y). Elle est transformée en problème de classification binaire : **Grave (1)** vs **Léger (0)**.

| Gravité (Entrée) | Description | Valeur Finale (Sortie) |
| :--- | :--- | :--- |
| `1` | Fatal | **`1`** |
| `2` | Serious | **`1`** |
| `3` | Slight | **`0`** |

```python
df.collision_severity = (df.collision_severity != 3).astype("int8")
```

**Pourquoi binariser ?**
* **Objectif métier** : Le système d'urgence doit décider : "Envoyer des moyens lourds ou légers ?"
* **Simplicité** : Plus facile à interpréter qu'une classification à 3 classes
* **Déséquilibre** : Fatal (classe 1) est très rare. En la fusionnant avec Serious, on équilibre mieux les classes
* **Réalisme** : Fatal et Serious nécessitent tous deux une réponse d'urgence prioritaire

-----

## 🗑️ Filtrage Final et Finalisation

Des filtres supplémentaires sont appliqués pour exclure les données non pertinentes ou inconnues, ainsi que pour limiter les plages de valeurs.

### Filtrage des conditions de luminosité

```python
df = df[df.light_conditions.isin([1, 4, 5, 6])]
```

**Catégories conservées** :
* 1 = Daylight (Jour)
* 4 = Darkness - lights lit (Nuit - éclairage allumé)
* 5 = Darkness - lights unlit (Nuit - éclairage non allumé)
* 6 = Darkness - no lighting (Nuit - pas d'éclairage)

**Pourquoi exclure les autres ?** : Catégories comme "Unknown" ou "Data missing" n'apportent pas d'information

### Filtrage du type de route et météo

```python
df = df[~df.road_type.isin([9, -1])]
df = df[~df.weather_conditions.isin([8, 9, -1])]
```

**Logique** : On exclut systématiquement :
* **9** = "Unknown" : Information non disponible
* **-1** = "Data missing" : Données manquantes
* **8** (météo) = "Other" : Catégorie fourre-tout peu informative

### Filtrage des âges

```python
df = df[~df.age_of_vehicle.isin([-1])]
df = df[~df.age_of_driver.isin([-1])]
df = df[df.age_of_driver >= 17]
df = df[df.age_of_driver <= 87]
df = df[df.age_of_vehicle >= 0]
df = df[df.age_of_vehicle <= 22]
```

**Justification des bornes** :

**Âge du conducteur (17-87 ans)** :
* **Minimum 17 ans** : Âge légal minimum pour conduire au Royaume-Uni
* **Maximum 87 ans** : Au-delà, les données deviennent très rares et potentiellement aberrantes (erreurs de saisie)
* **Distribution** : Capture 99%+ des conducteurs réels

**Âge du véhicule (0-22 ans)** :
* **Minimum 0 ans** : Véhicules neufs
* **Maximum 22 ans** : Au-delà, volume très faible et véhicules potentiellement atypiques (véhicules de collection)
* **Réalisme** : Correspond au parc automobile réel sur les routes

### Suppression des colonnes inutiles

```python
df.drop_duplicates()
df = df.drop(columns=["date", "collision_index", "local_authority_ons_district", "time"])
df = df[df.vehicle_type == 1].drop(columns=["vehicle_type"])
```

**Pourquoi supprimer ces colonnes ?**

* **`date` et `time`** : Information déjà extraite dans `day`, `month`, `hour`
* **`collision_index`** : Identifiant unique, inutile pour la prédiction (risque de surapprendre)
* **`local_authority_ons_district`** : Trop granulaire (centaines de valeurs), utilisé uniquement pour le filtrage
* **`vehicle_type`** : Après avoir gardé uniquement les voitures, cette colonne est constante

-----

## 📊 Dataset Final

Après l'ensemble du processus de nettoyage et de transformation, le dataset final contient :

**Dimensions**: **4,839,131 lignes × 12 colonnes**

**Colonnes finales**:
- `collision_severity` (int8) - **Variable cible** - 0=Léger, 1=Grave
- `road_type` (int8) - Type de route (rond-point, chaussée unique, etc.)
- `speed_limit` (int8) - Limite de vitesse en mph
- `light_conditions` (int8) - Conditions de luminosité
- `weather_conditions` (int8) - Conditions météorologiques
- `urban_or_rural_area` (int8) - Zone urbaine (1) ou rurale (2)
- `sex_of_driver` (int8) - Sexe du conducteur
- `age_of_driver` (int8) - Âge du conducteur (17-87 ans)
- `age_of_vehicle` (int8) - Âge du véhicule (0-22 ans)
- `day` (int8) - Jour de la semaine (0=Lundi, 6=Dimanche)
- `month` (int8) - Mois de l'année (1-12)
- `hour` (int8) - Heure de la journée (0-23)

**Utilisation mémoire**: **~92.3 MB** (réduction drastique par rapport aux ~1.3 GB initiaux !)

**Qualité des données** :
* ✅ Aucune valeur manquante
* ✅ Toutes les variables sont numériques (compatibles ML)
* ✅ Types optimisés (int8)
* ✅ Plages de valeurs validées
* ✅ Dataset homogène et cohérent

-----

## 💾 Export

Le DataFrame final, nettoyé et transformé, est sauvegardé au format **Parquet**. Ce format est optimisé pour le stockage et la lecture rapide des données analytiques.

```python
df.to_parquet("./data/clean_dataset.parquet")
```

**Pourquoi Parquet plutôt que CSV ?**

| Critère | CSV | Parquet | Gagnant |
|---------|-----|---------|---------|
| **Taille du fichier** | ~500 MB | ~50 MB | ✅ **Parquet** (10x plus petit) |
| **Vitesse de lecture** | Lent | Très rapide | ✅ **Parquet** |
| **Préservation des types** | ❌ Non | ✅ Oui | ✅ **Parquet** |
| **Compression** | ❌ Non | ✅ Oui | ✅ **Parquet** |
| **Lisibilité humaine** | ✅ Oui | ❌ Non | CSV |

**Parquet est le choix optimal pour** :
* Le machine learning (lecture rapide de grandes quantités de données)
* La préservation exacte des types de données
* L'économie d'espace disque
* Les pipelines de données en production
# 1\. 🏎️ Chargement et Optimisation des Données

La première étape consiste à charger les données en optimisant l'utilisation de la mémoire, en ne sélectionnant que les colonnes utiles (`usecols`) et en spécifiant des types de données plus légers (`dtype`).

### Configuration du Chargement

| Fichier | Colonnes Sélectionnées (`usecols`) | Types Spécifiés (`dtypes`) |
| :--- | :--- | :--- |
| **`vehicle.csv`** | `collision_index`<br>`age_of_driver`<br>`propulsion_code`<br>`vehicle_type`<br>`age_of_vehicle` | `collision_index: object`<br>`vehicle_type: int8`<br>`age_of_driver: int8`<br>`age_of_vehicle: int8`<br>`propulsion_code: int8` |
| **`collision.csv`** | `collision_index`<br>`urban_or_rural_area`<br>`speed_limit`<br>`date`<br>`road_type`<br>`light_conditions`<br>`weather_conditions`<br>`collision_severity`<br>`local_authority_ons_district` | `collision_index: object`<br>`road_type: int8`<br>`light_conditions: int8`<br>`weather_conditions: int8`<br>`collision_severity: int8`<br>`urban_or_rural_area: int8`<br>`speed_limit: float32` |

### Impact sur la Mémoire

| Fichier | Mémoire (Avant Optimisation) | Mémoire (Après Optimisation) |
| :--- | :--- | :--- |
| `vehicle.csv` | `737.0+ MB` | `199.6+ MB` |
| `collision.csv` | `619.0+ MB` | `283.7+ MB` |

```python
# Chargement optimisé des véhicules
df_vehicle = pd.read_csv("data/vehicle.csv", usecols=vehicle_fields, dtype=dtypes_vehicle)

# Chargement optimisé des collisions
df_collision = pd.read_csv("data/collision.csv", usecols=collision_fields, dtype=dtypes_collision)
```

-----

## 2\. 🤝 Fusion des Données

Les deux DataFrames (`df_vehicle` et `df_collision`) sont fusionnés en un seul DataFrame (`df`) en utilisant `collision_index` comme clé de jointure.

  * Une **jointure interne (`how="inner"`)** est utilisée, ce qui signifie que seuls les enregistrements présents dans *les deux* fichiers seront présents dans le DataFrame final.

<!-- end list -->

```python
df = pd.merge(df_collision, df_vehicle, on="collision_index", how="inner")
```

-----

## 3\. 🧹 Nettoyage et Filtrage Initial

Un premier ensemble de filtres est appliqué pour nettoyer le jeu de données fusionné.

  * **Suppression des nuls**: `df.dropna()` retire toutes les lignes contenant au moins une valeur `NaN`.
  * **Filtrage géographique**:
    1.  `df = df[df.local_authority_ons_district != -1]`: Exclut les codes de district manquants ou hors plage.
    2.  `df = df[df.local_authority_ons_district.apply(lambda x: x[0] == "E")]`: Sélectionne uniquement les districts dont le code commence par "E" (probablement l'Angleterre).
  * **Filtrage de zone**: `df = df[df.urban_or_rural_area.isin([1,2])]`: Sélectionne uniquement les zones urbaines (1) et rurales (2), excluant la classe (3) "Unallocated".

-----

## 4\. 🔬 Ingénierie des Variables (Feature Engineering)

Plusieurs colonnes sont transformées pour les rendre exploitables par un modèle.

### `vehicle_type` (Type de véhicule)

L'objectif est de binariser cette variable en **Voiture (1)** ou **Moto (0)**. Les véhicules non listés ci-dessous sont exclus.

| Catégorie | Codes Bruts | Valeur Finale |
| :--- | :--- | :--- |
| **Moto** | `[2, 3, 4, 5, 23, 97, 103, 104, 105, 106]` | **`0`** |
| **Voiture** | `[8, 9, 19, 108, 109, 110]` | **`1`** |

```python
df = df[df.vehicle_type.isin(cars + motrocycles)]
df['vehicle_type'] = df['vehicle_type'].replace(cars, 1)
df['vehicle_type'] = df['vehicle_type'].replace(motrocycles, 0)
```

### `propulsion_code` (Type de propulsion)

Cette variable est binarisée en **Thermique (1)** ou **Électrique/Hybride (0)**. Les autres types de propulsion sont exclus.

| Catégorie | Codes Bruts | Valeur Finale |
| :--- | :--- | :--- |
| **Élec./Hybride** | `[3, 8, 11, 12]` | **`0`** |
| **Thermique** | `[1, 2, 5, 6, 7, 9, 10]` | **`1`** |

```python
df = df[df.propulsion_code.isin(propulsion_thermique + propulsion_electrique_hybride)]
df['propulsion_code'] = df['propulsion_code'].replace(propulsion_thermique, 1)
df['propulsion_code'] = df['propulsion_code'].replace(propulsion_electrique_hybride, 0)
```

### `date` (Date de l'accident)

La colonne `date` est utilisée pour extraire de nouvelles caractéristiques temporelles.

1.  **Conversion**: `df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')`
2.  **Extraction**:
      * `df['day'] = df['date'].dt.day_name()` (Ex: "Monday")
      * `df['month'] = df['date'].dt.month` (Ex: 12)

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

-----

## 5\. 🗑️ Filtrage Final et Finalisation

Des filtres supplémentaires sont appliqués pour exclure les données non pertinentes ou inconnues.

  * `df[df.light_conditions.isin([1,4,5,6])]`: Sélectionne "Daylight", "Darkness - lights lit", "Darkness - lights unlit", "Darkness - no lighting".
  * `df[~df.road_type.isin([9,-1])]`: Exclut "Unknown" et "Data missing".
  * `df[~df.weather_conditions.isin([8,9,-1])]`: Exclut "Other", "Unknown" et "Data missing".
  * `df[~df.age_of_vehicle.isin([-1])]`: Exclut "Data missing".
  * `df[~df.age_of_driver.isin([-1])]`: Exclut "Data missing".

> **Note**: Dans le script fourni, ces filtres sont exécutés sans ré-assigner le DataFrame (ils devraient être écrits `df = df[...]`). Tel quel, le filtrage n'est pas appliqué au DataFrame final.

Enfin, les colonnes devenues inutiles sont supprimées :

```python
df = df.drop(columns=["date", "collision_index", "local_authority_ons_district"])
```

-----

## 6\. 💾 Export

Le DataFrame final, nettoyé et transformé, est sauvegardé au format **Parquet**. Ce format est optimisé pour le stockage et la lecture rapide des données analytiques.

```python
df.to_parquet("./data/clean_dataset.parquet")
```
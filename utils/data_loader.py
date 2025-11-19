import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

pd.options.display.max_columns = None

VEHICLE_FIELDS = [
    "collision_index",
    "age_of_driver",
    "propulsion_code",
    "vehicle_type",
    "age_of_vehicle",
    "sex_of_driver",
]
DTYPES_VEHICLE = {
    "collision_index": "object",
    "vehicle_type": "int8",
    "age_of_driver": "int8",
    "age_of_vehicle": "int8",
    "propulsion_code": "int8",
    "sex_of_driver": "int8",
}
COLLISION_FIELD = [
    "collision_index",
    "urban_or_rural_area",
    "speed_limit",
    "date",
    "road_type",
    "light_conditions",
    "weather_conditions",
    "collision_severity",
    "local_authority_ons_district",
    "time"
]
DTYPES_COLLISION = {
    "collision_index": "object",
    "road_type": "int8",
    "light_conditions": "int8",
    "weather_conditions": "int8",
    "collision_severity": "int8",
    "urban_or_rural_area": "int8",
    "weather_conditions": "int8",
    "speed_limit": "float32",
}
DAY_MAPPING = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
TARGETED_CARS = [8, 9, 19, 108, 109, 110]
TARGETED_MOTORCYCLES = [2, 3, 4, 5, 23, 97, 103, 104, 105, 106]
PROPULSION_THERMIQUE = [1, 2, 5, 6, 7, 9, 10]
PROPULSTION_ECTRIQUE_HYBRIDE = [3, 8, 11, 12]

def load_datset(collison_path:str, vehicle_path:str, save_path:str)->pd.DataFrame:
    df_vehicle = pd.read_csv(
        vehicle_path, usecols=VEHICLE_FIELDS, dtype=DTYPES_VEHICLE
    )
    df_collision = pd.read_csv(
        collison_path, usecols=COLLISION_FIELD, dtype=DTYPES_COLLISION
    )

    df = pd.merge(df_collision, df_vehicle, on="collision_index", how="inner")
    df = df.dropna()
    df = df[df.local_authority_ons_district != -1]
    df = df[df.local_authority_ons_district.apply(lambda x: x[0] == "E")]
    df = df[df.local_authority_ons_district.apply(lambda x: x[0] == "E")]

    df = df[df.urban_or_rural_area.isin([1, 2])]

    df = df[df.vehicle_type.isin(TARGETED_CARS + TARGETED_MOTORCYCLES)]
    df["vehicle_type"] = df["vehicle_type"].replace(TARGETED_CARS, 1)
    df["vehicle_type"] = df["vehicle_type"].replace(TARGETED_MOTORCYCLES, 0)

    df = df[df.propulsion_code.isin(PROPULSION_THERMIQUE + PROPULSTION_ECTRIQUE_HYBRIDE)]
    df = df.drop(columns=["propulsion_code"])

    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    df["day"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.month.astype("int8")

    df = df[df.light_conditions.isin([1, 4, 5, 6])]
    df = df[~df.road_type.isin([9, -1])]
    df = df[~df.weather_conditions.isin([8, 9, -1])]
    df = df[~df.age_of_vehicle.isin([-1])]
    df = df[~df.age_of_driver.isin([-1])]
    df = df[~df.sex_of_driver.isin([3, -1])]
    df = df[df.speed_limit.isin([30, 60, 40, 70, 50, 20])]

    df = df[df.age_of_driver >= 17]
    df = df[df.age_of_driver <= 87]

    df = df[df.age_of_vehicle >= 0]
    df = df[df.age_of_vehicle <= 22]

    df['hour'] = df['time'].str.split(':').str[0].astype("int8")

    df.speed_limit = df.speed_limit.astype("int8")

    df.day = df.day.map(DAY_MAPPING).astype("int8")

    df.collision_severity = (df.collision_severity != 3).astype("int8")

    df.drop_duplicates()

    df = df.drop(columns=["date", "collision_index", "local_authority_ons_district","time"])
    df = df[df.vehicle_type == 1].drop(columns=["vehicle_type"])

    df.to_parquet(save_path)

    print(df.info())
    return df

def one_hot_encode_dataset(dataset_to_encode:pd.DataFrame, features_to_encode:list) -> pd.DataFrame:
    encoder = OneHotEncoder()
    encoder = OneHotEncoder(sparse_output=False, dtype=np.int8)
    one_hot_encoded = encoder.fit_transform(dataset_to_encode[features_to_encode])
    one_hot_df = pd.DataFrame(one_hot_encoded, 
                            columns=encoder.get_feature_names_out(features_to_encode))
    df_one_hot_encoded = pd.concat([dataset_to_encode.drop(features_to_encode, axis=1).reset_index(drop=True), one_hot_df.reset_index(drop=True)], axis=1)
    return df_one_hot_encoded

def sin_cos_encode_dataset(dataset_to_encode:pd.DataFrame, features_to_encode:list) -> pd.DataFrame:
    df = dataset_to_encode.copy()
    
    for feature in features_to_encode:
        max_val = df[feature].max()
        min_val = df[feature].min()
        range_val = max_val - min_val
        
        df[f'{feature}_sin'] = np.sin(2 * np.pi * (df[feature] - min_val) / range_val)
        df[f'{feature}_cos'] = np.cos(2 * np.pi * (df[feature] - min_val) / range_val)
        df[f'{feature}_sin'] = df[f'{feature}_sin'].astype("float16")
        df[f'{feature}_cos'] = df[f'{feature}_cos'].astype("float16")
        
        df = df.drop(columns=[feature])
    
    return df
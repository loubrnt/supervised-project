import pandas as pd
pd.options.display.max_columns = None

vehicle_fields = ["collision_index","age_of_driver","propulsion_code","vehicle_type","age_of_vehicle","sex_of_driver"]
dtypes_vehicle = {
    'collision_index': 'object',
    'vehicle_type': 'int8',
    'age_of_driver': 'int8',
    'age_of_vehicle': 'int8',
    "propulsion_code": 'int8',
    "sex_of_driver": 'int8'
}

collision_fields = ["collision_index","urban_or_rural_area","speed_limit","date","road_type","light_conditions","weather_conditions","collision_severity","local_authority_ons_district"]
dtypes_collision = {
    'collision_index': 'object',
    'road_type': 'int8',
    "light_conditions": 'int8',
    "weather_conditions": 'int8',
    "collision_severity": 'int8',
    "urban_or_rural_area": 'int8',
    "weather_conditions": 'int8',
    "speed_limit": 'float32'
}

# df_vehicle = pd.read_csv("data/vehicle.csv", usecols=vehicle_fields, low_memory=True)
# print(df_vehicle.info())
df_vehicle = pd.read_csv("data/vehicle.csv", usecols=vehicle_fields, dtype=dtypes_vehicle)
# print(df_vehicle.info())

# df_collision = pd.read_csv("data/collision.csv", usecols=collision_fields, low_memory=True)
# print(df_collision.info())
df_collision = pd.read_csv("data/collision.csv", usecols=collision_fields, dtype=dtypes_collision)
# print(df_collision.info())

day_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}

cars = [8, 9, 19, 108, 109, 110]
motrocycles = [2, 3, 4, 5, 23, 97, 103, 104, 105, 106]
propulsion_thermique = [1, 2, 5, 6, 7, 9, 10]
propulsion_electrique_hybride = [3, 8, 11, 12]

df = pd.merge(df_collision,df_vehicle, on="collision_index", how="inner")
df = df.dropna()
df = df[df.local_authority_ons_district != -1]
df = df[df.local_authority_ons_district.apply(lambda x: x[0] == "E")]
df = df[df.local_authority_ons_district.apply(lambda x: x[0] == "E")]

df = df[df.urban_or_rural_area.isin([1,2])]

df = df[df.vehicle_type.isin(cars + motrocycles)]
df['vehicle_type'] = df['vehicle_type'].replace(cars, 1)
df['vehicle_type'] = df['vehicle_type'].replace(motrocycles, 0)

df = df[df.propulsion_code.isin(propulsion_thermique + propulsion_electrique_hybride)]
df['propulsion_code'] = df['propulsion_code'].replace(propulsion_thermique, 1)
df['propulsion_code'] = df['propulsion_code'].replace(propulsion_electrique_hybride, 0)

df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
df['day'] = df['date'].dt.day_name()
df['month'] = df['date'].dt.month

df = df[df.light_conditions.isin([1,4,5,6])]
df = df[~df.road_type.isin([9,-1])]
df = df[~df.weather_conditions.isin([8,9,-1])]
df = df[~df.age_of_vehicle.isin([-1])]
df = df[~df.age_of_driver.isin([-1])]
df = df[~df.sex_of_driver.isin([3,-1])]

df = df[df.age_of_driver>=17]
df = df[df.age_of_driver<=87]

df = df[df.age_of_vehicle>=0]
df = df[df.age_of_vehicle<=25]

df.speed_limit = df.speed_limit.astype('int8')

df.day = df.day.map(day_mapping).astype('int8')

df.collision_severity = (df.collision_severity != 3).astype("int8")

df.drop_duplicates()

df = df.drop(columns=["date","collision_index","local_authority_ons_district"])

df.to_parquet("./data/clean_dataset.parquet")
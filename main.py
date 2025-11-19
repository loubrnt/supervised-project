import models
from utils import data_loader, data_analyzer

COLLISION_PATH = "data/collision.csv"
VEHICLE_PATH = "data/vehicle.csv"
SAVE_PATH = "data/clean_dataset.parquet"
CATEGORICAL_FIELDS = ["road_type","weather_conditions","urban_or_rural_area","sex_of_driver"]
TIME_CYCLE_FIELDS = ["month","day","hour"]

if __name__ == '__main__':
    df = data_loader.load_datset(COLLISION_PATH, VEHICLE_PATH, SAVE_PATH)
    print("Main Dataframe loaded and cleaned.")
    print(f"Main Dataframe saved in the following path: {SAVE_PATH}")
    data_analyzer.generate_plots(df)
    print("Plots generated and saved in ./pictures.")

    df_time_encoded = data_loader.sin_cos_encode_dataset(df,TIME_CYCLE_FIELDS)
    print("Dataframe as successfully been time encoded using sin-cos transform.")
    df_one_hot_time_encoded = data_loader.one_hot_encode_dataset(df_time_encoded,CATEGORICAL_FIELDS)
    # xgboost_model = models.xgboost.train_and_save_results(df_one_hot_time_encoded)
    # decision_tree_model = models.decision_tree.train_and_save_results(df_one_hot_time_encoded)
    catboost_model = models.catboost.train_and_save_results(df_time_encoded,CATEGORICAL_FIELDS)
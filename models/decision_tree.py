import numpy as np
from utils import data_analyzer
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold, GridSearchCV
import time

def train_and_save_results(X, path_img="decision_tree"):
    print("Démarrage de l'entraînement du classifieur Decision Tree avec GridSearchCV")
    y = X['collision_severity']
    X = X.drop('collision_severity', axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    param_grid = {
        'max_depth': [3, 5, 7, 10, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'criterion': ['gini', 'entropy']
    }
    print(f"Grille de paramètres définie avec {len(param_grid['max_depth']) * len(param_grid['min_samples_split']) * len(param_grid['min_samples_leaf']) * len(param_grid['criterion'])} combinaisons possibles")

    pos_class_weight = ((len(y) - np.sum(y)) / np.sum(y))
    print(f"Poids de la classe positive : {pos_class_weight:.4f}")

    base_model = DecisionTreeClassifier(
        random_state=42,
        class_weight={1: pos_class_weight}
    )

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    print("Initialisation de StratifiedKFold avec 5 plis")

    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=skf,
        scoring='roc_auc',
        n_jobs=4,
        verbose=2
    )

    print("Lancement de la recherche par grille...")
    start_time = time.time()
    grid_search.fit(X_train, y_train)
    end_time = time.time()
    print(f"Temps d'entraînement : {end_time - start_time:.2f} secondes")
    print("Recherche par grille terminée")

    print(f"Meilleurs paramètres : {grid_search.best_params_}")
    print(f"Meilleur score CV : {grid_search.best_score_:.4f}")

    best_model = grid_search.best_estimator_
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]

    print("Sauvegarde de la matrice de confusion")
    data_analyzer.plot_confusion_matrix(y_pred_proba, y_test, path_img)
    print("Sauvegarde de la courbe ROC")
    data_analyzer.plot_roc_curve(y_pred_proba, y_test, path_img)
    print("Sauvegarde des features importances")
    data_analyzer.plot_feature_importance(best_model, X.columns, path_img)

    print("Processus d'entraînement du classifieur Decision Tree avec GridSearch achevé")

    return best_model
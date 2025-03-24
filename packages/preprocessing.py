import os

from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from joblib import dump, load
from interface.api_params import *

# Vérifier si les fichiers pickle existent
PICKLE_FILES = ['pkl_file/preprocessor.pkl', 'pkl_file/lst_to_drop.pkl', 'pkl_file/X_train_columns.pkl']
USE_PICKLE = all(os.path.exists(f) for f in PICKLE_FILES)

# Charger les données uniquement si nécessaire


def qualitative_to_quantitative(column_names, mapping, df):
    for col in column_names:
        if col in df.columns:
            df[{col}] = df[col].map(mapping[col])
        #else:
            #print(f"Colonne '{col}' non trouvée dans le DataFrame.")
    return df


def qualitative_to_quantitative_user(user_df, mapping):
    column_names = list(mapping.keys())
    for col in column_names:
        if col in user_df.columns and col in mapping.keys():
            # Remplacement des valeurs selon le mapping
            user_df[col] = user_df[col].map(mapping[col])
        elif col not in mapping.keys():
            print(f"Mapping pour la colonne '{col}' non trouvé dans le dictionnaire.")
        else:
            print(f"Colonne '{col}' non trouvée dans le DataFrame.")
    return user_df


def preprocess_features(mappings=seuils_performance):
    if USE_PICKLE:
        print("Les données transformées seront chargées à partir des fichiers pickle.")
        return load_preprocessing_objects()

    df = clean_user_data()
    df = qualitative_to_quantitative(mapping=mappings, column_names=list(seuils_performance.keys()), df=df)

    X = df.drop(columns=['Etiquette_DPE'])
    y = df[['Etiquette_DPE']]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    categorical_features = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_features = X.select_dtypes(include=["float", "int"]).columns.tolist()

    def impute_median(X):
        X = X.copy()
        for col in numerical_features:
            if col in X.columns:
                group_median = X.groupby(['Période_construction', 'Type_bâtiment'])[col].transform('median')
                X[col] = X[col].fillna(group_median)
        return X

    X_train_imputed = impute_median(X_train)
    X_test_imputed = impute_median(X_test)

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy='constant', fill_value="Na")),
        ("onehot", OneHotEncoder(drop='if_binary', handle_unknown='ignore', sparse_output=False))
    ])

    numerical_pipeline = Pipeline([
        ("numerical", StandardScaler())
    ])

    preprocessor = ColumnTransformer([
        ("categorical", categorical_pipeline, categorical_features),
        ("numerical", numerical_pipeline, numerical_features),
    ])

    preprocessor.set_output(transform='pandas')

    X_train_transformed = preprocessor.fit_transform(X_train_imputed)
    X_test_transformed = preprocessor.transform(X_test_imputed)

    lst_to_drop = [
        'categorical__Période_construction_1948-1974',
        'categorical__Période_construction_1975-1977',
        'categorical__Période_construction_1978-1982',
        'categorical__Période_construction_1983-1988',
        'categorical__Période_construction_1989-2000',
        'categorical__Période_construction_2001-2005',
        'categorical__Période_construction_2006-2012',
        'categorical__Période_construction_2013-2021',
        'categorical__Période_construction_après 2021',
        'categorical__Période_construction_avant 1948'
    ]
    X_train_transformed = X_train_transformed.drop(columns=lst_to_drop)
    X_test_transformed = X_test_transformed.drop(columns=lst_to_drop)

    target_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy='constant', fill_value="Na")),
        ("ordinal", OrdinalEncoder(categories=[["A", "B", "C", "D", "E", "F", "G"]]))
    ])

    y_train_transformed = target_pipeline.fit_transform(y_train).ravel()
    y_test_transformed = target_pipeline.transform(y_test).ravel()

    dump(preprocessor, 'pkl_file/preprocessor.pkl')
    dump(lst_to_drop, 'pkl_file/lst_to_drop.pkl')
    dump(X_train.columns.tolist(), 'pkl_file/X_train_columns.pkl')

    return X_train_transformed, X_test_transformed, y_train_transformed, y_test_transformed, preprocessor, lst_to_drop, X_train


def load_preprocessing_objects():
    preprocessor = load('pkl_file/preprocessor.pkl')
    lst_to_drop = load('pkl_file/lst_to_drop.pkl')
    X_train_columns = load('pkl_file/X_train_columns.pkl')
    return preprocessor, lst_to_drop, X_train_columns


def clean_user_data(user_df):
    user_df = user_df.drop(columns=['_score'], errors='ignore').drop_duplicates()

    for col in user_df.columns:
        if user_df[col].dtype == 'object' and user_df[col].str.contains(',', na=False).any():
            user_df[col] = user_df[col].str.replace(',', '.').astype(float, errors='ignore')
    user_df = user_df[user_df["Type_bâtiment"] != "immeuble"]
    user_df["Déperditions_menuiseries"] = user_df["Déperditions_portes"] + user_df["Deperditions_baies_vitrées"]
    user_df.drop(columns=['Déperditions_portes', 'Deperditions_baies_vitrées'])

    for col in deperditions_columns:
        user_df[f"{col}_m2"] = user_df[col] / user_df["Surface_habitable_logement"]
    user_df = user_df[sorted(user_df.columns)]
    return user_df


def preprocess_user_data(user_df):

    preprocessor, lst_to_drop, X_train_columns = load_preprocessing_objects()

    X_user = user_df.drop(columns=['Etiquette_DPE'], errors='ignore')

    missing_cols = set(X_train_columns) - set(X_user.columns)
    print("Colonnes manquantes :", missing_cols)

    for col in missing_cols:
        X_user[col] = "Na" if col.startswith("categorical__") else None

    extra_cols = set(X_user.columns) - set(X_train_columns)
    print("Colonnes supplémentaires :", extra_cols)
    X_user = X_user.drop(columns=extra_cols, errors="ignore")

    X_user_transformed = preprocessor.transform(X_user)
    X_user_transformed = X_user_transformed.drop(columns=lst_to_drop)

    return X_user_transformed

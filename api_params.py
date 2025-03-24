import pandas as pd

#Liste de caractères à détecter parmis toutes les columns du df globales
keywords_flex = [
    'Période',
    'Periode',
    'Type_bâtiment',
    'Type_énergie_principale',
    'perdition',
    'isolation',
    'Ubat',
    'Besoin'
]

#Liste de noms de colonnes strictes à détecter parmis toutes les columns du df globales
keywords_strict = [
    'Etiquette_DPE',
    'N°DPE',
    'Conso_5_usages_é_finale',
    'Conso_5_usages/m²_é_finale',
    'Emission_GES_5_usages',
    'Emission_GES_5_usages_par_m²',
    'Surface_habitable_logement'
]

deperditions_columns = [
    "Déperditions_menuiseries",
    "Déperditions_murs",
    "Deperditions_planchers_bas",
    "Deperditions_planchers_hauts"
    ]
deperditions_columns_m2 = [
    "Déperditions_menuiseries_m2",
    "Déperditions_murs_m2",
    "Deperditions_planchers_bas_m2",
    "Deperditions_planchers_hauts_m2"
    ]


seuils_performance = {
    "Qualité_isolation_menuiseries": {"insuffisante": 3, "moyenne": 2.2, "bonne": 1.6, "très bonne": 0.8},
    "Qualité_isolation_plancher_bas": {"insuffisante": 0.65, "moyenne": 0.45, "bonne": 0.25, "très bonne": 0.125},
    "Qualité_isolation_murs": {"insuffisante": 0.65, "moyenne": 0.45, "bonne": 0.3, "très bonne": 0.15},
    "Qualité_isolation_plancher_haut_comble_perdu": {"insuffisante": 0.3, "moyenne": 0.2, "bonne": 0.15, "très bonne": 0.075},
    "Qualité_isolation_plancher_haut_toit_terrase": {"insuffisante": 0.35, "moyenne": 0.3, "bonne": 0.25, "très bonne": 0.125},
    "Qualité_isolation_plancher_haut_comble_aménagé": {"insuffisante": 0.3, "moyenne": 0.25, "bonne": 0.18, "très bonne": 0.09}
}

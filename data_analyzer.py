import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

df = pd.read_parquet("data/clean_dataset.parquet", engine='pyarrow')

pivot_table = pd.crosstab(df['day'], df['month'], 
                         values=df['collision_severity'], 
                         aggfunc=lambda x: (x == 1).sum() / len(x) * 100)

jours_map = {
    0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 
    3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'
}
mois_map = {
    1: 'Janv', 2: 'Févr', 3: 'Mars', 4: 'Avr', 5: 'Mai', 6: 'Juin',
    7: 'Juil', 8: 'Août', 9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Déc'
}

jours_ordre = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
mois_ordre = ['Janv', 'Févr', 'Mars', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']

pivot_table = pivot_table.rename(index=jours_map, columns=mois_map)

jours_presents = [j for j in jours_ordre if j in pivot_table.index]
mois_presents = [m for m in mois_ordre if m in pivot_table.columns]
pivot_table = pivot_table.reindex(index=jours_presents, columns=mois_presents)

plt.figure(figsize=(12, 7), dpi=700) 
ax = sns.heatmap(pivot_table, 
                 annot=True,
                 fmt='.1f',
                 cmap='viridis',
                 linewidths=.5,
                 )
plt.title('Pourcentages d\'accidents graves par jour et mois:', 
          fontsize=12, 
          pad=15)
plt.xlabel('Mois', fontsize=12, labelpad=15)
plt.ylabel('Jour de la semaine', fontsize=12, labelpad=15)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.subplots_adjust(left=0.15, bottom=0.2, right=1.0, top=0.88)
plt.savefig('pictures/seasonality.png', bbox_inches='tight')
plt.close()

df_filtered = df[(df['age_of_driver'] >= 18) & (df['age_of_driver'] <= 85)]
severity_by_age = df_filtered.groupby('age_of_driver')['collision_severity'].agg(
    total='count',
    severe=lambda x: (x == 1).sum()
)
severity_by_age['percentage'] = (severity_by_age['severe'] / severity_by_age['total']) * 100
severity_by_age['moving_avg'] = severity_by_age['percentage'].rolling(window=5, center=True).mean()
sns.set_theme(style="whitegrid", palette="muted")
plt.figure(figsize=(14, 7), dpi=500)
sns.lineplot(
    data=severity_by_age,
    x=severity_by_age.index, 
    y='percentage', 
    color='steelblue', 
    alpha=0.5,
    linewidth=1.5,
    label='Pourcentage Original'
)

sns.lineplot(
    data=severity_by_age,
    x=severity_by_age.index, 
    y='moving_avg', 
    color='red', 
    linewidth=2.5,
    label='Moyenne Mobile (5 points)'
)
plt.title("Pourcentage d'accidents graves par Âge du Conducteur", fontsize=16, pad=20)
plt.xlabel("Âge du Conducteur", fontsize=12)
plt.ylabel("Pourcentage de Collisions Sévères (%)", fontsize=12)
plt.legend(loc='upper left', frameon=True, fontsize=11)
plt.tight_layout()
plt.savefig('pictures/driver_age.png', bbox_inches='tight')
plt.close()

severity_by_age = df.groupby('age_of_vehicle')['collision_severity'].agg(
    total='count',
    severe=lambda x: (x == 1).sum()
).sort_index()
severity_by_age_filtered = severity_by_age[severity_by_age['total'] > 10].copy()
severity_by_age_filtered['percentage'] = (severity_by_age_filtered['severe'] / severity_by_age_filtered['total']) * 100
severity_by_age_plot = severity_by_age_filtered.reset_index()
sns.set_theme(style="whitegrid")
plt.figure(figsize=(16, 8), dpi=300)
palette = "Spectral_r" 
scatter_plot = sns.scatterplot(
    data=severity_by_age_plot,
    x='age_of_vehicle',
    y='percentage',
    hue='percentage',      
    size='total',          
    sizes=(50, 1000),      
    palette=palette,       
    alpha=0.8,             
    legend='auto'
)
plt.title("Gravité des accidents par âge du véhicule", fontsize=18, pad=20)
plt.xlabel("Âge du véhicule (années)", fontsize=14)
plt.ylabel("Pourcentage de collisions sévères (%)", fontsize=14)
h, l = scatter_plot.get_legend_handles_labels()
plt.legend(h[0:7], l[0:7], bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., title='Pourcentage (%)')
size_legend = plt.legend(
    h[7:], l[7:], 
    bbox_to_anchor=(1.02, 0.5), 
    loc='center left', 
    borderaxespad=0, 
    labelspacing=2.5,
    borderpad=1.5,
)
plt.savefig('pictures/vehicle_age.png', bbox_inches='tight')
plt.close()

first_tree_map_data = df.groupby(["weather_conditions","light_conditions"]).agg({
    "collision_severity": ["mean", "count"]
}).reset_index()
first_tree_map_data.columns = ['Météo', 'Visibilité', 'pct', 'nombre']

weather_map = {
    1: "Beau temps",
    2: "Pluie",
    3: "Neige",
    4: "Beau temps + vents",
    5: "Pluie + vents",
    6: "Neige + vents",
    7: "Brouillard"
}

light_map = {
    1: "Jour",
    4: "Obscurité - feux",
    5: "Obscurité - sans feux",
    6: "Obscurité - sans écl."
}

first_tree_map_data["Météo"] = first_tree_map_data["Météo"].map(weather_map)
first_tree_map_data["Visibilité"] = first_tree_map_data["Visibilité"].map(light_map)
first_tree_map_data.pct = first_tree_map_data.pct.round(3)*100

fig = px.treemap(first_tree_map_data, path=[px.Constant("Conditions météorologiques:"), 'Météo', 'Visibilité'], values='nombre',
                  color='pct',
                  color_continuous_scale='RdBu_r',
                  color_continuous_midpoint=np.average(first_tree_map_data['pct'], weights=first_tree_map_data['nombre']))
fig.update_layout(
    margin=dict(t=10, l=10, r=10, b=10)
)
fig.write_image("pictures/meteo.png", format="png", width=800, height=450, scale=4)

first_tree_map_data = df.groupby(["speed_limit","road_type"]).agg({
    "collision_severity": ["mean", "count"]
}).reset_index()
first_tree_map_data.columns = ['Limite de vitesse', 'Type de route', 'pct', 'nombre']

road_type_map = {
    1: "Rond-point",
    2: "Rue à sens unique",
    3: "Route à chaussées séparées",
    6: "Route à chaussée unique",
    7: "Bretelle",
    9: "Inconnu",
    12: "Sens unique / Bretelle"
}

speed_limit_map = {
    20: "Limite : 20 mph",
    30: "Limite : 30 mph",
    40: "Limite : 40 mph",
    50: "Limite : 50 mph",
    60: "Limite : 60 mph",
    70: "Limite : 70 mph"
}

first_tree_map_data["Type de route"] = first_tree_map_data["Type de route"].map(road_type_map)
first_tree_map_data["Limite de vitesse"] = first_tree_map_data["Limite de vitesse"].map(speed_limit_map)
first_tree_map_data.pct = first_tree_map_data.pct.round(3)*100

import plotly.express as px
import numpy as np
fig = px.treemap(first_tree_map_data, path=[px.Constant("Conditions routieres:"), 'Limite de vitesse', 'Type de route'], values='nombre',
                  color='pct',
                  color_continuous_scale='RdBu_r',
                  color_continuous_midpoint=np.average(first_tree_map_data['pct'], weights=first_tree_map_data['nombre']))
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.update_layout(
    margin=dict(t=10, l=10, r=10, b=10)
)
fig.write_image("pictures/route.png", format="png", width=800, height=450, scale=4)
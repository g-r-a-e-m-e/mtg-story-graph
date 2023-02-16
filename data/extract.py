# import necessary packages
import pandas as pd
import numpy as np

# read in data to pandas DataFrame
path = 'data/oracle-cards-20230216100310.json'
df = pd.read_json(path)

# define columns to keep
keep_columns = ['name', 'mana_cost', 'cmc', 'type_line',
                'oracle_text', 'colors', 'color_identity', 
                'keywords', 'set_name',
                'power', 'toughness', 'produced_mana', 'loyalty',
                'life_modifier', 'hand_modifier',
                'rarity', 'flavor_text','content_warning']

# reassign DataFrame based on columns to keep
df = df[keep_columns]

# replace unescaped bullshit
df.replace(r"\n", " | ", inplace=True, regex=True)

# write nodes
df.to_csv("default_cards_nodes.csv", index=True, index_label="id")

# function to make edges
def make_edges(dataframe):
    df = dataframe
    raw_edge_list = []
#    for i in df.index:
#        edges = [i]
#        name = df.loc[i, "name"]
#        referenced = df[df["oracle_text"].str.contains(name, na = False, regex = False)]
#        
#        for j in referenced.index:
#            if i != j:
#                edges.append(j)
#
    for i, row in df.iterrows():
        edges = [i]
        name = row["name"]
        referenced = df[df["oracle_text"].str.contains(name, na = False, regex = False)]

        for j, row in referenced.iterrows():
            if i != j:
                edges.append(j)

        raw_edge_list.append(edges)
    
    edge_list = []
    for i in raw_edge_list:
        if len(i) > 1:
            edge_list.append(i)
    return edge_list

# make edges
edges = make_edges(df) 

# write out to .csv
with open("default_cards_edges.csv", "w") as f:
    for e in edges:
        f.write(f"{','.join([str(n) for n in e])}""\n")
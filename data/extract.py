# import necessary packages
import pandas as pd
import numpy as np
from collections import Counter

########## BEGIN DATA INPUT ##########
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

# dedupe based on card name and reset index
df = df.drop_duplicates(subset = ['name']).reset_index(drop = True)

########## END DATA INPUT ##########

########## BEGIN FEATURE CREATION ##########

### Feature 1: Mana Costs
# create mana_dict feature from mana cost
df['mana_dict'] = df['mana_cost'].str.findall("\{([A-Z0-9/]+)\}").apply(lambda x: Counter(x) if isinstance(x, list) else Counter())

# create mana_fields list
mana_fields = list(df["mana_cost"].str.findall("\{([A-Z0-9/]+)\}").apply(lambda x: Counter(x) if isinstance(x, list) else Counter()).explode().unique())

# define function to convert individual elements to int type
def try_int(ele):
    try:
        return int(ele)
    except:
        return ele

# sort mana_fields list and reconvert elements to strings
mana_fields = sorted([try_int(i) for i in mana_fields], key = lambda x: (isinstance(x, str), x))
mana_fields = [str(x) for x in mana_fields]
rem_list = ['nan', 'Y', 'Z']
mana_fields = [f for f in mana_fields if f not in rem_list]
mana_fields.append('GENERIC')

# create mana_df to generate mana features
mana_df = pd.DataFrame(data = 0, columns = mana_fields, index = df.index)

# loop over initial dataframe's mana_dict field and assign values from those dict values to mana_df
for i in df.index:
    if df.loc[i, 'mana_dict'] != np.nan:
        j = list(df.loc[i, 'mana_dict'].items())
        for n in j:
            try:
                mana_cost = int(n[0]) * n[1]
                if (df.loc[i, 'cmc'] != 0.0) and (df.loc[i, 'cmc'] != np.nan):
                    weighted_mana_cost = mana_cost / df.loc[i, 'cmc']
                    mana_df.loc[i, 'GENERIC'] = weighted_mana_cost
                else:
                    mana_df.loc[i, 'GENERIC'] = 0.0
            except:
                if (df.loc[i, 'cmc'] != 0.0) and (df.loc[i, 'cmc'] != np.nan):
                    mana_cost = n[1]
                    weighted_mana_cost = mana_cost / df.loc[i, 'cmc']
                    mana_df.loc[i, n[0]] = weighted_mana_cost
                else:
                    mana_df.loc[i, n[0]] = 0.0
    else:
        mana_df.loc[i, mana_fields] = 0

# create second remove_list to remove integer mana costs
rem_list_2 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "1000000", "2/B", "2/G", "2/R", "2/U", "2/W", "Y", "Z"]

# drop irrelevant columns
mana_df.drop(labels = rem_list_2, axis = 1, inplace = True)




########## BEGIN TESTING ##########
# create cleaned_mana_fields list for testing
cleaned_mana_fields = [f for f in mana_fields if f not in rem_list_2]
mismatched_cmc = []
for i in df.index:
    if df.loc[i, 'cmc'].astype('int') != int(sum(df.loc[i, cleaned_mana_fields]) - df.loc[i, 'X']):
        mismatched_cmc.append({i: [df.loc[i, 'name'],
                                    df.loc[i, 'cmc'].astype('int'), 
                                    sum(df.loc[i, cleaned_mana_fields])]})

print(len(mismatched_cmc))
print(f"Mismatched CMC Ratio: {len(mismatched_cmc) / len(df) * 100}")

for i in mismatched_cmc:
    print(i)

for i in df:
    print(f"{i}: {df.loc[583, i]}")
########## END TESTING ##########




### Feature 2: Card Types
type_list = list(df['type_line'].unique())
perm_types = ['Land', 'Creature', 'Artifact', 'Enchantment', 'Planeswalker']
non_perm_types = ['Instant', 'Sorcery']
supertypes = ['Basic', 'Legendary', 'Snow', 'World']


dual_card_types = []
for t in type_list:
    if "//" in t:
        dual_card_types.append(t)
    else:
        continue

subtypes = []
for t in type_list:
    if t not in dual_card_types:
        card_string = t.split(sep = " — ")
        subtypes.append(card_string[0])

subtypes = list(np.unique(subtypes))
subtypes

########## END FEATURE CREATION ##########

########## BEGIN JOINING FEATURES ##########
### Join Features ###
# merge initial dataframe with mana_df
df = df.merge(mana_df, left_index = True, right_index = True)

########## END JOINING FEATURES ##########



########## BEGIN GRAPH CONVERSION ##########
# write nodes
df.to_csv("default_cards_nodes.csv", index=True, index_label="id")

# function to make edges
def make_edges(dataframe):
    df = dataframe
    raw_edge_list = []
    
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

########## END GRAPH CONVERSION ##########

########## BEGIN DATA OUTPUT ##########
# write out to .csv
with open("default_cards_edges.csv", "w") as f:
    for e in edges:
        f.write(f"{','.join([str(n) for n in e])}""\n")

########## END DATA OUTPUT ##########
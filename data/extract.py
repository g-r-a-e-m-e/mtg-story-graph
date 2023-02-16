# import necessary packages
import pandas as pd
import numpy as np

# create test data
test_data = {"Elesh Norn": ["Karn", "Ajani", "Nissa", "Jace"],
             "Karn": ["Urza", "Mishra", "Teferi"],
             "Ajani": ["Elspeth, Teferi"],
             "Nissa": ["Elspeth", "Vraska", "Jace"],
             "Jace" : ["Vraska", "Nahiri"]}

# create test dataframe
df = pd.DataFrame(test_data, columns = ["node", "edge"])

# display first few records
df.head()
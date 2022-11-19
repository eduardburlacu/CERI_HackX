import pickle
import pandas as pd
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
from tensorflow import keras
import matplotlib.pyplot as plt

with open('model','rb') as f:
    model = pickle.load(f)
list_of_df= []
for (root, dirs, files) in os.walk(os.path.join(os.getcwd(), "county_data")):
    for file in files:
        if file[-4:] == ".csv": 
            df = pd.read_csv(os.path.join(root, file))
            df = df.dropna()
            if len(df):
                name = df["areaName"][5]
                df = df.drop(df.columns[:3], axis=1)[::-1].reset_index(drop=True)
                df['y'] = df["newCasesBySpecimenDate"]/df["newVirusTestsBySpecimenDate"]
                for i in range(len(df)):
                    if df["newVirusTestsBySpecimenDate"][i]==0:
                        df.loc[i,'y']=0
                df.columns=['Date','Cases','Deaths','Tests','y']
                #df=df.set_index('Date')
                list_of_df.append([name,df])
list_slopes=[]
list_means=[]
for name,data in list_of_df:
    slope, bias = np.polyfit(np.arange(0,data.shape[0]), data.y,1)
    list_slopes.append(slope)
    list_means.append(data.y.mean())

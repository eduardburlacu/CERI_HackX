import pickle
import pandas as pd
import os
import numpy as np

model_filename = os.path.join(os.getcwd(), "Covid_Cases_Predictor-main", "model")
data_dirname = os.path.join(os.getcwd(), "csvs")

def upload_model():
    with open(model_filename,'rb') as f:
        model = pickle.load(f)
    return model

def get_all_data():
    list_of_df= []
    for (root, dirs, files) in os.walk(data_dirname):
        for file in files:
            if file[-4:] == ".csv" and os.path.getsize(os.path.join(root, file)) > 100: 
                df = pd.read_csv(os.path.join(root, file))
                df = df.dropna()
                if len(df):
                    name = df["areaName"][5]
                    df = df.drop(df.columns[:3], axis=1)[::-1].reset_index(drop=True)
                    df['y'] = df["newCasesBySpecimenDate"]/df["newVirusTestsBySpecimenDate"]
                    for i in range(len(df)):
                        if df["newVirusTestsBySpecimenDate"][i]==0:
                            df.loc[i, 'y']=0
                    df.columns=['Date','Cases','Deaths','Tests','True_Positive']
                    #df=df.set_index('Date')
                    list_of_df.append((name,df))
    return list_of_df

def get_current_trends():
    list_of_df = get_all_data()
    trends_dict = {}
    for name,data in list_of_df:
        trends_dict[name] = {}
        for feature in data.columns[1:]:
            slope, bias = np.polyfit(np.arange(0,14), data[feature][-14:],1)
            trends_dict[name][feature] = (round(slope, 4), round(data[feature].mean(), 2))
    return trends_dict

def get_y_data(n, list_of_df):
    past_values = 50
    values=list(list_of_df[n][1]["True_Positive"])
    X = []
    y = []
    for i in range(len(values)-past_values):
        X.append(values[i:i+past_values])
        y.append(values[i+past_values])
    X = np.array(X)
    y = np.array(y)
    return X, y

def get_predicted():
    list_of_df = get_all_data()
    model = upload_model()
    prediction_dict = {}
    for i in range(len(list_of_df)):
        past_values = 50
        X, y = get_y_data(i, list_of_df)
        y_future = model.predict(X[-1:]*1000)/1000
        y_future = y_future[0]
        for j, val in enumerate(y_future):
            if val < 0: y_future[j] = 0
        prediction_dict[list_of_df[i][0]] = y_future
    return prediction_dict

def test_get_y_data():
    list_of_df = get_all_data()
    for n in range(len(list_of_df)):
        X,y = get_y_data(n, list_of_df)
        for element in y:
            assert (element>=0.) and (element<=1.)

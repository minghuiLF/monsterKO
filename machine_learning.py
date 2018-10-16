
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
import seaborn as sns
import sklearn.model_selection
from sklearn import svm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score


# In[2]:

def data_cleaning(data_train,data_test):
    want_list = ['Id','Neighborhood','YearBuilt','BldgType','BedroomAbvGr','BsmtFullBath','KitchenAbvGr','GarageCars']

    want_train_X = data_train[want_list]
    want_test = data_test[want_list] #test data in this dataset has no Y values(house price), not gonna use in training

    want_train_y = data_train[['SalePrice']]

    #find out the unique values for catergory data and transformed them into numeric

    Neighborhood_set = set(want_train_X['Neighborhood'])
    Neighborhood_set.union(set(want_test['Neighborhood']))
    Neighborhood = list(Neighborhood_set)

    #transfrom categroy data into numeric data
    BldgType = ['1Fam', '2FmCon', 'Duplx', 'TwnhsE','TwnhsI']
    #deal with spelling mistakes
    want_train_X.replace(to_replace= ['Duplex','Twnhs','2fmCon',], value = ['Duplx','TwnhsE','2FmCon'] ,inplace = True)

    for i in range(len(BldgType)):
        want_train_X.replace(to_replace=BldgType[i], value=i,inplace = True)
    for i in range(len(Neighborhood)):
        want_train_X.replace(to_replace=Neighborhood[i], value=i,inplace = True)

    #transform data type into float
    want_train_X.astype(float, inplace = True)
    want_train_y.astype(float, inplace = True)

    return want_train_X, want_train_y


# In[3]:

def model_predict(model, query):
    predict_houseprice = float(model.predict([query])[0])
    return predict_houseprice


# In[5]:

# # ---------------------->>>> COLLECT DATA FROM MLAB <<<<<<-----------------------
# # connect mLab
uri = 'mongodb://proj3:comp9321monsterko@ds125293.mlab.com:25293/data_service_monster_ko'
client = MongoClient(uri)
monster_db = client.get_database()
coll_train = monster_db['original_train']
coll_test = monster_db['original_test']

# get train data and test data and transfer to datafram
for i in coll_train.find():
    data_train = pd.DataFrame.from_dict(i)
for i in coll_test.find():
    data_test = pd.DataFrame.from_dict(i)
# # -------------------------------->>>> <<<<<<-----------------------------------

want_train_X,want_train_y = data_cleaning(data_train,data_test)
#format for single query [Id, Neighborhood,BldgType,YearBuilt,BsmtFullBath,BedroomAbvGr,KitchenAbvGr,GarageCars]
query = want_train_X.iloc[0]
model = RandomForestRegressor(n_estimators=100, max_features='sqrt')
model.fit(want_train_X,want_train_y)
a=model_predict(model, query)
print(a)

# In[ ]:

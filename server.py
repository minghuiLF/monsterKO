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


from flask import Flask, request, abort
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from bson.objectid import ObjectId
from functools import wraps
from requests.auth import HTTPBasicAuth


import json
#############Data Clearning Part########################
def data_cleaning(data_train,data_test):
	want_list = ['Neighborhood','YearBuilt','BldgType','BedroomAbvGr','BsmtFullBath','KitchenAbvGr','GarageCars']

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

	dict_hst = {}
	dict_nbd = {}

	for i in range(len(BldgType)):
		want_train_X.replace(to_replace=BldgType[i], value=i,inplace = True)
		dict_hst[BldgType[i]] = i
	for i in range(len(Neighborhood)):
		want_train_X.replace(to_replace=Neighborhood[i], value=i,inplace = True)
		dict_nbd[Neighborhood[i]]=i


	#transform data type into float
	want_train_X.astype(float, inplace = True)
	want_train_y.astype(float, inplace = True)

	return want_train_X, want_train_y,dict_hst,dict_nbd


#---------------------->>>> COLLECT DATA FROM MLAB <<<<<<-----------------------
uri = 'mongodb://proj3:comp9321monsterko@ds125293.mlab.com:25293/data_service_monster_ko'
client = MongoClient(uri)
monster_db = client.get_database()
coll_train = monster_db['original_train']
coll_test = monster_db['original_test']
for i in coll_train.find():
	data_train = pd.DataFrame.from_dict(i)
for i in coll_test.find():
	data_test = pd.DataFrame.from_dict(i)

data_train  = data_train.drop('_id',axis =1)
#data_train = data_train.to_json(orient='records')
want_train_X,want_train_y,dict_hst,dict_nbd = data_cleaning(data_train,data_test)

########################Build Machine Learning Model##################
model = RandomForestRegressor(n_estimators=100, max_features='sqrt')
model.fit(want_train_X,want_train_y)

def model_predict(model, query):
	predict_houseprice = float(model.predict([query])[0])
	return predict_houseprice

######################Search Part#################################

def FindMatchByInputFeatures(data_train, Suburb, Year_Built, Property_Type, Nb_of_Bedroom, Nb_of_Bathroom, Nb_of_Ktichen, Nb_of_Garage):
	# If there exists a match that fulfill exactly by the user's input, display that property
	q_1= f'Neighborhood=="{Suburb}" and YearBuilt=="{Year_Built}" and HouseStyle=="{Property_Type}" and BedroomAbvGr=="{Nb_of_Bedroom}" and BsmtFullBath=="{Nb_of_Bathroom}" and KitchenAbvGr=="{Nb_of_Ktichen}" and GarageCars=="{Nb_of_Garage}"'
	#print(q_1)
	search = data_train.query(q_1)
	if search.empty: # if dataframe is empty
		return None
	else:
		result_1 =search.sort_values(by = ['SalePrice'], ascending=True)
		out_1 = result_1.head(1)
		return out_1

def RecommendedData(data_train, predict_price, pricestep):
	# get all data in the original dataset by a range of prediction

	low_bound = predict_price - int(pricestep)
	high_bound = predict_price + int(pricestep)
	q_2 = f'SalePrice >= {low_bound} and SalePrice <= {high_bound}'
	recommended = data_train.query(q_2)

	if recommended.empty: # if dataframe is empty
		return None

	return recommended

def Bottom10ByPredictionRange(recommended):
	# get 10 recommended results by predict price range

	result_2 =recommended.sort_values(by = 'SalePrice', ascending=True)
	# bottom 10 properties
	rows = recommended["SalePrice"].count()
	if 10 > rows:
		out_2 = result_2.tail(rows)
	else:
		out_2 = result_2.tail(10)

	# get the median, maximum, minimum price property
	median = int(np.median([1,rows]))
	MedianProperty = result_2.iloc[median]
	MedianProperty = MedianProperty.to_frame().T
	MaximumProperty = result_2.iloc[-1]
	MaximumProperty = MaximumProperty.to_frame().T
	MinimumProperty = result_2.head(1)

	return out_2, MedianProperty, MaximumProperty, MinimumProperty

def TopXFeature(x, recommended, feature):
	result = recommended.sort_values(by = [feature], ascending=True)
	topx = result.head(x)
	return topx

def BottomXFeature(x, recommended, feature):
	result = recommended.sort_values(by = [feature], ascending=True)
	bottomx = result.tail(x)
	return bottomx



recommended = None

app = Flask(__name__)
api = Api(app,default = "comp9321",title ="assignment_3")

##### get prediction price

# Authentication part
def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth:
			abort(401)
		if not (auth.username == 'admin' and 'admin' == auth.password):
			abort(401)
		return f(*args, **kwargs)
	return decorated

@api.route('/ass3/authen')
class authen(Resource):
	@requires_auth
	def get(self):
		return

parser = reqparse.RequestParser()
#parser.add_argument('Id')
parser.add_argument('Suburb')
parser.add_argument('Nb_of_Bedroom')
parser.add_argument('Year_Built')
parser.add_argument('Nb_of_Bathroom')
parser.add_argument('Nb_of_Kitchen')
parser.add_argument('Nb_of_Garage')
parser.add_argument('Property_Type')
parser.add_argument('pricestep')

@api.route('/ass3')
#@api.param('Id', 'The property ID')
@api.param('Suburb', 'The physic locations of Suburb')
@api.param('Nb_of_Bedroom', 'The number of Bedrooms')
@api.param('Year_Built', 'The original construction date')
@api.param('Nb_of_Bathroom', 'The number of Bathrooms')
@api.param('Nb_of_Kitchen', 'The number of Kitchen')
@api.param('Nb_of_Garage', 'Car park capacity')
@api.param('Property_Type', 'The type of dwelling')
@api.param('pricestep', 'The step around the prediction price customer want')
class ass3(Resource):
	@api.response(200, 'OK')
	@api.response(400, 'parameters error')
	@api.response(404, 'Not found')
	@api.doc(description = "Get a result by its requirements")
	#@requires_auth
	def get(self):#, Suburb, Nb_of_Bedroom, Year_Built, Nb_of_Bathroom, Nb_of_Kitchen, Nb_of_Garage, Property_Type, pricestep):
		x_test = []
		try:
			args = parser.parse_args()
			#ID =args.get('Id')
			Suburb = args.get('Suburb')
			Neighborhood = dict_nbd[Suburb]
			x_test.append(Neighborhood)
			Property_Type = args.get('Property_Type')
			Style = dict_hst[Property_Type]
			x_test.append(Style)
			Year_Built = args.get('Year_Built')
			x_test.append(int(Year_Built))
			Nb_of_Bathroom = args.get('Nb_of_Bathroom')
			x_test.append(int(Nb_of_Bathroom))
			Nb_of_Bedroom = args.get('Nb_of_Bedroom')
			x_test.append(int(Nb_of_Bedroom))
			Nb_of_Kitchen = args.get('Nb_of_Kitchen')
			x_test.append(int(Nb_of_Kitchen))
			Nb_of_Garage = args.get('Nb_of_Garage')
			print("Nb_of_Garage {}".format(Nb_of_Garage))
			x_test.append(int(Nb_of_Garage))
			Pricestep = args.get('pricestep')
			print("price ste: {}".format(Pricestep))
		except:
			#print(x_test)
			return api.abort(400, "requirements invalid")
		#Match = FindMatchByInputFeatures(data_train, Suburb, Year_Built, Style, Nb_of_Bedroom,Nb_of_Bathroom,Nb_of_Kitchen,Nb_of_Garage)
		print(Pricestep)
		print(x_test)
		predict_price = model_predict(model, x_test)

		global recommended
		recommended = RecommendedData(data_train, predict_price, Pricestep)
		"""
		print("recommended: {}".format(recommended))
		print("type:{}".format(type(recommended))) # dataframe

		Bottom10, MedianProperty, MaximumProperty, MinimumProperty = Bottom10ByPredictionRange(recommended)
		#result={"predict": predict_price, "search": Match, "Median Property":MedianProperty, "Maximum Property": MaximumProperty, "Minimum Property": MinimumProperty, "Bottom10":Bottom10}
		print("Bottom10: {}".format(Bottom10))# dataframe
		print("type:{}".format(type(Bottom10)))
		print("MedianProperty: {}".format(MedianProperty)) #Series
		print("type:{}".format(type(MedianProperty)))
		print("MaximumProperty: {}".format(MaximumProperty)) #Series
		print("type:{}".format(type(MaximumProperty)))
		print("MinimumProperty: {}".format(MinimumProperty)) # dataframe
		print("type:{}".format(type(MinimumProperty)))

		print("predict_price: {}".format(predict_price)) # float
		print("type:{}".format(type(predict_price)))

		"""

		if recommended.empty:
			Bottom10, MedianProperty, MaximumProperty, MinimumProperty = None
			#result={"predict": predict_price, "Median Property":MedianProperty, "Maximum Property": MaximumProperty, "Minimum Property": MinimumProperty, "Bottom10":Bottom10}
		else:
			Bottom10, MedianProperty, MaximumProperty, MinimumProperty = Bottom10ByPredictionRange(recommended)


		MedianProperty = MedianProperty.to_json(orient='records')
		MaximumProperty = MaximumProperty.to_json(orient='records')

		MinimumProperty = MinimumProperty.to_json(orient='records')
		Bottom10 = Bottom10.to_json(orient='records')

		result={"predict": predict_price, "Median Property":MedianProperty, "Maximum Property": MaximumProperty, "Minimum Property": MinimumProperty, "Bottom10":Bottom10}

		return result, 200
"""

parser.add_argument('x')
parser.add_argument('price')
parser.add_argument('feature')

parser = reqparse.RequestParser()
"""
@api.route('/ass3/<x>/<feature>')
@api.param('x', 'The user input x (as Top X or Bottom X)')
#@api.param('price', 'The predict_price in the previous action')
@api.param('feature', 'The feature user want to compare with')

class CustomiseComparison(Resource):
	@api.response(200, 'OK')
	@api.response(400, 'parameters error')
	@api.response(404, 'Not found')
	@api.doc(description = "Customise comparison prediction results")

	#@requires_auth
	def get(self, x, feature):
		args = parser.parse_args()
		x = int(x)
		#print("{}".format(x))
		#print("{}".format(feature))
		#print("{}".format(recommended))
		if recommended is None:
			topx, bottomx = None

		elif recommended.empty:
			topx, bottomx = None
		else:

			topx = TopXFeature(x, recommended, feature)
			bottomx = BottomXFeature(x, recommended, feature)


			topx = topx.to_json(orient='records')
			bottomx = bottomx.to_json(orient='records')


		message={"topx":topx,"bottomx":bottomx}

		return message,200


if __name__ == '__main__':
	app.run(debug = True)

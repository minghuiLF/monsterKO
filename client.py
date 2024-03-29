import sys
import requests
import json
from requests.auth import HTTPBasicAuth

import numpy as np
import pandas as pd


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

housestyle = ['1Fam', '2FmCon', 'Duplx', 'TwnhsE','TwnhsI']
Neighborhood = ['BrkSide',
 'StoneBr',
 'NridgHt',
 'Mitchel',
 'NWAmes',
 'OldTown',
 'ClearCr',
 'NoRidge',
 'Sawyer',
 'BrDale',
 'Somerst',
 'SawyerW',
 'Blmngtn',
 'Crawfor',
 'Veenker',
 'Edwards',
 'MeadowV',
 'Timber',
 'SWISU',
 'NPkVill',
 'NAmes',
 'Blueste',
 'Gilbert',
 'CollgCr',
 'IDOTRR']
Price_range =["5000","7000","10000","20000","30000"]

features =["Year Built","Bedroom Number","Bathroom Number","Kitchen Number","Garage Capacity"]


features_dic={
    "Year Built":"YearBuilt",
    "Bedroom Number":"BedroomAbvGr",
    "Bathroom Number":"FullBath",
    "Kitchen Number":"KitchenAbvGr",
    "Garage Capacity":"GarageCars"
}
features_dic2={v:x for x,v in features_dic.items()}

class MoreInfor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(900*2, 550*2)
        self.setWindowTitle("More Information")
        self.Frame()

    def Frame(self):


        fontlabel = QFont()


        lineEditFont = QFont()


        # self.label_descrip.setFont(fontlabel)
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(30)
        grid_layout.setVerticalSpacing(100)




        # buttons --------------------------------
        # button for top
        self.button_get1 = QPushButton('Get Graph')
        self.button_get1.setFixedWidth(210)
        self.button_get1.clicked.connect(self.on_click1)


        self.getGraph_discription = QLabel('These pie charts show the comparison for each feature,the entire pie represent all the properties selected from your input range(e.g. (predicted price - 5000) ~ (predicted price + 5000)).')
        self.getGraph_discription.setFont(QFont("Times",12))
        self.getGraph_discription.setFixedSize(1200,120)
        self.getGraph_discription.adjustSize()
        self.getGraph_discription.setWordWrap(1)

        # graph
        self.ax=[0]*6
        self.figure1 = plt.figure()

        self.canvas1 = FigureCanvas(self.figure1)



        ##     addWidget(QWidget * widget, int fromRow, int fromColumn, int rowSpan, int columnSpan, Qt::Alignment alignment = 0)






        grid_layout.addWidget(self.button_get1,1,1)

        grid_layout.addWidget(self.getGraph_discription,1,6)


        grid_layout.addWidget(self.canvas1,3,1,10,10)






        grid_layout.setAlignment(Qt.AlignTop)


        # grid_layout.setAlignment(self.label_descrip,Qt.AlignCenter)
        # grid_layout.setAlignment(self.button_get1,Qt.AlignLeft)
        # grid_layout.setAlignment(self.button_get2,Qt.AlignLeft)


        #print (grid_layout.columnCount())
        #print (grid_layout.rowCount())
        # create a window object
        layout_widget = QWidget()
        layout_widget2 = QWidget()
        # design the window's layout
        layout_widget.setLayout(grid_layout)

        self.setCentralWidget(layout_widget)
        #self.setCentralWidget(layout_widget2)




        self.show()

    @pyqtSlot()
    def on_click1(self):
        ## get input


        # send requests to API
        url_2 = f"http://127.0.0.1:5000/ass3/feature"
        r2 = requests.get(url_2)
        result = r2.json()
        if result==None:
            return
        #print(result)
        input_data=pd.read_json(result)
        #print(input_data)
        dataDict={}
        n=1
        for feature in features[1:]:
            dataDict[feature]=input_data[features_dic[feature]]
            dataDict[feature].name=feature
            self.plot(dataDict[feature], n)
            n=n+1

        feature=features[0]
        dataDict[feature]=input_data[features_dic[feature]]
        dataDict[feature].name=feature
        self.plotyear(dataDict[feature])

        self.figure1.tight_layout()
        self.canvas1.draw()






        # data=input_data[0]
        # data.name=feature
        # ## if data not enrough
        # datalen=len(input_data)
        # N=min(N,datalen)
        #
        # ## data handle
        # featurecolumn=input_data
        # print(featurecolumn.tail(N))
        # sorted=featurecolumn.sort_values()
        #
        # print(sorted.tail(N))
        #
        # data=sorted.tail(N)
        # self.plot(data,N,0)

    def plotyear(self,data):
        data=data.value_counts()
        data=data.sort_index()
        ind=data.index
        value=data.values
        #print(data)
        ax = self.figure1.add_subplot(2,3,(5,6))
        ax.bar(ind,value)
        ax.set_title(data.name,fontsize="20",loc="left")
        #
        # ax.set_xticks(ind)
        ax.set_ylabel("Hourse number")
        ax.set_xlabel("Year")
        #
        # ax.set_xticklabels(data_df.index)


    def plot(self,data,n):

        # width=0.35
        # ind=[i+1 for i in range(N)]


        T=data.value_counts()
        labels=T.index
        sizes=T.values
        FontSize="14"
        R=0.5;
        # create an axis
        self.ax[n] = self.figure1.add_subplot(2,3,n)

        # discards the old graph



        def func(pct, allvals):

            absolute = int(pct/100.*np.sum(allvals))
            if pct < 1:
                return ""
            return "{:.1f}% ({:d})".format(pct, absolute)



        wedges, texts, autotexts = self.ax[n].pie(sizes,
                                                radius=R,
                                                autopct=lambda pct: func(pct, data),
                                                pctdistance=0.8,
                                                startangle =180,
                                                textprops=dict(color="black",fontsize=FontSize),
                                                wedgeprops=dict(width=0.9*R, edgecolor='w')
                                                )




        self.ax[n].legend(wedges, labels,
                  title=data.name,
                  fontsize="large",

                  )

        self.ax[n].set_title(data.name,fontsize="20",loc="left")

        self.ax[n].axis('equal')





class Userform(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(900*2, 600*2)
        self.setWindowTitle("Prediction of Property Price System Input Search Features")
        self.FormDesign()

    def FormDesign(self):   # grid style
        self.label_descrip = QLabel('Please Input Your Search Features')
        fontlabel = QFont("Times",11)

        self.label_descrip.setFont(fontlabel)



        self.label_1 = QLabel(' Suburb')
        self.label_1.setFont(fontlabel)
        self.label_2 = QLabel(' Property type')
        self.label_2.setFont(fontlabel)
        self.label_3 = QLabel(' Year Built')
        self.label_3.setFont(fontlabel)
        self.label_4 = QLabel(' Bedroom Number')
        self.label_4.setFont(fontlabel)
        self.label_5 = QLabel(' Bathroom Number')
        self.label_5.setFont(fontlabel)
        self.label_6 = QLabel(' Kitchen Number')
        self.label_6.setFont(fontlabel)
        self.label_7 = QLabel(' Garage capacity')
        self.label_7.setFont(fontlabel)
        self.label_8 = QLabel(' Price Range')
        self.label_8.setFont(fontlabel)

        # search button
        self.button_search = QPushButton('Search')
        self.button_search.setFixedWidth(210)

        # more information button
        self.button_more = QPushButton('More Information')
        self.button_more.setFixedWidth(210)

        # 8 input fileds
        lineEditFont = QFont()
        lineEditFont.setPixelSize(10)

        self.comboBox1 = QComboBox()
        self.comboBox1.addItem('Please Choose A Suburb')
        self.comboBox1.addItems(Neighborhood)
        self.comboBox1.setFixedWidth(210)
        self.comboBox2 = QComboBox()
        self.comboBox2.addItem('Please Choose A Property Type')
        self.comboBox2.addItems(housestyle)
        self.comboBox2.setFixedWidth(210)

        self.lineEdit3 = QLineEdit()
        self.lineEdit3.setFixedHeight(30)
        self.lineEdit3.setFixedWidth(180)
        self.lineEdit4 = QLineEdit()
        self.lineEdit4.setFixedHeight(30)
        self.lineEdit4.setFixedWidth(180)
        self.lineEdit5 = QLineEdit()
        self.lineEdit5.setFixedHeight(30)
        self.lineEdit5.setFixedWidth(180)
        self.lineEdit6 = QLineEdit()
        self.lineEdit6.setFixedHeight(30)
        self.lineEdit6.setFixedWidth(180)
        self.lineEdit7 = QLineEdit()
        self.lineEdit7.setFixedHeight(30)
        self.lineEdit7.setFixedWidth(180)

        self.comboBox3 = QComboBox()
        self.comboBox3.addItem('Please Choose A Price Range')
        self.comboBox3.addItems(Price_range)
        self.comboBox3.setFixedWidth(180)

        #search output
        self.label_9 = QLabel('Predict Price: $')
        self.label_9.setFont(fontlabel)
        self.lineEdit8 = QLineEdit()
        self.lineEdit8.setFixedHeight(30)
        self.lineEdit8.setFixedWidth(180*2)

        self.label_11 = QLabel('Bottom 10 Properties: \n[This is the bottom 10 properties from \nthe range(e.g. (predicted price - 5000) \n~ (predicted price + 5000)) you select]')
        self.label_11.setFont(fontlabel)
        self.Records = QTableWidget(10,81)
        #self.Records.setColumnCount(5)
        #self.Records.setRowCount(2)
        self.Records.setFixedHeight(170*2)
        self.Records.setFixedWidth(600*2)




        self.label_12 = QLabel('Maximum Property: \n[This is the maximum price property from \nthe range(e.g. (predicted price - 5000) \n~ (predicted price + 5000)) you select]')
        self.label_12.setFont(fontlabel)
        self.MaxRecords = QTableWidget(1,81)
        self.MaxRecords.setFixedHeight(65*2)
        self.MaxRecords.setFixedWidth(600*2)


        self.label_13 = QLabel('Median Property: \n[This is the median price property from \nthe range(e.g. (predicted price - 5000) \n~ (predicted price + 5000)) you select]')
        self.label_13.setFont(fontlabel)
        self.MedRecords = QTableWidget(1,81)
        self.MedRecords.setFixedHeight(65*2)
        self.MedRecords.setFixedWidth(600*2)

        self.label_14 = QLabel('Minimum Property: \n[This is the minimum price property from \nthe range(e.g. (predicted price - 5000) \n~ (predicted price + 5000)) you select]')
        self.label_14.setFont(fontlabel)
        self.MinRecords = QTableWidget(1,81)
        self.MinRecords.setFixedHeight(65*2)
        self.MinRecords.setFixedWidth(600*2)



        #Form layout
        grid_layout = QGridLayout()

        grid_layout.addWidget(self.label_descrip,0,1,1,3)

        grid_layout.addWidget(self.label_1,3,0)
        grid_layout.addWidget(self.comboBox1,3,1)
        grid_layout.addWidget(self.label_2,4,0)
        grid_layout.addWidget(self.comboBox2,4,1)
        grid_layout.addWidget(self.label_3,5,0)
        grid_layout.addWidget(self.lineEdit3,5,1)
        grid_layout.addWidget(self.label_4,6,0)
        grid_layout.addWidget(self.lineEdit4,6,1)

        grid_layout.addWidget(self.label_5,3,3)
        grid_layout.addWidget(self.lineEdit5,3,4)
        grid_layout.addWidget(self.label_6,4,3)
        grid_layout.addWidget(self.lineEdit6,4,4)
        grid_layout.addWidget(self.label_7,5,3)
        grid_layout.addWidget(self.lineEdit7,5,4)
        grid_layout.addWidget(self.label_8,6,3)
        grid_layout.addWidget(self.comboBox3,6,4)

        grid_layout.addWidget(self.button_search,7,1,1,3)
        grid_layout.addWidget(self.button_more,8,1,1,3)

        grid_layout.addWidget(self.label_9,9,0)
        grid_layout.addWidget(self.lineEdit8,9,1)

        grid_layout.addWidget(self.label_11,10,0)
        grid_layout.addWidget(self.Records,10,1,1,4)

        grid_layout.addWidget(self.label_12,11,0)
        grid_layout.addWidget(self.MaxRecords,11,1,1,4)

        grid_layout.addWidget(self.label_13,12,0)
        grid_layout.addWidget(self.MedRecords,12,1,1,4)

        grid_layout.addWidget(self.label_14,13,0)
        grid_layout.addWidget(self.MinRecords,13,1,1,4)

        grid_layout.setAlignment(Qt.AlignTop)
        grid_layout.setAlignment(self.label_descrip,Qt.AlignCenter)
        grid_layout.setAlignment(self.button_search,Qt.AlignCenter)
        grid_layout.setAlignment(self.button_more,Qt.AlignCenter)



        layout_widget = QWidget()

        layout_widget.setLayout(grid_layout)

        self.setCentralWidget(layout_widget)

        # search button connect to search function
        self.button_search.clicked.connect(self.Search)

        # more button connect to more function
        self.button_more.clicked.connect(self.Change_to_more)


    def Search(self):
        Suburb = self.comboBox1.currentText()
        Style = self.comboBox2.currentText()
        Built_year = self.lineEdit3.text()
        Bedroom_nb = self.lineEdit4.text()
        Bathroom_nb = self.lineEdit5.text()
        Kitchen_nb = self.lineEdit6.text()
        GarageCar_nb = self.lineEdit7.text()
        Price_Range = self.comboBox3.currentText()


        if (Suburb == 'Please Choose A Suburb' or Style =='Please Choose A Property Type' or Built_year =='' or Bedroom_nb =='' or Bathroom_nb =='' or Kitchen_nb =='' or GarageCar_nb =='' or Price_Range=='Please Choose A Price Range'):
            print(QMessageBox.warning(self, "Warning", "Features can not be None!", QMessageBox.Yes, QMessageBox.Yes))
            return
        if not (Built_year.isdigit() and Bedroom_nb.isdigit() and Bathroom_nb.isdigit() and Kitchen_nb.isdigit() and GarageCar_nb.isdigit()):
            print(QMessageBox.warning(self, "Warning", "Some Features must be digits!", QMessageBox.Yes, QMessageBox.Yes))
            return
        if len(Built_year) != 4:
            print(QMessageBox.warning(self, "Warning", "Year Built must be a 4-digit number!", QMessageBox.Yes, QMessageBox.Yes))
            return

        p = f"pricestep={Price_Range}&Property_Type={Style}&Nb_of_Garage={GarageCar_nb}&Nb_of_Kitchen={Kitchen_nb}&Nb_of_Bathroom={Bathroom_nb}&Year_Built={Built_year}&Nb_of_Bedroom={Bedroom_nb}&Suburb={Suburb}"
        #print("pricetep:{}".format(Price_Range))
        #print(p)
        url_1 = "http://127.0.0.1:5000/ass3?" + p




        #print(url_1)
        r = requests.get(url_1)
        #if r.ok:
        result = r.json()

        #print(result)
        '''
        else:
            print(QMessageBox.warning(self, "Warning", "Try again!", QMessageBox.Yes, QMessageBox.Yes))
            return
        '''


        # get search result and insert to layout
        price = result["predict"]
        #price =1234
        self.lineEdit8.setText(str(price))




        recommend_10 = result["Bottom10"]    ### json
        recommend_10 = json.loads(recommend_10)    ###list of 10 dict

        horizontalHeader = list(recommend_10[0].keys())  #recommend_10.columns.values.tolist()
        self.Records.setHorizontalHeaderLabels(horizontalHeader)
        self.MaxRecords.setHorizontalHeaderLabels(horizontalHeader)
        self.MedRecords.setHorizontalHeaderLabels(horizontalHeader)
        self.MinRecords.setHorizontalHeaderLabels(horizontalHeader)

        for row in range(len(recommend_10)):
            one_row = recommend_10[row]
            #print(one_row)
            datas = list(one_row.values())
            #print(datas)
            for column in range(len(datas)):
                data = datas[column]
                self.Records.setItem(row,column,QTableWidgetItem(str(data)))

        max_records = result["Maximum Property"]
        max_records = json.loads(max_records)  #list
        ##### if return is dict
        #max_records = pd.DataFrame.from_dict(max_records)
        max_row = list(max_records[0].values())      #dict
        #print(max_row)

        med_records = result["Median Property"]
        med_records = json.loads(med_records)
        ##### if return is dict
        #med_records = pd.DataFrame.from_dict(med_records)
        med_row = list(med_records[0].values())

        min_records = result["Minimum Property"]
        min_records = json.loads(min_records)
        ##### if return is dict
        #min_records = pd.DataFrame.from_dict(min_records)
        #print(min_records[0])
        min_row = list(min_records[0].values())

        for column in range(81):
            max_data = max_row[column]
            med_data = med_row[column]
            min_data = min_row[column]
            if max_data != None:
                self.MaxRecords.setItem(0,column,QTableWidgetItem(str(max_data)))
            if med_data != None:
                self.MedRecords.setItem(0,column,QTableWidgetItem(str(med_data)))
            if min_data != None:
                self.MinRecords.setItem(0,column,QTableWidgetItem(str(min_data)))
        #'''



    def Change_to_more(self):
        self.more = MoreInfor()
        self.more.show()

# StyleSheet_btn = "QPushButton{height:30px;background-color: transparent;color: grey;border: 2px solid ;border-radius: 6px;}"
# SytleSheet setting
StyleSheet_btn = """
QPushButton{
height:30px;
background-color: transparent;
color: grey;
border: 2px solid #555555;
border-radius: 6px;

}
QPushButton:hover {
background-color: white;
border-radius: 6px;
} """

StyleSheet_2 = """
QComboBox{
height: 20px;
border-radius: 4px;
border: 1px solid rgb(111, 156, 207);
background: white;
}
QComboBox:enabled{
color: black;
}
QComboBox:!enabled {
color: rgb(80, 80, 80);
}
QComboBox:enabled:hover, QComboBox:enabled:focus {
color: rgb(51, 51, 51);
}
QComboBox::drop-down {
background: transparent;
}
QComboBox::drop-down:hover {
background: lightgrey;
}

QComboBox QAbstractItemView {
border: 1px solid rgb(111, 156, 207);
background: white;
outline: none;
}

QLineEdit {
border-radius: 5px;
height: 30px;
border: 1px solid rgb(111, 156, 207);
background: white;
}
QLineEdit:enabled {
color: rgb(84, 84, 84);
}
QLineEdit:enabled:hover, QLineEdit:enabled:focus {
color: rgb(51, 51, 51);
}
QLineEdit:!enabled {
color: rgb(80, 80, 80);
}


"""


class Authentication(QWidget):

    def __init__(self):
        super(Authentication, self).__init__()

        self.setUpUI()

        self.setAutoFillBackground(True)



    def setUpUI(self):

        ################
        # DESIGN PART
        ################
        self._layout = QVBoxLayout(spacing=0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        self.main_layout = QGridLayout()
        # self.formlayout = QFormLayout()

        self.main_layout.setAlignment(Qt.AlignCenter)
        self.name_label = QLabel('        Username')
        self.name_label.setFont(QFont('Times',12))
        self.name_label.setStyleSheet("color:black;")
        self.passwd_label = QLabel('        Password')
        self.passwd_label.setFont(QFont('Times',12))
        self.passwd_label.setStyleSheet("color:black;")

        self.name_box = QLineEdit()



        self.passwd_box = QLineEdit()
        self.passwd_box.setEchoMode(QLineEdit.Password)

        self.name_box.setStyleSheet(StyleSheet_2)
        self.passwd_box.setStyleSheet(StyleSheet_2)
        # tip
        QToolTip.setFont(QFont('SanSerif',10))
        self.name_box.setToolTip('Type username')
        self.passwd_box.setToolTip('Type password')

        self.label = QLabel()
        self.login_btn = QPushButton("Login")
        self.login_btn.setFont(QFont('Times',10))
        self.login_btn.setStyleSheet(StyleSheet_btn)
        self.login_btn.clicked.connect(self.AuthenticationCheck)

        self.main_layout.addWidget(self.name_label,0,0,1,1)
        self.main_layout.addWidget(self.passwd_label,2,0,1,1)
        self.main_layout.addWidget(self.name_box,0,1,1,2)
        self.main_layout.addWidget(self.passwd_box,2,1,1,2)


        self.main_layout.addWidget(self.label,3,1,1,3)
        self.main_layout.addWidget(self.login_btn,4,1,1,3)

        self._layout.addLayout(self.main_layout)



        # close asking set
    def closeEvent(self,event):
        reply = QMessageBox.question(self,'Message', 'Are you sure to quit?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def AuthenticationCheck(self):
        username = self.name_box.text()
        password = self.passwd_box.text()


        #username="admin"
        #password="admin"
        if (username == "" or password == ""):
            print(QMessageBox.warning(self, "Warning", "username and password can not be Empty!", QMessageBox.Yes, QMessageBox.Yes))
            return

        r = requests.get("http://127.0.0.1:5000/ass3/authen", auth=HTTPBasicAuth(username, password))

        #print("12312313")
        if r.ok:
            print(QMessageBox.information(self, "Notification", "Authentication Successfully!", QMessageBox.Yes, QMessageBox.Yes))
            # r = requests.get("http://127.0.0.1:5000/books/206", auth=HTTPBasicAuth(username, password))
            # book = r.json()
            # print_book(book)
            self.hide()
            self.newForm = Userform()
            self.newForm.show()

        else:
            print(QMessageBox.information(self, "Notification", "Invalid username or password! Please try again.", QMessageBox.Yes, QMessageBox.Yes))



if __name__ == "__main__":
    app = QApplication(sys.argv)

    #app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    loginWindow = Authentication()
    loginWindow.setWindowTitle("House Price Prediction System Welcom Login")
    loginWindow.setFixedSize(QSize(380*2, 200*2))
    loginWindow.setWindowOpacity(0.9)
    pl = QPalette()
    pl.setBrush(loginWindow.backgroundRole(),QBrush(QPixmap('unsw.png')))
    loginWindow.setAutoFillBackground(True)
    loginWindow.setPalette(pl)

    loginWindow.show()
    sys.exit(app.exec_())

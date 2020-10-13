from flask import Flask, render_template, request, flash, redirect,session,  url_for, jsonify
import requests
import pandas
import numpy
import matplotlib
matplotlib.use('Agg')
from scipy import stats
import seaborn as sns
import json
import matplotlib.pyplot as plot
from io import BytesIO 
import base64
import urllib.parse
import math
from scipy.stats import norm
import io
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from apiclient.http import MediaIoBaseDownload
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = 'https://www.googleapis.com/auth/drive'
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'
app = Flask(__name__)
app.secret_key = 'dokynterkes'

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('dashboard'))

class Plot:
    
    figureWidth = 20
    figureHeight = 12
    xLabelRotationDegree = 90
    xAxisValuesLimit = 32
    xAxisLabelsRightLimit = -0.5
    xAxisLabelsLeftLimit = 50
    plotImageFormat = 'png'
    plotImageDPI = 200
    
    def createBarPlot(self, xData, yData):
        plot.figure(figsize=(self.figureWidth, self.figureHeight))
        plot.xticks(rotation = self.xLabelRotationDegree)
        plot.tight_layout()
        sns.barplot(x = xData, y = yData)
        if(xData.nunique() > self.xAxisValuesLimit):
            plot.xlim(self.xAxisLabelsRightLimit, self.xAxisLabelsLeftLimit)
        barPlotImage = self.createPlotImage()
        return barPlotImage
    
    def createBoxPlot(self, data):
        plot.figure(figsize=(self.figureWidth, self.figureHeight))
        sns.boxplot(data=data)
        plot.tight_layout()
        boxPlotImage = self.createPlotImage()
        return boxPlotImage
    
    def createBoxPlotOverload(self, xData, yData):
        figureWidth = 12
        figureHeight = 8
        plot.figure(figsize=(figureWidth, figureHeight))
        plot.tight_layout()
        sns.boxplot(x = xData, y = yData)
        boxPlotImage = self.createPlotImage()
        return boxPlotImage
    
    def createPairPlot(self, data):
        figureWidth = 18
        figureHeight = 11
        plot.figure(figsize=(figureWidth, figureHeight))
        plot.tight_layout()
        plot.xticks(rotation = self.xLabelRotationDegree)
        sns.pairplot(data.dropna())
        pairPlotImage = self.createPlotImage()
        return pairPlotImage

    def createPlotImage(self):
        img = BytesIO() 
        plot.savefig(img, format = self.plotImageFormat, dpi = self.plotImageDPI) 
        img.seek(0) 
        plot.clf()
        return base64.b64encode(img.read()).decode()
    
class HypothesisTests:
    
    decision = ''
    testValue = 0.0
    pValue = 0.0
    testInformations = []
    testName = ''
    statisticalSignificance = 0.05
    
    def setDecision(self):
        if(self.pValue < self.statisticalSignificance):
            return 'Należy odrzucić hipotezę H0'
        else:
            return 'Należy przyjąć hipotezę H0'
    
    def setTestInformations(self, firstAttribute, secondAttribute):
        self.testInformations.append({'name': self.testName+' dla: '+firstAttribute+' i '+secondAttribute,
                                'H0' : firstAttribute+' i '+secondAttribute+' nie są ze sobą powiązane',
                                'H1' : firstAttribute+' i '+secondAttribute+' są ze sobą powiązane',
                                'testvalue': self.testValue,
                                'pvalue': self.pValue,
                                'dec': self.decision})
        return None

    def checkIfGeneratePlot(self, firstAttribute, secondAttribute):
        generatePlot = False
        if(dataset[firstAttribute].dtype != 'object' or dataset[secondAttribute].dtype != 'object'):
            generatePlot = True
        return generatePlot
    
    def generatePlot(self, firstAttribute, secondAttribute):
        lastTestInformations = self.testInformations[-1]
        self.testInformations.pop()
        boxPlot = Plot()
        lastTestInformations['chart'] = boxPlot.createBoxPlotOverload(dataset[firstAttribute], dataset[secondAttribute])
        del boxPlot
        self.testInformations.append(lastTestInformations)
        return None

class ChiSquareTest(HypothesisTests):
    
    def runTest(self, firstAttribute, secondAttribute):
        self.testInformations = []
        self.testName = 'Test Chi-kwadrat'
        res = stats.chi2_contingency(pandas.crosstab(dataset[firstAttribute], dataset[secondAttribute]), correction=False)
        self.pValue = res[1].round(5)
        self.testValue = res[0].round(2)
        self.decision = self.setDecision()
        self.setTestInformations(firstAttribute, secondAttribute)
        if(self.checkIfGeneratePlot(firstAttribute, secondAttribute) == True):
            self.generatePlot(firstAttribute, secondAttribute)
        return self.testInformations

class SpearmanTest(HypothesisTests):
    
    def setDecision(self):
        if(self.testValue == 0.0):
            return 'Brak korelacji'
        elif(self.testValue > 0):
            return 'Korelacja dodatnia'
        elif(self.testValue < 0):
            return 'Korelacja ujemna' 
    
    def runTest(self, firstAttribute, secondAttribute):
        self.testInformations = []
        self.testName = 'Korelacja rho-Spearmana'
        res = stats.spearmanr(dataset[firstAttribute], dataset[secondAttribute], nan_policy = 'omit')
        self.pValue = res[1].round(5)
        self.testValue = res[0].round(2)
        self.decision = self.setDecision()
        self.setTestInformations(firstAttribute, secondAttribute)
        if(self.checkIfGeneratePlot(firstAttribute, secondAttribute) == True):
            self.generatePlot(firstAttribute, secondAttribute)
        return self.testInformations

class KruskalTest(HypothesisTests):
    
    def runTest(self, firstAttribute, secondAttribute):
        self.testInformations = []
        self.testName = 'Test Kruskala-Wallisa'
        unique = dataset[firstAttribute].unique()
        x = 0
        arr = []
        ub = []
        while x < len(unique):
            y = 0
            while y < len(dataset[firstAttribute]):
                if(unique[x] == dataset[firstAttribute][y]):
                    arr.append(dataset[secondAttribute][y])
                y += 1
            x += 1
            ub.append(arr)
            arr = []
        res = stats.kruskal(*ub)
        self.pValue = res[1].round(5)
        self.testValue = res[0].round(2)
        self.decision = self.setDecision()
        self.setTestInformations(firstAttribute, secondAttribute)
        if(self.checkIfGeneratePlot(firstAttribute, secondAttribute) == True):
            self.generatePlot(firstAttribute, secondAttribute)
        return self.testInformations

class UMannTest(HypothesisTests):
    
    def runTest(self, firstAttribute, secondAttribute):
        self.testInformations = []
        self.testName = 'Test U Manna-Whitneya'
        test = pandas.crosstab(dataset[firstAttribute],dataset[secondAttribute], margins=True)
        columns = len(test.columns) - 1
        rows = len(test.index)
        AllValues = test.iloc[rows-1]
        x = 0
        ranga = 0
        ostatnia = 1
        temp = 0
        rangs = []
        while x < (len(AllValues)-1):
            temp += AllValues.iloc[x]
            ranga = (ostatnia + temp) / 2
            ostatnia = temp + 1 
            rangs.append(ranga)
            x += 1
        FirstRowValues = test.iloc[0]
        x = 0
        Rfrv = 0
        while x < (len(FirstRowValues)-1):
            Rfrv += rangs[x] * FirstRowValues.iloc[x]
            x += 1
        Uv = 0
        Uv = Rfrv - (FirstRowValues.iloc[len(FirstRowValues)-1] * ((FirstRowValues.iloc[len(FirstRowValues)-1] +1 )) / 2)
        LastRowValues = test.iloc[:,-1]
        LastRowValues = test.iloc[:,-1]
        x = 0
        multiplication = 1
        addition = 0
        while x < (len(LastRowValues)-1):
            multiplication *= LastRowValues.iloc[x]
            addition += LastRowValues.iloc[x]
            x += 1
        Zv = 0
        Zv = (Uv - (multiplication / 2)) / (math.sqrt(( multiplication * (addition + 1)) / 12))
        Val = norm.cdf(Zv.round(2))
        Vk = 2 * (1 - Val)
        self.pValue = Vk.round(2)
        self.testValue = Zv.round(2)
        self.decision = self.setDecision()
        self.setTestInformations(firstAttribute, secondAttribute)
        if(self.checkIfGeneratePlot(firstAttribute, secondAttribute) == True):
            self.generatePlot(firstAttribute, secondAttribute)
        return self.testInformations

class Outliers:
    
    def getOutlier(self, columnName):
        outliers = []
        if self.checkIfSearchOutliers(columnName) == True:
            outliers = self.searchOutliers(columnName)
            if self.checkIfFoundAnyOutliers(outliers) == False:
                outliers.append("Brak wartości odstających!")
        return outliers
    
    def checkIfSearchOutliers(self, columnName):
        searchOutliers = False
        if dataset[columnName].dtype == 'int64':
            searchOutliers = True
        elif dataset[columnName].dtype == 'float64':
            searchOutliers = True
        return searchOutliers
    
    def searchOutliers(self, columnName):
        q1 = dataset[columnName].describe().round(2)[4]
        q3 = dataset[columnName].describe().round(2)[6]
        first = q1 - 1.5*(q3 - q1)
        second = q3 + 1.5*(q3 - q1)
        data = dataset[columnName].value_counts(dropna=False).rename_axis('Wartości').reset_index(name='Liczność')
        outliers = []
        for value in data['Wartości'].iteritems():
            if(value[1] < first or value[1] > second):
                outliers.append(value[1])
        return outliers
    
    def checkIfFoundAnyOutliers(self, outliers):
        outliersExist = False
        if(len(outliers) > 0):
            outliersExist = True
        return outliersExist
    
    def deleteOutliers(self, columnName):
        message = []
        outliers = self.getOutlier(columnName)
        if(len(outliers) > 0):
            for i in range(0,len(outliers)):
                dataset.drop(dataset[dataset[columnName] == outliers[i]].index, inplace=True)
                message = ["Brak wartości odstających!"]
        return message

class Values:
    
    columnName = ''
    
    def changeValues(self, oldValue, newValue, columnName):
        self.columnName = columnName
        self.checkValuesType(oldValue, newValue)
        return None
    
    def checkValuesType(self, oldValue, newValue):
        if dataset[self.columnName].dtype == 'float64':
              self.changeFloatValues(oldValue, newValue)
        elif dataset[self.columnName].dtype == 'int64':
              self.changeIntegerValues(oldValue, newValue)
        elif dataset[self.columnName].dtype == 'object':
            self.changeTextValues(oldValue, newValue)
        return None
    
    def changeFloatValues(self, oldValue, newValue):
        converted = self.convertToFloat(oldValue, newValue)
        if len(converted) > 0:
            oldVal = converted[0]
            newVal = converted[1]
            dataset[self.columnName].replace(to_replace=oldVal, value=newVal, inplace=True)
            flash('Wartości zostały zamienione pomyślnie', 'success')
        return None
    
    def convertToFloat(self, oldValue, newValue):
        converted = []
        try:
            oldValueFloat = float(oldValue)
            newValueFloat = float(newValue)
            converted = [oldValueFloat, newValueFloat]
        except Exception as e:
            flash('Podaj wartości po kropce!', 'danger')
            redirect(url_for('columnName', columnName = self.columnName))
        return converted
    
    def changeIntegerValues(self, oldValue, newValue):
        converted = self.convertToInteger(oldValue, newValue)
        if len(converted) > 0:
            oldVal = converted[0]
            newVal = converted[1]
            dataset[self.columnName].replace(to_replace=oldVal, value=newVal, inplace=True)
            flash('Wartości zostały zamienione pomyślnie', 'success')
        return None
    
    def convertToInteger(self, oldValue, newValue):
        converted = []
        try:
            oldValueFloat = int(oldValue)
            newValueFloat = int(newValue)
            converted = [oldValueFloat, newValueFloat]
        except Exception as e:
            flash('Podaj wartości całkowitoliczbowe!', 'danger')
            redirect(url_for('columnName', columnName = self.columnName))
        return converted
    
    def changeTextValues(self, oldValue, newValue):
        if oldValue == 'NaN':
            dataset[self.columnName].fillna(newValue, inplace = True)
        else:
            dataset[self.columnName].replace(to_replace=oldValue, value=newValue, inplace=True)
        flash('Wartości zostały zamienione pomyślnie', 'success')
        return None
    
    def deleteMissingValues(self, method, columnName):
        self.checkMethod(method, columnName)
        return None
    
    def checkMethod(self, method, columnName):
        if method == 'Drop':
            self.deleteByDrop(columnName)
        elif method == 'Frequent':
            self.deleteByFrequent(columnName)
        return None
    
    def deleteByDrop(self, columnName):
        try: 
            dataset.dropna(how='any', inplace = True)
            flash('Wartości zostały usunięte pomyślnie', 'success')
        except Exception as e:
            flash('Wystąpił problem przy usuwaniu pustych wartości!', 'danger')
            redirect(url_for('columnName', columnName = columnName))
        return None
      
    def deleteByFrequent(self, columnName):
        try: 
            dataset[columnName].fillna(dataset[columnName].value_counts().idxmax(), inplace = True)
            flash('Wartości zostały usunięte pomyślnie', 'success')
        except Exception as e:
            flash('Wystąpił problem przy usuwaniu pustych wartości!', 'danger')
            redirect(url_for('columnName', columnName = columnName))
        return None
    
global dataset
dataset = None
global fileTitle
fileTitle = None

@app.route("/")
def main():
    return render_template('index.html') 

#If authorization using a Google account has been successful gets information about files (title, id) 
#and forwards to files template
@app.route('/files')
def apiRequest():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    files = drive.files().list(q="mimeType='application/vnd.google-apps.spreadsheet'").execute().get('items', [])
    session['credentials'] = credentialsToDict(credentials)
    return render_template('files.html',files = files) 

#Google OAuth 2.0 code
@app.route("/authorize")
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)   
    flow.redirect_uri = url_for('oauth2callback', _external=True)   
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')   
    session['state'] = state  
    return redirect(authorization_url)

#Google OAuth 2.0 code
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentialsToDict(credentials)
    return redirect(url_for('apiRequest'))

#Google OAuth 2.0 code
def credentialsToDict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

#Loging out the user and redirecting to the homepage
@app.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke', params={'token': credentials.token}, headers = {'content-type': 'application/x-www-form-urlencoded'})
    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        if 'credentials' in session:
            del session['credentials']
        flash('Wylogowano pomyślnie', 'success')
        return redirect(url_for('main'))
    else:
        return redirect(url_for('main'))

#Loading the contents of the csv file with its id also saving its title (necessary if user wants to generate a PDF report)
@app.route("/load", methods = ['POST'])
def fileLoad():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    fileId = request.form['fileId']
    fileName = request.form['fileTitle']
    try:
        global fileTitle
        fileTitle = fileName
        global dataset
        url = 'https://docs.google.com/spreadsheets/d/' + fileId + '/pub?gid=0&single=true&output=csv'
        res = requests.get(url).content
        dataset = pandas.read_csv(io.StringIO(res.decode('utf-8')))
    except Exception as e:
        flash('Wystąpił problem przy wczytywaniu pliku', 'danger')
        flash('Upewnij się, że podany plik został udostępniony!', 'danger')
        return redirect(url_for('apiRequest'))
    else:
        flash('Plik został wczytany pomyślnie', 'success')
        return render_template('preprocessing.html', columns = dataset.columns.tolist())
    
#Showing the preprocessing possibilities (delete outliers, delete missing values etc. ) for the selected column
@app.route('/col/<columnName>')
def columnName(columnName):
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        columns = dataset.columns.tolist()
        if columnName in columns:
            outlier = Outliers()
            outliers = outlier.getOutlier(columnName)
            del outlier
            data = dataset[columnName].value_counts(dropna=False).rename_axis('Wartości').reset_index(name='Liczność')
            if(len(outliers) > 0):
                return render_template('preprocessing.html', columns = columns, data = data, columnName = columnName, outliers = outliers)
            else:
                return render_template('preprocessing.html', columns = columns, data = data, columnName = columnName)
        else:
            flash('Wybierz poprawną kolumnę!', 'danger')
            return render_template('preprocessing.html', columns = columns)            
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main')) 

#Changing values for the selected columns as one of the preprocessing possibilities
@app.route('/changeValues', methods = ['POST'])
def changeValues():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        oldVal = request.form['oldValue']
        newVal = request.form['newValue']
        columnName = request.form['columnName']
        columns = dataset.columns.tolist()
        if columnName in columns:
            value = Values()
            value.changeValues(oldVal, newVal, columnName)
            del value
            outlier = Outliers()
            outliers = outlier.getOutlier(columnName)
            del outlier
            data = dataset[columnName].value_counts(dropna=False).rename_axis('Wartości').reset_index(name='Liczność')
            if(len(outliers) > 0):
                return render_template('preprocessing.html', columns = columns, data = data, columnName = columnName, outliers = outliers)
            else:
                return render_template('preprocessing.html', columns = columns, data = data, columnName = columnName)   
        else:
            flash('Wybierz poprawną kolumnę!', 'danger')
            return render_template('preprocessing.html', columns = columns) 
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Replacement of missing values for the selected columns as one of the preprocessing possibilities
@app.route('/missingValues', methods = ['POST'])
def missingValues():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        method = request.form['method']
        columnName = request.form['columnName']
        columns = dataset.columns.tolist()
        if columnName in columns:
            value = Values()
            value.deleteMissingValues(method, columnName)
            del value
            outlier = Outliers()
            outliers = outlier.getOutlier(columnName)
            del outlier
            data = dataset[columnName].value_counts(dropna=False).rename_axis('Wartości').reset_index(name='Liczność')
            if(len(outliers) > 0):
                return render_template('preprocessing.html', columns = columns, data = data, columnName = columnName, outliers = outliers)
            else:
                return render_template('preprocessing.html', columns = columns, data = data, columnName = columnName)           
        else:
            flash('Wybierz poprawną kolumnę!', 'danger')
            return render_template('preprocessing.html', columns = columns) 
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Deleting outliers for the selected columns as one of the preprocessing possibilities
@app.route('/deleteOutliers', methods = ['POST'])
def deleteOutliers():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        columnName = request.form['columnName']
        columns = dataset.columns.tolist()
        if columnName in columns:
            outlier = Outliers()
            message = outlier.deleteOutliers(columnName)
            del outlier
            data = dataset[columnName].value_counts(dropna=False).rename_axis('Wartości').reset_index(name='Liczność')
            return render_template('preprocessing.html', columns = columns, data = data, columnName = columnName, outliers = message)
        else:
            flash('Wybierz poprawną kolumnę!', 'danger')
            return render_template('preprocessing.html', columns = columns)      
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Showing statistical informations (min, max, mean etc.) and correlation for the contents of the loaded file
@app.route("/dashboard")
def dashboard():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        columns = dataset.columns.tolist()
        info = dataset.describe().round(2)
        corr = dataset.corr().round(2) 
        if(len(corr) > 0):
            return render_template('dashboard.html', columns = columns, info = info, corr = corr) 
        else:
            return render_template('dashboard.html', columns = columns, info = info) 
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Redirecting to summary template (contents of the template will be downloaded by Ajax - see: /getSummaryContent)
@app.route("/summary")
def summary():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        columns = dataset.columns.tolist()
        return render_template('summary.html', columns = columns) 
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Showing possible tests for the contents of the loaded file
@app.route("/tests")
def tests():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        columns = dataset.columns.tolist()
        return render_template('tests.html', columns = columns) 
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Showing statistical informations (min, max, mean etc.) and plots for the selected column
@app.route('/res/<columnName>')
def columnInformations(columnName):
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        columns = dataset.columns.tolist()
        if columnName in dataset.columns.tolist():
            info = dataset[columnName].describe().reset_index().round(2)
            chartImages = []
            data = dataset[columnName].value_counts(dropna=False).rename_axis(columnName).reset_index(name='Liczność')
            global attributes 
            attributes = [columnName]
            tabcols = data.columns.tolist()
            barPlot = Plot()
            barPlotImage = barPlot.createBarPlot(data[columnName], data['Liczność'])
            del barPlot
            boxPlot = Plot()
            boxPlotImage = boxPlot.createBoxPlot(data)
            del boxPlot
            chartImages = [barPlotImage, boxPlotImage]
            return render_template('columninformations.html', columns = columns, data = data, info = info, charts = chartImages, tabcols = tabcols, columnName = columnName)
        else:
            flash('Wybierz poprawną kolumnę!', 'danger')
            return redirect(url_for('dashboard'))
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main')) 
    
#Showing statistical informations (min, max, mean etc.) and plots for the selected columns (min 2 columns, max 5 columns)   
@app.route("/summaryinfo", methods = ['POST'])
def summaryInformations():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        global attributes
        attributes = request.form.getlist('checky')
        if len(attributes) < 2 or len(attributes) > 5:
            flash('Wybierz od 2 do 5 atrybutów', 'danger')
            return redirect(url_for('summary'))
        else:   
            data = dataset.groupby([*attributes]).size().reset_index(name='Liczność')
            data = data.sort_values('Liczność', ascending = False)
            columns = dataset.columns.tolist()
            info = data.describe().reset_index().round(2)
            tabcols = data.columns.tolist()
            if len(data.select_dtypes(exclude=['object']).columns.tolist()) > 1:
                corr = dataset[[*attributes]].corr()
                pairPlot = Plot()
                pairPlotImage = pairPlot.createPairPlot(dataset[[*attributes]])
                del pairPlot
                charts = [pairPlotImage]
                return render_template('summaryinformations.html', columns = columns, info = info, tabcols = tabcols , charts = charts, corr = corr)
            else:
                return render_template('summaryinformations.html', columns = columns, tabcols = tabcols, info = info)
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Downloading contents of the summary template by Ajax (see: /summary)
@app.route('/getSummaryContent')
def getSummaryContent():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None and 'attributes' in globals():
        datas =  dataset.groupby([*attributes]).size().reset_index(name='Liczność')
        data = json.loads(datas.to_json(orient="split"))["data"]
        return jsonify({'data': data})
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))
    
#Downloading contents of the loaded file by Ajax and showing it as a table in dashboard template   
@app.route('/getDatasetContent')
def getDatasetContent():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        data = json.loads(dataset.to_json(orient="split"))["data"]
        return jsonify({'data': data})
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))
    
#Downloading title of the loaded file by Ajax to generate PDF report
@app.route('/getfileTitle',  methods = ['POST'])
def getFileTitle():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if dataset is not None:
        return jsonify({'data': fileTitle})
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))

#Downloading contents of the loaded file by Ajax to generate PDF report
@app.route('/dataraport', methods = ['POST'])
def dataRaport():
    if 'credentials' not in session:
        return redirect(url_for('main'))
    if 'results' in globals():
        return jsonify({'data': results})
    else:
        flash('Wczytaj plik!', 'danger')
        return redirect(url_for('main'))
    
#Obtaining columns and the name of the statistical test to perform
@app.route("/testsform", methods = ['POST'])
def testsForm():
    attributes = request.form.getlist('checky')
    method = request.form.get('methods')
    global results
    results = []
    if len(attributes) < 2 or len(attributes) > 5:
        flash('Wybierz od 2 do 5 atrybutów', 'danger')
        return redirect(url_for('tests'))
    if(method == 'Chi-kwadrat'):
        results = ChiSquare(attributes)
    elif(method == 'Kruskal-Wallis'):
        for i in range(0,len(attributes)):
            if(dataset[attributes[i]].nunique() <=2 ):
                flash('Atrybut '+attributes[i], 'danger')
                flash('Posiada mniej niż 3 grupy!', 'danger')
                return redirect(url_for('tests'))    
        results = Kruskal(attributes)
    elif(method == 'U Mann-Whitney'):
        results = UMann(attributes)
    elif(method == 'Korelacja rho-Spearmana'):
        for i in range(0,len(attributes)):
            if(dataset[attributes[i]].dtype == 'object'):
                flash('Wybrano atrybut tekstowy!', 'danger')
                flash('Wybierz tylko liczbowe!', 'danger')
                return redirect(url_for('tests'))    
        results = Spearman(attributes)
    return render_template('testinformations.html', columns = dataset.columns.tolist(), results = results) 

#Performing tests to given columns (each columns without repetition)
#eg. attr = [a, b ,c] so test will performs for: ab, ac, bc
def ChiSquare(attr):
    results = []
    i = 0
    j = 1
    z = 0
    chiSquareTest = ChiSquareTest()
    while i < len(attr):
        while j < len(attr):
            if( i != j):
                results = chiSquareTest.runTest(attr[i], attr[j])
            j = j + 1
        z = z + 1
        j = z
        i = i + 1
    del chiSquareTest
    return results

def Kruskal(attr):
    results = []
    i = 0
    j = 1
    z = 0
    kruskalTest = KruskalTest()
    while i < len(attr):
        while j < len(attr):
            if( i != j):
                results = kruskalTest.runTest(attr[i], attr[j])
            j = j + 1
        z = z + 1
        j = z
        i = i + 1
    del kruskalTest
    return results

def UMann(attr):
    results = []
    i = 0
    j = 1
    z = 0
    umannTest = UMannTest()
    while i < len(attr):
        while j < len(attr):
            if( i != j):
                results = umannTest.runTest(attr[i], attr[j]) 
            j = j + 1
        z = z + 1
        j = z
        i = i + 1
    del umannTest
    return results

def Spearman(attr):
    results = []
    i = 0
    j = 1
    z = 0
    spearmanTest = SpearmanTest()
    while i < len(attr):
        while j < len(attr):
            if( i != j):
                results = spearmanTest.runTest(attr[i], attr[j])
            j = j + 1
        z = z + 1
        j = z
        i = i + 1
    del spearmanTest
    return results

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0', port=port)
#importing required libraries
from flask import Flask, request, render_template, redirect, url_for
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
from pymongo import MongoClient
from feature import FeatureExtraction

warnings.filterwarnings('ignore')

file = open("pickle/model.pkl","rb")
gbc = pickle.load(file)
file.close()

# MongoDB setup
client = MongoClient('localhost', 27017)  # Assuming MongoDB is running locally on the default port
db = client['phishield']  # Create or connect to the 'phisheild' database
collection = db['domainData']  # Use or create a collection named 'domainData'
auth_collection = db['auth']  # Collection for storing user authentication data

app = Flask(__name__)

# Route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Query the database to find the user
        user = auth_collection.find_one({"username": username, "password": password})

        # Check if user exists and password matches
        if user:
            return redirect(url_for("index"))  # Redirect to the main index page
        else:
            return "Wrong credentials. Please try again."

    return render_template("login.html")

# Main index page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1,30) 

        y_pred =gbc.predict(x)[0]
        #1 is safe       
        #-1 is unsafe
        y_pro_phishing = gbc.predict_proba(x)[0,0]
        y_pro_non_phishing = gbc.predict_proba(x)[0,1]
        
        # Saving data to MongoDB
        domain_data = {
            'domain': url,
            'score': round(y_pro_non_phishing, 2),
            'result': 'Not_Spam' if y_pred == 1 else 'Spam'
        }
        collection.insert_one(domain_data)  # Insert data into MongoDB
        
        pred = "It is {0:.2f} % safe to go ".format(y_pro_phishing*100)
        return render_template('index.html', xx=round(y_pro_non_phishing, 2), url=url)
    return render_template("index.html", xx=-1)

if __name__ == "__main__":
    app.run(debug=True)

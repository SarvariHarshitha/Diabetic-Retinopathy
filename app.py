import numpy as np
import os
import uuid

from pathlib import Path

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests
from flask import Flask, request, render_template, redirect, url_for,request,session
import boto3
from flask_session import Session


##
model = load_model(r"model.h5")
app=Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#create a db using an initiated client
dynamo_client  =  boto3.resource(service_name = 'dynamodb',region_name = 'us-east-1',
              aws_access_key_id = 'AKIAU******MFY46HAXMI',
              aws_secret_access_key = 'LouA9W***FZcU*******XEqppyJ4d')

# dynamo_client.get_available_subresources()
# [3]: [Table]

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template("html/IndexPage.html")

@app.route('/Signup.html')
def signup():
    return render_template("html/Signup.html")

@app.route('/afterreg',methods=["POST"])
def afterreg():
    user_name=request.form['username']
    email=request.form['email']
    password=request.form['password']

    ### getting the product table
    user_table = dynamo_client.Table('User_Details')
    user_table.table_status
    user_table.put_item(Item = {"User Name":user_name,"Email":email,"Password":password})

    return "Successful"



#render html page


@app.route('/IndexPage.html')
def home():
    return render_template("html/IndexPage.html")

@app.route('/ForgotPassword.html')
def forget():
    return render_template('html/ForgotPassword.html')

@app.route('/forgetpwd',methods=['POST'])
def forgetpwd() :
    username = request.form['username']
    password = request.form['password']


    user_table = dynamo_client.Table('User_Details')
    response = user_table.get_item(Key={'User Name': username})  # Fix: use 'username' instead of 'input_username'

    if 'Item' in response:
        stored_username = response['Item']['User Name']

        if stored_username == username :
            user_table.update_item(Key={'User Name': username},UpdateExpression='SET Password = :new_password',
                    ExpressionAttributeValues={':new_password': password})
            return redirect(url_for('predict'))


        else :
            return "Invalid User"

    else :
        return "Invalid"


@app.route('/Login.html')
def login():
    return render_template('html/Login.html')

@app.route('/afterlogin',methods = ['POST'])
def afterlogin():
    session["username"] = request.form['username']
    username = request.form['username']
    password = request.form['password']
    
    user_table = dynamo_client.Table('User_Details')
    response = user_table.get_item(Key={'User Name': username})  # Fix: use 'username' instead of 'input_username'

    if 'Item' in response:
        stored_password = response['Item']['Password']

        if password == stored_password:
            # Passwords match, login successful
            return redirect(url_for('predict'))
        else:
            return render_template("html/Login.html", message="Incorrect Password")
            
    else:
        return render_template("html/Login.html", message="User Not Found")

   

@app.route('/PredictionPage.html')
def predict():
    if not session.get("username"):
        return redirect("/Login.html")
    return render_template('html/PredictionPage.html')
   
@app.route('/ContactUs.html')
def contact():
    return render_template('html/ContactUs.html')

#routes for logout and other pages

#result prediction
@app.route('/predict',methods=["GET","POST"])
def res():
    if request.method=='POST':
        # f=request.files['imagefile']
        # basepath=os.path.dirname(__file__)
        # #print("Current_path",basepath)
        # filepath=os.path.join(basepath,'uploads',f.filename)
        # print("Upload folder is"+filepath)
        # f.save(filepath)
        f = request.files['imagefile']

        # Use Path for handling file paths
        basepath = Path(__file__).parent
        upload_folder = basepath / 'uploads'
        
        # Ensure the 'uploads' folder exists
        upload_folder.mkdir(parents=True, exist_ok=True)

        # Create a unique filename using UUID
        filename = f"{str(uuid.uuid4())}_{f.filename}"
        
        filepath = upload_folder / filename
        filepath_str = str(filepath)  # Convert Path to string for compatibility with older functions

        f.save(filepath_str)
    
        img = image.load_img(filepath_str, target_size=(299,299))
        x = image.img_to_array(img) #img to array
        x = np.expand_dims(x, axis=0)  #add dimension
        #print(x)
        img_data = preprocess_input(x)
        prediction = np.argmax(model.predict(img_data),axis=1)
        #prediction = model.predict(x) #instead of predict_classes(x) we can use predict(x)----->predict_classes(x) gave error
        #print("prediction is",prediction)
        index = ['No diabetic retinopathy','Mild DR','Moderate DR','Severe DR','Proliferative DR']
        # result = str(index[output[0]])
        result = str(index[prediction[0]])
        print(result)
        return render_template('html/PredictionPage.html',prediction = result)

   



        
if __name__=='__main__':
    app.run(port=5000, debug=True)
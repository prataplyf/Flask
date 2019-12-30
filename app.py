#----- Sendinblue module ------------------
from __future__ import print_function
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
#----- Sendinblue module End ------------------
from flask import Flask, render_template, redirect, url_for, request, jsonify, request, make_response
import jwt # to jwt token
import datetime
# import pandas as pd
from functools import wraps
import pymongo
from flask import session
import string
import re
from random import *
import smtplib
from smtplib import SMTP
from socket import gaierror
from flask_cors import CORS, cross_origin



global password
password = ''
global pd
pd = ''

myclient = pymongo.MongoClient("mongodb+srv://prataplyf:Ashish12@ashish-hbjy0.mongodb.net/test?retryWrites=true&w=majority")
mydb = myclient.WSS
user = mydb["Users"]
course = mydb["Course"]
profile = mydb["Profile"]
User_delete = mydb["Delete"]
timeslotBooking = mydb["sessionBooking"]


app = Flask(__name__)
app.config['SECRET_KEY'] = "wharfstreetstrategies"
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})  # to hit an api comes from frontend

@app.route('/')  # page that help to go on a registration page
def api():
    return render_template('api.html')   


# @app.route('/register',methods = ['POST', 'GET'])
@app.route("/register", methods=['POST','GET'])
@cross_origin()
def register():
    if request.method == 'POST':
        uemail = request.form.get('email')
        uname = request.form.get('name')
        count = 0
        if uemail in [temp['Email'] for temp in user.find({}, {"Email":1} )]:
            return jsonify({"status":"Already used","message":"This Email ID Already Registered Us!"})
        elif uemail in [temp['Email'] for temp in User_delete.find({}, {"Email":1} )]:
            count += 1
            msg1 = "You are already registered with us and you Deleted your account Previously!"
            msg2 = "Want to Re-activate your account"
            return jsonify({"status":"Already used",'message':"Already Exist, Reactivate Account!"})
            # return jsonify({"Message": })
        else:
            user_count = user.find({}).count()
            delete_count = User_delete.find({}).count()
            result = user_count + delete_count + 1
            fid = "R-WSS"  # auto generated user id with R-WSS (i.e: R-WSS0000001)
            uid = fid + "%07d"%result
            def check():
                characters = string.ascii_letters  + string.digits
                password =  "".join(choice(characters) for x in range(randint(8,8)))
                if re.search("[0-9][a-z][A-Z]", password):
                    global pd
                    pd = password
                    configuration = sib_api_v3_sdk.Configuration()
                    configuration.api_key['api-key'] = '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'
                    api_instance = sib_api_v3_sdk.SMTPApi(sib_api_v3_sdk.ApiClient(configuration))
                    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                                        to=[{"email": uemail ,"name": uname}], 
                                        template_id=13, 
                                        params={"name": uname, "email": uemail, "pwd": pd}, 
                                        headers={"X-Mailin-custom": "custom_header_1:custom_value_1|custom_header_2:custom_value_2|custom_header_3:custom_value_3", "charset": "iso-8859-1"}) # SendSmtpEmail | Values to send a transactional email
                    try:
                        # Send a transactional email
                        api_response = api_instance.send_transac_email(send_smtp_email)
                        user.insert_one({"_id": uid, "Name": uname, "Email":uemail, "Password":pd })   
                        pprint(api_response)
                    except ApiException as e:
                        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
                    # 
                else:
                    return check()
            check()
            return jsonify({"status":"Success","message":"Register Successfully", "data":{"_id": uid, "name": uname, "email":uemail, "password": pd }})
                
    
    return render_template('register.html')


@app.route('/reactivate', methods=['POST','GET'])  # Re-activate Deleted Account From Delete Table
@cross_origin()
def reactivate():
    if request.method == 'POST':
        mail = request.form.get('email')
        if mail in [temp['Email'] for temp in User_delete.find({}, {"Email":1} )]:
            for x in User_delete.find({"Email":mail},{"Name":1, "Email":1, "Password":1, "_id":1}):
                uid = x['_id']
                name = x['Name']
                email = x['Email']
                
                
                # Code for Password send on User Email
                def check():
                    characters = string.ascii_letters  + string.digits
                    password =  "".join(choice(characters) for x in range(randint(8,8)))
                    if re.search("[0-9][a-z][A-Z]", password):
                        global pd
                        pd = password
                        configuration = sib_api_v3_sdk.Configuration()
                        configuration.api_key['api-key'] = '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'
                        api_instance = sib_api_v3_sdk.SMTPApi(sib_api_v3_sdk.ApiClient(configuration))
                        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                                            to=[{"email": email ,"name": name}], 
                                            template_id=14, 
                                            params={"name": name, "email": email, "pwd": password}, 
                                            headers={"X-Mailin-custom": "custom_header_1:custom_value_1|custom_header_2:custom_value_2|custom_header_3:custom_value_3", "charset": "iso-8859-1"}) # SendSmtpEmail | Values to send a transactional email
                        try:
                            # Send a transactional email
                            api_response = api_instance.send_transac_email(send_smtp_email)
                            user.insert_one({"_id": uid, "Name": name, "Email":email, "Password":pd })
                            User_delete.remove({"Email":email},{"Name":1, "Email":1, "Password":1, "_id":1})  
                            pprint(api_response)
                        except ApiException as e:
                            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
                        # 
                    else:
                        return check()
                check()
                return jsonify({"status":"Success","message":"Re-activate Account Successfully", 
                                "data":{
                                        "_id": uid, 
                                        "name": name, 
                                        "email":email, 
                                        "password": pd 
                                        }})
        else:
            return jsonify({"status":"Error","message":"Enter Correct Email ID!"})
    
    msg = "Enter your Email ID for Register Yourself !"
    return render_template('reactivate.html', message=msg)

 

@app.route('/login', methods=['POST','GET'])
@cross_origin()
def login():
    if request.method == 'POST':
        auth = request.authorization
        mail = request.form.get('lmail')
        enter_pass = request.form.get('lpassword')
        # print(mail)
        for x in user.find({"Email":mail},{"Name":1, "Email":1, "Password":1, "_id":1}):
            pwd = x['Password']
            uid = x['_id']
            uname = x['Name']
            umail = x['Email']
            if pwd == enter_pass:
                token = jwt.encode({'user':uname, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                # return jsonify({'Token':token.decode('UTF-8'), 'Message':"Login Success", "User ID":uid, "Name": uname, "Email":umail})
                msg = "Login Successful!"
                return jsonify({ "data":{"name": uname, 
                                 "userid": uid, 
                                 "email": umail, 
                                 "token":token.decode('UTF-8')}, 
                                 "message": msg,
                                 "status":"Success"
                                })
                #return "Login Success"
            else:
                return make_response('Wrong email ID or Password!', 
                                        401, {'WWW-Authenticate' : 'Basic realme="Login Required"'})

        

    return render_template('login.html')



@app.route('/prof')  # profile
@cross_origin()
def prof():
    for x in profile.find({"Email ID":"singh@gmail.com"}):
        return x



@app.route('/delete', methods=['POST', 'GET'])  # Delete an Account of Existing Users
@cross_origin()
def delete():
    if request.method == 'POST':
        did = request.form.get('cid')  # did -> (delete id)
        for x in user.find({"_id":did},{"Name":1, "Email":1, "Password":1, "_id":1}):
            uid = x['_id']
            name = x['Name']
            email = x['Email']
            password = x['Password']
            User_delete.insert_one({"_id": uid, "Name": name, "Email":email, "Password":password })
            user.remove({"_id":did},{"Name":1, "Email":1, "Password":1, "_id":1})
            return jsonify({"id":uid, "message": "Data Delete!", "status":"Success"})

            # else:
            #     return jsonify({'Message': "IDs Not Found!"})
        # elif did in User_delete.find({"_id":did}, {"_id":1}):
        #     return jsonify({"Message":"User Already Deleted"})
        else:
            return jsonify({"message":"This ID doesn't exist!","status":"Error"})
    
    return render_template('delete.html')

@app.route('/passupdate', methods=['POST', 'GET'])
@cross_origin()
def passupdate():
    msg = "Pending..."
    return render_template('passupdate.html', message=msg)



@app.route('/booking', methods=['POST', 'GET'])
@cross_origin()
def booking():
    if request.method == 'POST':
        uname = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        skypeID = request.form.get('skypeID')
        date = request.form.get('date')
        timeslot = request.form.get('timeslot')
        result = timeslotBooking.find({}).count() + 1
        uid = "B-WSS" + "%07d"%result
        name = uname.split()[0]
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = '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'
        api_instance = sib_api_v3_sdk.SMTPApi(sib_api_v3_sdk.ApiClient(configuration))
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                            to=[{"email": email ,"name": name}], 
                            template_id=15, 
                            params={"name": name, "date":date, "time":timeslot}, 
                            headers={"X-Mailin-custom": "custom_header_1:custom_value_1|custom_header_2:custom_value_2|custom_header_3:custom_value_3", "charset": "iso-8859-1"}) # SendSmtpEmail | Values to send a transactional email
        try:
            # Send a transactional email
            api_response = api_instance.send_transac_email(send_smtp_email) 
            timeslotBooking.insert_one({"_id":uid,"Name":name, "Email":email, "Contact":contact, "SkypeID":skypeID,"Date":date, "TimeSlot":timeslot})
            pprint(api_response)
            return jsonify({"Name":name, "Email":email, "Contact Number":contact, "SkypeID":skypeID,"Date":date, "TimeSlot":timeslot})
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
    

    return render_template('booking.html')



@app.route('/getbooking', methods=['GET'])
@cross_origin()
def getbooking():
    if request.method == 'GET':
        result = []
        for i in range(0,timeslotBooking.find({}).count()):
            for x in timeslotBooking.find({},{"_id":0,"Name":1, "Date":1, "TimeSlot":1}):
                result.append({"name":x['Name'], "date":x['Date'], "timeslot":x['TimeSlot']})            
            return jsonify({"message":"Data Information", "status":"success"},result)
    else:
        return jsonify({"message":"No Booking Available"})


if __name__ == "__main__":
    app.run(debug=False, port=32)







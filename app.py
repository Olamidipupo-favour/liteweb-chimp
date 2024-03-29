from flask import Flask, request,send_file
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from pyrebase import pyrebase
import datetime
import os
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import xlsxwriter
app=Flask(__name__)
CORS(app,resources={r"/api/v1/*": {"origins": "*"}})
app.config["JWT_SECRET_KEY"] = "vdA2CoHSyLCEiDzObYrnxQigdQuImERIh2T9DuTteBIJDXZS1FXcCuPdzCtNIb0d5r18LpII4a5iR4oBIK5Gn4wARH3X93QhSCiV"
jwt = JWTManager(app)
api = Api(app)
config = {
     "apiKey": "AIzaSyCwsl52eT2ju46ZWqI4ns1CgBzK4A-XJDM",
  "authDomain": "liteweb-chimp.firebaseapp.com",
  "databaseURL": "https://liteweb-chimp-default-rtdb.firebaseio.com",
  "projectId": "liteweb-chimp",
  "storageBucket": "liteweb-chimp.appspot.com",
  "serviceAccount": "liteweb-chimp-firebase-adminsdk-thz6s-03e1cfb488.json",
  "databaseURL": "https://liteweb-chimp-default-rtdb.firebaseio.com"
}
db = pyrebase.initialize_app(config).database()
app.config['MAIL_SERVER']='mail.litewebhq.com'
app.config['MAIL_PORT'] = 465
print(os.environ.get('MAIL_USERNAME'))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
class Login(Resource):
    def post(self):
        data = request.get_json()
        email=data['email'].replace(".", "_").replace("@", "__")
        password = data['password']
        try:
            user = db.child("users").child(email).get().val()
            if check_password_hash(user['password'],password):
                expires = datetime.timedelta(days=90000)
                access_token = create_access_token(identity=email, expires_delta=expires)
                return {"token": access_token}, 200
            else:
                return {"error": "Invalid username or password"}, 401
        except:
            return {"error": "Invalid username or password"}, 401
class Register(Resource):
    @jwt_required()
    def post(self):
        data=request.get_json()
        email=data['email'].replace(".", "_").replace("@", "__")
        password=data['password']
        print(db.child("users").child(email).get().val())
        try:
            if(db.child("users").child(email).get().val()!=None):
                return {"error": "Email already exists"}, 401
            else:
                db.child("users").child(email).set({"password":generate_password_hash(password)})
                return {"message": "User created successfully"}, 200
        except:
            return {"error": "Invalid username or password"}, 401
class Wait(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        print(current_user)
        data=request.get_json()
        email=data['email'].replace(".", "_").replace("@", "__")
        name=data.get('name','')
        whatsapp_number=data.get("whatsapp",'')
        try:
            if(db.child("suscribers").child(email).get().val()!=None):
                return {"error": "Email already exists"}, 401
            else:
                db.child("suscribers").child(email).set({"date":datetime.datetime.now().isoformat(),"name":name,"whatsapp number":whatsapp_number})
                #send a subscription email.
                em=email.replace("__","@").replace("_",".")
                print(em)
                msg=Message("Subscription", sender="o.favour@codecubehq.com", recipients=[em])
                #msg.body="Hello "+f"{name}"+",\n\nThank you for subscribing to our waitlist. We will keep you updated on our latest products and services.\n\nRegards,\n\nThe Liteweb Team"
                msg.body=   """
Hey there Chief 👋,

Welcome to the Liteweb Engine waitlist! 🎉 We're thrilled to have you on board and can't wait to show you what we've been working on! 🔥

We're on a mission to make website building super easy for everyone, and we're excited to have you be a part of it! 😎

Don't forget to spread the word and invite your friends to join the waitlist too! The more the merrier! 🤩

We'll be sure to keep you updated and let you know the moment we launch our platform! 🚀

Cheers! 🥳
The Liteweb Team

"""
                mail.send(msg)
                return {"message": "Suscribed!"}, 200
        except Exception as e:
            print(e)    
            return {"error": "An error occured!"}, 401
        return {"message":"User suscribed  successfully!"}, 200
class getSuscribers(Resource):
    @jwt_required()
    def get(self):
        suscribers=db.child("suscribers").get().val()
        workbook = xlsxwriter.Workbook('suscribers.xlsx')
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        # Open an excel file
        for i in suscribers:
            print(i)
            worksheet.write(row, col, i.replace("__","@").replace("_","."))
            worksheet.write(row, col+1, suscribers[i]['date'])
            worksheet.write(row, col+2, suscribers[i].get('name'))
            worksheet.write(row, col+2, suscribers[i].get('whatsapp number'))
            row+=1
            col=0
        workbook.close()
        return send_file('suscribers.xlsx', as_attachment=True)
class getSuscribersData(Resource):
    @jwt_required()
    def get(self):
        suscribers=db.child("suscribers").get().val()
        return suscribers
api.add_resource(Login, '/api/v1/login')
api.add_resource(Register, '/api/v1/register')
api.add_resource(Wait, '/api/v1/wait')
api.add_resource(getSuscribers, '/api/v1/getsuscribers')
api.add_resource(getSuscribersData,'/api/v1/getsuscribersdata')
if __name__ == '__main__':
    app.run(debug=True)
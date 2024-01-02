from models import db
from flask import Flask, render_template
from api.resource import api
from security import user_datastore, sec
from flask_security.utils import hash_password
from flask import request, jsonify
from flask_mail import Mail
from flask_cors import CORS

from worker import make_celery


from cache_config import initialize_cache


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI' ] = 'sqlite:///Primary_DataBase_IITM_MADII.db'
app.config['SECRET_KEY'] = "secretkey"
app.config['SECURITY_PASSWORD_SALT'] = "salt"
app.config["WTF_CSRF_ENABLED"] = False
app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = "Authentication-Token"
app.config["SECURITY_PASSWORD_HASH"] = 'bcrypt'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_JSON'] = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dpamneja@gmail.com'
app.config['MAIL_PASSWORD'] = 'xctn mdap gwok ewxr' 
app.config['SECURITY_EMAIL_SENDER'] = 'dpamneja@gmail.com'

cache = initialize_cache(app)

api.init_app(app)
db.init_app(app)
sec.init_app(app,user_datastore)
mail = Mail(app)


app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/1',
    result_backend='redis://localhost:6379/2'
)
celery = make_celery(app)
import tasks


with app.app_context():
    db.create_all()
    
         
@app.before_request
def load_database():
    if not user_datastore.find_role("Admin"):
        user_datastore.create_role(name = "Admin", description = "Admin Related Role. Access to the entire application and it's features.")
        db.session.commit()
        
    if not user_datastore.find_user(email = "dpamneja@gmail.com"):
        admin_user = user_datastore.create_user(username = "Dhruv_Pamneja", email = "dpamneja@gmail.com", password = hash_password("adminpass1234"))
        user_datastore.add_role_to_user(admin_user, "Admin")
        db.session.commit()
    
    if not user_datastore.find_role("Store Manager"):
        user_datastore.create_role(name="Store Manager", description="Manages store inventory and sales.")
        db.session.commit()

    if not user_datastore.find_role("User"):
        user_datastore.create_role(name="User", description="Regular user with purchasing abilities.")
        db.session.commit()
        


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register_app', methods=['POST'])
def register():
    data = request.json
    
    if not data['username'] or not data['email'] or not data['password']:
        return jsonify(message="Username, email, and password are required."), 400

    encrypted_password = hash_password(data['password'])
    user = user_datastore.create_user(username=data['username'],email=data['email'], password=encrypted_password)
    db.session.commit()

    role = user_datastore.find_role(data['role'])
    if role == 'User':
        user_datastore.activate_user(user)
    else:
        user_datastore.deactivate_user(user)
    
    user_datastore.add_role_to_user(user, role)
    db.session.commit()

    return jsonify(message="User registered successfully!"), 201


@app.route('/generate_csv/<int:user_id>/<string:email>', methods=['GET'])
@cache.memoize(timeout=15)
def generate_csv_endpoint(user_id,email):
    tasks.generate_csv.delay(user_id,email)
    return "True"
    


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
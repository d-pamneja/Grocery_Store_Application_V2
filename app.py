from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, StatementError, InvalidRequestError

from flask import Flask, render_template, request, redirect, url_for, flash, request, session, redirect
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import InputRequired, Email
from flask_login import UserMixin, RoleMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm, Form

db = SQLAlchemy()  #Initialising DataBase Here
app = Flask(__name__) #Initialising the Aplication in Flask

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Primary_DataBase_MADII.sqlite3"
app.config['SECRET_KEY'] = 'Dhruv_MAD2_Project_IITM'
db.init_app(app) # Connecting the Database to the App
bcrypt = Bcrypt(app) # Connecting the BCRYPT functionality to be used in our app

login_manager = LoginManager() #This will basically allow our app and flash login to work together i.e. it connects them
login_manager.init_app(app)
login_manager.login_view = 'Login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


## DATABASE CREATION

# Here, we will create classes for both of our primary tables i.e. Category and Product. This is for the creation of our databases. Now, we will use db.Model as a parameter of each class to inherit some useful methods such as Column, Integer, String etc. 
class Category(db.Model): #This is the class for Category, which will store all the prodcuts. Each product will be from a category, and a category may have multiple products
    category_id = db.Column(db.Integer(),primary_key = True) #ID of a category,set as the primary key
    category_name = db.Column(db.String(50), nullable = False) #Name of the category
    category_des = db.Column(db.String(150)) #This contains an optional short description of the category
    products = db.relationship("Product", backref = "category", cascade = "all, delete") #Products a category has in it. We use backref so that it does not create redundant column with a foreign key and operates in one column only i.e. it creates a pseudo column where it stores the relationship. We use cascade so that if a category is deleted, the system automatically deletes it's products

    def __repr__(self):
        return "< Category %r >" % self.category_name

class Product(db.Model): #This is the class for Product, each unique SKU will be stored as an item in this
    product_id = db.Column(db.Integer(),primary_key = True) #ID of a product, set as the primary key
    product_name = db.Column(db.String(50), nullable = False) #Name of the product
    product_manufacture_date = db.Column(db.Date()) #Manufacturing Date of the Product
    product_expiry_date = db.Column(db.Date()) #Expiration Date of the Product
    product_price = db.Column(db.Float(),nullable = False) #Price in Indian National Rupee (INR) of the Product
    product_quantity_available = db.Column(db.Integer(), nullable = False) #The quantity available with the supplier for the said product
    product_unit = db.Column(db.String(),nullable = False) #Unit of the product eg: Kg, Litre, Piece, Dozen
    product_des = db.Column(db.String(150)) #This contains an optional short description of the product
    product_cat = db.Column(db.Integer(),db.ForeignKey("category.category_id"),nullable = False) #This takes the section id i.e. it assigns category to each product
    

    def __repr__(self):
        return "< Product %r >" % self.product_name
  
# Next, we will create a different types of roles which can be present in our application, their user table login/registration forms

class Role(db.Model, RoleMixin): # This is the role which a person needs to have from either an Admin, Store Manager or User
    role_id = db.Column(db.Integer, primary_key=True) #Unique ID of a role
    role_name = db.Column(db.String(80), unique=True) #Name of the role
    role_des = db.Column(db.String(100)) #Short description of the role
    users = db.relationship('User', backref='user_role', lazy=True, order_by='User.user_id')
    

class User(db.Model, UserMixin): 
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False)
    user_email = db.Column(db.String(25), nullable=False, unique=True)
    user_password = db.Column(db.String(100), nullable=False)
    user_role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))
    
    def get_id(self):
            return str(self.user_id)
    

class Login_Info(FlaskForm): #This is the class for a person who signs in (Admin/Store Manager/User)
    log_email = StringField(validators=[InputRequired(),Email(),validators.Length(min=6, max=25)],render_kw={"placeholder":"Email"}) #Email ID of the person
    log_password = PasswordField(validators=[InputRequired(), validators.Length(min=6, max=25)],render_kw={"placeholder":"Password"}) #Password of the person
    log_sub = SubmitField("Login") #Confirming Login

class Registration_Info(FlaskForm): #This is the class for each new person who signs up (Store Manager/User)
    reg_user = StringField(validators=[InputRequired(),validators.length(min=6,max=25)],render_kw={'placeholder':'Username'}) # Username of the person 
    reg_email = StringField(validators=[InputRequired(),Email(),validators.Length(min=6, max=25)],render_kw={"placeholder":"Email"}) #Email ID of the person
    reg_password = PasswordField(validators=[InputRequired(), validators.Length(min=6, max=25)],render_kw={"placeholder":"Password"}) #Password of the person
    reg_sub = SubmitField("Register") #Confirming Registration

#Now, let us create the functions for setting up the roles and the Admin
def setup_roles():
    roles = ['Admin', 'Store Manager', 'User']
    existing_roles = [r.role_name for r in Role.query.all()]

    for role_name in roles:
        if role_name not in existing_roles:
            role = Role(role_name=role_name)
            db.session.add(role)
    db.session.commit()
    print("Roles created/verified successfully!")


def setup_admin():
    hashed_password = bcrypt.generate_password_hash("DhruvPamneja_IITMAD2Project").decode('utf-8')
    admin_role = Role.query.filter_by(role_name="Admin").first()
    
    if admin_role:
        existing_admin = User.query.filter_by(user_role=admin_role).first()
        if not existing_admin:
            admin = User(user_name="Dhruv Pamneja", 
                         user_email="dpamneja@gmail.com", 
                         user_password=hashed_password, 
                         user_role=admin_role)
            db.session.add(admin)
            db.session.commit()
            print("Admin created successfully!")
    else:
        print("Admin role not found. Ensure roles are created.")
        
# NOTE_IMP : The below two lines calling the function are only to be done once, after which these lines should be commented out
setup_roles()
setup_admin()

 
# LOGIN ROUTES

@app.route('/login_admin',methods=['GET', 'POST']) #This is the login framework for the admin
def login_admin():
    form = Login_Info(request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.log_email.data).first()
        if user is None:
            flash("Email not registered. Please check your email or register.", 'Admin_Email_Not_Found_Error')
            return render_template('login_admin.html', form=form)
        if bcrypt.check_password_hash(user.user_password,form.log_password.data):
            if user.user_role.role_name != "Admin":
                flash("Unauthorized Admin Access.", 'Unauthorized_Admin_Error')
                return redirect(url_for('login_admin'))
            login_user(user)
            return redirect(url_for('landing_admin'))
        else:
            flash("Incorrect Password. Try Again.",'Incorrect_Admin_Password_Error')
    return render_template('login_admin.html',form=form) #The HTML Template 'login_admin.html' contains the html file which will be displayed


@app.route('/login_store_manager',methods=['GET', 'POST']) #This is the login framework for the store manager
def login_store_manager():
    form = Login_Info(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.log_email.data).first()
        if user is None:
            flash("Email not registered. Please check your email or register.", 'Store_Manager_Email_Not_Found_Error')
            return render_template('login_store_manager.html', form=form)
        if bcrypt.check_password_hash(user.user_password,form.log_password.data):
            if user.user_role.role_name != "Store Manager":
                flash("Unauthorized Store Manager Access.",'Unauthorized_Store_Manager_Error')
                return redirect(url_for('login_store_manager'))
            login_user(user)
            return redirect(url_for('landing_store_manager'))
        else:
            flash("Incorrect Password. Try Again.",'Incorrect_Store_Manager_Password_Error')
    return render_template('login_store_manager.html',form=form) #The HTML Template 'login_manager.html' contains the html file which will be displayed


@app.route('/login_user',methods=['GET', 'POST']) #This is the login framework for the user
def login_use():
    form = Login_Info(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.log_email.data).first()
        if user is None:
            flash("Email not registered. Please check your email or register.", 'User_Email_Not_Found_Error')
            return render_template('login_user.html', form=form)
        if user:
            if bcrypt.check_password_hash(user.user_password,form.log_password.data):
                login_user(user)
                return redirect(url_for('landing_user'))
            else:
                flash("Incorrect Password. Try Again.",'Incorrect_User_Password_Error')
    return render_template('login_user.html',form=form) #The HTML Template 'login_user.html' contains the html file which will be displayed

# REGISTRATION ROUTES
@app.route('/register_user', methods=['GET', 'POST']) #This is the framework to register for a new user
def register_user(): #The HTML Template 'register.html' contains the html file which will be displayed
    form = Registration_Info(request.form)

    if form.validate_on_submit(): #If the registration form is valid, it will hash the password using bcrypt and store it in the database
        existing_user_email = User.query.filter_by(user_email=form.reg_email.data).first()
        if existing_user_email: #If the entered user email already exists, it will throw an error and redirect to user registration page
            flash('This email ID exists in the system. Kindly choose another one.', 'Email_Exists_Error')
            return redirect(url_for('register_user'))
        
        hashed_password = bcrypt.generate_password_hash(form.reg_password.data)
        user_role = Role.query.filter_by(role_name="User").first()
        new_user = User(user_name = form.reg_user.data, user_email = form.reg_email.data, user_password = hashed_password,user_role_id = user_role.role_id)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_user'))
        except IntegrityError:
            db.session.rollback()
            flash("Error: The Email entered already exists in our database. Try to Log In.", "Danger_Integirty_Error")
        except (StatementError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Statement_Error")
        except (InvalidRequestError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
        except:
            db.session.rollback()
            flash("An unexpected error occurred.", "Danger_Other")
        
    return render_template('register_user.html', form=form)

@app.route('/register_store_manager', methods=['GET', 'POST']) #This is the framework to register for a new Store Manager
def register_store_manager(): #The HTML Template 'register.html' contains the html file which will be displayed
    form = Registration_Info(request.form)

    if form.validate_on_submit(): #If the registration form is valid, it will hash the password using bcrypt and store it in the database
        existing_user_email = User.query.filter_by(user_email=form.reg_email.data).first()
        if existing_user_email: #If the entered user email already exists, it will throw an error and redirect to user registration page
            flash('This email ID exists in the system. Kindly choose another one.', 'Email_Exists_Error')
            return redirect(url_for('register_store_manager'))
        
        hashed_password = bcrypt.generate_password_hash(form.reg_password.data)
        user_role = Role.query.filter_by(role_name="Store Manager").first()
        new_user = User(user_name = form.reg_user.data, user_email = form.reg_email.data, user_password = hashed_password,user_role_id = user_role.role_id)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_store_manager'))
        except IntegrityError:
            db.session.rollback()
            flash("Error: The Email entered already exists in our database. Try to Log In.", "Danger_Integirty_Error")
        except (StatementError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Statement_Error")
        except (InvalidRequestError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
        except:
            db.session.rollback()
            flash("An unexpected error occurred.", "Danger_Other")
        
    return render_template('register_store_manager.html', form=form)

@app.route('/logout',methods = ['GET', 'POST'])
def logout(): #This will logout the user/admin and redirect them to the home page
    logout_user()
    return redirect('/')
 
## CRUD ROUTES FOR CATEGORY AND PRODUCT ##

## CATEGORY

# CREATE
# Now, we create a function of creating a category which will be having two methods i.e. POST and GET. This basically is the code for adding a new category to our database directly directly from a webpage
@app.route('/category/create', methods = ['POST','GET'])
def create_category():
    if request.method == "POST":
        #Whatever the user enters on the webpage, will be stored in these variables
        cat_name = request.form['cat_name'] 
        cat_des = request.form['cat_des']
        #Next, we use the variables which we have got from the user above and create a category via the class Category
        cat = Category(
            category_name = cat_name,category_des = cat_des
        )
        #Next, we add that to our database and commit changes using the try except block
        try:
            db.session.add(cat)
            db.session.commit()
            flash("Category created successfully!", "Success_Category_Create")

            return redirect(url_for('landing_admin')) #This redirects us back to the landing page
        except IntegrityError:
            db.session.rollback()
            flash("Error: A category with that name might already exist.", "Danger_Integirty_Error")
        except (StatementError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Statement_Error")
        except (InvalidRequestError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
        except:
            db.session.rollback()
            flash("An unexpected error occurred.", "Danger_Other")
            
    return render_template("create_category.html") #Notice how we have not created an else/elif column for GET method. If the request in not POST, it will automatically be get and we will display the template

# READ
# Moving ahead, we create a function to view all categories that are presently stored in our system
@app.route('/categories')
def view_categories():
    all = Category.query.all()
    return render_template('view_categories.html', all = all)


# UPDATE
# Moving ahead, we will create an update route for categories
@app.route('/category/edit/<int:category_id>', methods=['GET'])
def edit_category_page(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('edit_category.html', category = category)

@app.route('/category/update/<int:category_id>', methods=['POST'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)

    # Fetch data from the form and update the product object
    category.category_name = request.form['category_name'] 
    category.category_des = request.form['category_des']

    # Commit changes to the database using try except block
    try:
        db.session.commit()
        flash("Category updated successfully!", "Success_Category_Update")
        return redirect(url_for('categories'))  # Redirect back to the products view
    except IntegrityError:
        db.session.rollback()
        flash("Error: A category with that name might already exist.", "Danger_Integirty_Error")
    except (StatementError):
        db.session.rollback()
        flash("Error: There was an issue with your request.", "Danger_Statement_Error")
    except (InvalidRequestError):
        db.session.rollback()
        flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
    except:
        db.session.rollback()
        flash("An unexpected error occurred.", "Danger_Other")


# DELETE
# Moving ahead, we will create a delete route for category

@app.route('/category/confirm-delete/<int:category_id>', methods=['GET'])
def confirm_delete_category(category_id):
    return render_template('confirm_category_delete.html', category_id=category_id)

@app.route('/category/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    # Deleteing a category using the try except block
    try:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully!", "Success_Category_Delete")
        return redirect(url_for('categories'))  
    except IntegrityError:
        db.session.rollback()
        flash("Error: A category with that name might already exist.", "Danger_Integirty_Error")
    except (StatementError):
        db.session.rollback()
        flash("Error: There was an issue with your request.", "Danger_Statement_Error")
    except (InvalidRequestError):
        db.session.rollback()
        flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
    except:
        db.session.rollback()
        flash("An unexpected error occurred.", "Danger_Other")



## PRODUCT
# CREATE
# Now, we create a function of creating a product which will be having two methods i.e. POST and GET. This basically is the code for adding a new product to our database directly directly from a webpage
@app.route('/product/create', methods = ['POST','GET'])
def create_product():
    if request.method == "POST":
        #Whatever the user enters on the webpage, will be stored in these variables
        prod_name = request.form['product_name'] 
        prod_des = request.form['product_des']
        prod_manu_date = request.form['product_manufacture_date']
        prod_exp_date = request.form['product_expiry_date']
        prod_price = request.form['product_price']
        prod_unit = request.form['product_unit']
        prod_quant = request.form['product_quantity_available']
        cat_id = request.form['category_id']

        if date.fromisoformat(prod_exp_date) <= date.today():
            flash("Error, product expiry date must be ahead of today.",'Expiry_Date_Error')
        else:
            #Next, we use the variables which we have got from the user above and create a product via the class product
                prod = Product(
                    product_name = prod_name,product_des = prod_des,product_manufacture_date = prod_manu_date, product_expiry_date = prod_exp_date,
                    product_price = prod_price, product_unit = prod_unit,product_quantity_available = prod_quant, product_cat = cat_id)
                
                #Next, we add that to our database and commit changes using try except block
                try:
                    db.session.add(prod)
                    db.session.commit()
                    
                    flash("Product created successfully!", "Success_Product_Create")
                    return redirect(url_for('landing_admin')) #This redirects us back to the landing page
                    
                except IntegrityError:
                    db.session.rollback()
                    flash("Error: A product with that name might already exist.", "Danger_Integirty_Error")
                except (StatementError):
                    db.session.rollback()
                    flash("Error: There was an issue with your request.", "Danger_Statement_Error")
                except (InvalidRequestError):
                    db.session.rollback()
                    flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
                except:
                    db.session.rollback()
                    flash("An unexpected error occurred.", "Danger_Other")
                
    cats = Category.query.all()
    return render_template("create_product.html", cats = cats) #Notice how we have not created an else/elif column for GET method. If the request in not POST, it will automatically be get and we will display the template


# READ
@app.route('/product_admin')
def view_products_admin():
    all = Product.query.all()
    cats = Category.query.all()
    return render_template('view_products_admin.html', all = all, cats = cats)

# UPDATE
# Moving ahead, we will create an update route for products
@app.route('/product/edit/<int:product_id>', methods=['GET'])
def edit_product_page(product_id):
    product = Product.query.get_or_404(product_id)
    cats = Category.query.all()
    return render_template('edit_product.html', cats = cats, product=product)

@app.route('/product/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    product_expiry_date = request.form['product_expiry_date']

    if date.fromisoformat(product_expiry_date) <= date.today():
            flash("Error, product expiry must be ahead of today.",'Expiry_Date_Error')
    else:
        product.product_name = request.form['product_name'] 
        product.product_des = request.form['product_des']
        product.product_manufacture_date = request.form['product_manufacture_date']
        product.product_expiry_date = request.form['product_expiry_date']
        product.product_price = request.form['product_price']
        product.product_unit = request.form['product_unit']
        product.product_quantity_available = request.form['product_quantity_available']
        product.product_cat = request.form.get('category_id')

        try:
            db.session.commit()
            flash("Product updated successfully!", "Success_Product_Update")
        except IntegrityError:
            db.session.rollback()
            flash("Error: A product with that name might already exist.", "Danger_Integirty_Error")
        except (StatementError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Statement_Error")
        except (InvalidRequestError):
            db.session.rollback()
            flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
        except:
            db.session.rollback()
            flash("An unexpected error occurred.", "Danger_Other")

    return redirect(url_for('product_admin')) # Redirect back to the products view


# DELETE
#Moving ahead, we will create a delete route for product

@app.route('/product/confirm-delete/<int:product_id>', methods=['GET'])
def confirm_delete_product(product_id):
    return render_template('confirm_product_delete.html', product_id=product_id)

@app.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully!", "Success_Product_Delete")
        return redirect(url_for('product_admin'))  
    except IntegrityError:
        db.session.rollback()
        flash("Error: A product with that name might already exist.", "Danger_Integirty_Error")
    except (StatementError):
        db.session.rollback()
        flash("Error: There was an issue with your request.", "Danger_Statement_Error")
    except (InvalidRequestError):
        db.session.rollback()
        flash("Error: There was an issue with your request.", "Danger_Invalid_Request_Error")
    except:
        db.session.rollback()
        flash("An unexpected error occurred.", "Danger_Other")


# FILTERING AND SEARCH
@app.route('/filter_products', methods=['POST'])
# @login_required
def filter_products():
     #Here, we will collect any information given by the user based on filters
    min_price = request.form['min_price']
    max_price = request.form['max_price']
    min_manufacture_date = request.form['min_manufacture_date']
    max_manufacture_date = request.form['max_manufacture_date']
    min_expiry_date = request.form['min_expiry_date']
    max_expiry_date = request.form['max_expiry_date']
    category_id = request.form['category_id']

    #Saving the current filters to session
    session['filters'] = {
        'min_price': min_price,
        'max_price': max_price,
        'min_manufacture_date': min_manufacture_date,
        'max_manufacture_date':max_manufacture_date,
        'min_expiry_date':min_expiry_date,
        'max_expiry_date':max_expiry_date,
        'category_id':category_id
    }
    filtered_products = Product.query

    if min_price:
        filtered_products = filtered_products.filter(Product.product_price >= min_price)
    if max_price:
        filtered_products = filtered_products.filter(Product.product_price <= max_price)
    if min_manufacture_date:
        filtered_products = filtered_products.filter(Product.product_manufacture_date >= min_manufacture_date)
    if max_manufacture_date:
        filtered_products = filtered_products.filter(Product.product_manufacture_date <= max_manufacture_date)
    if min_expiry_date:
        filtered_products = filtered_products.filter(Product.product_expiry_date >= min_expiry_date)
    if max_expiry_date:
        filtered_products = filtered_products.filter(Product.product_expiry_date <= max_expiry_date)
    if category_id:
        filtered_products = filtered_products.filter(Product.product_cat == category_id)

    all_filtered_products = filtered_products.all()
    cats = Category.query.all()

    return render_template('landing_user.html', all=all_filtered_products, cats=cats)

@app.route('/clear_filters')
def clear_filters():
    # Clear all filters from the session
    if 'filters' in session:
        session.pop('filters')
    return redirect(url_for('landing_user'))

@app.route('/products_search', methods=['GET', 'POST'])
def products_search():
    search = request.args.get('search', '')
    if search:
        products = Product.query.filter(Product.product_name.like(f'%{search}%')).all()
    else:
        products = Product.query.all()
    return render_template('landing_user.html', all=products)



if __name__ == "__main__":
    app.run(debug=True)
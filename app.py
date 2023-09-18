from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, request, session, redirect

db = SQLAlchemy()  #Initialising DataBase Here
app = Flask(__name__) #Initialising the Aplication in Flask

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Primary_DataBase_MADII.sqlite3"
app.config['SECRET_KEY'] = 'Dhruv_MAD2_Project_IITM'
db.init_app(app) # Connecting the Database to the App

#Here, we will create classes for both of our primary tables i.e. Category and Product. This is for the creation of our databases. Now, we will use db.Model as a parameter of each class to inherit some useful methods such as Column, Integer, String etc. 
class Category(db.Model): #This is the class for Category, which will store all the prodcuts. Each product will be from a category, and a category may have multiple products
    category_id = db.Column(db.Integer(),primary_key = True) #ID of a category,set as the primary key
    category_name = db.Column(db.String(50), nullable = False) #Name of the category
    category_description = db.Column(db.String(150)) #This contains an optional short description of the category
    products = db.relationship("Product", backref = "category", cascade = "all, delete") #Products a category has in it. We use backref so that it does not create redundant column with a foreign key and operates in one column only i.e. it creates a pseudo column where it stores the relationship. We use cascade so that if a category is deleted, the system automatically deletes it's products

    def __repr__(self):
        return "< Category %r >" % self.category_name

class Product(db.Model): #This is the class for Product, each unique SKU will be stored as an item in this
    product_id = db.Column(db.Integer(),primary_key = True) #ID of a product, set as the primary key
    product_name = db.Column(db.String(50), nullable = False) #Name of the product
    product_manufacture_date = db.Column(db.String(50)) #Manufacturing Date of the Product
    product_expiry_date = db.Column(db.String(50)) #Expiration Date of the Product
    product_price = db.Column(db.Float(),nullable = False) #Price in Indian National Rupee (INR) of the Product
    product_quantity_available = db.Column(db.Integer(), nullable = False) #The quantity available with the supplier for the said product
    product_unit = db.Column(db.String(),nullable = False) #Unit of the product eg: Kg, Litre, Piece, Dozen
    product_description = db.Column(db.String(150)) #This contains an optional short description of the product
    product_cat = db.Column(db.Integer(),db.ForeignKey("category.category_id"),nullable = False) #This takes the section id i.e. it assigns category to each product
    

    def __repr__(self):
        return "< Product %r >" % self.product_name
    


if __name__ == "__main__":
    app.run(debug=True)
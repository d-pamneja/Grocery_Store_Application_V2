#Importing the Dependencies
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime

#Initialise SQLAlchemy
db = SQLAlchemy() 

##Define DataBases

#User and Role
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)
                       
class User(db.Model, UserMixin):
             __tablename__ = 'user' #Sends the ID of the user to the table roles_users
             id = db.Column(db.Integer(),autoincrement = True, primary_key = True) #ID of the User, set as the primary key
             username = db.Column(db.String(50)) #Username of the user
             email = db.Column(db.String(100), unique = True) #Email of the User, which is to be unique i.e. one person can register only once
             password = db.Column(db.String(255),nullable = False) #Password of the User, which cannot be empty
             active = db.Column(db.Boolean()) #Status of the User
             fs_uniquifier = db.Column(db.String(255),unique = True)
             roles = db.relationship('Role',secondary = roles_users,backref=db.backref('users',lazy = 'dynamic')) #This takes the user id & it assigns role to each user 
             

class Role(db.Model, RoleMixin): #This is the class to store Roles (Admin, Store Manager or User). Each person who uses the application will be one of these three, and a role may have multiple users
    __tablename__ = 'role' #Sends the ID of the role to the table roles_users
    id = db.Column(db.Integer(),primary_key = True) #ID of the Role, set as a primary Role
    name = db.Column(db.String(80),unique = True) #Name of the Role
    description = db.Column(db.String(255)) #Short Description of the Role
    
    
#Category and Product    
class Category(db.Model): #This is the class for Category, which will store all the prodcuts. Each product will be from a category, and a category may have multiple products
    id = db.Column(db.Integer(),primary_key = True) #ID of a category,set as the primary key
    name = db.Column(db.String(50), nullable = False,unique = True) #Name of the category
    description = db.Column(db.String(150)) #This contains an optional short description of the category
    products = db.relationship("Product", backref = "category", cascade = "all, delete") #Products a category has in it. We use backref so that it does not create redundant column with a foreign key and operates in one column only i.e. it creates a pseudo column where it stores the relationship. We use cascade so that if a category is deleted, the system automatically deletes it's products

    def __repr__(self):
        return "< Category %r >" % self.name

class Product(db.Model): #This is the class for Product, each unique SKU will be stored as an item in this
    id = db.Column(db.Integer(),primary_key = True) #ID of a product, set as the primary key
    name = db.Column(db.String(50), nullable = False) #Name of the product
    manufacture_date = db.Column(db.Date()) #Manufacturing Date of the Product
    expiry_date = db.Column(db.Date()) #Expiration Date of the Product
    price = db.Column(db.Float(),nullable = False) #Price in Indian National Rupee (INR) of the Product
    quantity_available = db.Column(db.Integer(), nullable = False) #The quantity available with the supplier for the said product
    unit = db.Column(db.String(),nullable = False) #Unit of the product eg: Kg, Litre, Piece, Dozen
    description = db.Column(db.String(150)) #This contains an optional short description of the product
    category_product = db.Column(db.Integer(),db.ForeignKey("category.id"),nullable = False) #This takes the section id i.e. it assigns category to each product
    created_by = db.Column(db.Integer(), db.ForeignKey('user.id'),nullable=False) #This defines that by which store manager was this product created
    creator = db.relationship('User')
    

    def __repr__(self):
        return "< Product %r >" % self.name
    
class CategoryRequest(db.Model): #This is the class to store and display requests from the store managers
    id = db.Column(db.Integer, primary_key=True) #ID of the request, set as primary key
    action = db.Column(db.String(10), nullable=False) # Action to be done in the request i.e. add,edit or remove
    name = db.Column(db.String(100), nullable=True) #Name of the category (as per the store manager)
    description = db.Column(db.String(1000), nullable=True) #Description of the category
    selectedCategory = db.Column(db.Integer(), db.ForeignKey("category.id"),nullable=True) #The id of the category which the user wishes to modify
    reason = db.Column(db.String(1000), nullable=True) #A string containing the subjective reasoning providied by the store manager
    
#Now, we will add the schemea for the functionality of the cart
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True) # ID of the cart
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # ID of the user to whom the cart belongs i.e. each user will have their own cart
    items = db.relationship('CartItem', backref='cart', cascade='all, delete') #Backred relationship with Cart Item i.e. if the cart is deleted, all the cart items in that cart get deleted as well

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True) # ID of the cart item
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id')) # ID of the cart where the item will be stored
    product_id = db.Column(db.Integer, db.ForeignKey('product.id')) # ID of the product which is stored in the cart
    quantity = db.Column(db.Integer) # Quantity of the item stored in the cart
    price = db.Column(db.Float) # Price of the item store in the cart
    product = db.relationship('Product') #Each item in cart item is eventually a product , hence we establish a relationship


# Now, we will add the functionality of buying and storing the order based on all order items
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True) # ID of that order
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # ID of the user which placed this order
    timestamp = db.Column(db.DateTime, default=datetime) # Datetime of the order
    grand_total = db.Column(db.Float, nullable=False) # Grand Total paid for the order
    items = db.relationship('OrderItem', backref='order') #Each order will have multiple orderitems, hence the relation

# Now, we will add the database to add the order items
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True) #ID of the orderitem
    order_id = db.Column(db.Integer, db.ForeignKey('order.id')) #ID of the order to which this item belongs
    product_id = db.Column(db.Integer, db.ForeignKey('product.id')) #ID of the product which this item is of
    quantity = db.Column(db.Integer, nullable=False) # Quantity of the order item sold
    price_at_purchase = db.Column(db.Float, nullable=False) # Price at purchase of the order item
    product = db.relationship('Product') #Each orderitem is eventually a product, hence we establish a relation
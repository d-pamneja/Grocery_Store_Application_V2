# Importing the dependencies
from flask_restful import Api,Resource, abort,fields,marshal,reqparse
from models import db, User as user_model, Category, Product,CategoryRequest, Cart,CartItem,Order, OrderItem
from datetime import datetime
from flask_security import auth_required,current_user
from flask import request
import json
import os



script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(script_directory)
relative_path = 'data/admin_settings.json'
admin_settings_file = os.path.join(parent_directory, relative_path)



# Initialising the API from flask_restful and setting the prefix
api = Api(prefix="/api") 


# Now, we will create some essential functions which we will use in one/multiple resources

def extract_role(user): #A function to extract the role of our user
    roles = [role.name for role in user.roles]
    return roles[0] if roles else None


def parse_date(date_string):
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. Expected YYYY-MM-DD.")
    
class DateToStringField(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d') if value else None

def choice_type(choices):
    def choice(arg):
        if arg not in choices:
            raise ValueError(f"Value {arg} is not in the allowed choices: {choices}")
        return arg
    return choice

allowed_units = ["Kilograms","Liters","Gallon","Grams","Millilitter","Ounce","Piece","Others/NA"]




# Now, below we will provide the necessary dictionaries to map fields of the respective items for serialisation
user_resource_fields = {
    'id': fields.Integer(attribute='id'),
    'username': fields.String,
    'email' : fields.String,
    'role' : fields.String
}


categories_resource_fields = {
    'id': fields.Integer,
    'name' : fields.String,
    'description': fields.String
}

admin_settings_fields = {
    'report_format':fields.String
}

products_resource_fields = {
    'id': fields.Integer,
    'name' : fields.String,
    'manufacture_date': DateToStringField,
    'expiry_date': DateToStringField,
    'price' : fields.Float,
    'quantity_available' : fields.Integer,
    'unit' : fields.String,
    'description': fields.String,
    'category_product': fields.Integer,
    'created_by' : fields.Integer
}

categories_request_fields = {
    'id': fields.Integer,
    'action':fields.String,
    'name':fields.String,
    'description':fields.String,
    'selectedCategory':fields.Integer,
    'reason':fields.String
}

cart_item_fields = {
    'id': fields.Integer,
    'cart_id':fields.Integer,
    'product_id':fields.Integer,
    'quantity':fields.Integer,
    'price':fields.Integer
}

discount_fields = {
    'discount': fields.Integer
}

order_item_fields = {
    'product_name': fields.String(attribute=lambda x: x.product.name),
    'price_at_purchase': fields.Float,
    'quantity': fields.Integer,
    'total': fields.Float(attribute=lambda x: x.price_at_purchase * x.quantity)
}

order_fields = {
    'order_id': fields.Integer(attribute='id'),
    'user_id': fields.Integer,
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'grand_total': fields.Float,
    'order_items': fields.Nested(order_item_fields, attribute='items', default=[])
}

# A default/dummy dictionary
user = {
    "username":"Enter your UserName Here",
    "email":"Enter your Email Here"
}

user_roles_fields = {
    'roles': fields.List(fields.String),
}


# Now, in the next stage we will list of the resources to handle data required from our respective databases, according to their usecase

# Get the user role
class UserRoleResource(Resource):
    @auth_required('token')
    def get(self, user_id):
        # Ensure that the logged-in user is the one making the request
        if current_user.id != user_id:
            return {'error': 'Unauthorized'}, 401

        # Fetch the user roles
        user = user_model.query.get(user_id)
        if user:
            roles = [role.name for role in user.roles]
            response = {'roles': roles}
            return marshal(response, user_roles_fields), 200
        else:
            return {'error': 'User not found'}, 404

# Resource class to handle individual user data
class User(Resource):
    
    @auth_required('token')
    def get(self,id = None):
        if id == current_user.id:
            user_data = marshal(current_user,user_resource_fields)
            user_data['role'] = current_user.roles[0].name if current_user.roles else None
            return user_data
        else:
            abort(400,message = "Not authorized to access this resource!")     
        return user
    
# Resource class to handle current user data
class User_Details(Resource):
    @auth_required('token')
    def get(self):
        return marshal(current_user, user_resource_fields)
   
# Resource class to handle the inactive users, typically store managers waiting for their accounts to be approved
class Inactive_Users(Resource):
    @auth_required('token')
    def is_admin(self,user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
        return user.has_role('Admin')
    
    @auth_required('token')
    def get(self):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only admins can view inactive users."}, 403
        
    
        inactive_users = user_model.query.filter_by(active=False).all()
        return marshal(inactive_users, user_resource_fields)
   
# Resource for the modification of the above inactive users, with the admin having the option to approve or deny a request
class Modify_Inactive_Users(Resource):
    @auth_required('token')
    def is_admin(self,user):
        return user.has_role('Admin')

    
    @auth_required('token')
    def put(self,user_id):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only admins can approve inactive users status."}, 403
    
        user = user_model.query.get_or_404(user_id)
        user.active = True
        db.session.commit()
        

        return {"message": f"User {user.username} has been approved."}, 200
    
    @auth_required('token')
    def delete(self, user_id): 
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only admins can decline inactive users."}, 403

        user = user_model.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        

        return {"message": f"User {user.username} has been declined and removed."}, 200

#----CATEGORY-----#
# Resource for the Admin to create a new category
class Category_Create_Resource(Resource):
    
    def is_admin(self,user):
        return user.has_role('Admin')
    
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Category name cannot be empty")
    parser.add_argument('description', type=str, help="Category description")

    @auth_required('token')
    
    def post(self):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only admins can create categories."}, 403
        
        data = Category_Create_Resource.parser.parse_args()

        # Check if category already exists
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            return {"message": "Category with name '{}' already exists.".format(data['name'])}, 400

        category = Category(name=data['name'], description=data['description'])
        db.session.add(category)
        db.session.commit()

        return {"message": "Category created successfully.", "id": category.id}, 201

# Resource for the admin to view the category, along with the option to edit and/or delete a pre existing category
class Category_View_Resource(Resource):
    @auth_required('token')
    def get(self):
        categories = Category.query.all()
        return marshal(categories,categories_resource_fields)
    
# Resource for the admin to edit a pre existing category
class Category_Modify_Resource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Category name cannot be empty")
    parser.add_argument('description', type=str, help="Category description")
    
    def is_admin(self,user):
        return user.has_role('Admin')

    @auth_required('token')
    def get(self,category_id):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only admins can edit categories."}
        category = Category.query.get_or_404(category_id)
        return marshal(category,categories_resource_fields)
    
    @auth_required('token')
    def put(self, category_id):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only admins can edit categories."}, 403
        
        data = Category_Modify_Resource.parser.parse_args()
        category = Category.query.get_or_404(category_id)
        
        category.name = data['name']
        category.description = data['description']

        db.session.commit()
        

        return {"message": "Category updated successfully.", "id": category.id}, 201

# Resource for the admin to delete a pre existing category
class Category_Deletion_Resource(Resource):    
    def is_admin(self,user):
        return user.has_role('Admin')

    @auth_required('token')
    def get(self,category_id):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only admins can delete categories."}
        category = Category.query.get_or_404(category_id)
        return marshal(category,categories_resource_fields)
    
    @auth_required('token')
    def delete(self,category_id):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only admins can delete categories."}
        
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        

        return {"message": "Category deleted successfully."}, 200
  
# Resource for the admin to view/modify report settings    
class AdminSettings(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('format', type=str, required=True, help='Report format is required')
    
    def is_admin(self,user):
        return user.has_role('Admin')
    
    @auth_required('token')
    def get(self):
        if not self.is_admin(current_user):
            return {"message": "Access denied. Only admins can view their settings."}
        
        with open(admin_settings_file, 'r') as f:
            admin_settings = json.load(f)
        
        return marshal(admin_settings,admin_settings_fields)
    
    @auth_required('token')
    def post(self):
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only admins can change their settings."}
        
        data = AdminSettings.parser.parse_args()
        new_format = data['format']
        
        with open(admin_settings_file, 'r') as f:
            admin_settings = json.load(f)

        admin_settings['report_format'] = new_format

        with open(admin_settings_file, 'w') as f:
            json.dump(admin_settings, f, indent=4)

        return {'message': 'Admin settings updated successfully'}
    
#----PRODUCT-----#
# Resource for the Store Manager to create a new Product
class Product_Create_Resource(Resource):
    def is_manager(self,user):
        return user.has_role('Store Manager')
    
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Product name cannot be empty")
    parser.add_argument('manufacture_date',required=False,type=parse_date,help = "Date argument must be in YYYY-MM-DD format")
    parser.add_argument('expiry_date',type=parse_date,help = "Date argument must be in YYYY-MM-DD format")
    parser.add_argument('price',type=float,required=True,help = "Price of the product cannot be empty")
    parser.add_argument('quantity_available',type=float,required=True,help = "Quantity of the product cannot be empty")
    parser.add_argument('unit', type=choice_type(allowed_units), help="Unit must be one of: %s" % ', '.join(allowed_units))
    parser.add_argument('description', type=str, help="Product description")
    parser.add_argument('category_id', type=int, required=True, help="Category ID cannot be empty")
    parser.add_argument('created_by',type=int,required=False,help="User by which the product is created")


    @auth_required('token')
    
    def post(self):
        if not self.is_manager(current_user): # Note that here, we have also added only the store managers to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only store managers can create products."}, 403
        
        data = Product_Create_Resource.parser.parse_args()
        
        
        if not data['unit'] or not data['category_id']:
            return {"message": "Kindly enter the unit of the product from the given options"}, 400
        
        elif not data['category_id']:
            return {"message": "Kindly enter the category of the  product from the given options"}, 400
        
        elif data['expiry_date']<datetime.now().date():
            return {"message": "Kindly enter the expiry date which is after today."}, 400
        
    
        product = Product(name=data['name'],manufacture_date = data['manufacture_date'],expiry_date = data['expiry_date'],price = data['price'],quantity_available = data['quantity_available'],unit=data['unit'],description = data['description'],category_product = data['category_id'],created_by=current_user.id)
        db.session.add(product)
        db.session.commit()

        return {"message": "Product created successfully.", "id": product.id}, 201

# Resource for the store manager to view all the products, along with the option to edit and/or delete a pre existing category
class Product_View_Resource(Resource):
    def is_manager(self,user):
        return user.has_role('Store Manager')
    
    @auth_required('token')
    def get(self):
        if not self.is_manager(current_user): # Note that here, we have also added only the store managers to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only store managers can view products."}, 403
        products = Product.query.filter_by(created_by=current_user.id).all()
        return marshal(products,products_resource_fields)
    
# Resource for the store manager to edit a pre existing product
class Product_Modify_Resource(Resource):
    def is_manager(self,user):
        return user.has_role('Store Manager')
    
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="Product name cannot be empty")
    parser.add_argument('manufacture_date',type=parse_date,help = "Date argument must be in YYYY-MM-DD format")
    parser.add_argument('expiry_date',type=parse_date,help = "Date argument must be in YYYY-MM-DD format")
    parser.add_argument('price',type=float,required=True,help = "Price of the product cannot be empty")
    parser.add_argument('quantity_available',type=float,required=True,help = "Quantity of the product cannot be empty")
    parser.add_argument('unit', type=choice_type(allowed_units), help="Unit must be one of: %s" % ', '.join(allowed_units))
    parser.add_argument('description', type=str, help="Product description")
    parser.add_argument('category_product', type=int, required=True, help="Category ID cannot be empty")
    

    @auth_required('token')
    def get(self,product_id):
        if not self.is_manager(current_user): # Note that here, we have also added only the store managers to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only store managers can edit products."}
        product = Product.query.get_or_404(product_id)
        if product.created_by != current_user.id:
            return {"message": "Access denied. You can only view products you created."}, 403
        return marshal(product,products_resource_fields)

    
    @auth_required('token')
    def put(self, product_id):
        if not self.is_manager(current_user): # Note that here, we have also added only the store managers to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only store manager can edit products."}, 403
        
        data = Product_Modify_Resource.parser.parse_args()
        product = Product.query.get_or_404(product_id)
        if product.created_by != current_user.id:
            return {"message": "Access denied. You can only view products you created."}, 403
        
        expiry_date = data['expiry_date']
        if expiry_date and expiry_date <= datetime.now().date():
            return {"message": "Expiry date must be greater than today."}, 400
        
        product.name=data['name']
        product.manufacture_date = data['manufacture_date']
        product.expiry_date = data['expiry_date']
        product.price = data['price']
        product.quantity_available = data['quantity_available']
        product.unit=data['unit']
        product.description = data['description']
        product.category_product = data['category_product']
        

        db.session.commit()

        return {"message": "Product updated successfully.", "id": product.id}, 201

# Resource for the store manager to delete a pre existing product
class Product_Deletion_Resource(Resource):   
    def is_manager(self,user):
        return user.has_role('Store Manager') 
    

    @auth_required('token')
    def get(self,product_id):
        if not self.is_manager(current_user): # Note that here, we have also added only the store managers to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only store managers can view products."}
        product = Product.query.get_or_404(product_id)
        if product.created_by != current_user.id:
            return {"message": "Access denied. You can only view products you created."}, 403
        return marshal(product,products_resource_fields)
    
    @auth_required('token')
    def delete(self,product_id):
        if not self.is_manager(current_user): # Note that here, we have also added only the store managers to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only store managers can delete products."}
        product = Product.query.get_or_404(product_id)
        if product.created_by != current_user.id:
            return {"message": "Access denied. You can only delete the products you created."}, 403
        db.session.delete(product)
        db.session.commit()

        return {"message": "Product deleted successfully."}, 200

#----CATEGORY_REQUEST-----#
#Resource to store a category request in the database
class CategoryRequestResource(Resource):
    def is_manager(self,user):
        return user.has_role('Store Manager') 
    
    parser = reqparse.RequestParser()
    parser.add_argument('action', type=str, required=True, help="The action name cannot be empty")
    parser.add_argument('name', type=str, help="Category name defined by you cannot be empty")
    parser.add_argument('description', type=str, help="Category description defined by you cannot be empty")
    parser.add_argument('selectedCategory', type=int, help="Selected Category to perform an operation on cannot be empty")
    parser.add_argument('reason', type=str, required = True,help="Reason by the user cannot be empty")

    @auth_required('token')
    def post(self):
        if not self.is_manager(current_user): # Note that here, we have also added only the admin to access these endpoints, as defiend in our business logic
            return {"message":"Access denied. Only store managers can add a new request."}
        
        data = CategoryRequestResource.parser.parse_args()
        
        category_request = CategoryRequest(
            action=data['action'],
            name=data['name'],
            description=data['description'],
            selectedCategory=data['selectedCategory'],
            reason=data['reason']
        )
        db.session.add(category_request)
        db.session.commit()
        return {"message": "Request added successfully!"}, 200

#Resource to view all category requests from the database
class AllCategoryRequestsResource(Resource):
    def is_admin(self, user):
        return user.has_role('Admin')
    
    @auth_required('token')
    def get(self):
        if not self.is_admin(current_user):
            return {"message": "Access denied. Only admins can view all category requests."}, 403
        
        all_requests = CategoryRequest.query.all()
       
        return marshal(all_requests,categories_request_fields)

api.add_resource(AllCategoryRequestsResource, '/api/all_category_requests', endpoint="all_category_requests")


#Resource to approve a category request of adding a new category
class CategoryRequestAdmitResource(Resource):
    def is_admin(self,user):
        return user.has_role('Admin')
    
    @auth_required('token')
    def put(self, category_request_id): #In case the admin accepts this request, then we add the category
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only admins can view inactive users."}, 403
        
        category_request = CategoryRequest.query.get_or_404(category_request_id)
        new_category = Category(name=category_request.name, description=category_request.description)
        db.session.add(new_category)
        db.session.delete(category_request)
        db.session.commit()
        return {"message": "Request approved!"}, 200

#Resource to approve a category request of editing a pre existing category
class CategoryRequestAdmitEditResource(Resource):
    def is_admin(self, user):
        return user.has_role('Admin')
    
    @auth_required('token')
    def put(self, category_request_id,category_id): 
        if not self.is_admin(current_user):
            return {"message": "Access denied. Only admins can edit categories."}, 403
        
        category_request = CategoryRequest.query.get_or_404(category_request_id)
        category = Category.query.get_or_404(category_id)
        
        if category:
            category.name = category_request.name
            category.description = category_request.description
            db.session.delete(category_request)
            db.session.commit()
            return {"message": "Category updated successfully as per request."}, 201
              
        else:
            return {"message": "Category not found."}, 404

#Resource to approve a category request of deleting a pre existing category
class CategoryRequestAdmitDeleteResource(Resource):    
    def is_admin(self, user):
        return user.has_role('Admin')
    
    @auth_required('token')
    def delete(self, category_request_id,category_id):
        if not self.is_admin(current_user): 
            return {"message":"Access denied. Only admins can delete categories."}
        
        category_request = CategoryRequest.query.get_or_404(category_request_id)
        print("Selected Category ID from request:", category_request.selectedCategory)
        
        category = Category.query.get_or_404(category_id)
        
        if category:
            db.session.delete(category)
            db.session.delete(category_request)
            db.session.commit()
            return {"message": "Category deleted successfully as per request."}, 200
        else:
            return {"message": "Category not found."}, 404
        
 
#Resource to deny the category request 
class CategoryRequestDenyResource(Resource):
    def is_admin(self,user):
        return user.has_role('Admin')

    @auth_required('token')
    def delete(self, category_request_id): #In case the admin denies this request
        if not self.is_admin(current_user): # Note that here, we have also added only the admins to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only admins can view inactive users."}, 403
        
        category_request = CategoryRequest.query.get_or_404(category_request_id)
        db.session.delete(category_request)
        db.session.commit()
        return {"message": "Request denied!"}, 200

#----PRODUCT_USER-----#
# Resource to fetch all products and for the user
class Product_View_User_Resource(Resource):
    def is_user(self,user):
        return user.has_role('User')
    
    @auth_required('token')
    def get(self):
        if not self.is_user(current_user): # Note that here, we have also added only the users to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only users can view products in this mode."}, 403
        products = Product.query.all()
        return marshal(products,products_resource_fields)
  

# Resource to fetch all products as per the filters given by the user
class FilteredProductsResource(Resource):
    def is_user(self,user):
        return user.has_role('User')
    
    parser = reqparse.RequestParser()
    parser.add_argument('min_price', type=float, required=False)
    parser.add_argument('max_price', type=float, required=False)
    parser.add_argument('min_manufacture_date', required=False)
    parser.add_argument('max_manufacture_date', required=False)
    parser.add_argument('min_expiry_date', required=False)
    parser.add_argument('max_expiry_date', required=False)
    parser.add_argument('category_id', type=int, required=False)


    @auth_required('token')
    def post(self):
        if not self.is_user(current_user): # Note that here, we have also added only the users to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only users can view products in this mode."}, 403
        
        args = FilteredProductsResource.parser.parse_args()

        filtered_products = Product.query

        if args.min_price:
            filtered_products = filtered_products.filter(Product.price >= args.min_price)
        if args.max_price:
            filtered_products = filtered_products.filter(Product.price <= args.max_price)
        if args.min_manufacture_date:
            filtered_products = filtered_products.filter(Product.manufacture_date >= args.min_manufacture_date)
        if args.max_manufacture_date:
            filtered_products = filtered_products.filter(Product.manufacture_date <= args.max_manufacture_date)
        if args.min_expiry_date:
            filtered_products = filtered_products.filter(Product.expiry_date >= args.min_expiry_date)
        if args.max_expiry_date:
            filtered_products = filtered_products.filter(Product.expiry_date <= args.max_expiry_date)
        if args.category_id:
            filtered_products = filtered_products.filter(Product.category_product == args.category_id)

        # Fetching the results
        all_filtered_products = filtered_products.all()


        return marshal(all_filtered_products,products_resource_fields)

# Resource to clear all filters and return all products in our database.
class ClearFiltersResource(Resource):
    def is_user(self,user):
        return user.has_role('User')
    
    @auth_required('token')
    def get(self):
        if not self.is_user(current_user): # Note that here, we have also added only the users to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only users can view products in this mode."}, 403
        all_filtered_products = Product.query.all()
        return marshal(all_filtered_products,products_resource_fields)

# Resource to perform string search on the name of the product and fetch matches
class ProductSearchResource(Resource):
    def is_user(self,user):
        return user.has_role('User')
    
    
    parser = reqparse.RequestParser()
    parser.add_argument('search', type=str, location='args', default='')
        
    @auth_required('token')
    def get(self):
        if not self.is_user(current_user): # Note that here, we have also added only the users to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only users can view products in this mode."}, 403
        
        args = ProductSearchResource.parser.parse_args()
        search = args['search']
        
        if search:
            products = Product.query.filter(Product.name.like(f'%{search}%')).all()
        else:
            products = Product.query.all()
        
        return marshal(products, products_resource_fields)


#----CART_FUNCTIONALITY-----#
# Resource to view all the products
class CartViewResource(Resource):    
    def is_user(self,user):
        return user.has_role('User')

    @auth_required('token')
    def get(self,user_id):
        if not self.is_user(current_user): # Note that here, we have also added only the users to access these endpoints, as defiend in our business logic
            return {"message": "Access denied. Only users can view products in this mode."}, 403
        
    
        cart = Cart.query.filter_by(user_id=user_id).first()
        
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()

        items = CartItem.query.filter_by(cart_id=cart.id).all()
        
        return marshal(items, cart_item_fields)
    

# Resource to add a product to the cart
class AddToCartItemResource(Resource):
    def is_user(self, user):
        return user.has_role('User')
    
    
    parser = reqparse.RequestParser()
    parser.add_argument('product_id', type=int,required=True, help="Product ID")
    parser.add_argument('quantity', type=int, default= 1 ,required=True, help="Quantity cannot be blank!")
    parser.add_argument('price', type=float, required=True, help="Product price cannot be blank!")
    
    @auth_required('token')
    def post(self):
        if not self.is_user(current_user):
            return {"message": "Access denied. Only users can add products to cart."}, 403

        data = AddToCartItemResource.parser.parse_args()

        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
            
        product = Product.query.get(data['product_id'])
        if not product:
            return {"message": "Product not found."}, 404
            
        if data['quantity'] > product.quantity_available:
            return {"message": "Requested quantity exceeds available stock."}, 400


        cart_item = CartItem(cart_id=cart.id, product_id=data['product_id'], quantity=data['quantity'], price=data['price'])
        db.session.add(cart_item)
        db.session.commit()
        
        
        return {"message": "Product added to cart successfully."}, 200

# Resource to check the percentage of the discount
class DiscountFinder(Resource):
    def is_user(self, user):
        return user.has_role('User')
    
    parser = reqparse.RequestParser()
    parser.add_argument('discount_code', type=str, required=True, help="Discount code is required.")

    @auth_required('token')
    def get(self, user_id):
        discount_code = request.args.get('discount_code')

        if not self.is_user(current_user):
            return {"message": "Access denied."}, 403

        if discount_code != 'WELCOME10':
            return {"message": "Invalid discount code."}, 400

        if not Order.query.filter_by(user_id=user_id).first(): 
            return {'discount':10},200
        
        return {'discount':0},200 

# Resource to add the functionality to edit the cart items
class EditCartItemResource(Resource):
    def is_user(self, user):
        return user.has_role('User')
    

    parser = reqparse.RequestParser()
    parser.add_argument('cart_item_id', type=int,required=True, help="Cart Item ID")
    parser.add_argument('product_id', type=int,required=True, help="Product ID")
    parser.add_argument('quantity', type=int, required=True, help="Quantity cannot be blank!")

    @auth_required('token')
    def put(self):
        if not self.is_user(current_user):
            return {"message": "Access denied. Only users can edit items in the cart."}, 403
        
        data = EditCartItemResource.parser.parse_args()

        item = CartItem.query.get(data['cart_item_id'])
        if not item:
            return {"message": "Item not found."}, 404
        
        product = Product.query.get(data['product_id'])
        if not product:
            return {"message": "Product not found."}, 404
            
        if data['quantity'] > product.quantity_available:
            return {"message": "Requested quantity exceeds available stock."}, 400
        
        
        item.quantity = data['quantity']
        db.session.commit()
        

        return {"message": "Cart item updated successfully."}, 200
    

# Resource to delete an item from the cart
class DeleteCartItemResource(Resource):
    def is_user(self, user):
        return user.has_role('User')
  

    @auth_required('token')
    def delete(self, item_id):
        if not self.is_user(current_user):
            return {"message": "Access denied. Only users can delete items from the cart."}, 403

        item = CartItem.query.get(item_id)
        if not item:
            return {"message": "Item not found."}, 404

        db.session.delete(item)
        db.session.commit()
        

        return {"message": "Cart item deleted successfully."}, 200
    
#----BUY_FUNCTIONALITY-----#
# Resource to buy all products in our cart and create an order.
class BuyNowResource(Resource):
    def is_user(self, user):
        return user.has_role('User')

    parser = reqparse.RequestParser()
    parser.add_argument('totalAmount', type=float, required=True, help="Total amount after discount is required.")
    parser.add_argument('items', type=list, location='json', required=True, help="Items in cart are required.")

    @auth_required('token')
    def post(self):
        if not self.is_user(current_user):
            return {"message": "Access denied. Only users can delete items from the cart."}, 403
        
        data = BuyNowResource.parser.parse_args()

        cart_items = data['items']
        if not cart_items:
            return {"message": "No items in cart."}, 400

        order = Order(user_id=current_user.id, timestamp=datetime.utcnow(), grand_total=data['totalAmount'])
        db.session.add(order)

        for item in cart_items:
            product = Product.query.get(item['product_id'])
            if product.quantity_available >= item['quantity']:
                product.quantity_available -= item['quantity']
                if product.quantity_available < 0:
                    product.quantity_available = 0

            order_item = OrderItem(order=order, product_id=item['product_id'], quantity=item['quantity'], price_at_purchase=item['price'])
            db.session.add(order_item)
            cart_item_to_delete = CartItem.query.get(item['id'])
            db.session.delete(cart_item_to_delete)


        db.session.commit()
        
        remaining_items = CartItem.query.filter_by(cart_id=current_user.id).all()
        
        if(len(remaining_items)==0):
            print(f"Remaining items: {remaining_items}")
            
        
        return {"message": "Order placed successfully.", "order_id": order.id}, 200
  
#----ORDER_FUNCTIONALITY-----#
# Resource to view the product
class LatestOrderResource(Resource):
    def is_user(self, user):
        return user.has_role('User')

    @auth_required('token')
    def get(self, user_id):
        if not self.is_user(current_user):
            return {"message": "Access denied. Only users can delete items from the cart."}, 403
        
        order = Order.query.filter_by(user_id=user_id).order_by(Order.timestamp.desc()).first()
        
        if not order:
            return {"message": "No orders found."}, 404
        
        return marshal(order, order_fields), 200

# Resource to View all Orders
class AllOrdersViewResource(Resource):
    def is_user(self, user):
        return user.has_role('User')
    
    @auth_required('token')
    def get(self,user_id):
        if not self.is_user(current_user):
            return {"message": "Access denied. Only users can delete items from the cart."}, 403
        
        user_orders = Order.query.filter_by(user_id=user_id).all()
        return marshal(user_orders,order_fields)


      
# In the end, we will add all these resources to register the API Endpoints, after which they can be used to perform the above actions
api.add_resource(UserRoleResource, '/user/<int:user_id>/roles')
api.add_resource(User,'/users/<int:id>')
api.add_resource(User_Details,'/user_details')
api.add_resource(Inactive_Users, '/inactive_users')
api.add_resource(Modify_Inactive_Users, '/modify_inactive_users/<int:user_id>')

api.add_resource(Category_Create_Resource, '/create_category')
api.add_resource(Category_View_Resource,'/view_categories')
api.add_resource(Category_Modify_Resource, '/edit_category/<int:category_id>')
api.add_resource(Category_Deletion_Resource,'/delete_category/<int:category_id>')
api.add_resource(AdminSettings, '/update_report_format',endpoint = "report_format_update")

api.add_resource(Product_Create_Resource,'/create_product')
api.add_resource(Product_View_Resource,'/view_products')
api.add_resource(Product_Modify_Resource,'/edit_product/<int:product_id>')
api.add_resource(Product_Deletion_Resource,'/delete_product/<int:product_id>')

api.add_resource(CategoryRequestResource, '/category_requests', endpoint="category_requests")
api.add_resource(AllCategoryRequestsResource,'/all_category_requests',endpoint="get_all_category_requests")
api.add_resource(CategoryRequestAdmitResource, '/category_requests/admit/<int:category_request_id>', endpoint="category_requests_admit")
api.add_resource(CategoryRequestAdmitEditResource, '/category_requests/admit/edit/<int:category_request_id>/<int:category_id>', endpoint="category_requests_admit_edit")
api.add_resource(CategoryRequestAdmitDeleteResource, '/category_requests/admit/delete/<int:category_request_id>/<int:category_id>', endpoint="category_requests_admit_delete")
api.add_resource(CategoryRequestDenyResource, '/category_requests/deny/<int:category_request_id>', endpoint="category_requests_deny")

api.add_resource(Product_View_User_Resource,'/view_products_user')
api.add_resource(FilteredProductsResource,'/filtered_products')
api.add_resource(ClearFiltersResource, '/clear_filters')
api.add_resource(ProductSearchResource, '/products_search')

api.add_resource(CartViewResource,'/cart_view/<int:user_id>')
api.add_resource(AddToCartItemResource, '/add_product_to_cart')
api.add_resource(DiscountFinder,'/check_discount/<int:user_id>')
api.add_resource(EditCartItemResource, '/edit_item/')
api.add_resource(DeleteCartItemResource, '/delete_item/<int:item_id>')

api.add_resource(BuyNowResource, '/buy_now')
api.add_resource(LatestOrderResource, '/get_latest_order/<int:user_id>')
api.add_resource(AllOrdersViewResource,'/my_orders/<int:user_id>')






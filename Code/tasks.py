import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


from models import Order,User,OrderItem,Product,Category,roles_users
from jinja2 import Template
import os

script_directory = os.path.dirname(os.path.realpath(__file__))
relative_path = 'data/admin_settings.json'
admin_settings = os.path.join(script_directory, relative_path)

from datetime import datetime as date, timedelta
import json
import os
from sqlalchemy import func,text
import plotly.graph_objs as go
from plotly.offline import plot
import plotly.io as pio
import base64
from weasyprint import HTML

import csv
from io import StringIO


from app import celery,db,app
from cache_config import initialize_cache
from celery.schedules import crontab

    
SMTP_SERVER_HOST = "localhost"
SMTP_SERVER_PORT = 1025
Sender_Mail_ID = "dpamneja@gmail.com"
Sender_Password = ""


def load_template(template_name):
    template_path = f"templates/{template_name}.html"
    with open(template_path, 'r') as template_file:
        return template_file.read()

def send_email(message, Subject, Receivers):    
    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(Sender_Mail_ID, Sender_Password)
    
    for receiver in Receivers:
        msg = MIMEMultipart()
        msg['From'] = Sender_Mail_ID
        msg['To'] = receiver
        msg['Subject'] = Subject
        
        msg.attach(MIMEText(message, 'html')) 
        s.send_message(msg)
        
    s.quit()

    return True

def send_attachement_email(message, Subject, Receiver,attachment_file = None):
    msg = MIMEMultipart()
    msg['From'] = Sender_Mail_ID
    msg['To'] = Receiver
    msg['Subject'] = Subject
    
    msg.attach(MIMEText(message, 'html'))
        
        
    if attachment_file:
        if isinstance(attachment_file, StringIO):
            attachment_data = attachment_file.getvalue()
            attachment_filename = "attachment.csv"
        else:
            with open(attachment_file, "rb") as attachment:
                attachment_data = attachment.read()
                attachment_filename = os.path.basename(attachment_file)
                
        part = MIMEBase("application","octet-stream")
        part.set_payload(attachment_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
        msg.attach(part)
        
        
        
    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(Sender_Mail_ID, Sender_Password)    
    
    s.send_message(msg)
        
    s.quit()

    return True


cache = initialize_cache(app)
@celery.task(name='daily_reminder')
@cache.memoize(timeout=100)
def daily_reminder():
    current_time = date.now()
    time_window = current_time - timedelta(hours=24)

    orders = Order.query.filter(Order.timestamp<=time_window).all()

    user_ids = [order.user_id for order in orders]
    unique_user_ids = set(user_ids)
    
    users_list = []
    
    users = User.query.filter(User.id.in_(unique_user_ids)).all()
    users_list = [user.email for user in users]
    print(users_list)
    
    reminder_text = load_template('daily_reminder')

    send_email(reminder_text, "Buy your household groceries from us",users_list)

    return 'Daily Reminder sent'

# Fetch the latest settings as defined by the admin
with open(admin_settings, 'r') as f:
            admin_settings = json.load(f)
            
admin_settings_format = admin_settings['report_format']

@celery.task(name='monthly_report')
def monthly_report(report_format="html"):
    users = User.query.join(roles_users).filter(text("roles_users.role_id = 3")).all()
    user_data = {}
    
    today = date.now()
    today_report = date.now().strftime('%Y-%m-%d')
    last_month = today - timedelta(days=30)
    
    main_template = load_template('PDF_report')
    template = Template(main_template)
    
    mega_report = template.render(today_report=today_report)
    

    for user in users:
        # Fetching product wise sales for the specific user
        product_sales = db.session.query(Product.name, func.sum(OrderItem.quantity)) \
            .join(OrderItem) \
            .join(Order) \
            .filter(Order.user_id == user.id) \
            .filter(Order.timestamp >= last_month).group_by(Product.name) \
            .all()

        # Fetching category wise revenues for the specific user
        category_revenues = db.session.query(Category.name, func.sum(Product.price * OrderItem.quantity)) \
            .join(Product) \
            .join(OrderItem) \
            .join(Order) \
            .filter(Order.user_id == user.id) \
            .filter(Order.timestamp >= last_month).group_by(Category.name) \
            .all()

        # Calculate total spending for the user
        total_spent = db.session.query(func.sum(Order.grand_total)).filter(Order.user_id == user.id).scalar()

        # Calculate average spending for the user
        num_orders = db.session.query(func.count(Order.id)).filter(Order.user_id == user.id).scalar()
        average_spent = total_spent / num_orders if num_orders > 0 else 0

        # Organizing user-specific data into the user dictionary
        user_data[user.id] = {
            "product_sales": product_sales,
            "category_revenues": category_revenues,
            "total_spent": total_spent,
            "average_spent": average_spent
        }
        
        product_sales_data = user_data[user.id]['product_sales']
        product_names = [product[0] for product in product_sales_data]
        sales_counts = [product[1] for product in product_sales_data]

        category_revenues_data = user_data[user.id]['category_revenues']
        category_names = [category[0] for category in category_revenues_data]
        revenues = [category[1] for category in category_revenues_data]
        
        order_timestamps = db.session.query(Order.timestamp).filter(Order.user_id == user.id).filter(Order.timestamp >= last_month).all()
        order_timestamps = [ts[0] for ts in order_timestamps] 
        order_timestamps.sort()
        order_counts = [i + 1 for i in range(len(order_timestamps))]


    
        #Pie Chart
        layout_pie = go.Layout(title='Most Brought Products')
        pie = go.Figure(data=[go.Pie(labels=product_names, values=sales_counts)],layout=layout_pie)
        pie_div = plot(pie, output_type='div')

        #Bar Chart
        layout_bar = go.Layout(title='Category Revenue')
        bar = go.Figure(data=[go.Bar(x=category_names, y=revenues)],layout=layout_bar)
        bar_div = plot(bar, output_type='div')
        
        #Line Time Series Chart
        layout_purchase_frequency = go.Layout(title='Purchase Frequency Over Time', xaxis=dict(title='Time'), yaxis=dict(title='Purchase Frequency'))
        purchase_frequency = go.Figure(data=[go.Scatter(x=order_timestamps, y=order_counts, mode='lines+markers')], layout=layout_purchase_frequency)
        time_series_div = plot(purchase_frequency, output_type='div')
        
        if report_format == "pdf":
            pie_image = pio.to_image(pie, format="png")
            pie_image_base64 = base64.b64encode(pie_image).decode("utf-8")
            
            bar_image = pio.to_image(bar, format="png")
            bar_image_base64 = base64.b64encode(bar_image).decode("utf-8")
            
            line_image = pio.to_image(purchase_frequency,format="png")
            line_image_base64 = base64.b64encode(line_image).decode("utf-8")
        
        user_report = f"""
            <h2>User Activity Report for {user.username}</h2>
            
            <div class="spending-table">
                <h2>Spending Insights</h2>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Total Spent</th>
                            <th>Average Spent</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{ total_spent }</td>
                            <td>{ average_spent }</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="graph-container">
                {'<img src="data:image/png;base64,' + pie_image_base64 + '">' if report_format == "pdf" else pie_div} <!-- Embed base64 image if PDF -->
            </div>
            
            <div class="graph-container">
                {'<img src="data:image/png;base64,' + bar_image_base64 + '">' if report_format == "pdf" else bar_div} <!-- Embed base64 image if PDF -->
            </div>
            
            <div class="graph-container">
                {'<img src="data:image/png;base64,' + line_image_base64 + '">' if report_format == "pdf" else time_series_div} <!-- Embed base64 image if PDF -->
            </div>
        """
        
        mega_report += user_report + '<hr>'
    
    if report_format == "pdf":
        html = HTML(string=mega_report)
        pdf = html.write_pdf()
        
        month_year = today.strftime('%b%y')
        output_directory = 'static/analysis'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        pdf_file_name = f'EBazaar_Monthly_Report-{month_year}.pdf'

        pdf_file_path = os.path.join(output_directory, pdf_file_name)

        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(pdf)
            
        pdf_welcome_mail = load_template("PDF_mail")

        send_attachement_email(pdf_welcome_mail, "Monthly Report for Users", "dpamneja@gmail.com", pdf_file_path)
    else:
        send_attachement_email(mega_report, "Monthly Report for Users", "dpamneja@gmail.com")

    
    return True
    

@celery.task(name='product_csv')
@cache.memoize(timeout=100)
def generate_csv(user_id,user_email):
    products = db.session.query(Product.name, func.strftime('%d-%m-%Y',Product.manufacture_date).label('manufacture_date'),func.strftime('%d-%m-%Y',Product.expiry_date).label('expiry_date'),Product.price,Product.unit,Product.quantity_available,Product.description, func.coalesce(func.sum(OrderItem.quantity), 0).label('quantity'),func.coalesce(func.sum(OrderItem.price_at_purchase * OrderItem.quantity), 0).label('total_revenue')).outerjoin(OrderItem, Product.id == OrderItem.product_id).filter(Product.created_by == user_id).group_by(Product.id).all()
    csv_buffer = StringIO()
    csv_headers = ["Name","Manufacture Date","Expiry Date","Price","Unit","Current Quantity Available","Description","Total Quantity Sold","Total Revenue Generated"]
    
    writer = csv.writer(csv_buffer)
    writer = csv.writer(csv_buffer)
    writer.writerow(csv_headers) 

    for product in products:
        writer.writerow(product)
    
    main_template = load_template('product_csv')
    send_attachement_email(main_template, "Product Data File", user_email, csv_buffer)
    
    
    return True
    

    
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):  
    # Schedule the daily reminder to run every day at 5:00 PM
    sender.add_periodic_task(crontab(hour=17, minute=00), daily_reminder.s(), name="Daily Reminder.")
    
    # Schedule the monthly report to run at the first of every month at midnight
    sender.add_periodic_task(crontab(day_of_month=1, hour=0, minute=0), monthly_report.s(admin_settings_format), name="Monthly Report.")
    
    
    
   
    
    
    
    

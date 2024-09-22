import os
import pandas as pd
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Order

def generate_order_excel_for_vendor(vendor):
    # Fetch orders for the given vendor
    orders = Order.objects.filter(vid=vendor)
    
    # Create a DataFrame
    data = {
        'Stock Name': [order.sid.sname for order in orders],
        'Model': [order.Model for order in orders],
        'Quantity': [order.Qty for order in orders],
    }
    df = pd.DataFrame(data)
    
    # Define file path for Windows
    temp_dir = 'C:\\Temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    file_path = os.path.join(temp_dir, f'orders_for_{vendor.Vid}.xlsx')
    
    # Save the DataFrame to an Excel file
    df.to_excel(file_path, index=False)
    
    return file_path

def send_email_with_attachment(subject, message, recipient_list, attachment):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list
    )
    
    # Attach the file
    email.attach_file(attachment)
    
    # Send the email
    email.send()

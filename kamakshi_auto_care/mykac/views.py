from django.shortcuts import render, redirect, get_object_or_404
from .models import Stock, Vendor, Order
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
import pandas as pd
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils import send_email_with_attachment, generate_order_excel_for_vendor

# Create your views here.
def index(request):
    return render(request, "index.html")

def check_stock_qty():
    """Check stock levels and manage orders accordingly."""
    stock_items = Stock.objects.all()

    for stock_item in stock_items:
        if stock_item.Qty < 2:
            # Check if the order already exists
            order_exists = Order.objects.filter(sid=stock_item, vid=stock_item.Vid).exists()

            if not order_exists:
                # If the stock quantity is less than 2 and order doesn't exist, create a new order
                new_order = Order(sid=stock_item, vid=stock_item.Vid, Qty=5,Model=stock_item.Model )  # Default quantity is 5
                new_order.save()

        elif stock_item.Qty >= 2:
            # If stock quantity is 2 or more, remove the respective order
            Order.objects.filter(sid=stock_item, vid=stock_item.Vid).delete()

def stock(request):
    # Call the function to check stock quantities and create orders
    check_stock_qty()

    if request.method == 'POST':
        # Handle adding new stock
        if 'add_stock' in request.POST:
            sname = request.POST['sname']
            model = request.POST['Model']
            price = float(request.POST['price'])
            qty = int(request.POST['Qty'])
            vendor_id = request.POST['vendor_id']
            sprice = price * 1.2  # Automatically calculate selling price
            sprice = round(sprice, 2)

            vendor = get_object_or_404(Vendor, pk=vendor_id)
            new_stock = Stock(sname=sname, Model=model, price=price, sprice=sprice, Qty=qty, Vid=vendor)
            new_stock.save()

        # Handle updating existing stock
        elif 'update_stock' in request.POST:
            sid = request.POST['sid']
            stock_item = get_object_or_404(Stock, pk=sid)
            stock_item.sname = request.POST['sname']
            stock_item.Model = request.POST['Model']
            stock_item.price = float(request.POST['price'])
            stock_item.Qty = int(request.POST['Qty'])
            stock_item.sprice = stock_item.price * 1.2
            stock_item.sprice= round(stock_item.sprice, 2) # Automatically update selling price
            stock_item.Vid = get_object_or_404(Vendor, pk=request.POST['vendor_id'])
            stock_item.save()

        # Handle deleting stock
        elif 'delete_stock' in request.POST:
            sid = request.POST['sid']
            stock_item = get_object_or_404(Stock, pk=sid)
            stock_item.delete()

        return redirect('stock')


    # Fetch all stock items and vendor list
    stock_items = Stock.objects.all().select_related('Vid')
    vendors = Vendor.objects.all()  # Fetch all vendors from the Vendor model
    unique_models = Stock.objects.values_list('Model', flat=True).distinct()

    context = {
        'stock_items': stock_items,
        'vendors': vendors,  # Add vendors to the context
        'unique_models': unique_models,
    }

    return render(request, 'stock.html', context)

@csrf_exempt
def update_stock(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sid = data.get('sid')
        try:
            stock_item = Stock.objects.get(pk=sid)
            stock_item.sname = data.get('sname', stock_item.sname)
            stock_item.Model = data.get('Model', stock_item.Model)
            stock_item.price = data.get('price', stock_item.price)
            stock_item.Qty = data.get('Qty', stock_item.Qty)
            stock_item.save()
            return JsonResponse({'success': True})
        except Stock.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Stock item not found'})
    return JsonResponse({'success': False})

@csrf_exempt
def delete_stock(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sid = data.get('sid')
        try:
            stock_item = Stock.objects.get(pk=sid)
            stock_item.delete()
            return JsonResponse({'success': True})
        except Stock.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Stock item not found'})
    return JsonResponse({'success': False})

def order(request):
    selected_vendor = None
    orders = Order.objects.all().select_related('vid', 'sid')  # Fetch related Stock and Vendor

    # Handle filtering orders by selected vendor
    if request.method == 'GET' and 'vendor_id' in request.GET:
        vendor_id = request.GET.get('vendor_id')
        if vendor_id:
            selected_vendor = get_object_or_404(Vendor, Vid=vendor_id)
            orders = orders.filter(vid=selected_vendor)

    # Fetch all vendors for the filter dropdown
    vendors = Vendor.objects.all()

    context = {
        'orders': orders,
        'vendors': vendors,
        'selected_vendor': selected_vendor,
    }

    return render(request, 'order.html', context)

@csrf_exempt
def send_order_email(request, vendor_id):
    if request.method == 'POST':
        try:
            vendor = get_object_or_404(Vendor, Vid=vendor_id)
            file_path = generate_order_excel_for_vendor(vendor)
            send_email_with_attachment(
                subject='Order Details',
                message='Please find the attached order details for your orders.',
                recipient_list=[vendor.Email],
                attachment=file_path
            )
            return JsonResponse({'success': True, 'message': 'Email sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def update_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            oid = data.get('oid')
            qty = data.get('Qty')
            vid = data.get('vid')

            # Fetch the order
            order = Order.objects.get(oid=oid)

            # Update the quantity and vendor
            if qty:
                order.Qty = qty
            if vid:
                vendor = Vendor.objects.get(Vid=vid)
                order.vid = vendor

            order.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            oid = data.get('oid')

            # Fetch and delete the order
            order = Order.objects.get(oid=oid)
            order.delete()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def generate_order_excel_for_vendor(vendor):
    import pandas as pd
    from io import BytesIO
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile

    # Query orders for the given vendor
    orders = Order.objects.filter(vid=vendor)

    # Create a DataFrame
    df = pd.DataFrame(list(orders.values('sid__sname','Model','Qty',)))

    # Save the DataFrame to an Excel file
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Orders')

    excel_file.seek(0)
    file_name = f'orders_{vendor.pk}.xlsx'
    file_path = default_storage.save(file_name, ContentFile(excel_file.read()))

    return file_path

from django.core.mail import EmailMessage
from django.conf import settings

def send_email_with_attachment(subject, message, recipient_list, attachment):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,  # Use your configured email host user
        to=recipient_list
    )
    
    # Attach the file
    email.attach_file(attachment)
    
    # Send the email
    email.send()



def vendors(request):
    # Handle POST request to add a new vendor
    if request.method == 'POST':
        vname = request.POST.get('vname')
        phno = request.POST.get('phno')
        GSTNo = request.POST.get('GSTNo')
        Email = request.POST.get('Email')
        Address = request.POST.get('Address')

        # Create new vendor and save to the database
        Vendor.objects.create(
            vname=vname,
            phno=phno,
            GSTNo=GSTNo,
            Email=Email,
            Address=Address
        )

        # Redirect to the vendor page after adding the vendor
        return redirect('vendors')

    # Fetch all vendors from the database
    vendors = Vendor.objects.all()

    return render(request, 'vendor.html', {'vendors': vendors})

# View to handle vendor updates (AJAX)
def update_vendor(request, vendor_id):
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        vname = request.POST.get('vname', vendor.vname)
        phno = request.POST.get('phno', vendor.phno)
        GSTNo = request.POST.get('GSTNo', vendor.GSTNo)
        email = request.POST.get('Email', vendor.Email)
        address = request.POST.get('Address', vendor.Address)
        
        # Update the vendor fields
        vendor.vname = vname
        vendor.phno = phno
        vendor.GSTNo = GSTNo
        vendor.Email = email
        vendor.Address = address
        vendor.save()

        return JsonResponse({'status': 'success', 'message': 'Vendor updated successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# View to handle deleting a vendor
def delete_vendor(request, vendor_id):
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        vendor.delete()
        return JsonResponse({'status': 'success', 'message': 'Vendor deleted successfully!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
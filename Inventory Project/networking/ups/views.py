from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render
from .models import SNMP, Manual
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone, formats

from datetime import datetime, timedelta, date
from django.http import JsonResponse
from .models import SNMP, Manual
from django.shortcuts import render
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests

from openpyxl import Workbook
from django.http import FileResponse

last_modified_date = timezone.now()
class CustomLoginView(LoginView):
    template_name = 'login.html'  # Specify the template for the login view
    success_url = reverse_lazy('welcome')  # Specify the URL name for the welcome page

@login_required  # This decorator ensures only authenticated users can access the welcome page
def welcome_view(request):
    return render(request, 'welcome.html')

@login_required
def dashboard(request):
    # Retrieve data from the SNMP and Manual tables
    snmp_data = SNMP.objects.all()
    manual_data = Manual.objects.all()

    # Create a list to store merged data
    merged_data = []

    for snmp_entry in snmp_data:
        matching_manual_entry = manual_data.filter(ip_address=snmp_entry.ip_address).first()
        if matching_manual_entry:
            # If a matching entry is found, create a dictionary with data from both tables
            merged_entry = {
                'ip_address': snmp_entry.ip_address,
                'model': snmp_entry.model,
                'ups_type': snmp_entry.ups_type,
                'battery_capacity': snmp_entry.battery_capacity,
                'building_name': matching_manual_entry.building_name,
                'lan_room': matching_manual_entry.lan_room,
                'battery_installed_date': matching_manual_entry.battery_installed_date,
                'ups_installed_date': matching_manual_entry.ups_installed_date,
                'battery_count': matching_manual_entry.battery_count,
                'management': matching_manual_entry.management,
                'last_modified_user': matching_manual_entry.last_modified_user,
                'last_modified_date': matching_manual_entry.last_modified_date,
                'room_temperature': snmp_entry.room_temperature,
                'battery_type': matching_manual_entry.battery_type,
            }
            merged_data.append(merged_entry)
        else:
            merged_entry = {
                'ip_address': snmp_entry.ip_address,
                'model': snmp_entry.model,
                'ups_type': snmp_entry.ups_type,
                'battery_capacity': snmp_entry.battery_capacity,
                'room_temperature': snmp_entry.room_temperature}
            merged_data.append(merged_entry)

    return render(request, 'dashboard.html', {'data': merged_data})


def update_manual_data(request):
    if request.method == 'POST':
        # Retrieve data from the form
        selected_ip = request.POST.get('selected_ip')  # Updated key to "selected_ip"
        building = request.POST.get('building')
        lan_room = request.POST.get('lanRoom')
        battery_installed_date = request.POST.get('batteryInstalledDate')
        ups_installed_date = request.POST.get('upsInstalledDate')
        battery_count = request.POST.get('batteryCount')
        management = request.POST.get('management')
        battery_type = request.POST.get('batteryType')



        # Check if a Manual entry with the selected IP already exists
        manual_entry = Manual.objects.filter(ip_address=selected_ip).first()

        if manual_entry:
            # Update the existing entry
            manual_entry.building_name = building
            manual_entry.lan_room = lan_room
            manual_entry.battery_installed_date = battery_installed_date
            manual_entry.ups_installed_date = ups_installed_date
            manual_entry.battery_count = battery_count
            manual_entry.management = management
            manual_entry.battery_type = battery_type
            manual_entry.last_modified_user = request.user.username
            manual_entry.last_modified_date = last_modified_date
            manual_entry.save()
        else:
            # Create a new Manual entry
            Manual.objects.create(
                ip_address=selected_ip,
                building_name=building,
                lan_room=lan_room,
                battery_installed_date=battery_installed_date,
                ups_installed_date=ups_installed_date,
                battery_count=battery_count,
                management=management,
                battery_type=battery_type,
                last_modified_date=last_modified_date,
                last_modified_user=request.user.username
            )

        return JsonResponse({'message': 'Data saved successfully'})
    else:
        return JsonResponse({'message': 'Invalid request'})

def get_manual_data(request):
    selected_ip = request.GET.get('ip', None)

    if selected_ip is not None:
        try:
            manual_data = Manual.objects.get(ip_address=selected_ip)
            data = {
                'building_name': manual_data.building_name,
                'lan_room': manual_data.lan_room,
                'battery_installed_date': manual_data.battery_installed_date,
                'ups_installed_date': manual_data.ups_installed_date,
                'battery_count': manual_data.battery_count,
                'management': manual_data.management,
                'battery_type': manual_data.battery_type,
            }
        except Manual.DoesNotExist:
            data = {'exists': False}
    else:
        data = {'exists': False}

    print(data, "from manual table ")  # Add this line to check the data being returned
    return JsonResponse(data)



def get_snmp_ip_addresses(request):
    if request.method == 'GET':
        # Retrieve a list of IP addresses from the SNMP table
        ip_addresses = SNMP.objects.values_list('ip_address', flat=True)
        return JsonResponse(list(ip_addresses), safe=False)
    else:
        return JsonResponse([], safe=False)

def scrape_product_price(url, product_name):
    # Options for headless Firefox
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")

    # Set up the Firefox driver using GeckoDriverManager
    driver = webdriver.Firefox(options=options)

    try:
        # Navigate to the website
        driver.get(url)

        # Wait for the search input to be present and interactable
        wait = WebDriverWait(driver,1)
        search_input = wait.until(EC.element_to_be_clickable((By.ID, "js-site-search-input")))

        # Find the search input and enter the product name
        search_input.send_keys(product_name)

        # Find and click the search button
        search_button = driver.find_element(By.CLASS_NAME, "js_search_button")
        search_button.click()

        # Wait for the search results to load
        product_price = None

        # Check if there is a list of products
        product_list = driver.find_elements(By.CLASS_NAME, "product-listing_product-wrapper")

        if product_list:
            # Use JavaScript to click the first product title link
            first_product_title_link = product_list[0].find_element(By.CSS_SELECTOR,
                                                                    ".product-listing_product-name h3.title a")
            driver.execute_script("arguments[0].click();", first_product_title_link)

            # Dynamically handle the dialog box if it appears
            try:
                dialog_box = driver.find_element(By.ID, "fsrInvite")
                wait.until(EC.element_to_be_clickable((By.ID, "fsrAbandonButton")))
                dialog_close_button = driver.find_element(By.ID, "fsrAbandonButton")
                dialog_close_button.click()
            except:
                pass

            # Extract and print the price from the product details page
            product_price_element = driver.find_element(By.CSS_SELECTOR, ".product-listing_product-exp__price-amount")
            product_price = product_price_element.text.strip()

        else:
            # If there is no product list, extract information from the single product page
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-details")))
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract the product details
            product_details = soup.find("div", class_="product-details")

            if product_details:
                # First attempt: Extract product price from <p> element
                product_price_element = soup.find("p", class_="price")
                product_price = product_price_element.text.strip() if product_price_element else None

                if product_price is None:
                    # Second attempt: Extract product price from <div> element within product details
                    product_price_element = soup.find("div", class_="product-listing_product-exp__price").find("span",
                                                                                                               class_="product-listing_product-exp__price-amount")
                    product_price = product_price_element.text.strip() if product_price_element else None

    except Exception as e:
        # If an error occurs, return the search page URL
        print("Error:", str(e))
        product_price = driver.current_url

    finally:
        # Close the Selenium WebDriver
        driver.quit()

    return product_price
# url = "https://www.graybar.com/"
# product_name = "SYBT5"
# result = scrape_product_price(url, product_name)
# print("Product Price:", result)
expiring_battery_types = []
expiring_ups_types = []
def get_expirations(request):
    if request.method == 'GET':
        selected_year = int(request.GET.get('year'))

        # Fetch data from the database (you may need to modify the query)
        manual_data = Manual.objects.all()
        snmp_data = SNMP.objects.all()

        # Convert querysets to lists of dictionaries
        manual_data = manual_data.values()
        snmp_data = snmp_data.values()

        # Calculate UPS and Battery expirations
        for entry in manual_data:
            ip_address = entry['ip_address']

            # Find the matching SNMP entry based on IP address
            snmp_entry = next((s for s in snmp_data if s['ip_address'] == ip_address), None)

            if snmp_entry:
                entry['ups_installed_date'] = entry['ups_installed_date']  # No need to remove tzinfo

                # Ensure 'ups_expiry_date' is a datetime object
                entry['ups_expiry_date'] = datetime.combine(entry['ups_installed_date'], datetime.min.time()) + timedelta(days=5 * 365)
                entry['ups_remaining_days'] = (entry['ups_expiry_date'] - datetime.now()).days
                entry['ups_type'] = snmp_entry['ups_type']

            # For battery, apply the same changes
            entry['battery_installed_date'] = entry['battery_installed_date']  # No need to remove tzinfo
            entry['battery_expiry_date'] = datetime.combine(entry['battery_installed_date'], datetime.min.time()) + timedelta(days=2 * 365)
            entry['battery_remaining_days'] = (entry['battery_expiry_date'] - datetime.now()).days
        battery_prices =[]
        ups_prices=[]
        # Filter data for UPS and battery that are expiring in the selected year
        expiring_ups = [entry for entry in manual_data if entry['ups_remaining_days'] > 0 and entry['ups_expiry_date'].year == selected_year] or [entry for entry in manual_data if entry['ups_remaining_days'] < 0 and entry['ups_expiry_date'].year == selected_year]
        expiring_battery = [entry for entry in manual_data if entry['battery_remaining_days'] > 0 and entry['battery_expiry_date'].year == selected_year] or [entry for entry in manual_data if entry['battery_remaining_days'] < 0 and entry['battery_expiry_date'].year == selected_year]

        for battery_info in expiring_battery:
            c = (battery_info['battery_type'].strip())
            expiring_battery_types.append(c)
            battery_product_name=c
            print(battery_product_name)
            # entry['battery_product_price'] = scrape_product_price(url="https://www.graybar.com/",product_name=battery_product_name)
            battery_price = scrape_product_price(url="https://www.graybar.com/",product_name=battery_product_name)
            battery_prices.append(battery_price)
            battery_info['battery_product_price']=[battery_price]
        for ups_info in expiring_ups:
            c = (ups_info['ups_type'].strip())
            expiring_ups_types.append(c)
            ups_product_name = c
            # entry['ups_product_price'] = scrape_product_price(url="https://www.graybar.com/",product_name=ups_product_name)
            ups_price = scrape_product_price(url="https://www.graybar.com/",product_name=ups_product_name)
            ups_prices.append(ups_price)
            ups_info['ups_product_price']= [ups_price]
        response_data = {
            'expiring_ups': expiring_ups,
            'expiring_battery': expiring_battery,
        }
        print(response_data)
        return JsonResponse(response_data, safe=False)
    else:
        return JsonResponse({}, safe=False)


def export_pdf(request, selected_year):
    if request.method == 'GET':
        # Fetch data from the database (you may need to modify the query)
        manual_data = Manual.objects.all()
        snmp_data = SNMP.objects.all()

        # Convert querysets to lists of dictionaries
        manual_data = manual_data.values()
        snmp_data = snmp_data.values()

        # Calculate UPS and Battery expirations
        for entry in manual_data:
            ip_address = entry['ip_address']

            # Find the matching SNMP entry based on IP address
            snmp_entry = next((s for s in snmp_data if s['ip_address'] == ip_address), None)

            if snmp_entry:
                entry['ups_installed_date'] = entry['ups_installed_date']  # No need to remove tzinfo

                # Ensure 'ups_expiry_date' is a datetime object
                entry['ups_expiry_date'] = datetime.combine(entry['ups_installed_date'], datetime.min.time()) + timedelta(days=5 * 365)
                entry['ups_remaining_days'] = (entry['ups_expiry_date'] - datetime.now()).days
                entry['ups_type'] = snmp_entry['ups_type']

            # For battery, apply the same changes
            entry['battery_installed_date'] = entry['battery_installed_date']  # No need to remove tzinfo
            entry['battery_expiry_date'] = datetime.combine(entry['battery_installed_date'], datetime.min.time()) + timedelta(days=2 * 365)
            entry['battery_remaining_days'] = (entry['battery_expiry_date'] - datetime.now()).days

        # Filter data for UPS and battery that are expiring in the selected year
        expiring_ups = [entry for entry in manual_data if entry['ups_remaining_days'] > 0 and entry['ups_expiry_date'].year == selected_year] or [entry for entry in manual_data if entry['ups_remaining_days'] < 0 and entry['ups_expiry_date'].year == selected_year]
        expiring_battery = [entry for entry in manual_data if entry['battery_remaining_days'] > 0 and entry['battery_expiry_date'].year == selected_year] or [entry for entry in manual_data if entry['battery_remaining_days'] < 0 and entry['battery_expiry_date'].year == selected_year]


        # Render the PDF template with the data
        template = 'pdf_template.html'  # Create an HTML template for PDF layout
        #expiring_entries = expiring_ups + expiring_battery
        context = {
            'selected_year': selected_year,
            'expiring_ups': expiring_ups,
            'expiring_battery': expiring_battery,
            #'expiring_entries': expiring_entries,
        }
        rendered_html = render_to_string(template, context)

        # Generate a PDF from the rendered HTML
        pdf_file = BytesIO()
        pisa.CreatePDF(BytesIO(rendered_html.encode('UTF-8')), dest=pdf_file)
        pdf_file.seek(0)

        # Create an HTTP response with the PDF file
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=report_{selected_year}.pdf'
        return response
    else:
        return JsonResponse({}, safe=False)

@login_required
def report(request):
    current_year = datetime.now().year
    years_range = range(current_year, current_year + 5)  # From the current year to 5 years ahead

    context = {
        'current_year': current_year,
        'years': years_range,
    }

    return render(request, 'report.html', context)

def logout_view(request):
    logout(request)
    # Implement your logout logic here (e.g., using Django's authentication system)
    # Redirect the user to the login page after logging out
    return redirect('login')
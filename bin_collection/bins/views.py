from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse


driver = None
driver_ready = False

# Singleton principle for getting/ creating driver object
def get_driver():
    global driver, driver_ready  # Declare driver_ready as global
    if driver is None:
        try:
            driver = webdriver.Chrome()  # Must be amended for non-Chrome browsers
            url = 'https://onlineservices.glasgow.gov.uk/forms/RefuseAndRecyclingWebApplication/AddressSearch.aspx'
            driver.get(url)

            # Enter postcode in search input
            postcode_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'Application_Addresses_Search'))
            )
            
            # Mark driver as ready
            driver_ready = True

        except Exception as e:
            print(f"An error occurred: {e}")
    return driver



def get_addresses(postcode):
    global driver
    try:
        driver = get_driver()

        url = 'https://onlineservices.glasgow.gov.uk/forms/RefuseAndRecyclingWebApplication/AddressSearch.aspx'
        driver.get(url)

        # Enter postcode in search input
        postcode_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Application_Addresses_Search'))
        )
        postcode_input.send_keys(postcode)

        search_button = driver.find_element(By.ID, 'Application_Addresses_ImageButton')
        search_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'DataGrid'))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        addresses = []
        
        # Iterate over all rows in the results table
        for row in soup.select('.DataGrid tr'):
            cells = row.find_all('td')
            
            if len(cells) > 1:
                # Separate address string into list of address line, city, postcode
                full_address = cells[2].text.strip() 
                address_parts = full_address.split(', ')  

                if len(address_parts) >= 3:
                    address = address_parts[0] 
                    city = address_parts[1] 
                    postcode = address_parts[2] 
                else:
                    address = full_address
                    city = "Unknown"
                    postcode = "Unknown"

                # Check if the address is expandable
                expand_button = cells[0].find('input', {'type': 'image'})
                if expand_button and 'id' in expand_button.attrs:
                    expand_action = expand_button['id'] 
                    addresses.append({
                        'address': [address, city, postcode],
                        'action': expand_action,
                        'expandable': True 
                    })
                else:
                    anchor = cells[1].find('a')
                    if anchor and 'id' in anchor.attrs:
                        address_id = anchor['id']
                        addresses.append({
                            'address': [address, city, postcode],
                            'action': address_id,
                            'expandable': False 
                        })

        return addresses
    except Exception as e:
        print(f"An error occurred while fetching addresses: {e}")
        return []

# Return a dictionary of relevant bin information
def get_bin_info(address_id, expandable):
    global driver
    try:
        driver = get_driver()

        # For addresses with multiple residancies (flats) expand and select first address
        if expandable:
            expand_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, address_id))
            )
            expand_button.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'DataGridAlternatingItemStyle'))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            sub_address_row = soup.find('tr', class_='DataGridAlternatingItemStyle')
            sub_select_button = sub_address_row.find('a')['id']

            select_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, sub_select_button))
            )
            select_button.click()

        # If address is not expandable- simply simulate pressing select button
        else:
            select_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, address_id))
            )
            select_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'fieldset'))
        )

        # bs4 to extract page info
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        bin_info = {}
        for p in soup.find_all('p'):
            text_content = p.get_text()
            if "Green" in text_content:
                bin_info["green"] = text_content
            elif "Blue" in text_content:
                bin_info["blue"] = text_content
            elif "Brown" in text_content:
                bin_info["brown"] = text_content
            elif "Purple" in text_content:
                bin_info["purple"] = text_content
            elif "Grey" in text_content:
                bin_info["grey"] = text_content

        return bin_info
    finally:
        pass 

def index(request):
    if request.method == 'POST':
        postcode = request.POST.get('postcode')
        if postcode:
            addresses = get_addresses(postcode) # Get a list of results (addresses) for enterred postcode
            if addresses:
                return render(request, 'bins/results.html', {'addresses': addresses})
            else:
                return render(request, 'bins/index.html', {'error_message': 'No addresses found!'})
    driver = get_driver() # Start the chrome driver upon the page loading

    return render(request, 'bins/index.html')

# Handle selection of an address from the table
def address_select(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_action')
        expandable = request.POST.get('expandable') == 'True' 

        if selected_address_id:
            bin_info = get_bin_info(selected_address_id, expandable)
            
            if bin_info:
                return render(request, 'bins/details.html', {'bin_info': bin_info})
            else:
                return HttpResponse("Bin information not found.")
        else:
            return HttpResponse("No address selected.")

def check_driver_status(request):
    global driver_ready
    return JsonResponse({'status': 'ready' if driver_ready else 'loading'})

def close_driver():
    global driver
    if driver:
        driver.quit()
        driver = None

def about(request):
    return render(request, 'bins/about.html')

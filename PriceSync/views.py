from django.shortcuts import render
from django.http import HttpResponse
from tablib import Dataset
from .models import PriceList, ExchangeRate, ProductCostMapping, MasterInventory
from .resources import pricelistResource
from .db_utils import get_db_connection, get_remote_db_connection
from datetime import datetime
from .forms import ExchangeRateForm
from django.db.utils import DatabaseError





from django.db import connection, transaction






# create your views here
def dashboard(request):
    return render(request, 'ps_blocks/dashboard.html')
    #return HttpResponse("Hello World")

def login(request):
    return render(request, 'ps_blocks/login.html')

def forgotpassword(request):
    return render(request, 'forgot-password.html')

def signup(request):
    return render(request, 'ps_blocks/signup.html')

from datetime import datetime  # Import the datetime module

def rateupdate(request):
    exchange_rate_model = ExchangeRate.objects.order_by('-rateDate')
    
    if request.method == 'POST':
        form = ExchangeRateForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            rate_date = data['rateDate']
            base_currency = data['rateBaseCurrency']
            target_currency = data['rateTargetCurrency']

            # Check if the rate already exists
            if not ExchangeRate.objects.filter(
                rateDate=rate_date,
                rateBaseCurrency=base_currency,
                rateTargetCurrency=target_currency
            ).exists():
                try:
                    # Data from the form is valid
                    exchange_rate = form.save(commit=False)  # Create an ExchangeRate object but don't save it yet
                    exchange_rate.rateUpdatedBy = "Keegan Solomon"  # You can set the user here
                    exchange_rate.rateUpdatedOn = datetime.now()  # Use timezone.now() if you're working with time zones
                    exchange_rate.save()
                    
                    form_sub_success = "Rate updated successfully."
                    return render(request, 'ps_blocks/rateUpdateLog.html', {'form_sub_success': form_sub_success, 'form': form, 'ExchangeRate': exchange_rate_model})
                
                except Exception as e:
                    save_err = "Error saving to the database"
                    return render(request, 'ps_blocks/rateUpdateLog.html', {'save_err': save_err, 'form': form, 'ExchangeRate': exchange_rate_model})
            
            else:
                form_sub_dup = "The specified rate with the same date and currencies already exists."
                return render(request, 'ps_blocks/rateUpdateLog.html', {'form_sub_dup': form_sub_dup, 'form': form, 'ExchangeRate': exchange_rate_model})
    
    else:
        form = ExchangeRateForm()
    
    return render(request, 'ps_blocks/rateUpdateLog.html', {'form': form, 'ExchangeRate': exchange_rate_model})



def costfactors(request):
    return render(request, 'ps_blocks/costfactorspanel.html')

# pages to create
def uploadplist(request):
    if request.method == 'POST':
        # Check if the PriceList model is not empty
        if PriceList.objects.exists():
            error_message = "PriceList is not empty. Cannot upload a new pricelist."
            return render(request, 'ps_blocks/uploadpricelist.html', {'error_message': error_message})

        if request.POST.get('supplier_name') and request.POST.get('pl_currency'):
            pricelist_resource = pricelistResource()
            dataset = Dataset()
            new_pricelist = request.FILES['my_file']
            imported_data = dataset.load(new_pricelist.read(), format='xlsx')
            supplier_val = request.POST.get('supplier_name')
            currency_val = request.POST.get('pl_currency')
            for data in imported_data:
                value = PriceList(
                    data[0],
                    data[1],
                    data[2],
                    currency_val,
                    supplier_val
                )
                value.save()

            success_message = "Pricelist uploaded successfully."
            return render(request, 'ps_blocks/uploadpricelist.html', {'success_message': success_message})

    return render(request, 'ps_blocks/uploadpricelist.html')


def viewpricelist(request):
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PriceSync_pricelist")
            # Commit the changes
            conn.commit()

            # After successfully updating records, return a success message
            success_message = "Price list cleared successfully."
            return render(request, 'ps_blocks/pricelist.html', {'success_message': success_message})

        except DatabaseError as e:
            # Handle database-related exceptions more precisely
            print(f"Database Error: {str(e)}")

        except Exception as e:
            # Handle other exceptions or errors here
            print(f"Error: {str(e)}")

        finally:
            # Close the cursor and connection in the finally block
            cursor.close()
            conn.close()


    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PriceSync_pricelist")
    result = cursor.fetchall()
    return render(request, 'ps_blocks/pricelist.html', {'PriceList':result})


def remoteinventoryaccess(request):
    import logging
# Configure logging
    logging.basicConfig(filename='app.log', level=logging.ERROR)

    if request.method == 'POST':
        try:
            # Execute the SELECT SQL statement
            conn = get_remote_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT LTRIM(RTRIM(fldInventoryCode)) AS prodCode, 
                           fldDescription AS prodDesc, 
                           fldCategoryDesc AS prodCategory, 
                           fldCreateDate AS prodDOC
                    FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory;
                """)

            # Fetch the results
            results = cursor.fetchall()

            # Execute the INSERT SQL statement if SELECT was successful
            conn = get_db_connection()
            cursor = conn.cursor()
            r_count = 0
            for row in results:
                prodCode = row[0]
    
                # Check if the prodCode already exists in the table
                cursor.execute("SELECT 1 FROM PriceSync_masterinventory WHERE prodCode = ?;", (prodCode,))
                if not cursor.fetchone():
                    # Insert the row if it doesn't exist
                    cursor.execute("""
                    INSERT INTO PriceSync_masterinventory (prodCode, prodDesc, prodCategory, prodDOC)
                    VALUES (?, ?, ?, ?);
                    """, row)
                    # Record the number of rows inserted
                    r_count = r_count + 1

            # Commit the changes
            conn.commit()

            sql2 = """
INSERT INTO PriceSync_productcostmapping (prodSupplierCode, prodNashuaCode, prodDesc, prodCategory, prodSupplierName, prodSupplierCurrency, prodSupplierCost, prodSupplierLandedCost_USD, prodNashuaSellingPrice_USD, prodCalculatedPriceDate)
SELECT prodCode, '', prodDesc, prodCategory, '', '', '0.00', '0.00', '0.00', prodDOC
FROM PriceSync_masterinventory
WHERE prodCode NOT IN (SELECT prodSupplierCode FROM PriceSync_productcostmapping);
"""
            cursor.execute(sql2)
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()


            conn = get_remote_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory")
            result = cursor.fetchall()
            success_message = "Success: Data for " + str(r_count) + " rows has been successfully synced from BPO."
            return render(request, 'ps_blocks/remoteinventoryaccess.html', {'results': result, 'success_message': success_message})


        except Exception as e:
            # Handle exceptions or errors here
            return HttpResponse(f"Error: {str(e)}")

    try:
        conn = get_remote_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory")
        result = cursor.fetchall()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        #return render(request, 'error_template.html', {'error_message': error_message})

    # Pass the results to the template
    return render(request, 'ps_blocks/remoteinventoryaccess.html', {'results': result})


def localinventoryaccess(request):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PriceSync_masterinventory")
        result = cursor.fetchall()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render(request, 'ps_blocks/under_maintenance.html', {'error_message': error_message})

    # Pass the results to the template
    return render(request, 'ps_blocks/localinventorylist.html', {'results': result})



def updatecurrencyrates(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def syncinventorydata(request):
    if request.method == 'POST':
        # Retrieve all rows from TableA
        rows_from_pricelist = PriceList.objects.all()

        if not rows_from_pricelist:
            # Handle the case where PriceList is empty
            error_message = "PriceList is empty. No records to sync."
            return render(request, 'ps_blocks/syncinventory.html', {'error_message': error_message})

        # Get the current date and time
        current_date = datetime.now()

        # Iterate through each row in TableA
        for row_a in rows_from_pricelist:
        # Check if field1 in TableA matches field2 in TableB
            matching_row_in_ProductCostMapping = ProductCostMapping.objects.filter(prodSupplierCode=row_a.prodCode).first()

            if matching_row_in_ProductCostMapping:
                # Update fields in TableB based on values from TableA
                matching_row_in_ProductCostMapping.prodSupplierName = row_a.prodSupplier  # Update field3 in TableB with field3 from TableA
                matching_row_in_ProductCostMapping.prodSupplierCurrency = row_a.prodCurrency  # Update field4 in TableB with field4 from TableA
                matching_row_in_ProductCostMapping.prodSupplierCost = row_a.prodPrice  # Update field4 in TableB with field4 from TableA
                matching_row_in_ProductCostMapping.prodCalculatedPriceDate = current_date  # Update field4 in TableB with field4 from TableA

                # Save the changes to TableB
                matching_row_in_ProductCostMapping.save()
        
        # After successfully updating records, return a success message
        success_message = "Records updated successfully."
        return render(request, 'ps_blocks/syncinventory.html', {'results': result, 'success_message': success_message})
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PriceSync_productcostmapping")
        result = cursor.fetchall()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render(request, 'ps_blocks/syncinventory.html', {'results': result, 'error_message': error_message})

    # Pass the results to the template
    return render(request, 'ps_blocks/syncinventory.html', {'results': result})












def bpoexclusiveaccess(request):
    try:
        # Execute the SELECT SQL statement
        conn = get_remote_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT LTRIM(RTRIM(fldInventoryCode)) AS prodCode, 
            fldDescription AS prodDesc, 
            fldCategoryDesc AS prodCategory, 
            fldCreateDate AS prodDOC
            FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory;
            """)

        # Fetch the results
        results = cursor.fetchall()

        # Filter out records that already exist in PriceSync_masterinventory
        existing_prodcodes = MasterInventory.objects.values_list('prodCode', flat=True)
        filtered_results = [row for row in results if row[0] not in existing_prodcodes]

        if not filtered_results:
            return render(request, 'ps_blocks/bpoexclusive.html')

        return render(request, 'ps_blocks/bpoexclusive.html', {'results': filtered_results})

    except Exception as e:
        # Handle exceptions or errors here
        return HttpResponse(f"Error: {str(e)}")
    




def xpressexclusiveaccess(request):
    try:
        # Execute the SELECT SQL statement for PriceSync_masterinventory
        conn = get_db_connection()  # Assuming this function returns the connection to your local database
        cursor = conn.cursor()
        cursor.execute("""
            SELECT prodCode, prodDesc, prodCategory, prodDOC
            FROM PriceSync_masterinventory
            """)

        # Fetch the results for PriceSync_masterinventory
        results_price_sync = cursor.fetchall()

        # Execute the SELECT SQL statement for [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory
        conn_remote = get_remote_db_connection()  # Assuming this function returns the connection to your remote database
        cursor_remote = conn_remote.cursor()
        cursor_remote.execute("""
            SELECT LTRIM(RTRIM(fldInventoryCode)) AS prodCode, 
            fldDescription AS prodDesc, 
            fldCategoryDesc AS prodCategory, 
            fldCreateDate AS prodDOC
            FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory
            """)

        # Fetch the results for [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory
        results_bpo = cursor_remote.fetchall()

        # Get a list of prodCode values from PriceSync_masterinventory
        existing_prodcodes = [row[0] for row in results_bpo]

        # Filter out records that are in PriceSync_masterinventory
        filtered_results = [row for row in results_price_sync if row[0] not in existing_prodcodes]

        if not filtered_results:
            return render(request, 'ps_blocks/xpressexclusive.html')

        return render(request, 'ps_blocks/xpressexclusive.html', {'results': filtered_results})

    except Exception as e:
        # Handle exceptions or errors here
        return HttpResponse(f"Error: {str(e)}")










def inventorypricing(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def lcostcalculations(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def integrationsetting(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def BPOreports(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def createaccount(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def usermgt(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def resetpwd(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def errorpage(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def systemaccesslog(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def viewactivitylog(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def audittrailconfigs(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def documentationpanel(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def faqspanel(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def contactsupport(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def releasenotes(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def systemconfigurations(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def securityandpermissions(request):
    return render(request, 'ps_blocks/under_maintenance.html')

def backupandrestore(request):
    return render(request, 'ps_blocks/under_maintenance.html')


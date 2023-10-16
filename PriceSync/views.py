from django.shortcuts import render
from django.http import HttpResponse
from tablib import Dataset
from .models import PriceList, ExchangeRate, ProductCostMapping, MasterInventory, ProductCostingFactors
from .resources import pricelistResource
from .db_utils import get_db_connection, get_remote_db_connection
from datetime import datetime
from .forms import ExchangeRateForm, ProductCostingFactorsform
from django.db.utils import DatabaseError
from django.db import connection, transaction
import logging
from django.db.models import Max







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
    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.ERROR)
    categories = ProductCostMapping.objects.values_list('prodCategory', flat=True).distinct().order_by('prodCategory')
    suppliers = ProductCostMapping.objects.values_list('prodSupplierName', flat=True).distinct().order_by('prodSupplierName')
    cost_factors_model = ProductCostingFactors.objects.order_by('StockCategory')

    if request.method == 'POST':
        form = ProductCostingFactorsform(request.POST)  # Replace 'YourForm' with your actual form class name

        #if form.is_valid():
            #data = form.cleaned_data
            #cf_supplier_name = data['cf_supplier_name']
            #cf_category = data['cf_category']
            #cf_currency = data['cf_currency']
            #cf_exc_rate = data['ExchangeRateFactor']
            #cf_duty = data['DutyFactor']
            #cf_freight = data['FreightChargesFactor']
            #cf_markup = data['MarkupFactor']
        cf_supplier_name = request.POST.get('supplier_name')
        cf_category = request.POST.get('category')
        cf_currency = request.POST.get('currency')
        cf_exc_rate = request.POST.get('exc_rate')
        cf_duty = request.POST.get('duty')
        cf_freight = request.POST.get('freight_charges')
        cf_markup = request.POST.get('markup')
        cf_UpdatedBy = "Keegan Solomon" 
        cf_UpdatedOn = datetime.now() 

        # Check if the rate already exists
        if not ProductCostingFactors.objects.filter(
            StockCategory=cf_category,
            SupplierName=cf_supplier_name,
            CurrencyCode=cf_currency
        ).exists():
                try:
                    new_cost_factor = ProductCostingFactors(
                        StockCategory=cf_category,
                        SupplierName=cf_supplier_name,
                        CurrencyCode=cf_currency,
                        ExchangeRateFactor=cf_exc_rate,
                        DutyFactor=cf_duty,
                        FreightChargesFactor=cf_freight,
                        MarkupFactor=cf_markup,
                        UpdatedBy = cf_UpdatedBy,
                        UpdatedOn = cf_UpdatedOn,
                    )
                    new_cost_factor.save()

                    form_sub_success = "Cost Factor Added Successfully."
                    return render(request, 'ps_blocks/costfactorspanel.html', {'results': cost_factors_model, 'form': form, 'form_sub_success': form_sub_success})

                except Exception as e:
                    save_err = "Error saving to the database"
                    return render(request, 'ps_blocks/costfactorspanel.html', {'save_err': save_err, 'form': form, 'results': cost_factors_model})
            
        else:
            form_sub_dup = "The specified cost factors already exist."
            return render(request, 'ps_blocks/costfactorspanel.html', {'form_sub_dup': form_sub_dup, 'form': form, 'results': cost_factors_model})

    else:
        form = ProductCostingFactorsform()  # Replace 'YourForm' with your actual form class name

    return render(request, 'ps_blocks/costfactorspanel.html', {'results': cost_factors_model, 'categories': categories, 'suppliers': suppliers, 'form': form})













# pages to create
from django.shortcuts import render
from .models import PriceList
from .resources import pricelistResource
from tablib import Dataset


def uploadplist(request):
    if request.method == 'POST':
        if request.POST.get('supplier_name') and request.POST.get('pl_currency'):
            pricelist_resource = pricelistResource()
            dataset = Dataset()
            new_pricelist = request.FILES['my_file']
            imported_data = dataset.load(new_pricelist.read(), format='xlsx')
            supplier_val = request.POST.get('supplier_name')
            currency_val = request.POST.get('pl_currency')
            count_empty_row = 0
            count_inserted_row = 0
            for data in imported_data:
                if data[0] is not None and data[1] is not None:
                    value = PriceList(
                        data[0],
                        data[1],
                        data[2],
                        currency_val,
                        supplier_val
                    )
                    value.save()
                    count_inserted_row += 1
                else:
                    count_empty_row += 1

            success_message = f"{count_inserted_row} Rows inserted successfully and {count_empty_row} rows skipped."
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
INSERT INTO PriceSync_productcostmapping (prodSupplierCode, prodNashuaCode, prodDesc, prodCategory, prodSupplierName, prodSupplierCurrency, prodCalculationModifier, prodSupplierCost, prodSupplierCostUSD, prodSupplierLandedCost_USD, prodNashuaSellingPrice_USD, prodCalculatedPriceDate)
SELECT prodCode, '', prodDesc, prodCategory, '', '', 'Null', '0.00', '0.00', '0.00', '0.00', prodDOC
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PriceSync_productcostmapping")
        result = cursor.fetchall()
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
    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.ERROR)

    suppliers = ProductCostMapping.objects.values_list('prodSupplierName', flat=True).distinct().order_by('prodSupplierName')
    rows_from_procostmapping = ProductCostMapping.objects.all()

    if request.method == 'POST':
        supplier_name = request.POST.get('supplier_name')
        lc_currency = request.POST.get('lc_currency')

        if not supplier_name or not lc_currency:
            required_fields_msg = "Supplier Name or Currency fields are empty"
            return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'suppliers': suppliers, 'missing_fields': required_fields_msg})

        selected_products_dataset = ProductCostMapping.objects.filter(prodSupplierName=supplier_name, prodSupplierCurrency=lc_currency)

        if not selected_products_dataset.exists():
            empty_list_msg = "There are no products ready for calculation"
            return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'empty_list': empty_list_msg})

        get_USD_Supplier_Cost_Exrate = ExchangeRate.objects.filter(rateBaseCurrency=lc_currency, rateTargetCurrency="USD")

        # Assuming that `ExchangeRate` has a `date` field to represent the date of the rate.
        most_recent_rate = get_USD_Supplier_Cost_Exrate.aggregate(max_date=Max('rateUpdatedOn'))
        most_recent_rate_record = get_USD_Supplier_Cost_Exrate.filter(rateUpdatedOn=most_recent_rate['max_date']).first()

        if most_recent_rate_record:
            conversion_rate = most_recent_rate_record.rateValue
        else:
            # Handle the case where no records were found
            rate_not_found_msg = "The Conversion Rate is not found"
            return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'rate_not_found': rate_not_found_msg})

        matching_row_in_costfactors = ProductCostingFactors.objects.filter(SupplierName=supplier_name, CurrencyCode=lc_currency)

        if matching_row_in_costfactors.count() != 1:
            count_error_msg = "Factor row not found or too many records found! Update in Cost Factor Panel"
            return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'count_error': count_error_msg})

       # ex_rate = matching_row_in_costfactors.first().ExchangeRateFactor
        duty = matching_row_in_costfactors.first().DutyFactor
        freight = matching_row_in_costfactors.first().FreightChargesFactor
        markup = matching_row_in_costfactors.first().MarkupFactor

        for prodRow in selected_products_dataset:
            if prodRow.prodSupplierCurrency != "USD":
                USD_SupplierCost = prodRow.prodSupplierCost / conversion_rate

                if prodRow.prodCalculationModifier == "Null":
                    #LandingCost_USD = USD_SupplierCost * ex_rate * duty * freight
                    LandingCost_USD = USD_SupplierCost * duty * freight
                    NashuaSellingPrice_USD = markup * LandingCost_USD
                    #prodRow.prodSupplierCurrency = "USD"
                    prodRow.prodSupplierCostUSD = USD_SupplierCost
                    prodRow.prodSupplierLandedCost_USD = LandingCost_USD
                    prodRow.prodNashuaSellingPrice_USD = NashuaSellingPrice_USD
                    prodRow.prodCalculatedPriceDate = datetime.now()
                    prodRow.save()

        success_calculation = "Landed Cost Calculated Successfully!"
        return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'count_error': success_calculation})

    return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'suppliers': suppliers})














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


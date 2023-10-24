from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from tablib import Dataset
from .models import PriceList, ExchangeRate, ProductCostMapping, MasterInventory, ProductCostingFactors, Suppliers, User
from .resources import pricelistResource
from .db_utils import get_db_connection, get_remote_db_connection
from datetime import datetime
from .forms import ExchangeRateForm, ProductCostingFactorsform, Userform
from django.db.utils import DatabaseError
from django.db import connection, transaction
import logging
from django.db.models import Max
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView



# create your views here


# class-based view (CBV)
# LoginRequiredMixin and login_required serve a similar purpose in Django
#from django.contrib.auth.mixins import LoginRequiredMixin
#from django.views.generic import View
class CustomLoginView(LoginView):
    template_name = "ps_blocks/login.html"
    fields = '__all__'
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy('dashboard')


# function-based views (FBVs)
#from django.contrib.auth.views import LoginView
#from django.urls import reverse_lazy
#from django.shortcuts import render, redirect

#def custom_login_view(request):
#    if request.user.is_authenticated:
#        return redirect('dashboard')
#
#    if request.method == 'POST':
#    return render(request, 'ps_blocks/login.html')


@login_required
def dashboard(request):
    #ZWL to USD rate
    get_USD_ZWL_Supplier_Cost_Exrate = ExchangeRate.objects.filter(rateBaseCurrency="USD", rateTargetCurrency="ZWL")
    most_ZAR_USD_recent_rate = get_USD_ZWL_Supplier_Cost_Exrate.aggregate(max_date=Max('rateUpdatedOn'))
    USD_ZWL_recent_rate = get_USD_ZWL_Supplier_Cost_Exrate.filter(rateUpdatedOn=most_ZAR_USD_recent_rate['max_date']).first()
    if USD_ZWL_recent_rate:
        USD_ZWL_rate = USD_ZWL_recent_rate.rateValue
    else:
        USD_ZWL_rate = 0

    #ZAR to USD rate
    get_ZAR_USD_Supplier_Cost_Exrate = ExchangeRate.objects.filter(rateBaseCurrency="ZAR", rateTargetCurrency="USD")
    most_recent_ZAR_USD_rate = get_ZAR_USD_Supplier_Cost_Exrate.aggregate(max_date=Max('rateUpdatedOn'))
    ZAR_USD_recent_rate = get_ZAR_USD_Supplier_Cost_Exrate.filter(rateUpdatedOn=most_recent_ZAR_USD_rate['max_date']).first()
    if ZAR_USD_recent_rate:
        ZAR_USD_rate = ZAR_USD_recent_rate.rateValue
    else:
        ZAR_USD_rate = 0

    #Xpress total
    xpress_total_num = MasterInventory.objects.all().count()

    #Total Suppliers
    suppliers_total_num = Suppliers.objects.all().count()

    return render(request, 'ps_blocks/dashboard.html',{'USD_ZWL':USD_ZWL_rate, 'ZAR_USD':ZAR_USD_rate, 'xpress_tt': xpress_total_num, 'supplier_tt':suppliers_total_num})



@login_required
def forgotpassword(request):
    return render(request, 'forgot-password.html')


def signup(request):
    return render(request, 'ps_blocks/signup.html')

from datetime import datetime  # Import the datetime module

@login_required
def rateupdate(request):
    exchange_rate_model = ExchangeRate.objects.order_by('-rateDate')

    if request.method == 'POST':
        if 'filter_xrate_search' in request.POST:
            form = ExchangeRateForm()
            source_rate = request.POST.get('source_currency')
            dest_rate = request.POST.get('target_currency')
            result = ExchangeRate.objects.filter(rateBaseCurrency=source_rate, rateTargetCurrency=dest_rate).order_by('-rateDate')
            return render(request, 'ps_blocks/rateUpdateLog.html', {'form': form, 'ExchangeRate': result})
        elif 'delete_ex_rate' in request.POST:
            form = ExchangeRateForm()
            rate_date = request.POST.get('rate_date')
            source_currency = request.POST.get('source_currency')
            target_currency = request.POST.get('target_currency')
        
            try:
                exchange_rate = ExchangeRate.objects.get(
                    rateDate=rate_date,
                    rateBaseCurrency=source_currency,
                    rateTargetCurrency=target_currency
                )
                exchange_rate.delete()
                results = f"Success! {source_currency} to {target_currency} rate as at {rate_date} removed"
                return render(request, 'ps_blocks/rateUpdateLog.html', {'form': form,'ExchangeRate': exchange_rate_model, 'form_sub_success':results})
            except ExchangeRate.DoesNotExist:
                results = "Rate not found."
                return render(request, 'ps_blocks/rateUpdateLog.html', {'form': form,'ExchangeRate': exchange_rate_model, 'form_sub_dup':results})
        
        elif 'add_exchange_rate' in request.POST:
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







@login_required
def costfactors(request):
    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.ERROR)
    categories = ProductCostMapping.objects.values_list('prodCategory', flat=True).distinct().order_by('prodCategory')
    suppliers = Suppliers.objects.values_list('SupplierName', flat=True).distinct().order_by('SupplierName')
    cost_factors_model = ProductCostingFactors.objects.order_by('StockCategory')

    if request.method == 'POST':
        form = ProductCostingFactorsform(request.POST)  
        cf_supplier_name = request.POST.get('supplier_name')
        cf_category = request.POST.get('category')
        cf_currency = request.POST.get('currency')
        cf_calc_modifier = request.POST.get('calc_modifier')
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
                        CalculationModifier=cf_calc_modifier,
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


@login_required
def uploadplist(request):
    suppliers = Suppliers.objects.values_list('SupplierName', flat=True).distinct().order_by('SupplierName')
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

    return render(request, 'ps_blocks/uploadpricelist.html', {'suppliers':suppliers})


@login_required
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


@login_required
def remoteinventoryaccess(request):
    logging.basicConfig(filename='app.log', level=logging.ERROR)

    try:
        if request.method == 'POST':
            with get_remote_db_connection() as remote_conn, get_db_connection() as local_conn:
                remote_cursor = remote_conn.cursor()
                local_cursor = local_conn.cursor()
                r_count, u_count = 0, 0

                # Execute the SELECT SQL statement
                remote_cursor.execute("""
                SELECT LTRIM(RTRIM(fldInventoryID)) AS prodID,
                       LTRIM(RTRIM(fldInventoryCode)) AS prodCode, 
                       fldDescription AS prodDesc, 
                       fldCategoryDesc AS prodCategory, 
                       fldCreateDate AS prodDOC
                FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory;
            """)
                results = remote_cursor.fetchall()

                for row in results:
                    prodID, prodCode, prodCategory = row[0], row[1], row[3]

                    # Check if the prodCode already exists in the table
                    local_cursor.execute("SELECT 1 FROM PriceSync_masterinventory WHERE prodCode = ? AND prodID = ? AND prodCategory = ?;", (prodCode, prodID, prodCategory))
                    if not local_cursor.fetchone():
                        local_cursor.execute("SELECT 1 FROM PriceSync_masterinventory WHERE prodID = ? AND prodCategory = ?;", (prodID, prodCategory))
                        master_exists = local_cursor.fetchone()

                        if not master_exists:
                            # Insert the row if it doesn't exist in PriceSync_masterinventory
                            local_cursor.execute("INSERT INTO PriceSync_masterinventory (prodID, prodCode, prodDesc, prodCategory, prodDOC) VALUES (?, ?, ?, ?, ?);", row)
                            r_count += 1
                        else:
                            # Update the existing row in PriceSync_masterinventory
                            local_cursor.execute("UPDATE PriceSync_masterinventory SET prodCode = ? WHERE prodID = ? AND prodCategory = ?;", (prodCode, prodID, prodCategory))
                            local_cursor.execute("UPDATE PriceSync_productcostmapping SET prodSupplierCode = ? WHERE prodID = ? AND prodCategory = ?;", (prodCode, prodID, prodCategory))
                            u_count += local_cursor.rowcount

                # Execute the second SQL statement
                local_cursor.execute("""
                    INSERT INTO PriceSync_productcostmapping (prodID, prodSupplierCode, prodNashuaCode, prodDesc, prodCategory, prodSupplierName, prodSupplierCurrency, prodCalculationModifier, prodSupplierCost, prodSupplierCostUSD, prodSupplierLandedCost_USD, prodNashuaSellingPrice_USD, prodCalculatedPriceDate)
                    SELECT prodID, prodCode, '', prodDesc, prodCategory, '', '', 'Null', '0.00', '0.00', '0.00', '0.00', prodDOC
                    FROM PriceSync_masterinventory
                    WHERE prodCode NOT IN (SELECT prodSupplierCode FROM PriceSync_productcostmapping);
                    """)

                # Commit the changes
                local_conn.commit()

                # Reconnect to the remote database for data retrieval
                remote_cursor.execute("SELECT * FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory")
                result = remote_cursor.fetchall()
                success_message = f"Success: Data for {r_count} rows inserted and {u_count} rows updated."

                return render(request, 'ps_blocks/remoteinventoryaccess.html', {'results': result, 'success_message': success_message})

        remote_conn = get_remote_db_connection()
        remote_cursor = remote_conn.cursor()
        remote_cursor.execute("SELECT * FROM [nashua-eva].BPO2_NASH_PROD.dbo.vw_INVNInventory")
        result = remote_cursor.fetchall()
        return render(request, 'ps_blocks/remoteinventoryaccess.html', {'results': result})

    except Exception as e:
        # Handle exceptions or errors more specifically
        return HttpResponse(f"Error: {str(e)}")



@login_required
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



@login_required
def updatecurrencyrates(request):
    return render(request, 'ps_blocks/under_maintenance.html')


@login_required
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











@login_required
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
    



@login_required
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









@login_required
def inventorypricing(request):
    return render(request, 'ps_blocks/under_maintenance.html')






@login_required
def lcostcalculations(request):
    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.ERROR)

    suppliers = Suppliers.objects.values_list('SupplierName', flat=True).distinct().order_by('SupplierName')
    rows_from_procostmapping = ProductCostMapping.objects.all()

    if request.method == 'POST':
        supplier_name = request.POST.get('supplier_name')
        lc_currency = request.POST.get('lc_currency')

        if not supplier_name or not lc_currency:
            required_fields_msg = "Supplier Name or Currency fields are empty"
            return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'suppliers': suppliers, 'missing_fields': required_fields_msg})

        selected_products_dataset = ProductCostMapping.objects.all()

        if not selected_products_dataset.exists():
            empty_list_msg = "There are no products ready for calculation"
            return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'empty_list': empty_list_msg})

        # Get the most recent USD conversion rate
        get_usd_supplier_cost_exrate = ExchangeRate.objects.filter(rateBaseCurrency="ZAR", rateTargetCurrency="USD")
        most_recent_rate = get_usd_supplier_cost_exrate.aggregate(max_date=Max('rateUpdatedOn'))
        most_recent_rate_record = get_usd_supplier_cost_exrate.filter(rateUpdatedOn=most_recent_rate['max_date']).first()

        if most_recent_rate_record:
            conversion_rate = most_recent_rate_record.rateValue
        else:
            rate_not_found_msg = "The Conversion Rate is not found"
            return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'rate_not_found': rate_not_found_msg})

        for prod_row in selected_products_dataset:
            if prod_row.prodCategory and prod_row.prodSupplierCurrency == "ZAR":
                usd_supplier_cost = prod_row.prodSupplierCost / conversion_rate
                matching_row_in_cost_factors = ProductCostingFactors.objects.filter(StockCategory=prod_row.prodCategory, CurrencyCode="ZAR")

                if matching_row_in_cost_factors.count() != 1:
                    count_error_msg = "Factor row not found or too many records found! Update in Cost Factor Panel"
                    return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'count_error': count_error_msg})
                else:
                    cost_factors = matching_row_in_cost_factors.first()
                    duty = cost_factors.DutyFactor
                    freight = cost_factors.FreightChargesFactor
                    markup = cost_factors.MarkupFactor

                    # Initialize landing_cost_usd and nashua_selling_price_usd with usd_supplier_cost
                    landing_cost_usd = usd_supplier_cost
                    nashua_selling_price_usd = usd_supplier_cost

                    # Calculate landing_cost_usd by excluding variables with a value of 0
                    if duty != 0:
                        landing_cost_usd *= duty
                    if freight != 0:
                        landing_cost_usd *= freight
                    if markup != 0:
                        nashua_selling_price_usd *= markup



                    prod_row.prodSupplierCostUSD = usd_supplier_cost
                    prod_row.prodSupplierLandedCost_USD = landing_cost_usd
                    prod_row.prodNashuaSellingPrice_USD = nashua_selling_price_usd
                    prod_row.prodCalculatedPriceDate = datetime.now()
                    prod_row.save()

        success_calculation = "Landed Cost Calculated Successfully!"
        return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'count_error': success_calculation})

    return render(request, 'ps_blocks/lcostcalculation.html', {'results': rows_from_procostmapping, 'suppliers': suppliers})


"""



            if prodRow.prodCategory == "" and prodRow.prodSupplierCurrency == "":
        




        
        if prodCate !=  "" AND currency != "":
        elif prodCate !=  "" AND currency != "ZWL":
        elif prodCate !=  "" AND currency != "USD":
        elif prodCate !=  "" AND productCode Like "%(L)"
        elif prodCate !=  "" AND currency != "ZAR":
            
        else:
            h=2 
"""


"""
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
 """               """
                if prodRow.prodSupplierCode like "%(L)":
                    NashuaSellingPrice_USD = markup * USD_SupplierCost
                    prodRow.prodSupplierCostUSD = USD_SupplierCost
                    prodRow.prodSupplierLandedCost_USD = USD_SupplierCost
                    prodRow.prodNashuaSellingPrice_USD = NashuaSellingPrice_USD
                    prodRow.prodCalculatedPriceDate = datetime.now()
                    prodRow.save()
                    """                 
"""
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

"""

























@login_required
def integrationsetting(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def BPOreports(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def createaccount(request):
    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.ERROR)
    if request.method == 'POST':
        ca_firstname = request.POST.get('firstname')
        ca_lastname = request.POST.get('lastname')
        ca_username = request.POST.get('username')
        ca_email = request.POST.get('email')
        ca_mobile = request.POST.get('mobile')
        ca_jobtitle = request.POST.get('jobtitle')
        ca_emp_status = request.POST.get('emp_status')
        ca_doh = request.POST.get('doh')
        ca_department = request.POST.get('department')
        ca_manager = request.POST.get('manager')
        ca_emp_role = request.POST.get('emp_role')
        ca_emp_id = request.POST.get('emp_id')
        ca_pwd = request.POST.get('pwd')
        hashed_password = make_password(ca_pwd)
        ca_profile_img = request.POST.get('profile_img')
        ca_UpdatedBy = "Keegan Solomon" 
        ca_UpdatedOn = datetime.now() 
        # Format the datetime as a string
        formatted_ca_UpdatedOn = ca_UpdatedOn.strftime('%Y-%m-%d %H:%M:%S.%f %z')




        from django.db.models import Q
        # Check if the user already exists
        if not User.objects.filter(
            Q(username=ca_username) | Q(email=ca_email) | Q(employee_id=ca_emp_id) | Q(contact_number=ca_mobile)
        ).exists():
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    sql = """
                    INSERT INTO PriceSync_user (username, password, first_name, last_name, email, employee_id, contact_number, job_title, employee_status, date_of_hire, account_creation_date, profile_picture_url, department_id, manager_id, role_id, updatedBy, updatedOn)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    values = (ca_username, hashed_password, ca_firstname, ca_lastname, ca_email, ca_emp_id, ca_mobile, ca_jobtitle, ca_emp_status, ca_doh, formatted_ca_UpdatedOn, ca_profile_img, ca_department, ca_manager, ca_emp_role, ca_UpdatedBy, ca_UpdatedOn)
                    cursor.execute(sql, values)

                    conn.commit()

                    # Close the cursor and the database connection
                    cursor.close()
                    conn.close()
                    


                    form_sub_success = "New user account created Successfully."
                    return render(request, 'ps_blocks/createuser.html', {'form_sub_success': form_sub_success})

                except Exception as e:
                    save_err = "Error saving to the database"
                    return render(request, 'ps_blocks/createuser.html', {'save_err': save_err})
            
        else:
            # Create a dictionary to map field names to their values
            field_values = {
                "username": ca_username,
                "email": ca_email,
                "employee_id": ca_emp_id,
                "contact_number": ca_mobile,
            }

            # Initialize a list to store the names of fields that are already in use
            fields_in_use = []

            # Check if any of the fields already exist in the User model
            for field_name, field_value in field_values.items():
                if User.objects.filter(Q(**{field_name: field_value})).exists():
                    fields_in_use.append(field_name)
            # Print the fields that are already in use
            if fields_in_use:
                user_exist_err = f"The following fields are already in use: {', '.join(fields_in_use)}"
                return render(request, 'ps_blocks/createuser.html', {'user_exist': user_exist_err})

    else:
        form = Userform()  # Replace 'YourForm' with your actual form class name

    return render(request, 'ps_blocks/createuser.html')















@login_required
def usermgt(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def resetpwd(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def errorpage(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def systemaccesslog(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def viewactivitylog(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def audittrailconfigs(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def documentationpanel(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def faqspanel(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def contactsupport(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def releasenotes(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def systemconfigurations(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def securityandpermissions(request):
    return render(request, 'ps_blocks/under_maintenance.html')

@login_required
def backupandrestore(request):
    return render(request, 'ps_blocks/under_maintenance.html')


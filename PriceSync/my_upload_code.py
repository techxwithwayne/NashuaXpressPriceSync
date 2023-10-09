def rateupdate(request):
    if request.method == 'POST':
        if request.POST.get('ratedate') and request.POST.get('basecurrency') and request.POST.get('targetcurrency') and request.POST.get('ratevalue'):
            # Create a datetime object
            current_datetime = datetime.now()
            current_datetime_str = str(current_datetime)
            insertdexrate = ExchangeRate()
            insertdexrate.rateDate = request.POST.get('ratedate')
            insertdexrate.rateBaseCurrency = request.POST.get('basecurrency')
            insertdexrate.rateTargetCurrency = request.POST.get('targetcurrency')
            insertdexrate.rateValue = request.POST.get('ratevalue')
            insertdexrate.rateUpdatedBy = "Keegan Solomon"
            insertdexrate.rateUpdatedOn = current_datetime_str
            # Query the database to check if the values exist
            if ExchangeRate.objects.filter(rateDate=request.POST.get('ratedate'), rateBaseCurrency=request.POST.get('basecurrency'), rateTargetCurrency=request.POST.get('targetcurrency')).exists():
                # Values already exist in the database, return JavaScript alert
                alert_rate_exists = "Rate Already Exists! "
                js_code = f"alert('{alert_rate_exists}');"
                return render(request, 'ps_blocks/rateUpdateLog.html', {'alert_rate_exists': alert_rate_exists})
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO PriceSync_exchangerate VALUES('"+insertdexrate.rateDate+"','"+insertdexrate.rateBaseCurrency+"','"+insertdexrate.rateTargetCurrency+"','"+insertdexrate.rateValue+"','"+insertdexrate.rateUpdatedBy+"','"+insertdexrate.rateUpdatedOn+"')")
                cursor.commit()
                #get the data back
                cursor.execute("SELECT * FROM PriceSync_exchangerate ORDER BY rateDate DESC")
                result = cursor.fetchall()
                return render(request, 'ps_blocks/rateUpdateLog.html', {'ExchangeRate':result})
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PriceSync_exchangerate ORDER BY rateDate DESC")
    result = cursor.fetchall()
    return render(request, 'ps_blocks/rateUpdateLog.html', {'ExchangeRate':result})
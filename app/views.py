from django.shortcuts import render, redirect, get_object_or_404
import requests
import json
import xmltodict, xmljson
from lxml.etree import fromstring, tostring
from .models import StockCategory, StockItem, StockGroup, Ledger
import re



def base(request):
    return render(request,'base.html')


def stock_category(request):
    x = """<ENVELOPE>
            <HEADER>
                  <VERSION>1</VERSION>
                  <TALLYREQUEST>EXPORT</TALLYREQUEST>
                  <TYPE>COLLECTION</TYPE>
                  <ID>STOCKCATEGORY</ID>

           </HEADER>
           <BODY>
           <DESC>
                  <STATICVARIABLES>
                         <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                  </STATICVARIABLES>
           </DESC>
           </BODY>
        </ENVELOPE>"""

    api = 'http://127.0.0.1:8000/'
    q = requests.post(api, data=x, verify=False, headers={"Content-Type": "text/xml"})


    data = xmltodict.parse(q.content)
    try:
        category_data = data['ENVELOPE']['BODY']['DATA']['COLLECTION']['STOCKCATEGORY']
    except Exception as e:
        category_data = []

    tally_categories = []
    if isinstance(category_data, list):
        for category in category_data:
            name = category['LANGUAGENAME.LIST']['NAME.LIST']['NAME']
            tally_categories.append(name)
    elif isinstance(category_data, dict):
        name = category_data['LANGUAGENAME.LIST']['NAME.LIST']['NAME']
        tally_categories.append(name)

    db_categories = StockCategory.objects.all()

    context = {
        'names': tally_categories,
        'db_categories': db_categories,
    }

    return render(request, 'stock-category.html', context)


def add_stock_category(request):
    if request.method == "POST":
        category = request.POST['category']

        data = """<ENVELOPE Action="">

                    <HEADER>
                        <VERSION>1</VERSION>
                        <TALLYREQUEST>IMPORT</TALLYREQUEST>
                        <TYPE>DATA</TYPE>
                        <ID>All Masters</ID>
                    </HEADER>

                    <BODY>
                        <DESC>
                          <STATICVARIABLES>
                            <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
                          </STATICVARIABLES>
                        </DESC>
                        <DATA>
                            <TALLYMESSAGE>
                                <STOCKCATEGORY ACTION="CREATE">
                                    <NAME>{category}</NAME>
                                </STOCKCATEGORY>
                            </TALLYMESSAGE>
                        </DATA>
                    </BODY>
                    </ENVELOPE>"""

        api = 'http://127.0.0.1:8000/'
        q = requests.post(api, data=data.format(category=category), verify=False,
                          headers={"Content-Type": "application/xml"})

        data = xmltodict.parse(q.content)
        data2 = json.dumps(data)
        StockCategory.objects.get_or_create(name=category)

        context = {'data': json.loads(data2)}

        return redirect('stock_category')
    else:
        return render(request, 'add-stock-category.html')


def update_stock_category(request, name):
    if request.method == "POST":
        category = request.POST['category']
        data = """<ENVELOPE Action="">

                    <HEADER>
                        <VERSION>1</VERSION>
                        <TALLYREQUEST>IMPORT</TALLYREQUEST>
                        <TYPE>DATA</TYPE>
                        <ID>All Masters</ID>
                    </HEADER>

                        <BODY>
                            <DESC>
                              <STATICVARIABLES>
                                <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
                              </STATICVARIABLES>
                            </DESC>
                            <DATA>
                                <TALLYMESSAGE>
                                    <STOCKCATEGORY NAME="{name}" ACTION="ALTER">
                                        <NAME>{category}</NAME>
                                    </STOCKCATEGORY>
                                </TALLYMESSAGE>
                            </DATA>
                        </BODY>

                    </ENVELOPE>"""
        api = "http://127.0.0.1:8000/"
        response = requests.post(api, data.format(category=category, name=name), verify=False)
        StockCategory.objects.filter(name=name).update(name=category)

        return redirect('stock_category')
    else:
        return render(request, 'update-stock-category.html', {'name': name})


def delete_stock_category(request, name):
    api = 'http://127.0.0.1:8000/'
    data = """<ENVELOPE Action="">

                <HEADER>
                    <VERSION>1</VERSION>
                    <TALLYREQUEST>IMPORT</TALLYREQUEST>
                    <TYPE>DATA</TYPE>
                    <ID>All Masters</ID>
                </HEADER>

                    <BODY>
                        <DESC>
                            <STATICVARIABLES>
                            <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
                            </STATICVARIABLES>
                        </DESC>
                        <DATA>
                            <TALLYMESSAGE>
                                <STOCKCATEGORY NAME="{name}" ACTION="DELETE">
                                    <NAME>{name}</NAME>
                                </STOCKCATEGORY>
                            </TALLYMESSAGE>
                        </DATA>
                    </BODY>

            </ENVELOPE>"""
    response = requests.post(api, data.format(name=name), verify=False)
    StockCategory.objects.filter(name=name).delete()
    return redirect('stock_category')


def stock_items(request):
    api = 'http://127.0.0.1:8000/'

    # stock_data = """
    #                 <ENVELOPE Action="">
    #                   <HEADER>
    #                     <VERSION>1</VERSION>
    #                     <TALLYREQUEST>EXPORT</TALLYREQUEST>
    #                     <TYPE>COLLECTION</TYPE>
    #                     <ID>STOCKITEM</ID>
    #                   </HEADER>
    #                   <BODY>
    #                     <DESC>
    #                       <STATICVARIABLES />
    #                       <TDL>
    #                         <TDLMESSAGE>
    #                             <TYPE>STOCKITEM</TYPE>
    #                         </TDLMESSAGE>
    #                       </TDL>
    #                     </DESC>
    #                   </BODY>
    #                 </ENVELOPE>"""
    # try:
    #     response = requests.post(api, data=stock_data, verify=False, headers={"Content-Type": "text/xml"})
    #
    #     data = xmltodict.parse(response.content)
    #     items = data['ENVELOPE']['BODY']['DATA']['COLLECTION']['STOCKITEM']
    #
    #     names = []
    #     # for category in category_data:
    #     #     name = category['LANGUAGENAME.LIST']['NAME.LIST']['NAME']
    #     #     names.append(name)
    #     #
    #     # context = {'names': names}
    #
    #     if isinstance(items, list):
    #         for item in items:
    #             name = item['LANGUAGENAME.LIST']['NAME.LIST']['NAME']
    #             names.append(name)
    #     elif isinstance(items, dict):
    #         name = items['LANGUAGENAME.LIST']['NAME.LIST']['NAME']
    #         names.append(name)
    #
    # except Exception as e:
    #     print(f"Error fetching stock items: {e}")
    #     names = []
    data = StockItem.objects.all()
    names = []
    for num in data:
        names.append(num.name)
    context = {'names': names}
    return render(request, 'stock-items.html', context)


def stock_groups(request):
    groups_data = """<ENVELOPE Action="">
                          <HEADER>
                            <VERSION>1</VERSION>
                            <TALLYREQUEST>EXPORT</TALLYREQUEST>
                            <TYPE>COLLECTION</TYPE>
                            <ID>STOCKGROUP</ID>
                          </HEADER>
                          <BODY>
                            <DESC>
                              <STATICVARIABLES/>
                              <TDL>
                                <TDLMESSAGE>
                                  <COLLECTION ISMODIFY="No" ISFIXED="No" ISINITIALIZE="No" ISOPTION="No" ISINTERNAL="No" NAME="CUSTOMSTOCKGROUPCOL">
                                    <TYPE>STOCKGROUP</TYPE>
                                  </COLLECTION>
                                </TDLMESSAGE>
                              </TDL>
                            </DESC>
                          </BODY>
                        </ENVELOPE>"""
    api = 'http://127.0.0.1:8000/'
    try:
        response = requests.post(api, data=groups_data, verify=False, headers={"Content-Type": "text/xml"})
        data = xmltodict.parse(response.content)
        items = data['ENVELOPE']['BODY']['DATA']['COLLECTION']['STOCKGROUP']

        names = []

        if isinstance(items, list):
            for item in items:
                name = item['LANGUAGENAME.LIST']['NAME.LIST']['NAME']
                names.append(name)
        elif isinstance(items, dict):
            name = items['LANGUAGENAME.LIST']['NAME.LIST']['NAME']
            names.append(name)
    except Exception as e:
        print(f"Error fetching stock items: {e}")
        names = []
    context = {'names': names}
    return render(request, 'stock-groups.html', context)


def add_stock_item(request):
    if request.method == "POST":
        item = request.POST['item']
        item_data = """<ENVELOPE Action="">
                            <HEADER>
                                <VERSION>1</VERSION>
                                <TALLYREQUEST>IMPORT</TALLYREQUEST>
                                <TYPE>DATA</TYPE>
                                <ID>All Masters</ID>
                            </HEADER>
                            <BODY>
                                <DESC>
                                    <STATICVARIABLES>
                                        <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
                                    </STATICVARIABLES>
                                </DESC>
                                    <DATA>
                                        <TALLYMESSAGE>
                                            <STOCKITEM ACTION="CREATE">
                                                <NAME>{item}</NAME>
                                            </STOCKITEM>
                                        </TALLYMESSAGE>
                                    </DATA>
                                   </BODY>
                            </ENVELOPE>"""

        api = 'http://127.0.0.1:8000/'
        q = requests.post(api, data=item_data.format(item=item), verify=False,
                          headers={"Content-Type": "application/xml"})

        data = xmltodict.parse(q.content)
        data2 = json.dumps(data)

        context = {'data': json.loads(data2)}
        StockItem.objects.get_or_create(name=item)
        return redirect('stock_items')

    else:
        return render(request, 'add-stock-item.html')




def add_stock_group(request):
    if request.method == "POST":
        group = request.POST['group']
        group_data = """<ENVELOPE Action="">
                            <HEADER>
                                <VERSION>1</VERSION>
                                <TALLYREQUEST>IMPORT</TALLYREQUEST>
                                <TYPE>DATA</TYPE>
                                <ID>All Masters</ID>
                            </HEADER>
                            <BODY>
                                <DESC>
                                    <STATICVARIABLES>
                                        <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
                                    </STATICVARIABLES>
                                </DESC>
                                    <DATA>
                                        <TALLYMESSAGE>
                                            <STOCKGROUP ACTION="CREATE">
                                                <NAME>{group}</NAME>
                                            </STOCKGROUP>
                                        </TALLYMESSAGE>
                                    </DATA>
                            </BODY>
                            </ENVELOPE>"""

        api = 'http://127.0.0.1:8000/'
        q = requests.post(api, data=group_data.format(group=group), verify=False,
                          headers={"Content-Type": "application/xml"})

        data = xmltodict.parse(q.content)
        data2 = json.dumps(data)

        context = {'data': json.loads(data2)}
        StockGroup.objects.get_or_create(name=group)
        return redirect('stock_groups')
    else:
        return render(request, 'add-stock-group.html')



def groups_list(request):

    xml_request = """
    <ENVELOPE>
        <HEADER>
            <VERSION>1</VERSION>
            <TALLYREQUEST>EXPORT</TALLYREQUEST>
            <TYPE>COLLECTION</TYPE>
            <ID>Group Collection</ID>
        </HEADER>
        <BODY>
            <DESC>
                <STATICVARIABLES>
                    <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
                </STATICVARIABLES>
                <TDL>
                    <TDLMESSAGE>
                        <COLLECTION NAME="Group Collection" ISMODIFY="No">
                            <TYPE>Group</TYPE>
                            <FETCH>NAME, PARENT, GUID</FETCH>
                        </COLLECTION>
                    </TDLMESSAGE>
                </TDL>
            </DESC>
        </BODY>
    </ENVELOPE>"""

    try:

        response = requests.post("http://127.0.0.1:8000/", data=xml_request.encode('utf-8'),
                                 headers={"Content-Type": "text/xml"})
        raw_xml = response.content.decode('utf-8', errors='replace')

        cleaned = re.sub(r'&#4;', '', raw_xml)
        data = xmltodict.parse(cleaned)

        groups_raw = data['ENVELOPE']['BODY']['DATA']['COLLECTION'].get('GROUP', [])
        groups = []

        if isinstance(groups_raw, list):
            for group in groups_raw:
                name = group.get('@NAME', 'Unnamed')
                parent = group.get('PARENT',{}).get('#text', 'None')
                groups.append({'name': name, 'parent': parent})
        elif isinstance(groups_raw, dict):
            name = groups_raw.get('NAME', 'Unnamed')
            parent = groups_raw.get('PARENT',{}).get('#text', 'None')
            groups.append({'name': name, 'parent': parent})

    except Exception as e:
        print(f"Error fetching groups from Tally: {e}")
        groups = []

    return render(request, 'tally-groups.html', {'groups': groups})

# name - Customer ABC
# parent - Sundry Debtors
def create_ledger(request):
    if request.method == "POST":
        name = request.POST['name']
        parent = request.POST['parent']

        xml_request = """
                        <ENVELOPE>
                            <HEADER>
                                <TALLYREQUEST>Import Data</TALLYREQUEST>
                            </HEADER>
                            <BODY>
                            <IMPORTDATA>
                                <REQUESTDESC>
                                    <REPORTNAME>All Masters</REPORTNAME>
                                      </REQUESTDESC>
                                      <REQUESTDATA>
                                  <TALLYMESSAGE xmlns:UDF="TallyUDF">
                                         <LEDGER Action="Create">
                                            <NAME>{name}</NAME>
                                            <PARENT>{parent}</PARENT>
                                         </LEDGER>
                                  </TALLYMESSAGE>
              </REQUESTDATA>
            </IMPORTDATA>
            </BODY>
            </ENVELOPE>"""

        response = requests.post("http://127.0.0.1:8000/", data=xml_request, headers={"Content-Type": "text/xml"})
        data = xmltodict.parse(response.content)
        data2 = json.dumps(data)

        context = {'data': json.loads(data2)}
        Ledger.objects.get_or_create(name=name, parent=parent)
        return redirect('stock_items')
    else:
        return render(request, 'add-ledger.html')



def ledger_list(request):
    xml_request = """
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Collection</TYPE>
                <ID>Ledger</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <COLLECTION NAME="Ledger" ISMODIFY="No">
                                <TYPE>Ledger</TYPE>
                            </COLLECTION>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>
        """

    response = requests.post("http://127.0.0.1:8000/", data=xml_request, headers={"Content-Type": "text/xml"})
    data_dict = xmltodict.parse(response.content)
    ledgers = []
    try:
        ledgers_raw = data_dict['ENVELOPE']['BODY']['DATA']['COLLECTION']['LEDGER']
        if isinstance(ledgers_raw, list):
            for ledger in ledgers_raw:
                name = ledger.get('@NAME', 'Unnamed')
                parent = ledger.get('PARENT', {}).get('#text', 'None')
                ledgers.append({'name': name, 'parent': parent})
        else:
            ledgers.append({
                'name': ledgers_raw.get('NAME', 'Unnamed'),
                'parent': ledgers_raw.get('PARENT', 'None')
            })
    except Exception as e:
        print("Error parsing:", e)
        ledgers = []
    return render(request, 'ledger-list.html', {'ledgers': ledgers})



def sales_voucher(request):
    xml_request = """<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Vouchers</REPORTNAME>
        <STATICVARIABLES>
          <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
        </STATICVARIABLES>
      </REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE xmlns:UDF="TallyUDF">
          <VOUCHER VCHTYPE="Sales" ACTION="Create" OBJVIEW="Accounting Voucher View">
            <DATE>20250705</DATE>
            <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
            <VOUCHERNUMBER>1</VOUCHERNUMBER>
            <PARTYLEDGERNAME>Customer ABC</PARTYLEDGERNAME>
            <PERSISTEDVIEW>Accounting Voucher View</PERSISTEDVIEW>
            <ISINVOICE>Yes</ISINVOICE>
            <LEDGERENTRIES.LIST>
              <LEDGERNAME>Customer ABC</LEDGERNAME>
              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
              <ISPARTYLEDGER>Yes</ISPARTYLEDGER>
              <AMOUNT>-21546.00</AMOUNT>
            </LEDGERENTRIES.LIST>
            <LEDGERENTRIES.LIST>
              <LEDGERNAME>Cash</LEDGERNAME>
              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
              <AMOUNT>21546.00</AMOUNT>
            </LEDGERENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>
"""

    response = requests.post("http://127.0.0.1:8000/", data=xml_request, headers={"Content-Type": "text/xml"})
    data = xmltodict.parse(response.content)
    data2 = json.dumps(data)
    context = {'data': json.loads(data2)}
    return redirect('stock_items')


def create_balance_sheet(request):
    xml_request = """
    <ENVELOPE>
      <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Balance Sheet</ID>
      </HEADER>
      <BODY>
        <DESC>
          <STATICVARIABLES>
            <SVCURRENTCOMPANY>ABC</SVCURRENTCOMPANY>
            <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
          </STATICVARIABLES>
        </DESC>
      </BODY>
    </ENVELOPE>
    """

    response = requests.post("http://127.0.0.1:8000/", data=xml_request, headers={"Content-Type": "text/xml"})

    try:
        data = xmltodict.parse(response.content)
        envelope = data.get("ENVELOPE", {})
        names = envelope.get("BSNAME", [])
        amounts = envelope.get("BSAMT", [])

        balance_sheet = []

        for i in range(min(len(names), len(amounts))):
            name = names[i].get("DSPACCNAME", {}).get("DSPDISPNAME", "Unknown")
            amt_dict = amounts[i]
            amount = amt_dict.get("BSMAINAMT") or amt_dict.get("BSSUBAMT") or "0.00"

            balance_sheet.append({
                'name': name,
                'amount': amount
            })

    except Exception as e:
        print("Error:", e)
        balance_sheet = []

    return render(request, 'balance-sheet.html', {'balance_sheet': balance_sheet})

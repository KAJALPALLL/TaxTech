from django.urls import path
from. import views

urlpatterns= [

    path('base', views.base, name='base'),
    #                           Stock Category
    path('stock-category',views.stock_category,name='stock_category'),
    path('add-stock-category',views.add_stock_category,name='add_stock_category'),
    path('update-stock-category/<str:name>',views.update_stock_category,name='update_stock_category'),
    path('delete-stock-category/<str:name>', views.delete_stock_category, name='delete_stock_category'),

#     Stock Items
    path('stock-items',views.stock_items,name='stock_items'),
    path('add-stock-item',views.add_stock_item,name='add_stock_item'),

#     Stock Groups
    path('stock-groups', views.stock_groups, name='stock_groups'),
    path('add-stock-group',views.add_stock_group,name='add_stock_group'),

#      Ledger and Group
    path('groups-list', views.groups_list, name='groups_list'),
    path('create-ledger', views.create_ledger, name='create_ledger'),
    path('ledger-list', views.ledger_list, name='ledger_list'),
    path('sales-voucher', views.sales_voucher, name='sales_voucher'),
    path('create-balance-sheet', views.create_balance_sheet, name='create_balance_sheet'),

]




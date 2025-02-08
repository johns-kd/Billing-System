# Billing-System

Configuration in backend/app/app/core/config.py

1.Open the config.py file in the project directory.
2.Update them as needed.

  base_url = "http://your-new-ip-or-domain" 
  base_dir = "/your/new/upload/path"
  base_upload_folder = "/your/new/base/upload/folder"

3.Save the file and restart the application for the changes to take effect.


Frontend Configuration

To update the base URL in the frontend, follow these steps:

1.Open the relevant frontend/index.html file where the baseUrl is defined.
  Locate the following line:

  const baseUrl = 'http://192.168.1.214:8002';

2.Update it with your new URL. For example:

   const baseUrl = 'http://your-new-ip-or-domain:port';

3.save the file and restart the application if necessary.


Database Location

You can view the database file at:

   backend/app/app/billing_system.db
   
Projectflow Picture Location

You can view the Picture's at:

   pictures/
   
You can view the sample invoice at:
  backend/app/app/test.pdf
  
  
Billing Process

1 Select Product & Quantity
2 Generate Bill (Preview)
3 Create Order & Send Invoice
4 Order List - Download Invoice & Send Email

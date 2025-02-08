from app.core.config import settings
from datetime import datetime
from app.models import *
import sys
import math
import os
import shutil
import smtplib
import tracemalloc
from num2words import num2words
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
tracemalloc.start()

async def send_mail(receiver_email, message):  # Demo
    sender_email = "maestronithishraj@gmail.com"
    password = "ycjanameheveewtb"

    msg = message

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg)
    server.quit()

    return True

def file_upload(file, f_name=None):
    base_dir = settings.BASE_UPLOAD_FOLDER + settings.BASE_DIR

    dt = str(int(datetime.utcnow().timestamp()))

    try:
        os.makedirs(base_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit(f"Can't create {base_dir}: {e}")

    output_dir = base_dir + "/"

    filename = file.filename

    file_ext = os.path.splitext(filename)[1]
    files_name = filename.split(".")

    save_full_path = f'{output_dir}{files_name[0]}{dt}{file_ext}'
    print(save_full_path)
    file_store_path = f"{settings.BASE_DIR}/{files_name[0]}{dt}{file_ext}"
    with open(save_full_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return save_full_path, file_store_path

def get_pagination(row_count=0, current_page_no=1, default_page_size=10):
    current_page_no = current_page_no if current_page_no >= 1 else 1

    total_pages = math.ceil(row_count / default_page_size)

    if current_page_no > total_pages:
        current_page_no = total_pages

    limit = current_page_no * default_page_size
    offset = limit - default_page_size

    if limit > row_count:
        limit = offset + (row_count % default_page_size)

    limit = limit - offset

    if offset < 0:
        offset = 0

    return [total_pages, offset, limit]

from fpdf import FPDF
import os, sys

class InvoicePdf(FPDF):
    def header(self):
        self.set_font('Times', 'B', 8)
    
    def footer(self):
        pass

def profile(pdf, data):
    data = data

    pdf.add_page() 
    pdf.set_draw_color(0, 0, 0)

    pdf.set_font("Times", size=15)

    pdf.text(90, 7, "Invoice")

    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)
    
    pdf.set_font("Times", "B", size=20)

    pdf.text(75, 16, "Billing Project")

    pdf.set_font("Times", size=12)

    pdf.text(58, 25, "2nd Floor,10B,Nehru Road,State Bank of India opposite,")
    pdf.text(65, 30, "Anna nagar,Tirupur-641652")
    pdf.text(73, 35, "State Name : Tamil Nadu, Code : 33")
    pdf.text(75, 40, "Contact : 91992992,9737737")
    pdf.text(71, 45, "E-Mail : test.india@gmail.com")

    pdf.set_font("Times",size=10)

    pdf.text(130,50,"Customer Email :")
    pdf.set_font("Times", "B", size=10)

    pdf.text(155,50,data["email_id"])

    pdf.set_font("Times", "B", size=18)

    pdf.set_font("Times", size=12)

    pdf.line(10, 55, 200, 55)  

    end_line = 55

    pdf.set_font("Times", "B", size=12)

    pdf.text(13, 267, "Declaration")
    pdf.line(13, 269, 35, 269)

    pdf.set_font("Times", size=10)
    pdf.text(13, 273, "We declare that this invoice shows the actual price of the ")
    pdf.text(13, 278, "goods described and that all particulars are true and correct.")

    pdf.line(105, 263, 200, 263)
    pdf.line(105, 263, 105, 287)

    pdf.set_font("Times", "B", 12)
    pdf.text(115, 267, "for Billing System")

    pdf.set_font("Times", size=12)
    pdf.text(150, 284, "Authorised Signatory")

    return end_line

def header_for_item(pdf, line_y):
    if line_y >= 280:
        profile_pg = profile(pdf, [])
        line_y = 60

    pdf.line(10, line_y, 200, line_y)  

    header_y = line_y + 6
    pdf.set_font("Times", "B", size=10)

    pdf.line(10, line_y, 10, line_y + 12) 
    
    pdf.text(13, header_y - 1, txt="S. ")
    pdf.text(12, header_y + 3, txt="No")
    pdf.line(20, line_y, 20, line_y + 12)  

    pdf.text(26, header_y, txt="Product Name")
    pdf.line(105, line_y, 105, line_y + 12)  

    pdf.text(106, header_y, txt="Quantity")
    pdf.line(123.5, line_y, 123.5, line_y + 12)  

    pdf.text(124, header_y, txt="Price")
    pdf.line(139, line_y, 139, line_y + 12)  

    pdf.text(142, header_y, txt="Gst")
    pdf.line(149, line_y, 149, line_y + 12)  

    pdf.text(149, header_y, txt="Gst Amount")
    pdf.line(168, line_y, 168, line_y + 12)  

    pdf.text(173, header_y, txt="Total Amount")
    pdf.line(10, line_y + 12, 200, line_y + 12)  

    return line_y + 12

def end_page(pdf, data, line_y):
    data = data
    header_y = line_y + 15

    if (header_y + 10) >= 262:
        profile_pg = profile(pdf, [])
        header_y = 60
    else:
        header_y += 4

    pdf.set_font("Times", size=12)

    pdf.text(115, header_y, "Company's Bank Details")
    pdf.text(115, header_y + 5, "Bank Name")
    pdf.text(115, header_y + 10, "A/c No.")
    pdf.text(115, header_y + 15, "Branch&IFS Code")

    pdf.text(148, header_y + 5, ":")
    pdf.text(148, header_y + 10, ":")
    pdf.text(148, header_y + 15, ":")

    pdf.set_font("Times", "B", size=10)

    pdf.text(152, header_y + 5, "KOTAK MAHINDRA BANK")
    pdf.text(152, header_y + 10, "2438458078")
    pdf.text(152, header_y + 15, "Tiruppur & K#$000492")
  
    return True

def generate_invoice(data):
    data_lt = data

    pdf = InvoicePdf('P', 'mm', 'A4')

    base_dir = settings.BASE_UPLOAD_FOLDER + "/"
    
    try:
        os.makedirs(base_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit(f"Can't create {base_dir}: {e}")

    output_dir = base_dir + settings.BASE_DIR + "/invoice_export/"
    out_dir_2 = f"{settings.BASE_DIR}/invoice_export/"
    
    try:
        os.makedirs(output_dir, mode=0o777, exist_ok=True)
    except OSError as e:
        sys.exit(f"Can't create {output_dir}: {e}")

    dt = str(int(datetime.utcnow().timestamp()))

    file_name = f"{output_dir}Invoice{dt}.pdf"
    file_name2 = f"{out_dir_2}Invoice{dt}.pdf"  

    profile_page = profile(pdf, data_lt)

    page_limit = 20
    s_no = 0
    order_list = data["product_list"]
    total = 0

    if order_list != []:
        y_for_val = header_for_item(pdf, profile_page)

        for row in order_list:
            pdf.set_font('Times', size=9)

            prod_name = f'{row["product_code"]}-{row["product_name"]}'
            product_txt_width = pdf.get_string_width(prod_name)
            lines_for_product = (product_txt_width / 32)

            if lines_for_product > int(lines_for_product):
                lines_for_product = int(lines_for_product) + 1

            s_no += 1
            check_y = y_for_val + (lines_for_product * 4) + 4

            if check_y >= 262:
                y_for_val = header_for_item(pdf, check_y)

            y_for_bottom = y_for_val + (lines_for_product * 4) + 4
            last_bottom_y = y_for_val
            y_for_val = y_for_val + 4

            pdf.set_font('Times', size=9)
            pdf.line(10, last_bottom_y, 10, y_for_bottom)  

            pdf.text(13, y_for_val, txt=str(s_no))
            pdf.line(20, last_bottom_y, 20, y_for_bottom)  

            pdf.set_xy(23, y_for_val - 3)
            pdf.multi_cell(75, 4, txt=prod_name)
            pdf.line(105, last_bottom_y, 105, y_for_bottom)  

            pdf.set_font('Times', size=8.5)
            pdf.text(106, y_for_val, txt=str(row["quantity"] or ""))
            pdf.line(123.5, last_bottom_y, 123.5, y_for_bottom)  

            pdf.text(126, y_for_val, txt=str(row["unit_price"] or ""))
            pdf.line(139, last_bottom_y, 139, y_for_bottom)  

            pdf.text(141, y_for_val, txt=str(row["gst_percent"] or ""))
            pdf.line(149, last_bottom_y, 149, y_for_bottom)  

            pdf.text(152, y_for_val, txt=str(row["gst_amount"] or ""))
            pdf.line(168, last_bottom_y, 168, y_for_bottom)  

            pdf.set_font('Times', "B", size=10)
            tota_amt_width = pdf.get_string_width(str(row["total_price"] or 0.00))
            total += float(row["total_price"] or 0.00)
            pdf.text(196.5 - tota_amt_width, y_for_val, txt=str(row["total_price"] or 0.00))

            pdf.set_font('Times', size=9)
            pdf.line(10, y_for_bottom, 200, y_for_bottom)
            y_for_val += (lines_for_product * 4)

        if total != 0:        
            pdf.set_font('Times', "B", size=10)
            pdf.text(155, y_for_bottom + 5, txt="Total")
            total_width = pdf.get_string_width(str(f"{total:.2f}"))
            pdf.line(168, y_for_bottom, 168, y_for_bottom + 7)  
            pdf.line(10, y_for_bottom + 7, 200, y_for_bottom + 7)  
            pdf.text(196.5 - total_width, y_for_bottom + 5, txt=str(f"{total:.2f}"))

        pdf.set_font("Times", size=8)
        amount_det = data["amount_details"]
        data_set = {}

        if y_for_bottom + 50 >= 262:
            y_for_bottom = profile(pdf, data_lt)
        y_for_bottom += 14

        for each_tax in amount_det:
            width = pdf.get_string_width(str(each_tax["value"] or ""))
            data_set[each_tax["sort_order"]] = {
                "title": each_tax["title"],
                "value": each_tax["value"] or "",
                "width": width
            }

        for name, each_amt in data_set.items():
            pdf.set_font("Times", "B", size=10)
            pdf.text(139, y_for_bottom, each_amt["title"])
            pdf.text(164, y_for_bottom, ":")
            pdf.text(196.5 - each_amt["width"], y_for_bottom, str(each_amt["value"]))
            y_for_bottom += 5
        
        y_for_bottom += 5
        deno_det = data["denominations"]
        data_set = {}

        if y_for_bottom + 50 >= 262:
            y_for_bottom = profile(pdf, data_lt)
        y_for_bottom += 5

        for each_tax in deno_det:
            width = pdf.get_string_width(str(each_tax["value"] or ""))
            data_set[each_tax["sort_order"]] = {
                "title": each_tax["title"],
                "value": each_tax["value"] or "",
                "width": width
            }
        pdf.set_font("Times", "B", size=10)
        pdf.text(139, y_for_bottom-6, "Balance Denominations")

        for name, each_amt in data_set.items():
            pdf.set_font("Times", "B", size=10)
            pdf.text(139, y_for_bottom, each_amt["title"])
            pdf.text(164, y_for_bottom, ":")
            pdf.text(196.5 - each_amt["width"], y_for_bottom, str(each_amt["value"]))
            y_for_bottom += 5




        # if "amount_details" in data:   
        #     pdf.set_font('Times', "B", size=9)

        #     for order_value in data["amount_details"]:
        #         check_y = y_for_bottom
        #         if check_y >= 262:
        #             y_for_bottom = header_for_item(pdf, check_y)
        #         pdf.text(58, y_for_bottom + 5, txt="title")
        #         pdf.line(70, y_for_bottom, 70, y_for_bottom + 7)  
        #         total_tax_value = pdf.get_string_width(str(order_value["value"] or 0.00))
        #         pdf.text(93 - total_tax_value, y_for_bottom + 5, txt=str(order_value["value"] or 0.00))
        #         pdf.line(95, y_for_bottom, 95, y_for_bottom + 7)  
        #         y_for_bottom += 5

        pdf.line(10, y_for_bottom + 7, 200, y_for_bottom + 7)
        
        if "total_amount" in data:
            pdf.set_font('Times', size=10)
            pdf.text(15, y_for_bottom + 5, "Amount Chargeable (in words) :")
            words = num2words(data["total_amount"], lang='en_IN').title()
            pdf.set_font('Times', "B", size=10)
            pdf.set_xy(63, y_for_bottom + 1)
            pdf.multi_cell(130, 5, str(words))

    end_page(pdf, data_lt, y_for_bottom + 5)
    pdf.output(file_name)
    pdf.output("test.pdf")

    reply = f"{settings.BASE_DOMAIN}{file_name2}"
    return {"status": 1, "msg": "Success", "file_url": reply, 
            "save_path":file_name2,
            "file_path": file_name}


async def send_mail_for_invoice(receiver_email,subject, message,attachment_path):  # Demo

    from_email =settings.FROM_MAIL
    # from_email = "sales.cbe@rkecran.com"
    to_email = receiver_email
    # to_email = receiver_email->set list method

    subject = subject
    body = message


    filename = "invoice.pdf"
    attachment_path = attachment_path

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    # msg['To'] = ", ".join(to_email) 

    msg['Subject'] = subject
    html = """\
    <html>
    <head></head>
    <body>
        <p>{message}</p>
    </body>
    </html>
    """

    html = html.format(message=body) 
    msg.attach(MIMEText(html, 'html'))


    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)


    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, settings.APP_PASSWORD)

        # server.login(from_email, "spxe jtwe qcvq qdsx")
        server.sendmail(from_email, to_email, msg.as_string())
    
    return {"status":1,"msg":"Success"}

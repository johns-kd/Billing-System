from fastapi import APIRouter, Depends ,Form
from sqlalchemy.orm import Session
from app.models import *
from app.schemas import *
from app.utils import *
from app.api import deps
from app.core.config import settings
from datetime import datetime
from app.utils import get_pagination

router = APIRouter()

@router.post("/create-order")
async def create_order(
    *, db: Session = Depends(deps.get_db),
    data_obj: OrderCreate
):
    if data_obj.token:
        user = deps.get_user_by_token(db=db, token=data_obj.token)
        if not user:
            return {"status": -1, "msg": "Token expired"}
        user_id = user.id

    if data_obj.email:
        exist_user = db.query(User).filter(
            User.status==1,
            User.email==data_obj.email
        ).first()
        if not exist_user:
            add_customer = User(
                email = data_obj.email,
                created_at = datetime.now(settings.tz_IN),
                updated_at = datetime.now(settings.tz_IN),
                status  = 1
            )
            db.add(add_customer)
            db.commit()
            user_id = add_customer.id
        else:
            user_id = exist_user.id

        
    total_order_price = 0
    total_order_tax_price = 0
    get_order = db.query(Orders)
    
    get_last_order = get_order.filter(Orders.status==1,
                                    Orders.customer_id==user_id).\
                                        order_by(Orders.order_no.desc()).first()


    create_order = Orders(
                    order_no = (int(get_last_order.order_no if get_last_order.order_no else 0) + 1) if get_last_order else 1,
                    email_id = data_obj.email if data_obj.email else None,
                    paid_amount =data_obj.paid_amount,
                    customer_id = user_id,
                    created_at = datetime.now(settings.tz_IN),
                    status = 1,
                )
    db.add(create_order)
    db.commit()
    
    product_list =  data_obj.product_list

    tax_det={}
            
    for each_product in product_list:
        get_product = db.query(Products).filter(Products.id == each_product.product_id,
                                               Products.status == 1).first()
        
        if not get_product:
            continue

        if get_product.available_quantity < each_product.quantity:
            create_order.status = -1
            db.commit()
            return {"status":0,"msg":f"Product {get_product.name} is out of stock"}
                    
        total_price = each_product.quantity*get_product.actual_price
                
        add_products = OrderedProducts(
            order_id = create_order.id,
            product_id = each_product.product_id,
            quantity = each_product.quantity,
            unit_price = get_product.actual_price,
            total_price = total_price,
            gst_percent = get_product.tax_percentage,
            status = 1
        )
        db.add(add_products)
        db.commit()
        get_product.available_quantity = float(get_product.available_quantity) - each_product.quantity
        db.commit()

        total_order_price += total_price
        
        gst_amount = float((float(total_price) * float(get_product.tax_percentage))/100)
           
        add_products.gst_amount = gst_amount
        total_order_tax_price+=gst_amount
        db.commit()

        if get_product.tax_percentage not in tax_det:
            tax_det[get_product.tax_percentage] = gst_amount
        else:
            tax_det[get_product.tax_percentage] += gst_amount
            
    grant_total_price = float(total_order_tax_price) + float(total_order_price)
        

    add_total = OrderTotal(
        order_id = create_order.id,
        code = "sub_total",
        title = "Sub Total",
        value = total_order_price,
        sort_order = 1,
        amount_type =1,
        status = 1
    )    
    db.add(add_total)
    db.commit()
    i=1
    for name ,data in tax_det.items():
        i+=1
        add_total = OrderTotal(
        order_id = create_order.id,
        code = "tax",
        title = f"{name}%",
        value = data,
        sort_order = i,
        amount_type =1,
        status = 1
    )    
        db.add(add_total)
        db.commit()

    add_total = OrderTotal(
        order_id = create_order.id,
        code = "grand_total",
        title = "Grand Total",
        value = grant_total_price,
        amount_type =1,
        sort_order = i+1,
        status = 1
    )    
    db.add(add_total)
    db.commit()
    
    sort_order = i+2

    i=0
    paid_amount =0
    for data_obj in data_obj.denominations:
        i+=1
        add_total = OrderTotal(
            order_id = create_order.id,
            code = data_obj.amount,
            title = f'{data_obj.amount}*{data_obj.count}',
            value = data_obj.amount*data_obj.count,
            sort_order = i,
            amount_type =2,
            status = 1
        )    
        db.add(add_total)
        db.commit()
        paid_amount+=data_obj.amount*data_obj.count

    add_total = OrderTotal(
        order_id = create_order.id,
        code = "paid_amount",
        title = "Paid Amount",
        value = paid_amount,
        amount_type =1,
        sort_order = sort_order,
        status = 1
    )    
    db.add(add_total)
    db.commit()
    balance_amount = grant_total_price - paid_amount
    add_total = OrderTotal(
        order_id = create_order.id,
        code = "balance_amount",
        title = "Balance Amount",
        value = balance_amount,
        amount_type =1,
        sort_order = sort_order+1,
        status = 1
    )    
    db.add(add_total)
    db.commit()

    msg = "Order Placed Successfully"
    create_order.total_amount = grant_total_price
    create_order.paid_amount = paid_amount
    create_order.balance_amount = balance_amount
            
    db.commit()

    return {"status":1,"msg":f"{msg}","order_id":create_order.id,"order_no":create_order.order_no,"total":grant_total_price}
   



@router.post("/demo-view")
def demo_view( *,db: Session = Depends(deps.get_db),
              data_obj:DemoView
                  ):
       
    total_order_price = 0
    total_order_tax_price = 0
    data_lt=[]
    tax_det = {}
    for each_product in data_obj.product_list:
        get_product = db.query(Products).filter(Products.id == each_product.product_id,
                                               Products.status == 1).first()
        
        if not get_product:
            continue
        total_price = each_product.quantity*get_product.actual_price
        gst_amount = float((float(total_price) * float(get_product.tax_percentage))/100)
        
        data_lt.append({
        "product_id":each_product.product_id,
        "quantity":each_product.quantity,
        "name":get_product.name  ,
        "product_code":get_product.product_code  ,
        "short_description":get_product.short_description  ,
        "actual_price":get_product.actual_price,
        "price":get_product.price,
        "tax_percentage":get_product.tax_percentage,
        "total_price":total_price,
        "gst_amount":gst_amount,
        "img_path":f"{settings.BASE_DOMAIN}{get_product.img_path}" if get_product.img_path else None,
        "img_alt":get_product.img_alt ,
        
        })

        total_order_price += total_price
            
        total_order_tax_price += gst_amount


        if get_product.tax_percentage not in tax_det:
            tax_det[get_product.tax_percentage] = gst_amount
        else:
            tax_det[get_product.tax_percentage] += gst_amount
    
    grant_total_price = float(total_order_tax_price) + float(total_order_price)
    final_data=[]
    final_data.append({"code": "sub_total",
        "title": "Sub Total",
        "value": total_order_price,
        "amount_type": 1,
        "sort_order": 1})
    i=0

    for name ,data in tax_det.items():
        i+=1

        final_data.append({"code": "tax",
            "title": f"{name}%",
            "value": data,
            "amount_type": 1,
            "sort_order": i})
        

    paid_amount = 0
    final_data.append({"code": "grand_total",
        "title": "Grand Total",
        "value": grant_total_price,
        "sort_order": i+1})
    
    denomina = []
    i=0
    for each_den in data_obj.denominations:
        i+=1
        denomina.append({
            "code": each_den.amount,
            "title": f"{each_den.amount}*{each_den.count}",
            "value": each_den.amount*each_den.count,
            "sort_order": i,
            "amount_type": 2
        })
        paid_amount+=each_den.amount*each_den.count

    final_data.append({"code": "paid_amount",
        "title": "Paid Amount",
        "value": paid_amount,
        "sort_order": i+2})
    

    final_data.append({"code": "balance_Amount",
        "title": "Balance Amount",
        "value": grant_total_price-paid_amount,
        "sort_order": i+3})
    
    return {
        "status": 1, "msg":"success",
        "items":data_lt,
        "denominations":denomina,
        "amount_details":final_data
            }            


@router.post("/order-list")
def order_list( *,db: Session = Depends(deps.get_db), token: str = Form(None),order_no:str=Form(None),
               email:str=Form(None),
              from_date :datetime = Form(None), to_date :datetime = Form(None),
              customer_id : int= Form(None),page:int=1,size:int=10):
    
    get_order = db.query(Orders).filter(Orders.status == 1)
    
    if token:
        user = deps.get_user_by_token(db=db, token=token)
        if not user:
            return {"status": -1, "msg": "Token expired"}

        if user.type == 2:
            get_order = get_order.filter(Orders.customer_id == user.id)

    if email:
        get_order = get_order.filter(Orders.email_id == email)


    if customer_id:
        get_order = get_order.filter(Orders.customer_id == customer_id)
        
    if order_no:
        get_order = get_order.filter(Orders.order_no.like("%"+order_no+"%"))
                    

    if from_date:
        get_order = get_order.filter(Orders.created_at >= from_date)
    if to_date:
        get_order = get_order.filter(Orders.created_at <= to_date)
        
    count=get_order.count()

    total_pages, offset, limit = get_pagination(row_count=count, current_page_no=page, default_page_size=size)
    
    get_order = get_order.order_by(Orders.created_at.desc())


    get_order=get_order.limit(limit).offset(offset)


    get_order = get_order.all()
    data_lt = []

    for row in get_order:
        data_lt.append({
            "id":row.id ,
            "paid_amount":row.paid_amount ,
            "balance_amount":row.balance_amount ,
            "order_no":row.order_no ,
            "customer_id":row.customer_id ,
            "email_id":row.email_id,
            "total_amount":row.total_amount ,
            "customer_name":row.user.user_name if row.customer_id else None,
            "created_at":row.created_at ,
            })
    return {
        "status": 1, "msg":"success",
        "items":data_lt,
        "total": count,
        "total_page":total_pages,
        "page": page,"size": size
        }
   



@router.post("/view-order")
def view_order( *,db: Session = Depends(deps.get_db),email:str=Form(None),
                token: str = Form(None),order_id:int=Form(...)):
  
    get_order = db.query(Orders).filter(Orders.status == 1,
                                        Orders.id == order_id)
    user = None
    if token:
        user = deps.get_user_by_token(db=db,token = token)
        if not user:
            return {"status": -1, "msg": "Token expired"}
        if user.type == 2:
            get_order = get_order.filter(Orders.customer_id == user.id)

            if not get_order.first():
                return {"status":0,"msg":"Invalid Request"}
    
    elif email:
        user = db.query(User).filter(User.status==1,
                                     User.email==email).first()
        if not user:
            return {"status":0,"msg":"Invalid Email Id"}
        get_order = get_order.filter(Orders.customer_id == user.id)

        if not get_order.first():
            return {"status":0,"msg":"Invalid Request"}

    get_order = get_order.first()
        
    data_lt = []
    if get_order:
        
        get_products = db.query(OrderedProducts).filter(OrderedProducts.status == 1, OrderedProducts.order_id == get_order.id).all()
        for row in get_products:
            
            data_lt.append({
                "id":row.id if row.id else None,
                "product_id":row.product_id ,
                "product_name":row.products.name if row.product_id else None,
                "product_code":row.products.product_code if row.product_id else None,
                "quantity":row.quantity ,
                "unit_price":row.unit_price if row.unit_price else None,
                "total_price": row.total_price if row.total_price else None,
                "gst_percent":row.gst_percent ,
                "gst_amount": row.gst_amount,
            })
        
        order_total =[]
        get_order_amounts = db.query(OrderTotal).\
            filter(OrderTotal.status == 1,
                    OrderTotal.amount_type==1,
                        OrderTotal.order_id == get_order.id).all()
        for each_data in get_order_amounts:
            order_total.append({
                "id":each_data.id,
                "title":each_data.title,
                "sort_order":each_data.sort_order,
                "code":each_data.code,
                "value":each_data.value,
            })
        denomi_total =[]
        get_den_amounts = db.query(OrderTotal).\
            filter(OrderTotal.status == 1,
                    OrderTotal.amount_type==2,
                        OrderTotal.order_id == get_order.id).all()
        for each_data in get_den_amounts:
            denomi_total.append({
                "id":each_data.id,
                "title":each_data.title,
                "sort_order":each_data.sort_order,
                "code":each_data.code,
                "value":each_data.value,
            })

        
        data = ({
            "id":get_order.id ,
            "paid_amount":get_order.paid_amount ,
            "order_no":get_order.order_no ,
            "email_id":get_order.email_id ,
            "total_amount":get_order.total_amount ,
            "paid_amount":get_order.paid_amount ,
            "balance_amount":get_order.balance_amount ,
            "customer_id":get_order.customer_id ,
            "customer_name":get_order.user.user_name if get_order.customer_id else None,
            "created_at":get_order.created_at,
            "invoice_path": f"{settings.BASE_DOMAIN}{get_order.invoice_path}" if get_order.invoice_path else None,
            "product_list":data_lt,
            "amount_details":order_total,
            "denominations":denomi_total                
            })

        return {
                "status":1,"msg":"Success","data":data
                }
    else:
        return ({"status":0,"msg":"Invalid Request"}) 
            

@router.post("/export-invoice")
async def export_invoice(*,
    db: Session = Depends(deps.get_db),
    token:str=Form(None),
    email_id:str=Form(None),
    is_send_email:int=Form(None,description="1->Send Email"),
    order_id:int=Form(...)
    ):
    if token:
        user = deps.get_user_by_token(db=db, token=token)
        if not user:
            return {"status": -1, "msg": "Token expired"}
    
    get_order = db.query(Orders).filter(Orders.status ==1,
                                        Orders.id == order_id)
    if email_id:
        user = db.query(User).filter(User.status==1,
                                     User.email==email_id).first()
        if not user:
            return {"status":0,"msg":"Invalid Email Id"}
        get_order = get_order.filter(Orders.customer_id == user.id,
                                     )
        
    if not get_order.first():
        return {"status":0,"msg":"Invalid Request"}
    get_order = get_order.first()
    get_products = db.query(OrderedProducts).filter(OrderedProducts.status == 1, 
                            OrderedProducts.order_id == get_order.id).all()
    data_lt = []
    for row in get_products:
        
        data_lt.append({
            "id":row.id if row.id else None,
            "product_id":row.product_id ,
            "product_name":row.products.name if row.product_id else None,
            "product_code":row.products.product_code if row.product_id else None,
            "quantity":row.quantity ,
            "unit_price":row.unit_price if row.unit_price else None,
            "total_price": row.total_price if row.total_price else None,
            "gst_percent":row.gst_percent ,
            "gst_amount": row.gst_amount,
        })
    
    order_total =[]
    get_order_amounts = db.query(OrderTotal).\
        filter(OrderTotal.status == 1,
                OrderTotal.amount_type==1,
                    OrderTotal.order_id == get_order.id).all()
    for each_data in get_order_amounts:
        order_total.append({
            "id":each_data.id,
            "title":each_data.title,
            "sort_order":each_data.sort_order,
            "code":each_data.code,
            "value":each_data.value,
        })
    denomi_total =[]
    get_den_amounts = db.query(OrderTotal).\
        filter(OrderTotal.status == 1,
                OrderTotal.amount_type==2,
                    OrderTotal.order_id == get_order.id).all()
    for each_data in get_den_amounts:
        denomi_total.append({
            "id":each_data.id,
            "title":each_data.title,
            "sort_order":each_data.sort_order,
            "code":each_data.code,
            "value":each_data.value,
        })

    
    data = ({
        "id":get_order.id ,
        "paid_amount":get_order.paid_amount ,
        "order_no":get_order.order_no ,
        "email_id":get_order.email_id ,
        "total_amount":get_order.total_amount ,
        "paid_amount":get_order.paid_amount ,
        "balance_amount":get_order.balance_amount ,
        "customer_id":get_order.customer_id ,
        "customer_name":get_order.user.user_name if get_order.customer_id else None,
        "created_at":get_order.created_at,
        "product_list":data_lt,
        "amount_details":order_total,
        "denominations":denomi_total                
                })
    
    try:
        pdf_generate = generate_invoice(data)
    except Exception as e:
        return {"status": 0, "msg": "Failed to generate invoice"}
    
    get_order.invoice_path = pdf_generate["save_path"]
    db.commit()
    if is_send_email==1:
        try:

            attachmentPath = pdf_generate["file_path"]

            sendMail = await send_mail_for_invoice(
                receiver_email=get_order.email_id,
                subject="Billing Invoice",
                message=f"Dear Customer,\n\nPlease find the attached invoice for your order no. {get_order.order_no}.\n\nThank you for shopping with us.\n\nRegards,\nTeam",
                attachment_path=attachmentPath
            )

            if sendMail["status"] != 1:
                return {"status": 0, "msg": "Failed to send email"}

            return {"status": 1, "msg": "Email sent successfully","file_url":pdf_generate["file_url"]}

        except Exception as e:
        # Log the exception details
            print(f"Error occurred: {e}")
            return {"status": 0, "msg": "An error occurred while processing the request"}

    else:
        return {
        "status":1,"msg":"Success","file_url":pdf_generate["file_url"]
                        }

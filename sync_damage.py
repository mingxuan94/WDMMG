def my_laz_orders(last_order_id):
    """
    Launch a webdriver that enables User to login to Lazada to allow Bot to start scraping order details 
    @last_order_id (String): Last order ID used to exit this function to avoid unneccessary scraping 
    @time_period (Int): Orders in the last X time_period 
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By 
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time 
    from datetime import datetime

    driver = webdriver.Chrome("/WDMMG/chromedriver")
    driver.get('https://my.lazada.sg/customer/order/index/')

    # Explicitly wait 5 minutes until user is logged in and is able to see past orders
    load_pages = WebDriverWait(driver, 5*60).until(
        EC.presence_of_element_located((By.XPATH,"//i[@class='next-icon next-icon-arrow-down next-icon-small next-select-arrow']"))
    )
    driver.execute_script("arguments[0].click();", load_pages)

    
    # Select last 6 months orders to load pages 
    select_time_period = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH,"//ul[@class='next-menu-content']/li[@value='4']"))
    )
    select_time_period.click()

    # Get total number of pages 
    WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH,"//button[@class='next-btn next-btn-normal next-btn-small next-pagination-item']"))
                )
    find_pages = driver.find_elements_by_xpath("//button[@class='next-btn next-btn-normal next-btn-small next-pagination-item']") 
    pages = int(find_pages[len(find_pages)-1].text)

    # OrderID
    order_ids = []
    current_page = 1
    while current_page <= pages:
        orders = driver.find_elements_by_xpath("//div[@class='orders']/div[@class='order']")

        # Append orderID to list
        for order in orders: 
            order_id = order.find_element_by_xpath('.//div[@class="info-order-left-text"]/a[@class="link"]').text
            try:
                order_status = order.find_element_by_xpath('.//p[@class="capsule"]').text
            except:
                order_status = None
            order_ids.append([order_id, order_status])

            # If we reach last OrderID recorded in transactions table, break the loop and move on 
            if last_order_id == order_id:
                break
        current_page += 1 

        try: 
            # Go to the next page 
            next_page = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH,"//button[text()=\'{current_page}\' and @class='next-btn next-btn-normal next-btn-small next-pagination-item']".format(current_page=current_page)))
                    )
            driver.execute_script("arguments[0].click();", next_page)
            time.sleep(3)
            
        except:
            break

    all_orders = [] 
    for order_id in order_ids: 
        order_data = {} 
        item_list = []
        driver.get('https://my.lazada.sg/customer/order/view/?tradeOrderId=%s'%order_id[0].replace('#',''))
        details = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,"//body[@data-spm='order_details']"))
            )
        order_data["order_id"] = order_id[0]
        order_data["status"] = order_id[1]
        order_data["cart_total"] = details.find_element_by_xpath('.//span[@class="detail-info-total-value"]').text
        order_data["merchant"] = details.find_element_by_xpath('.//span[@class="text link"]').text
        order_date = details.find_element_by_xpath('.//p[@class="text desc light-gray"]').text
        order_data["date"] = datetime.strptime(order_date.split("Placed on ")[1][0:11], "%d %b %Y").strftime("%Y-%m-%d")

        items = details.find_elements_by_xpath('.//div[@class="order-item"]')

        # Multiple items per order
        for item in items:
            item_data = {}
            item_data["name"] = item.find_element_by_xpath('.//div[@class="text title item-title"]').text
            item_data["quantity"] = item.find_element_by_xpath('./div[@class="item-quantity"]').text
            item_data["price"] = item.find_element_by_xpath('.//div[@class="item-price text bold"]').text
            item_list.append(item_data)

        order_data["items"] =  item_list   
        all_orders.append(order_data)
    driver.quit()
    return(all_orders)

def my_shopee_orders(last_order_id, last_x_days):
    """
    Launch a webdriver that enables User to login to Shopee to allow Bot to start scraping order details 
    @last_order_id (String): Last order ID used to exit this function to avoid unneccessary scraping 
    @time_period (Int): Orders in the last X time_period 
    """   
    from selenium import webdriver
    from selenium.webdriver.common.by import By 
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time 
    from datetime import datetime, timedelta

    driver = webdriver.Chrome("/Users/mingxuan/Desktop/flask-plotly/chromedriver")
    driver.get('https://shopee.sg/user/purchase/')

    """
    Last 90 days of data 
    Load 30 orders first
    """
    init_order = 30

    # Explicitly wait 5 minutes until user is logged in and is able to see past orders
    WebDriverWait(driver, 5*60).until(
        EC.presence_of_element_located((By.XPATH,"//div[@class='purchase-list-page__checkout-card-wrapper']"))
    )
    current_orders = driver.find_elements_by_xpath("//div[@class='purchase-list-page__checkout-card-wrapper']")
    last_order_count = 0
    driver.execute_script("window.open('');")
    while len(current_orders) < init_order:
        driver.switch_to.window(driver.window_handles[0])
        last_order_count = len(current_orders)

        # Scroll till end of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait a max of 10 seconds for orders to complete load 
        time.sleep(6)
        current_orders = driver.find_elements_by_xpath("//div[@class='purchase-list-page__checkout-card-wrapper']")
        current_order_count = len(current_orders)

        # Reached the end of the page, exit loop
        if current_order_count == last_order_count:
            break 
        # When we reach the 30th order, open order link in a new tab to find the order date 
        elif current_order_count == init_order:
            # Get order link of the last order 
            last_order = current_orders[current_order_count - 1].find_element_by_xpath('.//a[@class="order-content__item-wrapper"]')
            last_order_link = last_order.get_attribute('href')
            # Open a new tab
            # Switch to the new window
            driver.switch_to.window(driver.window_handles[1])
            driver.get(last_order_link)
            # Check order date
            last_order_date = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH,"//div[@class='stepper__step-date']"))
                )
            if datetime.strptime(last_order_date.text[0:10],"%d-%m-%Y") < datetime.now() - timedelta(last_x_days):
                break
            else:
                init_order += init_order
                # Go back to the original tab and continue scrolling 
                driver.switch_to.window(driver.window_handles[0])

    all_orders = []
    driver.switch_to.window(driver.window_handles[0])
    current_orders = driver.find_elements_by_xpath("//div[@class='purchase-list-page__checkout-card-wrapper']")
    for order in current_orders:
        order_data = {} 
        item_list = []
        order_link = order.find_element_by_xpath('.//a[@class="order-content__item-wrapper"]')
        order_data["order_id"] = order_link.get_attribute('href')

        if last_order_id == order_data["order_id"]:
            break

        order_data["status"] = order.find_element_by_xpath('.//div[@class="order-content-status"]').text
        order_data["cart_total"] = order.find_element_by_xpath('.//span[@class="purchase-card-buttons__total-price"]').text
        order_data["merchant"] = order.find_element_by_xpath('.//span[@class="order-content__header__seller__name"]').text
        
        items = order.find_elements_by_xpath('.//a[@class="order-content__item-wrapper"]')
        for item in items: 
            item_data = {}
            item_data["name"] = item.find_element_by_xpath('.//div[@class="order-content__item__name"]').text
            item_data["quantity"] = item.find_element_by_xpath('.//div[@class="order-content__item__quantity"]').text
            item_data["price"] = item.find_element_by_xpath('.//div[@class="order-content__item__price-text"]').text
            item_list.append(item_data)
        
        order_data["items"] = item_list
        all_orders.append(order_data)

    for i in range(0, len(all_orders)):
        driver.switch_to.window(driver.window_handles[1])
        driver.get(all_orders[i]["order_id"])
        order_date = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,"//div[@class='stepper__step-date']"))
        ).text
        all_orders[i]["date"] = datetime.strptime(order_date[0:10], "%d-%m-%Y").strftime("%Y-%m-%d")
        
    driver.quit()
    return(all_orders)


def upload_order_data(platform, my_orders, db, db_conn, username):
    """
    Clean scraped data before uploading to transactions table 
    @platform (String): Either 'Lazada' or 'Shopee'
    @my_orders (List): Order details (in a dictionary)
    @db (Sqlite3 connection)
    @db_conn (Sqlite3 connection)
    @username (String): Username of session 
    """
    import json

    for i in range(0, len(my_orders)):
        meta = {}
        meta["merchant"] = my_orders[i]["merchant"]

        cart_total = float(my_orders[i]["cart_total"].replace('$','').replace(',',''))
        meta["cart_total"] = cart_total
        total_item_prices = 0
        total_quantity = 0

        for j in range(0, len(my_orders[i]["items"])):
            if platform == 'Shopee':
                my_orders[i]["items"][j]["quantity_int"] = int(my_orders[i]["items"][j]["quantity"].split("x ")[1])
                try:
                    my_orders[i]["items"][j]["total_price"] = float(my_orders[i]["items"][j]["quantity"].split("x ")[1]) * float(my_orders[i]["items"][j]["price"].split("\n")[1].replace("$",""))
                except:
                    my_orders[i]["items"][j]["total_price"] = float(my_orders[i]["items"][j]["quantity"].split("x ")[1]) * float(my_orders[i]["items"][j]["price"].replace("$",""))
                
            else:
                my_orders[i]["items"][j]["quantity_int"] = int(my_orders[i]["items"][j]["quantity"].split("Qty: ")[1])
                my_orders[i]["items"][j]["total_price"] = float(my_orders[i]["items"][j]["quantity"].split("Qty: ")[1]) * float(my_orders[i]["items"][j]["price"].replace("$","").replace(',',''))
                
            total_item_prices += my_orders[i]["items"][j]["total_price"]
            total_quantity += my_orders[i]["items"][j]["quantity_int"]
                
        shipping_per_item = (cart_total - total_item_prices) / max(total_quantity,1)

        for item in  my_orders[i]["items"]:
            db.execute("""
            INSERT INTO
            transactions 
            (username, platform, description, category, damage, date, order_id, source, order_status,meta)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (username
            , platform
            , item["name"]
            , platform
            , item["total_price"] + (shipping_per_item * item["quantity_int"])
            , my_orders[i]["date"]
            , my_orders[i]["order_id"]
            , 'sync'
            , my_orders[i]["status"]
            , json.dumps(meta)
            ))
            db_conn.commit()
import os
from datetime import datetime
from sqlite3 import connect
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Markup
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from login_required import login_required
from updates import update_cat, update_history
import logging 
from sync_damage import my_laz_orders, my_shopee_orders, upload_order_data
from werkzeug.serving import run_simple

from dashplot import create_plot
logging.basicConfig(level=logging.DEBUG)

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLite database
db_conn = connect("wdmmg.db", check_same_thread=False)
db = db_conn.cursor()

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """
    If Get, load index.html
    Else, 
        Check for updated Date & Category filters 
        Call create_plot() function with new parameters
        Reload page 
    """
    global categories
    global damage
    global dash_date_range_filter
    global dash_category_filter
    global date_range

    damage = update_history(db, db_conn, username, date_range_filter, category_filter)
    
    bar, line, total_damage = create_plot(damage, dash_date_range_filter, dash_category_filter)

    for i in date_range:
        if i[0] == dash_date_range_filter:
            summary_date = i[1]
            break 

    if request.method == "GET":
        return render_template('index.html'
        , plot=bar
        , plot_line=line
        , total_damage=round(total_damage,2)
        , categories=categories
        , date_range=date_range
        , select_date=dash_date_range_filter
        , select_cat=dash_category_filter
        , summary=summary_date)
    else:
        # Allow users to toggle date range
        
        if request.form.get("filter-date"):
            dash_date_range_filter = int(request.form.get("filter-date"))

        # Allow users to filter by category: 
        if request.form.get("filter-cat"):
            dash_category_filter = request.form.get("filter-cat")
        
        return redirect('/')



@app.route("/category", methods=["GET", "POST"])
@login_required
def cat():
    categories = update_cat(db, db_conn, username)
    # [('COVID Protection',), ('Clothes',), ('Food',), ('Grocery',), ('Health Supplements',), ('Hygiene',), ('Make up',), ('Online Subscriptions',), ('Shoes',), ('Skincare',), ('Sports',), ('Useless Stuff',), ('WFH Office Supplies',)]
    # Show all categories, allow user to add / delete categories
    if request.method == "GET":
        return render_template('category.html', categories=categories)
    
    else: 
        # E.g response
        # [('add_cat', 'AA'), ('add', '')]
        
        # If user adds a category
        if request.form.get("add_cat") and request.form.get("add"):
            # Check if new cat already exists 
            new_cat = request.form.get("add_cat").strip()
            if tuple([new_cat]) in categories:
                return render_template('category.html', message="Category already exists.", categories=categories)
            else:
                db.execute("""
                        INSERT INTO 
                        category 
                        (username, category_name) 
                        values (?,?)
                        """, (username,new_cat) )
                db_conn.commit()
                return redirect('/category')
        
        if request.form.get("remove_cat") and request.form.get("remove"):
            db.execute("""
            UPDATE category
            SET
            is_deleted=1
            , updated_timestamp=?
            WHERE
            username=?
            and category_name=?
            """, (datetime.now().strftime("Y-%m-%d"), username, request.form.get("remove_cat")))
            db_conn.commit()
            return redirect('/category')


@app.route("/sync_damage", methods=["GET", "POST"])
@login_required
def scrape():
    if request.method == "GET":
        return render_template('sync_damage.html')
    else:
        platform = request.form.get("platform") 
        time_period = int(request.form.get("time_period"))
        db.execute("""
                SELECT 
                order_id
                FROM transactions
                WHERE platform = ?
                and order_id is not null
                and not is_deleted
                and username=?
                order by date desc
                limit 1
                """,(platform,username))
        last_order_id = db.fetchall()

        if platform == "Lazada":
            orders = my_laz_orders(last_order_id)
        else:
            orders = my_shopee_orders(last_order_id, time_period)

        upload_order_data(platform, orders, db, db_conn, username)
        
        return redirect('/damage_history')


        
                

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('login.html', message='Please provide username!')

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('login.html', message='Please provide password!')

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?",
                          (request.form.get("username"),) )
        rows = db.fetchall()
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template('login.html', message='Invalid credentials!')
        
        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        global username
        username = request.form.get("username")

        # Filters applied to Damage History tab 
        global date_range_filter
        date_range_filter = 90

        global category_filter
        category_filter = "all"

        # Filters applied to Dashboard tab 
        global dash_date_range_filter
        dash_date_range_filter = 90

        global dash_category_filter
        dash_category_filter = "all"

        # Load all data 
        global categories
        categories = update_cat(db, db_conn, username)

        global damage 
        damage = update_history(db, db_conn, username, date_range_filter, category_filter)

        global date_range 
        date_range = [(7,'7 Days'), (30,'Month'), (60, '2 Months'), (90, '3 Months'), (180, '6 Months')]
        # Redirect user to home page
        return redirect("/")

        

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
        
    


@app.route("/add_damage", methods=["GET","POST"])
@login_required
def add():
    categories = update_cat(db, db_conn, username)
    if request.method == "GET":
        return render_template('add_damage.html', categories=categories)
    else:
        if not request.form.get("platform"):
            return render_template('add_damage.html', categories=categories, message="Please provide platform")
        if not request.form.get("description"):
            return render_template('add_damage.html', categories=categories, message="Please provide description")
        if not request.form.get("category"):
            return render_template('add_damage.html', categories=categories, message="Please select category")
        if not request.form.get("damage"):
            return render_template('add_damage.html', categories=categories, message="Please provide $$")
        if not request.form.get("date"):
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            date = request.form.get("date")
        # Insert into transactions table
        db.execute("""
        INSERT 
        INTO transactions
        (username, platform, description, category, damage, date)
        values
        (?,?,?,?,?,?)
        """,
        (username
        , request.form.get("platform")
        , request.form.get("description")
        , request.form.get("category")
        , request.form.get("damage")
        , date)
        )
        db_conn.commit()
        return redirect('/add_damage')
    
@app.route("/damage_history", methods=["GET", "POST"])
@login_required
def history():
    global date_range_filter
    global category_filter
    global date_range
    
    global damage
    global damage_history
    damage_history = damage

    global categories
    damage_categories = categories

    # Reload data 
    
    damage_history = update_history(db, db_conn, username, date_range_filter, category_filter)

    if request.method =="GET":
        return render_template('damage_history.html'
        , damages=damage_history
        , categories=damage_categories
        , select_date=date_range_filter
        , date_range=date_range
        , select_category=category_filter)

    else:
        # Allow users to toggle date range
        if request.form.get("history"):
            date_range_filter = int(request.form.get("history"))

        # Allow users to filter by category: 
        if request.form.get("filter-cat"):
            category_filter = request.form.get("filter-cat")

        # Allow user to recategorise transactions and remove transactions 
        for damage in damage_history:
            if request.form.get(str(damage[0])):
                if request.form.get(str(damage[0])) != 'no-updates':
                    db.execute("""
                        UPDATE
                        transactions
                        SET 
                        category=?
                        , updated_timestamp=?
                        WHERE id = ?
                        """, 
                        (request.form.get(str(damage[0]))
                        ,datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        , damage[0]
                        ))
                    db_conn.commit()         

                if request.form.get(str(damage[0])+"del"):
                    db.execute("""
                    UPDATE
                    transactions
                    SET 
                    is_deleted=1
                    , updated_timestamp=?
                    WHERE id = ?
                    """, 
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    , request.form.get(str(damage[0])+"del")
                    ))
                    db_conn.commit()
                    


        return redirect('/damage_history')        
                    




@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    # If GET, displays Form 
    if request.method == "GET":
        return render_template("register.html")
    else: 
        # Check if user has filled up user name
        if not request.form.get('username'):
            return render_template('register.html', message="Please provide username!")

        else:
            # Check if username exists in users 
            db.execute("SELECT * FROM users WHERE username = ? ", (request.form.get("username"), ) )
            rows = db.fetchall()

            if len(rows) != 0:
                # return apology("username taken!", 403)
                return render_template('register.html', message="Username taken!")
        
        if not request.form.get('password'):
            # return apology("must provide password", 403)
            return render_template('register.html', message="Please provide password!")
        
        if not request.form.get('confirm_password'):
            # return apology("must confirm password", 403)
            return render_template('register.html', message="Please confirm password!")

        if request.form.get('password') != request.form.get('confirm_password'):
            # return apology("passwords doesn't match", 403)
            return render_template('register.html', message="Passwords do not match!")
        
        # Update users table 
        db.execute("INSERT INTO users (username, password) values (?, ?);",
                        (request.form.get("username")
                        , generate_password_hash(request.form.get("password")) ) )

        # Create a default list of categories for new user 
        reg_category = ['Sports'
        , 'Food'
        , 'Grocery'
        , 'WFH Office Supplies'
        , 'Clothes' 
        , 'Make up'
        , 'Shoes'
        , 'COVID Protection'
        , 'Online Subscriptions'
        , 'Skincare'
        , 'Hygiene'
        , 'Useless Stuff'
        , 'Health Supplements'
        , 'Lazada'
        , 'Shopee']

        for cat in reg_category:
            # Update category table with default categories
            db.execute("INSERT INTO category (username, category_name) values (?, ?);",
                            (request.form.get("username")
                            , cat ) )
            db_conn.commit()     

        return redirect("/login")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return 1

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True)





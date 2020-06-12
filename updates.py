from sqlite3 import connect
import datetime 

def update_cat(db, db_conn, username):
    db.execute("""
    SELECT 
    category_name
    FROM category
    where username=?
    and not is_deleted
    ORDER BY 
    category_name""", (username,) )
    return(db.fetchall())


def update_history(db, db_conn, username, date_range, category):
    if category == "all": 
        db.execute("""
        SELECT 
        id
        , date
        , platform
        , description
        , category
        , damage
        FROM transactions
        where username=?
        and not is_deleted
        and date >= datetime('now', ?)
        and (order_status in ('Delivered','Processing','Request cancelled','Return rejected','Shipped', 'COMPLETED','RATED','TO RECEIVE') or order_status is null)
        ORDER BY 
        date desc""", (username, str(date_range*-1) + ' day' ) ) 
    else:
        db.execute("""
        SELECT 
        id
        , date
        , platform
        , description
        , category
        , damage
        FROM transactions
        where username=?
        and not is_deleted
        and date >= datetime('now', ?)
        and (order_status in ('Delivered','Processing','Request cancelled','Return rejected','Shipped', 'COMPLETED','RATED','TO RECEIVE') or order_status is null)
        and category=?
        ORDER BY 
        date desc""", (username, str(date_range*-1) + ' day' , category))

    rows = db.fetchall()
    
    # Converting tuple row to list for formatting changes
    new_rows = [list(row) for row in rows]

    # Appending new date format and ensure that prices are rounded to 2 DP for aesthetic 
    for i in range(0, len(new_rows)):
        format_date = datetime.datetime.strptime(new_rows[i][1], "%Y-%m-%d")
        new_rows[i].append(format_date.strftime('%d%b'))
        new_rows[i][5] = round(new_rows[i][5],2)

    return(new_rows)







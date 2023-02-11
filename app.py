#imports all requirements
import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session,url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from loginreq import login_required
#database sample from : https://data.world/promptcloud/product-listing-walmart

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

#intialise a constante liste
DH=[200,100,50,20,10,5,2,1]

#Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#Redirects the default route to login
@app.route("/",methods=["GET"])
def choice():
    return redirect("/login")



#Login route
@app.route("/login",methods=["GET","POST"])
def login():
    #logs the user out
     session.clear()

     if request.method == "POST":
        #checks for empty username/password form
        if not request.form.get("username"):
            return render_template("login.html",text="Must provide username")
        elif not request.form.get("password"):
            return render_template("login.html",text="Must provide password")

        #checks if the username and password do exist in the database
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").lower())
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html",text="Invalid username and/or password")

        #logs in the user
        session["user_id"] = rows[0]["id"]

        #redirects the user depending on his type: emp or adm (employee or admin)
        if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] =="emp":
            return redirect("/workspace")
        else:
            return redirect("/admin")

    #for "GET" requests
     else:
        return render_template("login.html")


#the route in which we add new items to be sold.(start of cashier interface)
@app.route("/workspace",methods=["GET","POST"])
@login_required
def workspace():
    if request.method == "POST":

        #there are three possible POST requests, either add item, remove an added item or pay.
        if request.form["btn_identifier"] == "add":

            #error checks: empty barcode input
            if not request.form.get("barcode"):
                rows = db.execute("SELECT * FROM product")
                if len(rows)!=0:
                    totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
                    return render_template("workspace.html",text="Must provide barcode",totale=totale, rows=rows)
                else:
                    return render_template("workspace.html",text="Must provide barcode",totale=0, rows=rows)

            #error checks: empty items input
            elif not request.form.get("items"):
                rows = db.execute("SELECT * FROM product")
                if len(rows)!=0:
                    totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
                    return render_template("workspace.html",text="Must provide number of items",totale=totale, rows=rows)
                else:
                    return render_template("workspace.html",text="Must provide number of items",totale=0, rows=rows)

            #error checks: valid inputed barcode
            elif len(db.execute("SELECT * FROM products WHERE barcode = ?", request.form.get("barcode")))==0:
                rows = db.execute("SELECT * FROM product")
                if len(rows)!=0:
                    totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
                    return render_template("workspace.html",text="Invalid barcode",totale=totale, rows=rows)
                else:
                    return render_template("workspace.html",text="Invalid barcode",totale=0, rows=rows)


            else:#Adds items to a temporary table named "product".
                barcode = request.form.get("barcode")
                data = db.execute("SELECT * FROM products WHERE barcode = ?", request.form.get("barcode"))[0]
                for i in range(int(request.form.get("items"))):#if input is negative, this loop simply doesn't start, so no need to check if input is negative.
                    db.execute("INSERT INTO product(barcode, product,price) VALUES(?, ?, ?)", barcode, data["product"], data["price"])#Adds items to a temporary table named "product".
                rows = db.execute("SELECT * FROM product")
                totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
                return render_template("workspace.html", totale = totale , rows=rows)

        #the second possible POST request
        elif request.form["btn_identifier"] == "pay":
            return redirect("/payment")

        #Deletes the product from the temporary liste
        else:#else, the request is assured to be remove.
            db.execute("DELETE FROM product WHERE barcode =? LIMIT 1", request.form["btn_identifier"])
            rows = db.execute("SELECT * FROM product")
            data = db.execute("SELECT * FROM products WHERE barcode = ?", request.form["btn_identifier"])[0]
            if len(rows)!=0:
                totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
                return render_template("workspace.html",text="DELETED :"+ data["product"],totale=totale, rows=rows)
            else:
                return render_template("workspace.html",text="DELETED :"+ data["product"],totale=0, rows=rows)
            #notice that i never checked if the product is in stock. i accept selling a product even if it's not declared in stock.
            #it's not an error, it's by choice.

    #GET request:
    else:
        #the temp table is cleared
        db.execute("DELETE FROM product")
        try:
            #this prints a message when the previous sell is registered succefully
            return render_template("workspace.html",text2 = request.args['text2'])
        except:
            return render_template("workspace.html")



#in the page,the emp is supposed to enter the cash handed to him by the costumer in moroccan currency
@app.route("/payment",methods=["POST","GET"])
@login_required
def payment():
    if request.method == "POST":

        #saves all cash handed by the costumer
        Cash=[0 for i in range(len(DH))]
        for i in range(len(DH)):
            mad = "MAD"+str(DH[i])
            Cash[i]= int(request.form.get(mad))
            db.execute("UPDATE variables SET cash=? WHERE id=? ",Cash[i],mad)#there is a second temporary table (variables) that is used to store these variables.

        #calculate the totale cost of items, and the sum of the cash handed
        totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
        cash= Cash[0]*200 + Cash[1]*100 + Cash[2]*50 + Cash[3]*20 + Cash[4]*10 + Cash[5]*5 + Cash[6]*2 + Cash[7]

        #calculate the perfect amount of change to give back and saves it in "suggest".(inspired by Pset: "cash")
        if cash>=totale:
            suggest=[0 for i in range(len(DH))]
            change = cash - totale
            for  i in range(len(DH)):
                mad = "MAD"+str(DH[i])
                suggest[i] = int(change//DH[i])
                change -= suggest[i]*DH[i]
                db.execute("UPDATE variables SET suggest=? WHERE id=? ",suggest[i],mad)
            return redirect("/change")

        else:#checks if customer is giving less cash then needed
            rows = db.execute("SELECT * FROM product")
            return render_template("payment.html",totale = totale , rows=rows, text = "Not enough cash.")
    #GET request
    else:
        rows = db.execute("SELECT * FROM product")
        totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
        return render_template("payment.html",totale = totale , rows=rows)



#in this page, the costumer should enter the amount of change his taking out of the "safe" adn giving to the customer
@app.route("/change",methods=["POST","GET"])
@login_required
def change():
    #Calculates the totale, the cash .... (Hence the use of the tmp table "variables")
    totale=int(db.execute("SELECT sum(price) FROM product")[0]["sum(price)"])
    variables = db.execute("SELECT * FROM variables")
    Cash=[0 for i in range(len(DH))]
    suggest=[0 for i in range(len(DH))]
    for i in range(len(variables)):
        Cash[i]=variables[i]["cash"]
        suggest[i]=variables[i]["suggest"]
    cash= Cash[0]*200 + Cash[1]*100 + Cash[2]*50 + Cash[3]*20 + Cash[4]*10 + Cash[5]*5 + Cash[6]*2 + Cash[7]

    #POST means the emp has clicked the final validation button
    if request.method == "POST":

        #the list back represents the amount that emp decided to give back to costumer
        Back=[0 for i in range(len(DH))]
        for i in range(0,len(DH)):
            Back[i]= int(request.form.get("MAD"+str(DH[i])))
        back= Back[0]*200 + Back[1]*100 + Back[2]*50 + Back[3]*20 + Back[4]*10 + Back[5]*5 + Back[6]*2 + Back[7]

        #checks if emp is giving ctmer more or less
        if back> cash - totale :
            return render_template("change.html",text="You are giving more change",suggest=suggest, totale=totale,cash=cash)
        elif back< cash - totale :
            return render_template("change.html",text="You are giving less change",suggest=suggest, totale=totale,cash=cash)


        else:
            #Checks if the change entered exists in the "safe"
            for i in range(0,len(DH)):
                mad = "MAD"+str(DH[i])
                if int(db.execute("SELECT * FROM bank ORDER BY tran_id DESC LIMIT 1")[0][mad]) < Back[i]:
                    return render_template("change.html",text=f"You don't have{Back[i]}*{DH[i]} MAD",suggest=suggest, totale=totale,cash=cash)

            #INSERTS transaction
            id=session["user_id"]
            trans=[0 for i in range(len(DH))]
            for i in range(0,len(DH)):
                mad = "MAD"+str(DH[i])
                trans[i]=int(db.execute("SELECT * FROM bank ORDER BY tran_id DESC LIMIT 1")[0][mad])+Cash[i]-Back[i]
            db.execute("INSERT INTO bank(id,MAD200,MAD100,MAD50,MAD20,MAD10,MAD5,MAD2,MAD1) VALUES(?, ?, ?, ? , ? ,? ,? ,?,?)", id, trans[0], trans[1],trans[2],trans[3],trans[4],trans[5],trans[6],trans[7])
            rows =db.execute("SELECT * FROM product")

            #UPDATES product lists
            barcodess=[]
            S=0
            for row in rows:
                if row["barcode"] not in barcodess:
                    barcodess.append(row["barcode"])
                    for row2 in rows:
                        if row["barcode"]==row2["barcode"]:
                            S+=1
                        db.execute("UPDATE products SET stock=? WHERE barcode=? ",db.execute("SELECT stock FROM products WHERE barcode=?",row["barcode"])[0]["stock"]-S ,row["barcode"])
            #RECORDS sells
            for row in rows:
                db.execute("INSERT INTO sells(id,barcode,tran_id) VALUES(?, ?, ?)", id,row["barcode"],db.execute("SELECT tran_id FROM bank ORDER BY tran_id DESC LIMIT 1")[0]["tran_id"])
            db.execute("DELETE FROM product")
            return redirect(url_for('.workspace', text2="The previous sell in regustered successfully"))

    else:
        #the fact that i'm passing suggest each time there is an error helps the emp figure out the perfect change to give back
        return render_template("change.html",suggest=suggest, totale=totale,cash=cash)

#From this line, all the functionalities are inaccessable by regular employees.
#_______________________________________________________________________________________________________________________________________________________________________


@app.route("/admin",methods=["POST","GET"])
@login_required
def admin():
    #the NiceTry function is my attempt to stop regular emps for accessing admin stuff.
    if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] !="adm":
        return render_template("nicetry.html")
    else:
        return render_template("admin.html")



@app.route("/register",methods=["GET","POST"])
@login_required
def register():
    #the NiceTry function
    if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] !="adm":
        return render_template("nicetry.html")

    else:
         if request.method == "POST":
            rows=db.execute("SELECT * from users order by type ASC")[1:]
            if request.form["btn_identifier"] == "add":

                #error checking
                if not request.form.get("username"):
                    return render_template("register.html",text="user must have username",rows=rows)
                elif not request.form.get("password"):
                    return render_template("register.html",text="user must have password",rows=rows)
                elif not request.form.get("type") or request.form.get("type") not in ["adm", "emp"]:
                    return render_template("register.html",text="admine or employee")
                elif len(db.execute("SELECT * FROM users_archive WHERE username = ?", request.form.get("username")))!=0:
                    return render_template("register.html",text="username taken",rows=rows)

                #Adds the employee or admin
                else:
                    username = request.form.get("username")
                    password= generate_password_hash(request.form.get("password"))
                    type=request.form.get("type")
                    db.execute("INSERT INTO users(username,hash,type) VALUES(?, ?, ?)", username, password,type)
                    id = db.execute("select id from users where username=?",username)[0]["id"]
                    db.execute("INSERT INTO users_archive(id,username,hash,type) VALUES(?,?, ?, ?)", id,username, password,type)
                    rows=db.execute("SELECT * from users order by type ASC")[1:]
                    return render_template("register.html",rows=rows,text2="added successfully")

            #else if the POST request is not "add" then the admin is removing access for an employee.
            else:
                db.execute("DELETE FROM users WHERE id =? LIMIT 1", request.form["btn_identifier"])
                rows=db.execute("SELECT * from users order by type ASC")[1:]
                return render_template("register.html",rows=rows)

         else:
            rows=db.execute("SELECT * from users order by type ASC")[1:]#you can't remove the main admin from the database not display him.
            return render_template("register.html",rows=rows)



@app.route("/sells",methods=["GET"])
@login_required
def sells():
    #the NiceTry function
    if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] !="adm":
        return render_template("nicetry.html")

    #displays or sells
    else:
        id=session["user_id"]
        products= db.execute("SELECT * FROM products")
        sells=  db.execute("SELECT * FROM sells")
        tableaux =[dict() for i in range(len(sells))]
        for i in range(len(sells)):
            tableaux[i]["employee"]=db.execute("SELECT * FROM users_archive WHERE id=?",sells[i]["id"])[0]["username"]
            tableaux[i]["barcode"]=sells[i]["barcode"]
            tableaux[i]["product"]=db.execute("SELECT product FROM products WHERE barcode=?",sells[i]["barcode"])[0]["product"]
            tableaux[i]["date"]= sells[i]["date"]
            tableaux[i]["tran_id"]= sells[i]["tran_id"]
            tableaux[i]["profit"]= db.execute("SELECT price FROM products WHERE barcode=?",sells[i]["barcode"])[0]["price"]
        return render_template("sells.html",rows=tableaux)


@app.route("/products",methods=["GET","POST"])
@login_required
def products():
    #the NiceTry function
    if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] !="adm":
        return render_template("nicetry.html")


    else:
        rows=db.execute("SELECT * FROM products")
        if request.method == "POST":

            #checks if missing barcode
            if not request.form.get("barcode"):
                return render_template("products.html",rows=rows,text="missing barcode")

            #checks whether the admin is trying to add an entirely new products, or just restock an existing product in the database.
            elif len(db.execute("SELECT * FROM products WHERE barcode = ?", request.form.get("barcode")))!=0:
                #checks if missing barcode
                if not request.form.get("items"):
                    return render_template("products.html",rows=rows,text="missing items")
                #adds items to existing product
                else:
                    old = int(db.execute("SELECT * FROM products WHERE barcode = ?", request.form.get("barcode"))[0]["stock"])
                    db.execute("UPDATE products SET stock=? WHERE barcode=? ",str(int(request.form.get("items"))+old),request.form.get("barcode"))
                    rows=db.execute("SELECT * FROM products")
                    return render_template("products.html",rows=rows,text2="Items add")

            #else, then we are adding an entirely new product, hence should provide price barcode and everything plus check for overlapping barcodes:
            elif not request.form.get("product"):
                return render_template("products.html",rows=rows,text="missing product")
            elif not request.form.get("price"):
                return render_template("products.html",rows=rows,text="missing price")
            elif not request.form.get("items"):
                return render_template("products.html",rows=rows,text="missing items")
            else:
                if len(db.execute("SELECT * FROM product WHERE barcode = ?", request.form.get("barcode")))!=0:
                    return render_template("products.html",rows=rows,text="repeated barcode")

                #if no error is detected: INSTERT new product
                else:
                    db.execute("INSERT INTO products(barcode,product,stock,price) VALUES(?, ?, ?,?)",request.form.get("barcode"),request.form.get("product"),request.form.get("items"),request.form.get("price"))
                    rows=db.execute("SELECT * FROM products")
                    return render_template("products.html",rows=rows,text2="Items add")

        #GET:
        else:
            rows=db.execute("SELECT * FROM products")
            return render_template("products.html",rows=rows)



#Shows current emps and past emps that have been inactivated
@app.route("/users_archive",methods=["GET"])
@login_required
def users_archive():
    #the NiceTry function
    if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] !="adm":
        return render_template("nicetry.html")
    else:
        rows=db.execute("SELECT * FROM users_archive")
        table=db.execute("SELECT * FROM users")
        return render_template("users_archive.html",rows=rows, table = table)


#this allows the admin to add to the "safe" or take money out.
@app.route("/bank",methods=["GET","POST"])
@login_required
def bank():
    #the NiceTry function
    if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] !="adm":
        return render_template("nicetry.html")

    else:
        if request.method == "POST":

            #variable
            id=session["user_id"]
            trans=[0 for i in range(len(DH))]
            new=[0 for i in range(len(DH))]

            #if admin wants add money:
            if request.form["action"] == "add":
                for i in range(len(DH)):
                    mad = "MAD"+str(DH[i])
                    new[i]=int(request.form.get(mad))
                    trans[i]=int(db.execute("SELECT * FROM bank ORDER BY tran_id DESC LIMIT 1")[0][mad])+new[i]


            #if take
            else:
                 for i in range(len(DH)):
                    mad = "MAD"+str(DH[i])
                    new[i]=int(request.form.get(mad))
                    trans[i]=int(db.execute("SELECT * FROM bank ORDER BY tran_id DESC LIMIT 1")[0][mad])-new[i]

            #updates the tables.
            db.execute("INSERT INTO bank(id,MAD200,MAD100,MAD50,MAD20,MAD10,MAD5,MAD2,MAD1) VALUES(?, ?, ?, ? , ? ,? ,? ,?,?)", id, trans[0], trans[1],trans[2],trans[3],trans[4],trans[5],trans[6],trans[7])
            row=db.execute("SELECT * FROM bank ORDER BY tran_id DESC LIMIT 1")[0]
            totale=0
            for i in range(len(DH)):
                mad = "MAD"+str(DH[i])
                totale+= row[mad]*DH[i]
            return render_template("bank.html",row=row,totale=totale)

        #GET
        else:
            row=db.execute("SELECT * FROM bank ORDER BY tran_id DESC LIMIT 1")[0]
            totale=0
            for i in range(len(DH)):
                mad = "MAD"+str(DH[i])
                totale+= row[mad]*DH[i]

            return render_template("bank.html",row=row,totale=totale)


#simply displayes a table of all trasanctions and who made them etc
@app.route("/trans",methods=["GET"])
@login_required
def trans():
    #the NiceTry function
    if db.execute("SELECT type FROM users WHERE id = ?", session["user_id"])[0]["type"] !="adm":
        return render_template("nicetry.html")


    else:
        emp=db.execute("SELECT * FROM users_archive")
        employees=dict()
        for employee in emp:
             id=employee["id"]
             employees[str(id)]= str(employee["username"])
        rows= db.execute("SELECT * FROM bank")
        for i in range(len(rows)):
            rows[i]["username"]= employees[str(rows[i]["id"])]
        return render_template("trans.html",rows=rows)

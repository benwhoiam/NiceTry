# NiceTry: cashiering
## Video Demo: https://www.youtube.com/watch?v=9DixTugOTyk&ab_channel=Alibentaout
## Description:
For testing purposes. Log in as

 Username :admin | Password :admin

All the preregistered employees and admin have the username as their password.
### I -General introduction:
Generally speaking, my project is a cashiering system for a medium size supermarket/store. it consists of many interfaces. However, we can group them into two categories.  The employee interfaces/functionalities and the admin ones.

This project implements many SQL tables.

First of which is the products table: barcode | product | stock | price.  This table is prefilled with a Walmart database found in this URL: https://data.world/promptcloud/product-listing-walmart using csv file. The names are uncompleted and the prices are not accurate. However, it is just a test/demonstration database.

Users table: id | username | hash |type. This table allows users to login. The hash column represents the password but it is hashed for security reasons.   There is an identical table called user_archive. In which all users are stored. Even the ones are no longer active, hence they cannot access the site even if the entered the username and password. This table could have not existed by simply adding a column to the users table in which I specify whether it is an active or inactive user. However, that would have taken a bit of time to adjust the flask script. Therefore, I decided to do the simple imperfect way.

The sells table records every the time and date every product is sold at. As well as which employee sold it and assigns it a transaction id. The transaction id is used in the bank table to keep track of every DH that enters or leaves the bank/cashier/safe. DH is Moroccan currency. From now on, I will use the term “bank” to refer to the place where the money is stored in the store. The bank table contains columns that record how many pieces of each time divisions of money is in the bank. The Moroccan currency is divided to 8 pieces:  200dh (blue), 100dh (brown), 50dh (green), 20dh (purple) papers. In addition to a 10dh (yellow), 5dh (greenish), 2dh (gray) and 1dh (gray) in form of coins. The colors are an important thing. Since the web app assumes the user is familiar with them. Therefor the inputs are colored as the money paper without even stating what they represent.

The “product” and “variables” are just temporary tables that are used through the app.py execution.


### II -The employee interface:

The first thing any users sees is a login page. Depending on your type (admin or employee) the login button will redirect you different interfaces. Supposedly, our user is an employee. He will be directed to the /workspace route. Which includes a place where the scanner will copy a barcode. A place where he can specify how many of the same product the costumer has bought, and an add button. On click the add button checks all errors and if there are not any, the product will be added to the list of products bought by that customer. If the customer decided that, he does not want an item. Alternatively, an item was mistakenly scanned. The employee can click remove to remove the item from the list. After all items have been scanned the employee clicks on pay to precede.

The next interface: /payment consists of a list of all items scanned, a total, and 8 inputs colored the same color as the Moroccan papers. The employee is supposed to enter the exact combination of the money giving to him buy the customer. If the sum of the money given is not greater than the total, the applications returns a message stating the above. Else when validate is clicked It will redirect the employee to the next page.

The /change: this page shows the user the total that the costumer should pay. How much the customer has giving him as cash, and suggest the best possible way of change as a default value of the change input values. The user is supposed to enter the exact combination of the money that he will take out of the bank and give to the customer as change.  If the user tripped and inputs more or less then he is supposed to enter. The applications return an error message and resets the values to the default combination that it thinks is optimal to give back, the algorithm also check if the change that the user will be giving back to the costumer does exist in bank or not. If all goes right with no errors the user is redirect to the workspace page with a message in green confirming the registration of the past sell.

The employee can only loop in this loop and he does not have any buttons to access the admin options. The user might want to access the admin options buy sending a /admin get request. However, the web app will realise that it is an unauthorized request and will redirect him to a nice try page. Hence the name of my project.



### III -The admin interface:
If the log in is an admin, he will be redirected to a multi-choice page:
#### 1 -Workspace:
Which will simply redirect him to the same page that employees use to sell stuff. The admin can equally sell product.
#### 2 -Employees:
From this page, the admins can add or remove employees and other admins except the main admin with the username: admin and id =1. It does not even show on the list of registered users. The web app checks all possible error before registering a new employee like empty inputs and repeating usernames etc. Only active users (the one that can sign in) show in this page.
#### 3 -Records:
Lists all the sales and who sold them and when and what was the transactions id and the profit. Sells with the same transaction id were sold to the same costumer. This part assumes that the profit is equal to the items price, however if I had a more valid database  I could’ve calculated the price of bought – sell + tax …

#### 4-Product:
Lists all the products that have been registered. This page is a bit slow considering the huge data that it deals with. This page allows two actions: adding to stock an entirely new product. In that case, the algorithm will check if all columns are filled etc. the second functionality is “restocking” one, the admin only needs to enter the barcode of an existing product and the items he is adding to stock for the actions to be registered.

#### 5-Archive:
Allows the admin to see all the account that have ever been made.
#### 6-Bank:
The bank page starts buy showing a table of all the distribution of all the money in the bank. And it allows the admin to do two actions, either take money from the bank. Or put money into the bank, the admin is asked to enter the exact combinations of the money he is putting in or taking out of the bank.
#### 7-Transaction:
It lists all the transactions made. For every transaction id. Who made it and what exchange happened in everyone.




This was CS50 <3
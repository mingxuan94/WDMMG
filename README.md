# WDMMG?
Where did my money go? Or WDMMG in short, is a web app that allows users to track and categorise their expenses. 

## Installation & Usage 
1. Download this repo
2. Pip install requirements.txt
3. Change working directory to this folder
3. Run `flask run` on command line

## Project description

WDMMG comes along with an in built Bot that enables the App to automatically download and store your Online E-commerce expenses in a database! 
This functionality saves users the hassle of having to manually log in expenses one by one (Good news for shopaholics out there!), as this process will be fully automated. 
This Bot currently supports Online E-commerce platforms Lazada and Shopee. 

This web app features 5 pages. 

When you arrive at the homepage, you will be able to view your expense summary in the form of time series and bar charts. 
Using the date and category filters, you will be able to toggle accordingly to look at only a specific time period. 
You may also notice that your expenses tend to spike around days like Black Fridays or 12.12 where popular Ecommerce sites launch Mega Sales to suck your bank account dry!

In the 2nd page, is the Manage Category page. 
Every new account comes along with a default list of category. However, you are free to personalise this list of categories and tailor it to your own needs! 
With this Category Manager, you will be able to Add or Remove Categories. You can make it as detailed as you like! 

In the 3rd page, is the Sync Damage page. 
In this page, you will be able to import your Expenses from Online E-commerce platforms such as Lazada and Platform. 
This is where you will put the Bot to work! Simpy choose which platform you would like to import your expenses as well as the time period. 
A new webpage will be launched, and you will be asked to login. The Bot will automatically fetch your orders and store it in the database where you will be able to view afterwards!

In the 4th page, is the Add Damage page. 
In this page, you will be able to manually add Expenses and also categorise them. 

In the 5th page, is the Damage History page. 
This is where you will be able to view all your logged expenses from the Add Damage page as well as Sync Damage tab. 
In this page, you will be able to either recategorise your expenses using the dropdown bars or delete your expenses by checking the box at the end of each row! 
When you're ready to save the changes, simply click the "Update" button to logged all changes in the database.  
You can also use the filters available to look at expenses over a specific date period or category. 

When you are ready to view the updated summary of your expenses, click the title of the webpage on the top left corner and you will be brought back to the Homepage.

Hope that this web app is able to help you track your finances a little bit better! 
This was WDMMG?!


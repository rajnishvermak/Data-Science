# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 10:24:07 2021

@author: racha
"""

# import relevant packages
import sqlite3
from IPython.display import display
from datetime import datetime
import pandas as pd
from datetime import date
from random import randint
import folium
import numpy as np
import matplotlib.pyplot as plt
from folium import features
import sys
import webbrowser
import hashlib
from dateutil.relativedelta import relativedelta
import re
import warnings
warnings.filterwarnings("ignore")

# set up the cursor and connect to the database
with sqlite3.connect("bike_sharing_system.db")as db:
        cursor = db.cursor()
        
# ---Sign in---
           
# define a function to hash a string using sha256
def hash_str(input):
    # need to transform the string into byte form so it can be hashed
    byte_input = input.encode()
    
    # hash the byte version of the string
    hash_object = hashlib.sha256(byte_input)
    
    # return the hashed string
    return hash_object

# define a function to get the username from the customer
# and the current usernames in the datcabase
def get_usernames():
    # ask customer for their username
    username = input("Enter your username: ")
   
    # get all saved customer usernames from database
    cursor.execute("SELECT username FROM Customer")
    db_customer = [x[0] for x in cursor.fetchall()]
    
    # get all saved admin usernames from database
    cursor.execute("SELECT username FROM Admin")
    db_admin = [x[0] for x in cursor.fetchall()]
    
    # return the values
    return (username, db_customer, db_admin)
 
# define a function for the user to sign in
def sign_in(): 
    
    # delete any leftover data from the sign in table
    cursor.execute("DELETE FROM User_details")
    db.commit()
    
    # display a sign in message
    print("\nPlease sign in.")
    
    # get the usernames
    (username, db_customer, db_admin) = get_usernames()
    
    # set flag to True
    flag = True
    
    # check if username is valid by seeing if it is in either Customer or Admin table
    while username not in db_customer and username not in db_admin and flag:
        # while it is not in either table display an error and ask for their username again
        print("\nUsername does not exist!")
       
        # ask user if they'd like to create a new account
        create_acc = input("Would you like to create an account? (y/n): ")
        
        # if they enter y then set flag to False to stop the loop
        if create_acc.lower() == "y":
            flag = False
        # otherwise ask for their username again    
        else:
            username = input("Enter your username: ")
    
    # if flag is False then take the user to sign up
    if flag == False:
        sign_up()
    
    # else continue the sign in process
    else:
        # if user a customer then get customer passwords
        if username in db_customer:
        
            # ask customer for their password and convert it to hash
            password = hash_str(input("Enter your password: "))
        
            # get the customer's name and saved password from the database
            cursor.execute("SELECT first_name, password FROM Customer WHERE username==?", (username,))
            db_details = [x for x in cursor.fetchall()][0]
            (name, db_password) = db_details
        
        # else user is admin so get admin passwords
        else:
            # ask admin for their password and convert it to hash
            password = hash_str(input("Enter your password: "))
        
            # get the admin's name and saved hash password from the database
            cursor.execute("SELECT first_name, password FROM Admin WHERE username==?", (username,))
            db_details = [x for x in cursor.fetchall()][0]
            (name, db_password) = db_details
    
        # check if password is valid
        # only allowed 3 attempts so start at n = 0
        n = 0
        while password.hexdigest() != db_password:
            # if n<2 then still allowed to attempt to enter the password
            if n<2:
                print("\nInvalid password!", 2-n, "attempts remaining.")
                password = hash_str(input("Enter your password: "))
                # once they've tried 3 times then the sign in is unsuccessful
                # and the program exits
            else:
                print("\nInvalid password! No attempts remaining.")
                sys.exit()  
                n += 1
    
        # enter the username into user_details table so other functions can access it
        # if the user is a customer enter their customer id
        if username in db_customer:
            cursor.execute("""SELECT customer_id FROM Customer WHERE username==?""", (username,))
            customer_id = [x[0] for x in cursor.fetchall()][0]
            cursor.execute("""INSERT INTO user_details (id, username, customer_id)
                           VALUES(1, ?, ?)""", (username, customer_id))
                          
        # otherwise user is an admin so enter their admin id                    
        else:
            cursor.execute("""SELECT admin_id FROM Admin WHERE username==?""", (username,))
            admin_id = [x[0] for x in cursor.fetchall()][0]
            cursor.execute("""INSERT INTO user_details (id, username, admin_id)
                           VALUES(1, ?, ?)""", (username, admin_id))
        # save changes
        db.commit()
    
        # if password is valid then display successful message with their name
        print("\nSign in successful. Welcome " + name + "!")
        
# ---Sign up--- 
 
# ---Checker functions---

# define a function to check if the password is valid
def check_password(password):
    # set number and length to their initial values
    number = False
    length = True
    
    # loop through each character in the password
    for i in range(len(password)):
       # if at least one character in the password is a number then 
       # set number to True
        if password[i].isdigit() == True:
            number = True
    # if number is False display an error telling the user what is wrong
    if number == False:
        print("\nPassword must contain a number.")
            
    # if the password is not long enough display an error and set length to False  
    if len(password) < 8:
        print("\nPassword must contain at least 8 characters: ")
        length = False
        
    # valid is only True when number and length are both True
    valid = number and length
    
    # return valid
    return valid

# define a function to check if the date of birth is valid
def check_dob(dob):
    # set all the initial boolean values
    digit = True
    length = True
    slashes = True
    day = True
    month = True
    year = True
    
    # if dob does not have the slashes in the correct place display an error and set slashes to False
    if dob[2] != '/'  or dob[5] != '/':
        print("\nWrong format. Must contain '/'s.")
        slashes = False
    # if dob is not entered as a number then display an error and set digit to False
    elif not dob[0:2].isdigit() or not dob[3:5].isdigit() or not dob[6:10].isdigit():
        print("\nError! Must enter your date of birth as a number.")
        digit = False
        
    # if the length of dob is not 10 display an error and set length to False    
    elif len(dob) != 10:
        print("\nIncorrect length.")  
        length = False
        
    # if the day entered is not between 1 and 31 display an error and set day to False    
    elif int(dob[0:2]) > 31 or int(dob[0:2]) < 1:
        print("\nDay must be between 1 and 31.")
        day = False
    
    # if the month is not between 1 and 12 display an error and set month to False
    elif int(dob[3:5]) > 12 or int(dob[3:5]) < 1:
        print("\nMonth must be between 1 and 12.")
        month = False
        
    # if the year is not between 1921 and 2021 display an error and set year to False    
    elif int(dob[6:10]) > 2021 or int(dob[6:10]) < 1921:
        print("\nYear must be between 1921 and 2021.")
        year = False
        
    # valid is only True if all other variables are True    
    valid = digit and length and slashes and day and month and year
    return valid

# define a function to get all the emails from the database
def get_emails():
    cursor.execute("SELECT email FROM Customer")
    db_email = [x[0] for x in cursor.fetchall()]
    return db_email

# define a function to get all the contact numbers from the database
def get_numbers():
    cursor.execute("SELECT contact_number FROM Customer")
    db_number = [x[0] for x in cursor.fetchall()]
    return db_number

# define a function to check if the email is valid
def check_email(email):
    
    # set intial values
    form = False
    unique = True
    flag = False
    
    # get all the saved emails from the database
    db_email = get_emails()
    
    # set a regular expression for validating an email
    regex= r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # use fullmatch from re to check if the email entered matches the format required
    # if yes then set form to True
    if(re.fullmatch(regex, email)):
        form = True
        
    # else display an error message    
    else:
        print("\nInvalid email address.")
       
    # if the email already exists then display an error and set unique to False    
    if email in db_email:
        print("\nThere is already an account with this email address!")
        unique = False
        
        # ask user if they'd like to sign in since they might already have an account
        log_in = input("Would you like to sign in? (y/n): ")
        
        # if yes set flag to True
        if log_in.lower() == 'y':
            flag = True
    
    # valid is only True if all conditions are satisified
    valid = form and unique
    return (valid, flag)

# define a function to check if the contact number is valid
def check_number(number):
    
    # set the inital values
    length = True
    digit = True
    start = True
    unique = True
    flag = False
    
    # get all the saved numbers from the database
    db_number = get_numbers()
    
    # if the number is not the right length display an error and set length to False
    if len(number) != 11:
        print("\nPhone number must be 11 digits.")
        length = False
        
    # if the number is not a number display an error and set digit to False    
    elif not number.isdigit():
        print("\nError! You must enter a phone number.")
        digit = False
        
    # if the number does not start with 0 display an error and set start to False    
    elif number[0] != '0':
        print("\nPhone number must start with 0.")
        start = False
        
    # if the number already exists in the database then display an error and set unique to False    
    elif number in db_number:
        print("There is already an account with this contact number!")
        unique = False
        
        # ask the user if they'd like to sign in since they might already have an account
        log_in = input("Would you like to sign in? (y/n): ")
        
        # if yes set flag to True
        if log_in.lower() == 'y':
            flag = True
        
    # valid is only True if everything else is True    
    valid = length and digit and start and unique
    return (valid, flag)

# define a function to check if the selection is valid
def check_selection(selection, limit):
    # set intial values
    digit = True
    bounds = True
    
    # if selection is not a digit display an error and set digit to False
    if not selection.isdigit():
        print("\nSelection must be a number from 1-" + str(limit) + ".")
        digit = False
        
    # if selection is not between 1-limit display error and set bounds to False
    elif int(selection) not in range(1, limit + 1):
        print("\nInvalid selection - must be between 1-" + str(limit) + ".")
        bounds = False
        
    # valid is only True if conditions are met
    valid = digit and bounds
    return valid
   
# ---Sign up function---
   
# define a function for the customer to sign up
def sign_up():
    
    # display sign up message
    print("\nPlease sign up.")
    
    # get the usernames
    (username, db_customer, db_admin) = get_usernames()
    
    # check that they have not left username blank
    full = check_empty(username)
    while not full:
        username = input("Enter your username: ")
        full = check_empty(username)
    
    # check if username already exists in customer and admin table so that
    # no two usernames are the same
    while username in db_customer or username in db_admin:
        # if it already exists ask for a new username
        print("\nUsername already exists!")
        username = input("Enter your username: ")
        
    # otherwise ask customer to create a password with certain requirements
    print("\nPlease create a password. It must contain a number and be at least 8 characters.")
    password = input("Enter your password: ")
    
    # check that they have not left password blank
    full = check_empty(password)
    while not full:
        password = input("Enter your password: ")
        full = check_empty(password)
    
    # check if the password meets the conditions
    valid = check_password(password)
    while not valid:
        password = input("Enter your password: ")
        valid = check_password(password)
    
    # once password meets the requirements hash it so that it is more secure           
    password = hash_str(password).hexdigest()
    
    # ask the user for their details
    print("\nPlease enter your details: ")
    
    # for each field ask for the information and check it is not left empty
    first_name = input("Enter your first name: ")
    full = check_empty(first_name)
    while not full:
        first_name = input("Enter your first name: ")
        full = check_empty(first_name)
    
    last_name = input("Enter your last name: ")
    while not full:
        last_name = input("Enter your last name: ")
        full = check_empty(last_name)
    
    # take note of the date they signed up
    today = date.today()
    
    dob = input("Enter your date of birth (DD/MM/YYYY): ")
    full = check_empty(dob)
    while not full:
        dob = input("Enter your date of birth (DD/MM/YYYY): ")
        full = check_empty(dob)
        
    # check the date of birth is valid
    valid = check_dob(dob)
    while not valid:
        dob = input("Enter your date of birth (DD/MM/YYYY): ")
        valid = check_dob(dob)
        
    # convert the dob entered into a format we can enter into datetime date function   
    day = dob[0:2]
    month = dob[3:5]
    year = dob[6:10]
    
    # convert each component into an integer    
    day = int(day)
    month = int(month)
    year = int(year)
    
    # use the date function to convert it into a date
    dob = date(year, month, day)
        
    # calculate the age of the user using relativedelta to check they are old enough    
    age = relativedelta(today, dob).years
    
    # if the user is under 18 then display an error message and quit
    if int(age) < 18:
        print("\nSorry you must be 18 or older to create an account.")
        sys.exit()
        
    email = input("Enter your email address: ")
    full = check_empty(email)
    while not full:
        email = input("Enter your email address: ")
        full = check_empty(email)
        
    # check if the email is valid    
    (valid, flag) = check_email(email)
    while not valid and not flag:
        email = input("Enter your email address: ")
        (valid, flag) = check_email(email)
    
    # if the email already exists and they want to log in take them to sign_in    
    if flag == True:
        sign_in()
        
    contact_number = input("Enter your contact number: ")
    full = check_empty(contact_number)
    while not full:
        contact_number = input("Enter your contact_number: ")
        full = check_empty(contact_number)
        
    # check if the contact number is valid
    (valid, flag) = check_number(contact_number)
    while not valid and not flag:
        contact_number = input("Enter your contact number: ")
        (valid, flag) = check_number(contact_number)
        
    # if th number already exists and they want to log in take them to sign_in    
    if flag == True:
        sign_in()
    
    # create a new entry in the Customer table
    cursor.execute("""INSERT INTO Customer(first_name, last_name, dob, username, password, date_of_signup, email, contact_number, balance) 
                   VALUES(?, ?, ?, ?, ?, ?, ?, ?, 0)""", (first_name, last_name, dob, username, password, today, email, contact_number))
    # save changes
    db.commit()
    
    # display message to confirm account has been created
    print("\nAccount created!")
    
    # ask the user if they would now like to sign in
    log_in = input("Do you want to sign in? (y/n): ")
    
    # if yes then take them to sign in
    if log_in.lower() == 'y':
        # take them to sign in
        sign_in()

# ---Sign out---

# define a function to sign out
def sign_out():
    # delete any data in the Sign_in table
    cursor.execute("DELETE FROM user_details")
    db.commit()
    
    # print sign out message
    print("\nSign out successful! Goodbye!")        

# ---Payment---

# ---Auxiliory functions---

# the function check_input checks if the value(Station ID) enterded by customer is an integer          
def check_input(flag):
        while flag:
            try:
                print("Please select a station ID from the list above or enter 0 to quit:")
                selected_station_id = int(input())
                if selected_station_id == 0: break
                flag = False
            except  Exception:
                print("\nERROR! You should have",
                      "entered an integer from the list fo station above")
        return (selected_station_id)

# checks if the station entered by the customer is valid
def selecting_station(stations_id_list):
    flag = True
    selected_station_id = check_input(flag)
    while (selected_station_id not in stations_id_list and selected_station_id != 0):
        print("Incorrect Entry")
        selected_station_id = check_input(flag)
        if selected_station_id == 0:
            print("Quiting the program")
            break
    
    return selected_station_id;

# confirm_selection function checks if the customer is assured of his/her selection of station and 
# if they need to change
def confirm_station_selection(tag, confirm_station, selected_station_id, stations_id_list):
    while tag:
    
        if(confirm_station == "y"):
            tag = False
            break;
        elif (confirm_station == "n"):

            # direct customer to the selecting station once again
                bike_station = pd.read_sql_query("""SELECT * FROM Bike_station """, db)
                bike_station.style.set_properties(**{'text-align': 'center'})
                selected_station_id = selecting_station(stations_id_list)
                # Ask cutomer if they are certain of station
                if selected_station_id == 0: break
                 # The line below ensures the selected_station_name is assigned correctly when
                 # iterating by entering incorrect entries or when customer changes his/her 
                 # decision by not confirming previous choice
                selected_station_name = bike_station[bike_station["station_id"] 
                                     == selected_station_id]["station_name"].values[0]
                print("You selected ", selected_station_name, 
                      " with Station ID of ", selected_station_id)
                confirm_station = input("Do you confirm the station? y/n ")
                confirm_station = str.lower(confirm_station)
        else:
            confirm_station = input("please enter y/n to continue ")
    return (tag, selected_station_id, confirm_station)

# This is the main funciton that combines all other functions reevant to selecting a station. It recieves 
# bike_station as an argument, display it to the user and go through abive funcitons and finally return a station
# which is used to select a bike in case the return is not zero
def STATION(bike_station):
    # Display the stations infromation to the customer
    
    display(bike_station.rename(columns={
        'station_id': 'Station ID', 'station_name': 'Station Name', 
        'location': 'Location', 'station_latitude': 'Station Latitude', 
        'station_longitude': 'Station Latitude','country': 'Country',
        'city': 'City', 'number_of_bikes_available': 'Number of Bikes Available',
        'capacity_left': 'Capacity Left'
    }).iloc[: , :9]) 
    # store stations id
    stations_id_list = bike_station["station_id"].tolist()

    # Ask user to select a station using function selecting_station() 
    selected_station_id = selecting_station(stations_id_list) 
    ######## By entering Zero customer must be guided to main menu #####################
    tag = True
    confirm_station = "n"
    while ( selected_station_id != 0 and tag and confirm_station == "n"):
        selected_station_name = bike_station[bike_station["station_id"] 
                                         == selected_station_id]["station_id"].values[0]
        print("You selected ", selected_station_name, " with Station ID of ", selected_station_id)
        # Ask cutomer if they are certain of station
        confirm_station = input("Do you confirm the station? y/n ")
        confirm_station = str.lower(confirm_station)
        if (confirm_station == "yes"):
            confirm_station = "y"
        elif (confirm_station == "no"):
           confirm_station = "n" 

        tag = True
        (tag, selected_station_id, 
         confirm_station) = confirm_station_selection(tag, confirm_station, selected_station_id,
                                                     stations_id_list)
        if selected_station_id != 0:
            # The line below ensures the selected_station_name is assigned correctly when 
            # iterating by entering incorrect entries or when customer changes his/her decision
            # by not confirming previous choice
            selected_station_name = bike_station[bike_station["station_id"] 
                                         == selected_station_id]["station_name"].values[0]
            print("\nBelow you can see information about the station and" ,
                  "list of bikes available at the station of ", selected_station_name, "\n")
            display(bike_station[bike_station["station_id"] == 
                         selected_station_id].rename(columns={
            'station_id': 'Station ID', 'station_name': 'Station Name', 
            'location': 'Location', 'station_latitude': 'Station Latitude', 
            'station_longitude': 'Station Latitude','country': 'Country',
            'city': 'City', 'number_of_bikes_available': 'Number of Bikes Available',
            'capacity_left': 'Capacity Left'}).iloc[: , :9]) 
    return selected_station_id;

# The function recieves selected bike by the user and checks if the entry is valid. To prevent any crash in 
# program, the errors are handled using try and except blocks         
def selecting_bike(flag, bike_selected, bikes_available_at_station):
    while flag:
        try:
            bike_selected = int(bike_selected)
            if bike_selected == 0:
                flag = False
                bike_selected_index = bike_selected
                return bike_selected_index
           # number of bikes is used to check the user input for index of bike
            station_number_of_bikes = len(bikes_available_at_station)
            if bike_selected in range(1, station_number_of_bikes + 1):
                    flag = False
                    bike_selected_index = bike_selected
                    return bike_selected_index
            else:
                print("Your selected bike is not in the list.",
                     "please select again or press 0 to quite ")
                bike_selected = input()
        except:
            bike_selected = str.upper(bike_selected)
            # Create a list of bikes available at the station for comparison in while loop
            bikes_available_at_station_list = bikes_available_at_station["bike_id"].tolist()
            if (bike_selected not in bikes_available_at_station_list):
                print("Your selected bike is not in the list.",
                     "please select again or press 0 to quite ")
                bike_selected = input()
            else:
                bike_selected_index = bikes_available_at_station.index[
                    bikes_available_at_station["bike_id"]== bike_selected].tolist()
                bike_selected_index = bike_selected_index[0]
                flag = False
                return bike_selected_index

# This function is the main function in selecting a bike which implements other relevant functions. The station
#  entered by the user and a list of all bikes are passed as arguments which then is filtered down to the list
#  of available bikes at the station of interest from which the customer should select one. the funciton deals with
# input errors to prevent any crasha nd finally checks if the custoer is assure of his/her selection. 
def BIKE(bikes, selected_station_id):
    bikes_available_at_station = bikes[(bikes["station_id"] == 
                  selected_station_id) & (bikes["booking_status"] == 1)].iloc[:, :4];
    if (selected_station_id != 0):
        print("\nSelect a Bike ID or Index from the list of bikes available below",
              "or enter 0 to quit: ")
        bikes_available_at_station.reset_index(drop=True, inplace=True)
        bikes_available_at_station = bikes_available_at_station.rename(index = lambda x: x + 1)
        bikes_available_at_station.index.name = "Index"
        pd.set_option('display.max_rows', len(bikes_available_at_station))
        display(bikes_available_at_station.rename(columns={
            "bike_id":"Bike ID", "station_id":"Station ID", "station":"Station", 
            "fare_per_h":"Fare per Hr"}))
        bike_selected = input();
        flag = True
        #Select a bike using function selecting_bike
        bike_selected_index = selecting_bike(flag, bike_selected, bikes_available_at_station)

    flag = True
    i = 1; # it is used to control the flow of if statment within while loop. it is used to display
    # bike table only once
    while (bike_selected_index != 0 and  flag):
        
        print ("You selected \"", bikes_available_at_station.iloc[bike_selected_index - 1,0],
               "\" bike with following details")
        display(bike_selected =  bikes_available_at_station.loc[[bike_selected_index]])
        display(bikes_available_at_station.loc[[bike_selected_index]])

        confirm_bike = input("Do you confirm the bike ? y/n  ")
        confirm_bike = str.lower(confirm_bike)

        while not (confirm_bike == "yes" or confirm_bike == "y" 
                or confirm_bike == "n" or confirm_bike == "no"):
            confirm_bike = input("Please enter y/n to continue: ")

        if (confirm_bike == "yes"):
            confirm_bike = "y"
        elif (confirm_bike == "no"):
           confirm_bike = "n"

        if confirm_bike != "y":
            #         Just show the table once
            if (i < 2):
                display(bikes_available_at_station)
                i = i + 1

            print("\nSelect a Bike ID or Index from the list of bikes available above or",
                  "enter 0 to quit: ")

            bike_selected = input();
            bike_selected_index = selecting_bike(flag, bike_selected, bikes_available_at_station)
        else:
            flag = False
    if (bike_selected_index != 0):
        print ("Your selection of  \"", bikes_available_at_station.iloc[bike_selected_index - 1,0],
               "\" confirmed, here are details: ")
        display(bikes_available_at_station.loc[[bike_selected_index]])
        bike_selected = bikes_available_at_station.iloc[bike_selected_index - 1,0]
        bike_selected_fare = bikes_available_at_station.iloc[bike_selected_index - 1,3]
    else:
        bike_selected_fare = 1
        bike_selected = 1
    return bike_selected_index, bike_selected, bike_selected_fare

# ---Payment---

#  checks if the card number is valid in terms of the number of character and type which should be a integer.
# The any possible errors are dealt with using try-except block. Finally the card number is returned
def card_number_validation(card_number):
    flag = True
    while flag:
        try:
            type(int(card_number)) # Check if the input is the number otherwise go to exeption
            if ( len(card_number) != 5):
                print("Card number is not valid. Please enter again or enter 0 to quit")
                card_number = (input())
                if card_number == "0":
                    flag = False

                    break
                continue
            else:
                flag = False
        except:
            print("You should enter a 5 digit number or enter 0 to quit")
            card_number = (input())
            if card_number == "0":
                flag = False

            continue
    return card_number

# The function is run if the card number is valid. The validity is initially checked against the type of charachters
# and errors are handled using try-except block. Afterwards, the validity is checked in terms of years and month
# (which should be a two digit number between 01 and 12). At each step the user can correct mistakes. Then it is
# verified if the card is expired or the entered date is more than five years from now, In either of the 
# aforementioned cases the card will be rejected and asks customer if they want to continue. If the checks are passed
# customer is prompted for cvv and full name
def card_date_validity(card_number):
    if card_number != "0":
        print("Enter your card expiray date:")
        print("Please enter the 2 digit year:")
        year = input()
        print("Please enter the 2 digit month number:")
        month = input()
        flag = True
        while flag:
            try:
                type(int(year)) # Check if the input is the number otherwise go to exeption
                type(int(month))
                if (len(month) != 2 or int(month) not in range(1, 13)) :
                    print ("The month number should be a two digit number between 1 and 12")
                    print("Please enter the 2 digit month number:")
                    month = input()
                    continue
                elif (len(year) != 2):
                    print("Please enter the 2 digit year:")
                    year = input()
                    continue
                elif int(year) <= 0:
                    print("Invalid year number, Please Enter again: ")
                    year = input()
                    continue
                else:
                    print ("The card date is mm/yy", month, "/", year)
                    #Check card expiry date validity
                    duration =  datetime(int("20" + year), 
                                         int(month), 1, 0, 0, 0) - datetime.now()
                    duration = duration.days # time difference in days
                    duration = duration/365 # duration in years
                    if duration < 0:
                        print ("Your card has been expired:")
                        print("Do you want to continue y/n? ")
                        temp_flag = True
                        while temp_flag:
                            confrimation = input()
                            confrimation = str.lower(confrimation)
                            if confrimation == "y" or confrimation == "n":
                                break;
                            else:
                                print("Please enter y/n to continue:")
                        if confrimation == "y":
                            print("Please Enter your 5 digit card number: ")
                            card_number = input()
                            card_number = card_number_validation(card_number)
                            if card_number == "0":
                                status = False
                                break
                            
                            print("Enter your new card expiray date:")
                            print("Please enter the 2 digit year:")
                            year = input()
                            print("Please enter the 2 digit month number:")
                            month = input()
                            continue
                        else:
                            status = False
                            break

                    if duration > 5:
                        print("Your card date is not valid")
                        print("Do you want to continue y/n? ")
                        temp_flag = True
                        while temp_flag:
                            confrimation = input()
                            confrimation = str.lower(confrimation)
                            if confrimation == "y" or confrimation == "n":
                                break;
                            else:
                                print("Please enter y/n to continue:")
                        if confrimation == "y":
                            print("Please Enter your 5 digit card number: ")
                            card_number = input()
                            card_number = card_number_validation(card_number)
                            if card_number == "0":
                                status = False
                                break
                            print("Enter your new card expiray date:")
                            print("Please enter the 2 digit year:")
                            year = input()
                            print("Please enter the 2 digit month number:")
                            month = input()
                        else:
                            status = False
                            break
                    else:
                        flag = False
                        status = True
            except:
                print("You should enter a two digit number for the year and month")
                print("Please enter the 2 digit year:")
                year = input()
                print("Please enter the 2 digit month number:")
                month = input()
                continue
    
    if status:
        print("Enter the 3 or 4 digit cvv: ")
        cvv = input()
        tag = True
        while tag:
            try:
                int(cvv) # check if the cvv is an interger
                if not (len(cvv) == 3 or len(cvv) == 4):
                    print("CVV number is not valid.\n")
                    print("Please enter again:")
                    cvv = input()
                    continue
                else:
                    break
            except:
                print("CVV number is not valid.\n")
                print("Please enter again:")
                cvv = input()
                continue
            
    return status

# Once the validity check is passed the top_up_function is implemented to increase the user balance. The erros are
#  are dealt with using try-catch block to prevent and cash
def top_up_function(customer_balance, customer_id):
    print("Please Enter your 5 digit card number: ")
    card_number = input()

#     Check if the card number is valid. the card number should have 16 digits
    card_number = card_number_validation(card_number)
#     Check if the expiry date is valid
    if card_number != "0":
        status = card_date_validity(card_number)
        if status:
            print("Enter the full name on the card")
            full_name = input()
            print("\nHow much do you want to top up in £")
            top_up_amount = input()
            flag = True
            while flag:
                try:
                    # Check if the value is a positive number
                    if float(top_up_amount) < 0:
                        raise ValueError('the value  must be greater than 0')
                    type(float(top_up_amount))
                    flag = False
                except:
                    print ("Wrong entery")
                    print("How much do you want to top up in £")
                    top_up_amount = input()
    
            customer_balance = customer_balance + float(top_up_amount);
            
            #update payment table
            cursor.execute("""
            INSERT INTO payment (customer_id, card_number, name_on_card, amount) 
            VALUES (?, ?, ?, ?)
            """,(customer_id, card_number, full_name, top_up_amount))
            db.commit();
            #update customer balance with regards to their recent payment in customer table
            cursor.execute("""
            UPDATE customer SET balance = ?
            WHERE customer_id = ? """,(customer_balance, customer_id))
            db.commit();
            


            payment_failure = False;
        else:
            payment_failure = True;
    else:
        payment_failure = True;
            
    return customer_balance, payment_failure;

# This function initially checks if the user wants to proceed with payment and returns the payments status to confirm
# if the payment has been conducted successfully. It is main function in the payement which implements other relevant
#  functions for top_up
def PAYMENT(top_up, customer_balance, customer_id):
    flag= True
    while flag:
        if (top_up == "t"):
            customer_balance, payment_failure = top_up_function(customer_balance, customer_id);
            flag = False
            if payment_failure:
#                 flag = True
                break
        elif (top_up == "0"):
            print("Quitting the program")
            payment_failure = True
            flag = False
            break
        else:
            print("Wrong enter. Please Enter t to top up money into your account",
              " or enter 0 to quit")
            top_up = input()
    return customer_balance, payment_failure

# the BOOKING function combines the functionality of all other functions- STATIONS, BIKES and PAYMENT to help user 
# go through a booking process and finally, when booking is completed all relevant tables are updated accordingly.

def BOOKING(customer_id):
        #Retrieving data from database and store in as a dataframe
        pd.set_option('display.max_rows', 100)

        bike_station = pd.read_sql_query("""SELECT * FROM Bike_station WHERE 
                                         number_of_bikes_available > 0 """, db)
        bike_station = bike_station.rename(index = lambda x: x + 1);

        selected_station_id = STATION(bike_station)


        #Retrieving data from database and store in as a dataframe
        pd.set_option('display.max_rows', 25)
        bikes = pd.read_sql_query("SELECT * FROM Bikes", db)
        bikes = bikes.rename(index = lambda x: x + 1)

        if selected_station_id != 0:
            bike_selected_index, bike_selected,  bike_selected_fare = BIKE(bikes, selected_station_id)
            if (bike_selected_index != 0):
#             Check if the customer has sufficient balance
                min_balance = 1.0
                print("Minimum balance should exceed", "£{:,.2f}".format(min_balance),
                      "to rent a bike")

                cursor.execute("""
                SELECT balance FROM Customer WHERE customer_id = ?
                """, [customer_id]);

                customer_balance = float(cursor.fetchone()[0]);

                print("You have ", "£{:,.2f}".format(customer_balance)," in your account\n")


                flag = True
                while flag:
                    if (customer_balance >= min_balance):
                        print ("£{:,.2f}".format(min_balance), 
                               "will be deducted from your account to secure the booking")
                        # Update customer balance
                        customer_balance = customer_balance - min_balance

                        cursor.execute("""
                        UPDATE Customer SET balance = ? WHERE customer_id = ? """, 
                                       (customer_balance, customer_id) );
                        db.commit();

                         # creat an otp to unlock the bike
                        otp = randint(100000, 999999);

                        # Booking Date and time
                        date_and_time = datetime.now()
                        date_of_booking = date_and_time.strftime("%b-%d-%Y")
                        time_of_booking = date_and_time.strftime("%H:%M:%S")
                        # Retrieve Start Station Name
                        cursor.execute("""
                            SELECT station_name FROM bike_station WHERE station_id = ?
                            """, [selected_station_id]);
                        start_location = cursor.fetchall()[0][0]
                        
                        # updating booking table
                        print("\nCongrats! You have sufficeint balance to proceed with the booking")
                        cursor.execute("""
                        INSERT INTO Booking(start_location,start_station_id,customer_id, 
                        bike_id, fare, start_time, start_date, otp, current_balance, return) 
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (start_location, selected_station_id, customer_id, 
                              bike_selected,bike_selected_fare,
                              time_of_booking, date_of_booking, str(otp), customer_balance, "False" ));
                        db.commit();

                        # updating bikes table by setting booking_status to 0
                        cursor.execute("""
                        UPDATE Bikes SET booking_status = 0 WHERE bike_id = ? AND 
                        functionality_status = 1""", [bike_selected] );
                        db.commit();
                        
                        # updating Bike_station table with the number of bikes available 
                        # at the bike station
                        cursor.execute("""
                        SELECT SUM(booking_status) FROM Bikes WHERE station_id = ? AND 
                        functionality_status = 1""", [selected_station_id]);
                        update_no_of_bikes = cursor.fetchone()[0];
                        db.commit();
                        cursor.execute("""
                           UPDATE Bike_station SET number_of_bikes_available = ?
                           WHERE  station_id = ? """,(update_no_of_bikes, selected_station_id))
                        db.commit();

                        # Update Station table with regards to the capacity
                        cursor.execute(""" UPDATE Bike_station SET capacity_left = 
                            total_capacity - number_of_bikes_available 
                            """)
                        db.commit()

                        print("Booking confirmed. Here are your booking details: ")

                        last_booking = pd.read_sql_query("""SELECT * FROM booking ORDER BY booking_id 
                            DESC LIMIT 1 """, db).rename(index = lambda x: x + 1)

                        last_booking = last_booking.iloc[: , [0,1,2,3,6,8,10,13,14]]
                        last_booking.columns = ["Booking ID", "Customer ID", "Bike ID",
                                                "Fare per hour", "Start Station Name","Start Time", 
                                                "Start Date", "OTP", "Current Balance"]
                        display(last_booking)
                        flag = False
                    else:
                        print("Booking failed! You need to top up you account to at least",
                              "£{:,.2f}".format(1))
        #                remove print("You current balance is: ", "£{:,.2f}".format(customer_balance))
                        print("Please enter t to top up or 0 to quit")
                        top_up = input()
                        customer_balance, payment_failure = PAYMENT(top_up, customer_balance, customer_id)
                        if (payment_failure or customer_balance < min_balance):
                            print("Booking failed! for unsufficeint balance")
        #                     flag = False
                            break
                        
# The function is similar to STATION funcntion and has been minorly modified to comply with the return process. The 
#  customer is diplsay a list of stations, and then aksed to enter a station to which they want to take the bike 
# and checks validity of input. The station ID is returned for the next steps to update the relevant data into 
#  database
def STATION_RETURN(bike_station):
    # Display the statoins infromation to the customer
    display(bike_station.rename(columns={
        'station_id': 'Station ID', 'station_name': 'Station Name', 
        'location': 'Location', 'station_latitude': 'Station Latitude', 
        'station_longitude': 'Station Latitude','country': 'Country',
        'city': 'City', 'number_of_bikes_available': 'Number of Bikes Available',
        'capacity_left': 'Capacity Left'
    }).iloc[: , :9])  
    # store stations id
    stations_id_list = bike_station["station_id"].tolist()

    # Ask user to select a station using function selecting_station() 
    selected_station_id = selecting_station(stations_id_list) 
    ######## By entering Zero customer must be guided to main menu #####################
    tag = True
    confirm_station = "n"
    while ( selected_station_id != 0 and tag and confirm_station == "n"):
        selected_station_name = bike_station[bike_station["station_id"] 
                                         == selected_station_id]["station_id"].values[0]
        print("You selected ", selected_station_name, " with Station ID of ", selected_station_id)
        # Ask cutomer if they are certain of station
        confirm_station = input("Do you confirm the station? y/n ")
        confirm_station = str.lower(confirm_station)
        if (confirm_station == "yes"):
            confirm_station = "y"
        elif (confirm_station == "no"):
           confirm_station = "n" 

        tag = True
        (tag, selected_station_id, 
         confirm_station) = confirm_station_selection(tag, confirm_station, selected_station_id,
                                                     stations_id_list)
        if selected_station_id != 0:
            # The line below ensures the selected_station_name is assigned correctly when 
            # iterating by entering incorrect entries or when customer changes his/her decision
            # by not confirming previous choice
            selected_station_name = bike_station[bike_station["station_id"] 
                                         == selected_station_id]["station_name"].values[0]
            print("\nBelow you can see information about the station and" ,
                  "list of bikes available at the station of ", selected_station_name, "\n")
            display(bike_station[bike_station["station_id"] == 
                         selected_station_id].rename(columns={
            'station_id': 'Station ID', 'station_name': 'Station Name', 
            'location': 'Location', 'station_latitude': 'Station Latitude', 
            'station_longitude': 'Station Latitude','country': 'Country',
            'city': 'City', 'number_of_bikes_available': 'Number of Bikes Available',
            'capacity_left': 'Capacity Left'}).iloc[: , :9]) 
    return selected_station_id;

# Funciton used to top up money
def WALLET(customer_id):
    cursor.execute(""" SELECT balance FROM customer WHERE customer_id = ?
    """, [customer_id])
    customer_balance = (cursor.fetchall()[0][0]);
    top_up = "t"
    customer_balance, payment_failure = PAYMENT(top_up, customer_balance, customer_id)
    if payment_failure:
        print("The payment failed!")
        print("Your current balance is: ", "£{:,.2f}".format(customer_balance))
    else:
        print("Your balance increased to ", "£{:,.2f}".format(customer_balance))      

# ---Rent a bike---

# function ised to rent a bike
def RENT_A_BIKE(customer_id):
    #Check customer previous records
    record = pd.read_sql_query("""SELECT booking_id FROM Booking WHERE customer_id = ? AND 
    return = "False" """, db, params=[customer_id])
   # Retrieve customer balance
    cursor.execute(""" SELECT balance FROM customer WHERE customer_id = ?
    """, [customer_id])
    customer_balance_record = (cursor.fetchall()[0][0]);

    if record.empty and customer_balance_record >= 0:
        # Go through the booking Process
        BOOKING(customer_id)
    elif not record.empty:
        print("You have already booked a bike with the following information:")
        temp = pd.read_sql_query("""SELECT * FROM booking  WHERE customer_id = ? 
         AND return = "False" """, db, params= [customer_id]).rename(index = lambda x: x + 1)
        temp = temp.iloc[: , [0,1,2,3,6,8,9,13,14]]
        temp.columns = ["Booking ID", "Customer ID", "Bike ID",
                                                "Fare per hour", "Start Station Name","Start Time", 
                                                "Start Date", "OTP", "Current Balance"]
        display(temp)
    else:
        print("Your credit is negative by ", "£{:,.2f}".format(customer_balance_record))
        print("You should first increase your balance to the minimum of ""£{:,.2f}".format(1))
        print("If you like to continue with payment please enter t, otherwise 0 to quit")
        top_up = input()
        while not (top_up == "t" or top_up == "0"):
                    print("please enter t to continue with payment otherwise 0 to quite ")
                    top_up = input()
        customer_balance, payment_failure = PAYMENT(top_up, customer_balance_record, customer_id)
        if customer_balance > 1:
            BOOKING(customer_id)
        else:
            print("You do not have suffcient credit to continue")

# ---Return a bike---

# function used to return a bike
def RETURN_A_BIKE(customer_id):
    #Check customer previous records
    record = pd.read_sql_query("""SELECT booking_id FROM Booking WHERE customer_id = ? AND 
    return = "False" """, db, params=[customer_id])

    #Those customers which have already booked a bike can go through return process
    if not record.empty:


        bike_station = pd.read_sql_query("""SELECT * FROM Bike_station """, db)
        bike_station = bike_station.rename(index = lambda x: x + 1);
        selected_station_id = STATION_RETURN(bike_station)

        if selected_station_id != 0:
                #Calculate the fee and trip duratin
            date_and_time = datetime.now()
            date_of_return = date_and_time.strftime("%b-%d-%Y")
            time_of_return = date_and_time.strftime("%H:%M:%S")
            date_of_booking_db = pd.read_sql_query("""SELECT start_date FROM booking WHERE customer_id = ? AND
                                                   return = "False" """
                                               , db, params=[customer_id]).iloc[0,0]



            time_of_booking_db = pd.read_sql_query("""SELECT start_time FROM booking WHERE customer_id = ? AND
                                                   return = "False" """
                                               , db, params=[customer_id]).iloc[0,0]#Convert the start time and date from string to date
            start_date_time = datetime.strptime(date_of_booking_db + " " 
                                                + time_of_booking_db, "%b-%d-%Y %H:%M:%S")
            trip_duration_hr =  (datetime.now() - start_date_time)
            trip_duration_hr = round(trip_duration_hr.total_seconds()/3600, 2)
            
            # trip_duration_hr remove
            fee_per_hr = pd.read_sql_query("SELECT fare FROM booking WHERE customer_id = ?"
                                                   , db, params=[customer_id]).iloc[0,0]
            
            total_fee = round(trip_duration_hr * fee_per_hr,2)
            print("Your total fee is ", "£{:,.2f}".format(total_fee), "which will be deducted from",
                 "your account")
            customer_balance = pd.read_sql_query("SELECT balance FROM customer WHERE customer_id = ?"
                                                   , db, params=[customer_id]).iloc[0,0]
            if (customer_balance - total_fee) < 0:
                print("Your current balance is", "£{:,.2f}".format(customer_balance))
            # "£{:,.2f}".format(customer_balance) remove
            # debt = customer_balance - total_fee
            if (customer_balance - total_fee) < 0:
                print("You do not have sufficent money in your account")
                print("if you like to continue with the payment press t otherwise 0 to quite")
                recharge = input()
                while not (recharge == "t" or recharge == "0"):
                    print("please enter t to continue with payment otherwize 0 to quite ")
                    recharge = input()
                if recharge == "t":
                    flag = True
                    while flag:
                        top_up = recharge
                        customer_balance, payment_failure = PAYMENT(top_up, customer_balance, customer_id)
                        if (payment_failure):
                            print("Payment failed")
                            print("Your credit is : ", "£{:,.2f}".format(customer_balance - total_fee))
                            break
                        elif (customer_balance < total_fee):
                            print("Not sufficient balance yet")
                            print("You need to pay ", "£{:,.2f}".format(customer_balance - total_fee),
                                  " to pay off:")
                            recharge = input("Please enter t to continue with payment or 0 to quite: ")
                            while not (recharge == "t" or recharge == "0"):
                                print("please enter t to continue or 0 to quit: ")
                                recharge = input()
                            if recharge == "y":
                                top_up = input()
                                customer_balance, payment_failure = PAYMENT(top_up, customer_balance, customer_id)
                                continue
                            else:
                                print("Your credit is : ", 
                                      "£{:,.2f}".format(customer_balance - total_fee))
                                break
                        else:
                            break
                else:
                    print("Your credit is : ", "£{:,.2f}".format(customer_balance - total_fee))

            customer_balance = customer_balance - total_fee
            # Update customer balance
            cursor.execute("""UPDATE Customer SET balance = ? WHERE customer_id = ? """, 
                           (customer_balance, customer_id) );
            db.commit()

            # updating bikes table by setting booking_status to 1
            cursor.execute("""
            SELECT bike_id FROM Booking WHERE customer_id = ? and return = "False" """
                                           , [customer_id]);
            bike_selected = cursor.fetchone()[0];
            cursor.execute("""
            UPDATE Bikes SET booking_status = 1 WHERE bike_id = ? """, [bike_selected] );
            db.commit();

        #     Update station ID of the bike above
            cursor.execute("""
            UPDATE Bikes SET station_id = ? WHERE bike_id = ? """
                           , (selected_station_id,bike_selected) );
            db.commit();


            # updating Bike_station table with the number of bikes available 
            # at the bike station
            cursor.execute("""
            SELECT SUM(booking_status) FROM Bikes WHERE station_id = ? AND 
                        functionality_status = 1 """, [selected_station_id]);
            update_no_of_bikes = cursor.fetchone()[0];
            cursor.execute("""
               UPDATE Bike_station SET number_of_bikes_available = ?
               WHERE station_id = ? """,(update_no_of_bikes, selected_station_id))
            db.commit();


            # Retrive the name of station
            cursor.execute("""
                                SELECT station_name FROM bike_station WHERE station_id = ?
                                """, [selected_station_id]);
            end_location = cursor.fetchall()[0][0]

            # Update Booking table and set the return to True
            cursor.execute(""" UPDATE booking SET 
            end_station_id = ?,
            end_location = ?,
            end_time = ?,
            end_date = ?,
            time_duration = ?,
            current_balance = ?,
            total_fee = ?,
            return = "True" 
            WHERE return = "False" AND customer_id = ?
            """, (selected_station_id, end_location, time_of_return, date_of_return, trip_duration_hr,
                 customer_balance, total_fee, customer_id))

            # Update Station table with regards to the capacity
            cursor.execute(""" UPDATE Bike_station SET capacity_left = 
                total_capacity - number_of_bikes_available 
                """)
            db.commit()
            
            cursor.execute("""SELECT sum(total_fee) 
                            FROM Booking WHERE customer_id = ?""", [customer_id])
            total_fee = cursor.fetchall()[0][0]
            cursor.execute("""
                            UPDATE customer SET total_spend = ? WHERE customer_id = ?""", 
                            (total_fee, customer_id))
            db.commit()

            print("Bike returned successfully")
            # Show relevant data to customer
            temp = pd.read_sql_query("""SELECT * FROM booking  WHERE customer_id = ? 
             ORDER BY booking_id DESC LIMIT 1 """, db, params= [customer_id]).rename(index = lambda x: x + 1)
            temp = temp.iloc[: , [0,1,2,3,6,7,8, 9,10,11,12,15, 14]]
            temp.columns = ["Booking ID", 
                            "Customer ID", "Bike ID", "Fare per hour", "Start Station Name", 
                            "Final Station", "Start Time","Start Date", "End Time","End Date",
                            "Time Duration (hr)","Total Fee","Current Balance"]
            display(temp)

            if customer_balance < 0:
                print("Your credit balance is: ", "£{:,.2f}".format(customer_balance))
    else:
        print("You have no bike to return")                  
        
pd.set_option('display.max_rows', 100)

# ---Report a bike---
    
# define a function to check if an input is left empty   
def check_empty(x):
    # set full to True initially
    full = True
    
    # if the input is left blank display an error and set full to False
    if x == "":
        print("\nCannot leave field empty!")
        full = False
        
    # return the value of full
    return full    

# define a function to check if an input is an integer
def check_int(x):
    # set integer to True initally
    integer = True
    # if the input is not an integer display an error message and set integer to False
    if not x.isdigit():
        print("\nMust enter an integer!")
        integer = False
    return integer
 
# create a function for customer to report a bike
def report_bike():
    
    # set customer_id to that of the current customer signed in
    customer_id = get_customer_id()

    # get the most recent bike id that the current customer has booked
    cursor.execute("""SELECT bike_id FROM Booking WHERE customer_id==? 
                   ORDER BY booking_id DESC LIMIT 1""", (customer_id,))
    bike_id = [x[0] for x in cursor.fetchall()]
    
    # display the bike    
    print("\n-----------------------Report a Bike------------------------")
    
    # if the customer doesn't have any bikes booked display an error and quit
    if bike_id == []:
        print("\nYou don't have any booked bikes to report!")
        
    # else continue with report bike process    
    else:
        # create a data frame for the bike and the relevant details for the customer
        bike_frame = pd.read_sql_query("""SELECT bike_id, booking_id FROM Bikes 
                                       WHERE bike_id==?""", db, params = bike_id)
        bike_frame.columns = ["Bike ID", "Booking ID"]
        bike_frame = bike_frame.rename(index = lambda x: x + 1)
        bike_frame.style.set_properties(**{'text-align': 'center'})
        bike_frame.style.hide_index()
        bike_id = bike_id[0]
        
        # display the bike
        print("\nYour Booked Bikes")
        bike_frame = bike_frame.to_string(index = False)
        print(bike_frame)
        
        # check that they want to report this bike
        bike = input("Would you like to report this bike? (y/n): ")
        if bike.lower() != 'y':
            print("Report cancelled.")
        
        else:
            # set booking_id to the booking associated with the reported bike
            cursor.execute("SELECT booking_id FROM Booking WHERE bike_id==?", (bike_id,))
            booking_id = [x[0] for x in cursor.fetchall()][0]
                
            # ask customer for the issue with the bike
            issue = input("Please describe the issue with the bike (e.g. flat tyre/ broken chain): ")
            
            # check they have not left it blank
            full = check_empty(issue)
            while not full:
                issue = input("Please describe the issue with the bike (e.g. flat tyre/ broken chain): ")
                full = check_empty(issue)
                
            # update the database to make bike unavailable
            cursor.execute("""UPDATE Bikes SET functionality_status=0 
                               WHERE bike_id==?""", (bike_id,))
            # save changes
            db.commit()  
            # update the database to record the issue with the bike
            cursor.execute("""INSERT INTO Report_Bike(issue_comments, booking_id, bike_id, report_status)
                               VALUES(?, ?, ?, 'open')""", (issue, booking_id, bike_id))
            # save changes
            db.commit()
            
            print("\nThank you for reporting bike " + str(bike_id) + ".")
       
# ---Track bikes---

def track_bike():
    
    with sqlite3.connect("bike_sharing_system.db")as db:
            cursor = db.cursor()      
  
    lat = cursor.execute("SELECT bike_latitude FROM Bikes ").fetchall()
    lats = []
    for i in range(len(lat)):
        lats.append(lat[i][0])
        #print(lats)
        
        lon = cursor.execute("SELECT bike_longitude FROM Bikes ").fetchall()
        lons = []
        for i in range(len(lon)):
            lons.append(lon[i][0])
            #print(lons)
            #lons[0]
    
    bid = cursor.execute("SELECT bike_id FROM Bikes ").fetchall()
    ids = []
    for i in range(len(bid)):
        ids.append(bid[i][0])
        #print(ids)
        
    
    ##track the location (latitude, longitude) of bikes     

    print("--------------------Track Bike-------------------------")
    df = pd.read_sql_query("""SELECT bike_id, bike_latitude, bike_longitude, at_station, booking_status FROM
                           Bikes """, db).rename(index = lambda x: x + 1)
    df.iloc[:][:]
    print(df.iloc[:][:])
    
    m = folium.Map([55.862773315974685, -4.250273471243701],zoom_start=12)
    
    for i in range(len(lats)):
        mk = features.Marker([lats[i],lons[i]])
        popuptext = ("Bike_ID : " + str(ids[i]) +
                     "\nlatitude: " + str(lats[i]) +
                     "\nlongitude: " + str(lons[i]))
        iframe = folium.IFrame(popuptext, width=300, height=100)
        pp = folium.Popup(iframe)    
        #pp = folium.Popup("Bike_ID: "+ str(ids[i]))
        ic = features.Icon(color="blue")
        mk.add_child(ic)
        mk.add_child(pp)
        m.add_child(mk)

    m.save("mymap.html")

    # open a tab to display the map
    webbrowser.open_new_tab('mymap.html')
     
# ---Move bikes---

#Move bikes menu for the manager
def move_bike():
    print("***************Move bikes***************")
    choice = int(input("Press 1 to track bikes. \nPress 2 for move bikes \n"))
    
    #Validate user input for choice
    if choice < 1 and choice >2:
        print("Please enter correct choice")
        move_bike()
        
    else :    
        #If manager wants to track the bikes on the map.
        if choice == 1:
            track_bike()
        
        #If manager wants to move the bikes
        if choice == 2:
            
            #input Bike Id and Station id from the user
            bike_id_input = input("Enter the Bike id you want to move \n")
            station_id_input = input("Enter the Station Id at which you want to move the bike \n")
            
            #Validate the Bike Id and Station Id from the database
            bike_id = get_bike_id()
            station_id = get_station_id(station_id_input)
            
            #Fetch location of Station and update the same with Bike because bike and station have the same location
            bike_lat = pd.read_sql_query(""""SELECT station_latitude FROM bike_station where station_id = ?""", db, params = (station_id,)).rename(index = lambda x: x + 1)
            bike_long = pd.read_sql_query(""""SELECT station_longitude FROM bike_station where station_id = ?""", db, params = (station_id,)).rename(index = lambda x: x + 1)   
                
            
            cursor.execute(" Update Bikes set bike_latitude = %s, bike_longitude = %s where bike_id = %s" %( bike_lat, bike_long, bike_id))
            db.commit()
            
            print("Bike id : %s has been moved to station Id : %s and updated in the database")

# ---Repair a bike---

def validate_report_bike():
    print("--------------Report Bike Data--------------------")
    
    df = pd.read_sql_query("""SELECT * FROM report_bike WHERE report_status = ?""", db, params = ('open',)).rename(index = lambda x: x + 1)
    
    print(df.iloc[:][:])
    
    
    issue_id_input = int(input("Enter the issue id to validate : "))
    issue_id = get_issue_id(issue_id_input)
    
    issue_record_df = pd.read_sql_query("""SELECT * FROM
                                    report_bike WHERE issue_id = ?""", db, params = (issue_id,)).rename(index = lambda x: x + 1)
    bike_id_df = pd.read_sql_query("""SELECT bike_id FROM
                                    report_bike WHERE issue_id = ?""", db, params = (issue_id,)).rename(index = lambda x: x + 1)
    
    bike_id = bike_id_df.iloc[0][0]
    db.commit()
    print(issue_record_df.iloc[:][:])
    update_report_bike_status(issue_id,bike_id)
 
def update_report_bike_status(issue_id,bike_id):
    
   
    valid_status = input("Is report valid? Press y/n")
    
    if not  (valid_status =='y' or valid_status == 'n') :
        print("Not a valid input..")
        update_report_bike_status(issue_id,bike_id)
    
    if valid_status == 'y':
        cursor.execute(" Update report_bike set valid_status = 'valid' and report_status = 'closed'  where issue_id = ?""", ( issue_id,))
        db.commit()
        repair_menu(issue_id,bike_id)    
        
    if valid_status == 'n':
        cursor.execute(" Update report_bike set valid_status = 'invalid' and report_status = 'closed'  where issue_id = ?""", ( issue_id,))
        db.commit()
        
def get_issue_id(issue_id_input):
    
    try :
        issue_id_df = pd.read_sql_query("""SELECT issue_id FROM
                                    report_bike WHERE issue_id = ?""", db, params = (issue_id_input,)).rename(index = lambda x: x + 1)
    
        issue_id = issue_id_df.iloc[0][0]
        return int(issue_id)
    
    #IF user enter invalid bike_id the fucntion will be called again
    except:
        issue_id_input1 = input("Please enter a valid Issue Id :")
        get_issue_id(issue_id_input1)
        
#Function to fetch the Bike issue from the manager of the system
def repair_menu(issue_id, bike_id):
    
    with sqlite3.connect("bike_sharing_system.db") as db:
        cursor=db.cursor()
    #Repair Menu for the manager
    print("----------------------------Repair-----------------------------")
    print("\n\n\n")
    print("Select an issue inorder to repair the bike")
    print("1. Issue with Chain \n")
    print("2. Issue with handle \n")
    print("3. Issue with seat \n")
    print("4. Issue with pedals \n")
    print("5. Issue with motor \n")
    print("6. For any other issue \n")
    print("7. To update repair status \n")
    
    #validation for choice field from the user
    choice = int(input())
    if choice < 1 and choice >7:
        print("Please enter correct choice")
        repair_menu(issue_id,bike_id)
        
        
    #If the manager wants to update the repair status    
    elif choice == 7:
        update_repair_status(bike_id)
        
    #Call function to insert the repair details
    else:
        bike_id = get_bike_id()
        #print("In bike")
        repair_insert_data(choice,bike_id,issue_id)
 
#Function to fetch the bike_id from the user and vlaidate it from the database
def get_bike_id():
    
    with sqlite3.connect("bike_sharing_system.db") as db:
        cursor=db.cursor()
    bike_id_input = input("Enter Bike Id of the bike which you want to repair : \n")
    #cursor.execute("SELECT bike_id FROM Bikes WHERE bike_id=?", (bike_id_input,))
    
    #Validate bike_id from the database
    bike_id_df = pd.read_sql_query("""SELECT bike_id FROM
                                    bikes WHERE bike_id = ?""", db, params = (bike_id_input,)).rename(index = lambda x: x + 1)
   
    #Returning the bike_id back to parent function
    try :
        bike_id = bike_id_df.iloc[0][0]
        print(bike_id)
        return bike_id
    
    #IF user enter invalid bike_id the fucntion will be called again
    except:
        print("Invalid Bike Id. Please enter valid Bike Id")
        get_bike_id()

#Function to insert repair details into Repair table
def repair_insert_data(choice,bike_id,issue_id):
    
    with sqlite3.connect("bike_sharing_system.db") as db:
        cursor=db.cursor()
    #Insert repair for chain issue
    if choice == 1:
        #print("inside")
        #print(bike_id)
        cursor.execute("""INSERT INTO Repair(chain_issue, handle, seat, pedals, motor, others, repair_status, bike_id,issue_id)
                   VALUES(?, ?,?,?,?,?,?,?,?)""", ('1','0','0','0','0','0','Open', bike_id,issue_id))

        
        db.commit()
        #print("In choice")
        
        
    #Insert repair for handle issue
    if choice == 2:
        cursor.execute("""INSERT INTO Repair(chain_issue, handle, seat, pedals, motor, others, repair_status, bike_id,issue_id)
                   VALUES(?, ?,?,?,?,?,?,?,?)""", ('0','1','0','0','0','0','Open', bike_id,issue_id))
        db.commit()
        
    
    #Insert repair for seat issue
    if choice == 3:
        cursor.execute("""INSERT INTO Repair(chain_issue, handle, seat, pedals, motor, others, repair_status, bike_id,issue_id)
                   VALUES(?, ?)""", ('0','0','1','0','0','0','Open', bike_id,issue_id))
        db.commit()
           
     #Insert repair for pedals issue
    if choice == 4:
        cursor.execute("""INSERT INTO Repair(chain_issue, handle, seat, pedals, motor, others, repair_status, bike_id,issue_id)
                   VALUES(?, ?,?,?,?,?,?,?,?)""", ('0','0','0','1','0','0','Open', bike_id,issue_id))
        db.commit()
    
     #Insert repair for motor issue               
    if choice == 5:
        cursor.execute("""INSERT INTO Repair(chain_issue, handle, seat, pedals, motor, others, repair_status, bike_id,issue_id)
                   VALUES(?, ?,?,?,?,?,?,?,?)""", ('0','0','0','0','1','0','Open', bike_id,issue_id))
        db.commit()
          
        
     #Insert repair for any other issue
    if choice == 6:
        other_issue = input("Please say some lines about the issue you are having with the bike")
        cursor.execute("""INSERT INTO Repair(chain_issue, handle, seat, pedals, motor, others, repair_status, bike_id,issue_id)
                   VALUES(?, ?,?,?,?,?,?,?,?)""", ('0','0','0','0','0',other_issue,'Open', bike_id,issue_id))
        db.commit()
        
    show_data()
    
                   
#Function to update the repair status of bikes
def update_repair_status(bike_id):
    
    with sqlite3.connect("bike_sharing_system.db") as db:
        cursor=db.cursor()
    print("---------------------Update Repair Status-------------------------------------")
    
    #fetch repair_id from manager
    repair_id = int(input("Enter repair id of the bike "))
    status = int(input("Enter 1 if the repair is in process. \n. Press 2 if the bike has been repaired.\n Press 3 if the issue has been closed"))
    
    #Validate user choice
    if status < 1 and status > 3:
        print("Please enter correct choice")
        update_repair_status()
        
    # Set repair status to In-progress
    if status == 1:
         cursor.execute(""" Update Repair set repair_status = ? where repair_id = ?""", ('In-Progress', repair_id))
         db.commit()
    
    # Set repair status to Repaired
    if status == 2:
         cursor.execute(""" Update Repair set repair_status = ? where repair_id = ?""", ('Repaired', repair_id))
         db.commit()
    
    #Repair status to Closed
    if status == 3:
         cursor.execute(""" Update Repair set repair_status = ? where repair_id = ?""", ('Closed', repair_id))
         cursor.execute(""" Update Bikes set functionality_status = ? where bike_id = ?""", ('Y', bike_id))
         db.commit()
         
    show_data()
        
#Function to show data of Repair table for manager      
def show_data():
    with sqlite3.connect("bike_sharing_system.db") as db:
        cursor=db.cursor()
    df = pd.read_sql_query("""SELECT * FROM
                           Repair """, db).rename(index = lambda x: x + 1)
    df.iloc[:][:]
    print(df.iloc[:][:])
    
# ---Generate reports---
       
def data_viasualisation():
    print("-------------------data visualisation-------------------------")   
    with sqlite3.connect("bike_sharing_system.db")as db:
        cursor = db.cursor()    
        
        time = cursor.execute("SELECT time_travelled FROM Bikes ").fetchall()
        y1 = []
        for i in range(len(time)):
            y1.append(time[i][0])
   
        x1 = np.arange(1,len(y1)+1,1)

    #draw scatter
    plt.scatter(x1, y1, alpha=0.8)
    #plt.scatter(x1, y1, alpha=0.8)
    plt.xlabel('bike_id')
    plt.ylabel('time_travelled')
    plt.title('time period',fontsize=20)
    plt.show()
    #plt.savefig('myplot.jpg')
    
    ##draw pie chart
    with sqlite3.connect("bike_sharing_system.db")as db:
        cursor = db.cursor()
            
        normal = cursor.execute("SELECT bike_type FROM Bikes WHERE bike_type=?",[1]).fetchall()
        x2 = len(normal)
        #print(x2)
    
    special = cursor.execute("SELECT bike_type FROM Bikes WHERE bike_type=?",[0]).fetchall()
    x3 = len(special)
    #print(x3)

    #index = np.arange(2)
    labels1 = ["normal","special"]
    values1 = [x2, x3]
    colors = ["yellow", "orange"]
    plt.title("the types of bike", fontsize=20)
    plt.pie(values1,labels=labels1,colors=colors)
    plt.show()
    
    ##draw a bar chart
    with sqlite3.connect("bike_sharing_system.db")as db:
        cursor = db.cursor()
    
    df = pd.read_sql_query("""SELECT bike_id, bike_latitude, bike_longitude, at_station FROM
                           Bikes """, db).rename(index = lambda x: x + 1)
    df.iloc[:][:]
    print(df.iloc[:][:])
    
    #cursor.execute("SELECT bike_id, bike_latitude, bike_longitude, booking_status, at_station FROM Bikes ORDER BY at_station")
    #for x in cursor.fetchall():
        #print(x)
    with sqlite3.connect("bike_sharing_system.db")as db:
        cursor = db.cursor()  
    n = cursor.execute("SELECT at_station FROM Bikes WHERE at_station=?",["North"]).fetchall()
    x4 = len(n)
    #print(x4)
    s = cursor.execute("SELECT at_station FROM Bikes WHERE at_station=?",["South"]).fetchall()
    x5 = len(s)
    w = cursor.execute("SELECT at_station FROM Bikes WHERE at_station=?",["West"]).fetchall()
    x6 = len(w)
    e = cursor.execute("SELECT at_station FROM Bikes WHERE at_station=?",["East"]).fetchall()
    x7 = len(e)
    c = cursor.execute("SELECT at_station FROM Bikes WHERE at_station=?",["Center"]).fetchall()
    x8 = len(c)
    
    index = np.arange(5)
    values = [x4, x5, x6, x7, x8]
    plt.title("the number of bikes per station", fontsize=20)
    plt.bar(index, values, label = "distrubution", color = "green")
    plt.xticks(index,["North","South", "West", "East", "Centre"])
    plt.show()
    
    ####draw  map
    m = folium.Map([55.862773315974685, -4.250273471243701], zoom_start=12)
    
    #North
    mk = features.Marker([55.9844325490751, -4.32232734035766])
    popuptext = "North Station\n: "+"There are "+str(len(n))+" bikes"
    iframe = folium.IFrame(popuptext, width=300, height=70)
    pp = folium.Popup(iframe)
    #pp = folium.Popup("North Station\n"+"There are "+str(len(n))+" bikes")
    ic = features.Icon(color="red")
    mk.add_child(ic)
    mk.add_child(pp)
    m.add_child(mk)
    
    #Sorth
    mk = features.Marker([55.7309828619415, -4.0219092444521])
    popuptext = "South Station\n: "+"There are "+str(len(s))+" bikes"
    iframe = folium.IFrame(popuptext, width=300, height=70)
    pp = folium.Popup(iframe)
    #pp = folium.Popup("South Station\n"+"There are "+str(len(s))+" bikes")
    ic = features.Icon(color="green")
    mk.add_child(ic)
    mk.add_child(pp)
    m.add_child(mk)
    
    #west
    mk = features.Marker([55.7599958808589, -4.64387500933889])
    popuptext = "West Station\n: "+"There are "+str(len(w))+" bikes"
    iframe = folium.IFrame(popuptext, width=300, height=70)
    pp = folium.Popup(iframe)
    #pp = folium.Popup("Weat Station\n"+"There are "+str(len(w))+" bikes")
    ic = features.Icon(color="blue")
    mk.add_child(ic)
    mk.add_child(pp)
    m.add_child(mk)
    
    #East
    mk = features.Marker([55.7899958808589, -3.64387500933889])
    popuptext = "East Station: "+"There are "+str(len(e))+" bikes"
    iframe = folium.IFrame(popuptext, width=300, height=72)
    pp = folium.Popup(iframe)
    #pp = folium.Popup("East Station\n"+"There are "+str(len(e))+" bikes")
    ic = features.Icon(color="gray")
    mk.add_child(ic)
    mk.add_child(pp)
    m.add_child(mk)
    
    #centre
    mk = features.Marker([55.862773315974685, -4.250273471243701])
    popuptext = "Centre Station\n: "+"There are "+str(len(c))+" bikes"
    iframe = folium.IFrame(popuptext, width=300, height=70)
    pp = folium.Popup(iframe)
    #pp = folium.Popup("Centre Station\n"+"There are "+str(len(c))+"bikes")
    ic = features.Icon(color="orange")
    mk.add_child(ic)
    mk.add_child(pp)
    m.add_child(mk)
# =============================================================================
#     m.save("mymap1.html")
#     print("***************Show it on map(please open mymap1.html)***************")
# =============================================================================
  
    lat = cursor.execute("SELECT bike_latitude FROM Bikes ").fetchall()
    lats = []
    for i in range(len(lat)):
        lats.append(lat[i][0])
        #print(lats)
        
    lon = cursor.execute("SELECT bike_longitude FROM Bikes ").fetchall()
    lons = []
    for i in range(len(lon)):
        lons.append(lon[i][0])

    bid = cursor.execute("SELECT bike_id FROM Bikes ").fetchall()
    ids = []
    for i in range(len(bid)):
        ids.append(bid[i][0])
        
        
    time = cursor.execute("SELECT time_travelled FROM Bikes ").fetchall()
    times = []
    for i in range(len(time)):
        times.append(time[i][0])
        
        
    statu = cursor.execute("SELECT booking_status FROM Bikes ").fetchall()
    status = []
    for i in range(len(statu)):
        status.append(statu[i][0])
        #print(status)

    btype = cursor.execute("SELECT bike_type FROM Bikes ").fetchall()
    types = []
    for i in range(len(btype)):
        types.append(btype[i][0])
        #print(types)
        
        
    with sqlite3.connect("bike_sharing_system.db")as db:
            cursor = db.cursor()     

    #m = folium.Map([55.862773315974685, -4.250273471243701],zoom_start=12)

    for i in range(len(lats)):
        mk = features.Marker([lats[i],lons[i]])
        popuptext =(" Bike_ID: "+ str(ids[i]) + "\n"+
                    "The duration is " +str(times[i]) +" hours" + "\n"+
                    "booking status is "+str(status[i]) + "(0:booked 1:availiable)"+"\n"+
                    "The type is " + str(types[i]) + " (0:special bike 1:normal bike)")
        iframe = folium.IFrame(popuptext, width=350, height=100)
        pp = folium.Popup(iframe)
# =============================================================================
#         #pp = folium.Popup("Bike_ID: "+ str(ids[i]) + "\n\nThe duration is " +
#                           str(times[i]) +" hours\n" + "\nbooking status is "+
#                           str(status[i]) + "\n\n(0:booked 1:availiable)"+
#                           "\n\nThe type is " + str(types[i]) + " \n(0:special bike 1:normal bike)")
# =============================================================================
        ic = features.Icon(color="blue")
        mk.add_child(ic)
        mk.add_child(pp)
        m.add_child(mk)

    #m.save("mymap.html")
    m.save("mymap1.html")
    
    #open a tab to display the map
    webbrowser.open_new_tab('mymap1.html')

# ---Getter functions---

# define a function to get the customer_id of the signed in customer
def get_customer_id():
    # get the customer_id stored in the log in table
    cursor.execute("SELECT customer_id FROM user_details")
    customer_id = [x[0] for x in cursor.fetchall()][0]
    
    # return the customer id
    return customer_id

# define a function to get the admin_id of the signed in admin
def get_admin_id():
    # get the admin_id stored in the log in table
    cursor.execute("SELECT admin_id FROM user_details")
    admin_id = [x[0] for x in cursor.fetchall()][0]
    
    # return the admin id
    return admin_id

# define a function to get the customer and admin ids from the database
def get_db_ids():
    # get all saved customer ids from database
    cursor.execute("SELECT customer_id FROM Customer")
    db_customer = [x[0] for x in cursor.fetchall()]
    
    # get all saved admin ids from database
    cursor.execute("SELECT admin_id FROM Admin")
    db_admin = [x[0] for x in cursor.fetchall()]
    
    # return a tuple with both lists of ids
    return (db_customer, db_admin)

# define a function to check the signed in user is a customer
def check_customer():
    # set customer to False
    customer = False
    
    # get the id of the signed in user and the database customer ids
    customer_id = get_customer_id()
    db_customer = get_db_ids()[0]
    
    # if the customer is in the database list set customer to True
    if customer_id in db_customer:
        customer = True
    return customer

# define a function to check the signed in user is an admin
def check_admin():
    # set admin to False
    admin = False
    
    # get the id of the signed in user and the database admin ids
    admin_id = get_admin_id()
    db_admin = get_db_ids()[1]
    
    # if the admin is in the database list set admin to True
    if admin_id in db_admin:
        admin = True
    return admin

# define a function to get the designation of the admin
def get_designation():
    # get the id of the signed in admin
    admin_id = get_admin_id()
    
    # get the designation of that admin from the database
    cursor.execute("SELECT designation FROM Admin WHERE admin_id==?", (admin_id,))
    designation = [x[0] for x in cursor.fetchall()][0]
    
    # return the designation
    return designation

#Function to fetch the station_id from the user and vlaidate it from the database
def get_station_id(station_id_input):
    
    
    #Validate bike_id from the database
    station_id_df = pd.read_sql_query("""SELECT station_id FROM
                                    bike_station WHERE station_id = ?""", db, params = (station_id_input,)).rename(index = lambda x: x + 1)
   
    
    #Returning the station_id back to parent function
    try :
        station_id = station_id_df.iloc[0][0]
        left_capacity = pd.read_sql_query("""SELECT left_capacity FROM
                                    bike_station WHERE station_id = ?""", db, params = (station_id_input,)).rename(index = lambda x: x + 1)
        if(left_capacity > 0):
             return station_id 
        else :
            print("This station doesn't have capacity to accomodate more bikes ")
            station_id_input1 = input("Please enter a different station Id :")
            get_station_id(station_id_input1)
       
    
    #IF user enter invalid bike_id the fucntion will be called again
    except:
        station_id_input1 = input("Please enter a valid station Id :")
        get_station_id(station_id_input1)

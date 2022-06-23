# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 21:57:11 2021

@author: racha
"""

# import sys and the functions as f
import sys
import functions as f

# ---Welcome menu---

# define a function to display a welcome menu
def welcome_menu():
    print("\n---------------------------Menu----------------------------")
    print("1) Sign in")
    print("2) Sign up")
    print("3) Exit")
    # ask for the user's selection
    selection = input("Enter your selection: ")
    
    # check whether the selection is valid
    valid = f.check_selection(selection, 3)
    
    # if not ask the user to try again
    while not valid:
        selection = input("Enter your selection: ")
        valid = f.check_selection(selection, 3)
        
    selection = int(selection)
    
    # if user selects 1 then take them to sign in
    if selection == 1:
        f.sign_in()
    # if user selects 2 then take them to sign up
    elif selection == 2:
        f.sign_up()
    # if user selects 3 then exit the menu
    elif selection == 3:
        print("\nGoodbye!")
        sys.exit()

# ---Customer menu---
        
# define a function to display the customer menu
def customer_menu():
    # display the menu
    print("\n-------------------Menu--------------------")
    print("1) Rent a bike")
    print("2) Return a bike")
    print("3) Report a bike")
    print("4) Payment")
    print("5) Sign out")
    
    customer_id = f.get_customer_id()
    
    # ask user for their selection
    selection = input("Enter your selection: ")
    
    # check whether the selection is valid
    valid = f.check_selection(selection, 5)
    
    # if not ask the user to try again
    while not valid:
        selection = input("Enter your selection: ")
        valid = f.check_selection(selection, 5)
    
    # convert selection to an integer
    selection = int(selection)
    
    # execute the appropriate function for the user's selection
    if selection == 1:
        f.RENT_A_BIKE(customer_id)
        customer_menu()
    elif selection == 2:
        f.RETURN_A_BIKE(customer_id)
        customer_menu()
    elif selection == 3:
        f.report_bike()
        customer_menu()
    elif selection == 4:
        f.WALLET(customer_id)
        customer_menu()
    elif selection == 5:
        f.sign_out()
        
# ---Operator menu---

# define a function to display a operator menu
def operator_menu():
    print("\n----------------------Operator Menu-------------------------")
    print("Operator Menu")
    print("1) Track bikes")
    print("2) Repair bikes")
    print("3) Move bikes")
    print("4) Sign Out")
    
    # ask for the user's selection
    selection = input("Enter your selection: ")
    
    valid = f.check_selection(selection, 4)
    
    # if not ask the user to try again
    while not valid:
        selection = input("Enter your selection: ")
        valid = f.check_selection(selection, 4)
    
    # convert selection to an integer
    selection = int(selection)
    
    # if operator selects 1 then take them to track bike
    if selection == 1:
        f.track_bike()
        operator_menu()
        
    # if operator selects 2 then take them to repair
    elif selection == 2:
        f.validate_report_bike()
        operator_menu()
    
    # if operator selects 3 then take them to move bikes
    elif selection == 3:
        f.move_bike()
        operator_menu()
        
    # if operator selects 4 then take them to sign out
    elif selection == 4:
        f.sign_out()
        
    # if operator selects anything other than 1, 2, 3 or 4 then display an error message
    else:
        print("Invalid selection.")    
    
# ---Manager menu---

def manager_menu():
    print("\n----------------------Manager Menu-------------------------")
    print("1) Generate reports")
    print("2) Sign out")
    selection = input("Enter your selection: ")
    
    valid = f.check_selection(selection, 2)
    
    # if not ask the user to try again
    while not valid:
        selection = input("Enter your selection: ")
        valid = f.check_selection(selection, 2)
    
    # convert selection to an integer
    selection = int(selection)
    
    # if operator selects 1 then take them to data viasualisation
    if selection == 1:
        f.data_viasualisation()
        manager_menu()
        
    # if operate selects 2 then take them to sign out    
    elif selection == 2:
        f.sign_out()
        

# Bike Sharing System

## Table of contents
* [General Info] (#general-info)
* [Technologies] (#technologies)
* [Setup] (#setup)
* [Usage] (#usage)

## General Info
This project is a command line program to operate a bike sharing system.

## Technologies
This project is created with:
* Python version: 3.8.5
* Spyder version: 4.1.5
* Jupyter version: 6.1.4
* Folium version: 0.12.1

## Setup
To run this system first download and save in the same directory the following files:
* bike_sharing_system.db
* functions.py
* menus.py
* main.ipynb

Next ensure that folium is installed on your device. This can be done in the main.ipynb on Jupyter:
````
pip install folium

````

## Usage
To use the program please follow these steps:
* Ensure all the files are saved in the same directory
* Ensure folium is installed
* Launch main.ipynb in Jupyter
* Press run

### Welcome Menu
You will first be guided to a welcome menu where you can:
1) Sign in
2) Sign up
3) Exit

Depending on the number you enter you will be directed to the appropriate function. You can only sign up as a customer.

### Customer Menu
If you sign in as a customer you will be directed to the following menu:
1) Rent a bike
2) Return a bike
3) Report a bike
4) Payment
5) Sign out

Similar to the welcome menu, you will be taken to the corresponding function of your choice. When you sign out the welcome menu will be displayed
again, allowing you to sign in as another user.

An example customer you can use to sign in is:
* username: user1
* password: password1

### Operator Menu
If you sign in as an operator you will be directed to the following menu:
1) Track bikes
2) Repair bike
3) Move bikes
4) Sign out

This menu works in the same way as the previous menus.

An example operator you can use to sign in is:
* username: admin1
* password: password1

### Manager Menu
If you sign in as a manager, you will be directed to the following menu:
1) Generate reports
2) Sign out

This menu works in the same way as the previous menus.

An example manager you can use to sign in is:
* username: admin5
* password: password5

### Exiting the program
Once you are finished and wish to exit the program:
* Sign out of the current account
* Select exit



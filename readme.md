# README

This repository contains a scrapy spider for downloading the 2024 NBA standings from basketball-reference.com.

The script downloads the target html page locally if it isn't already present. Then, the spider's parse method extracts the standings for all the teams combined using xpath. After isolating and extracting the data, we save it to a pandas dataframe for further processing before printing it to the console and finally saving it to a local database we can query later on. 


# Step-by-Step

## Step 0: Start a scrapy project 
In your project folder start a scrapy project with an appropriate name. This will create a number of files and subdirectories in your project folder. One of those subdirectories is the spiders folder where this spider will live. The spiders folder will be located 2 levels down from your project folder: your path should look something like this ```project-name/project-name/spiders```. 

## Step 1: Import packages 
The script starts by importing the packages/libraries it needs to run. Here, we're using scrapy, os, datetime, requests, sqlite3 and pandas. 

## Step 2: Define global variables
We need to define our current directory, the name of the file we're writing, and the absolute path of the file.

## Step 3: Download HTML
To minimize the number of requests we're making to the server, we download the html file locally. Here, we're going to save it to the spiders folder, but you can specify any directory you wish. With the file saved locally, we can tweak our code without repeatedly pinging the server. 

Before downloading the file, we ask if the file is already present. If not, we'll download it using the requests package which provides an easy interface for the task. Checking if the file exists is as easy as using os.path.exists().

## Step 4.0: Define your custom class of spider
Because our needs are unique in each scraping project, we have to write a custom class of spider tailored to our situation. We define it by making it a child of the scrapy.Spider class. 

## Step 4.1 Define the spider's attributes
Each spider has a number of attributes which can be manipulated. For this spider we're just interested in the name, allowed_domains, and start_urls attributes. We give the spider a name to make it easy to deploy using the scrapy shell. Since we're scraping the NBA standings, I've named it 'basketball'. For the allowed_domains attribute we set it to www.basketball-reference.com and for the start_urls we pass it the file's full absolute path. 

## Step 4.2 Define the spider's parse method
This is where the meat and potatoes of the spider's work is defined. We want our spider to do a few things: It should extract the data, discard the data we don't want to retain, and format the data so that we're able to perform analyses of the data later on. 

### Step 4.2.1 Identify the table of interest
I'm interested in isolating the 2nd table from the bottom of the page. When we inspect the HTML we notice that the the div it is contained in has a specific id associated with it as does the table we're interested in. We can use those id's to hone in on the table we want as such:

``` table = response.xpath("//div[@id = 'div-id']").xpath("//table[@id = 'table-id']").xpath("tbody")```

Note that when searching for your tables using the attributes as we're doing here, it's important to use the double forward slash "//". Once you're 'in' the table's path, however, it's important to stop using the "//" in your subsequent xpath calls:

``` # Incorrect: len( table.xpath("//tr") )```

``` # Correct: len( table.xpath("tr") )```

This is because using the double slash will bring you ALL of the table row elements in the HTML whereas we just want the rows in the table we're interested in. 

### Step 4.2.2  Extract the data
We define an empty dictionary and label it table_data. This will be a nested dictionary wherein the team names will be the keys and their values will be a dictionary of statistics and associated values. 

We iterate through the rows and columns of the table in order to extract the data. For each row, we extract the team name and check if their name is already in the dictionary. If their name isn't already in the dicitonary, we define an empty dictionary where we'll store their statistics. 

For each teamn we'll iterate through the row's td tags to extract the statistic name and its value and assign it to the dictionary. 

## Step 4.3 Add the data to a data frame
Once we've gathered the data, we'll convert the dicitionary into a dataframe so we can perform some manipulations prior to uploading it to a local database. The script adds a team column, updates the index to be numeric, and adds a rank column. After adding these, we update their data types accordingly.

I've chosen to restrict the number of retained columns as I'm only interested in select statistics. 

Each cell represents a similar pattern that we can exploit to split using the str.split() method. This lets us split the columns of interest into multiple columns. As we split the columns, we set their data types as integers. Once we've gone through every column, we print the final data frame to the console before moving on to the next step. 


# Step 4.4 Persist locally
Finally, using sqlite3 we connect to the local database and append the records to the standings table, appending the data if there's already data there. 

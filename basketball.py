import scrapy
import os
import pandas as pd
import sqlite3
from datetime import date

current_directory = os.path.dirname(os.path.abspath(__file__))
file_name = 'NBA_2024_standings.html'


# Download html locally if it isn't already there
if os.path.exists(os.path.abspath(os.path.join(current_directory, file_name))) == False:
    print("File Not Detected. Downloading Now....")
    import requests

    url = 'https://www.basketball-reference.com/leagues/NBA_2024_standings.html'
    page = requests.get(url)
    html = page.content

    # write the file
    with open(os.path.join(current_directory, file_name), 'wb+') as file:
        file.write(html)

file_url = os.path.abspath(os.path.join(current_directory, file_name))   

class getStandings(scrapy.Spider):
    name = "basketball"
    allowed_domains =  ['www.basketball-reference.com']
    # start_urls = [f'https://www.basketball-reference.com/leagues/NBA_2024_standings.html']
    start_urls = [f"file:///{file_url}"]


    def parse(self, response):
        #######################################
        # -------- Extract HTML Data -------- #
        #######################################
        
        # Isolate the expanding standings table:
        table = response.xpath("//div[@id='div_expanded_standings']").xpath("//table[@id='expanded_standings']").xpath("tbody")
        
        # Dict for table data
        table_data = {}

        for i in range(30):
            team_name = table.xpath('tr').xpath('td/a/text()')[i].get()
            
            # check if existing
            if team_name not in table_data.keys():
                table_data[team_name] = {}
            else:
                continue
            
            # retrieve table data & add to dictionary
            for j in range(22):
                stat_name = table.xpath('tr')[i].xpath('td')[j+1].attrib['data-stat']
                stat_value = table.xpath('tr')[i].xpath('td/text()')[j].get()
                table_data[team_name][stat_name] = stat_value
       
        ##################################################
        # ------- DataFrame: Create & Manipulate ------- #
        ##################################################
        
        # convert
        table_data_df = pd.DataFrame.from_dict(table_data, orient = 'index')

        # rank and date column
        table_data_df['Team'] = table_data_df.index
        table_data_df['Rank'] = list(range(1,31,1))
        table_data_df['Date'] = pd.to_datetime(date.today())
        
        # columns to keep
        cols = ['Date', 'Team', 'Rank', 'Overall', 
                'Home', 'Road', 'Oct', 'Nov', 'Dec', 
                'Feb', 'Mar', 'Apr']

        # re-organize & change index
        table_data_df = table_data_df[cols]
        table_data_df.index = range(1,31,1)

        # transform the data
        for column in cols[3:]:
            # new column names
            name_1 = column + "_wins"
            name_2 = column + "_losses"

            # split and expand columns
            table_data_df[[name_1,name_2]] = table_data_df[column].str.split("-", expand = True)
            
            # convert to int
            convert_dict = {name_1: int, name_2: int}
            table_data_df = table_data_df.astype(convert_dict)
        
        convert_dict = {"Team":"category", 'Rank': int}
        table_data_df = table_data_df.astype(convert_dict).select_dtypes(exclude='object')


        # print to screen
        print(table_data_df)
        


        #############################################
        # -------- Persist Standings to DB -------- #
        #############################################
        
        # connect
        connection = sqlite3.connect('nba_standings.db')
        cursor = connection.cursor()

        # add to the table
        table_data_df.to_sql('standings', connection, if_exists='append')

        ### close the connection
        connection.close()
            
           
        
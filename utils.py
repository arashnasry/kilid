import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import pandas as pd
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class Kilid():
    def __init__(self,user,password):
        self.user=user
        self.password=password
    def create_database(self,name_Database):
        con = psycopg2.connect(f"user={self.user} password={self.password}");

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);

        # Obtain a DB Cursor

        cursor          = con.cursor();


        # Create table statement
        sqlCreateDatabase = "create database "+name_Database+";"
        # Create a table in PostgreSQL database
        cursor.execute(sqlCreateDatabase);
        con.close ()
        
    def create_table(self,name_database,name_table):
        #Establishing the connection
        conn = psycopg2.connect(
           database=name_database, user=self.user, password=self.password, host='127.0.0.1', port= '5432'
        )
        #Creating a cursor object using the cursor() method
        cursor = conn.cursor()

        #Doping EMPLOYEE table if already exists.
        cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")
        
        #Creating table as per requirement
        sql =f'CREATE TABLE {name_table}(date CHAR(20) NOT NULL,price_open float NOT NULL,price_close float NOT NULL,price_high float NOT NULL,price_low float NOT NULL)'
        cursor.execute(sql)
        print("Table created successfully........")
        conn.commit()
        conn.close ()
      
    def crawl(self,name_database,name_table,executable_path):
         conn = psycopg2.connect(
           database=name_database, user=self.user, password=self.password, host='127.0.0.1', port= '5432'
          )
         cursor = conn.cursor()
         

         driver = webdriver.Chrome(executable_path=executable_path)
         driver.maximize_window()
         driver.get("https://www.tgju.org/profile/price_dollar_rl/history")   
         date=False
         end=False
         while end==False:
             time.sleep(5)
            
             try:
                 nextpage_button=driver.find_element(by=By.CSS_SELECTOR, value='#DataTables_Table_0_next')

                 number_row=1
                 while end==False:
                     try:
                         number_row=number_row+1
                         table_row=driver.find_element(by=By.CSS_SELECTOR, value=f'#table-list > tr:nth-child({number_row})')
                         day=table_row.text.split(' ')[7]
                         print(day)
                         if date==False:
                             
                             day_BETA=table_row.text.split(' ')[7].split('/')
                             day_BETA[0]='1400'
                             day_end="/".join(day_BETA)
                             date=True
                         ###
                         price_open=table_row.text.split(' ')[0].split(',')
                         price_close=table_row.text.split(' ')[3].split(',')
                         price_high=table_row.text.split(' ')[2].split(',')
                         price_low=table_row.text.split(' ')[1].split(',')
                         
                         ###
                         record_to_insert = (day.strip(), float('.'.join(price_open)), float('.'.join(price_close)), float('.'.join(price_high)), float('.'.join(price_low)))
                         cursor.execute(f"INSERT INTO {name_table} (date,price_open,price_close,price_high,price_low) VALUES(%s,%s,%s,%s,%s)", record_to_insert)

                         conn.commit()
                       

                         if day==day_end:
                             print('One year reviewed')
                             end=True
                 
                     except:
                         break
                 driver.execute_script("arguments[0].click();", nextpage_button)
                                 
             except:
                 break
         driver.close()
         conn.close ()


    def plot_dailyclose(self,name_database,name_table,path_output):
        tgju_records=[]
        try:
            connection = psycopg2.connect(
              database=name_database, user=self.user, password=self.password, host='127.0.0.1', port= '5432'
             )
            cursor = connection.cursor()
            postgreSQL_select_Query = f"select * from {name_table}"

            cursor.execute(postgreSQL_select_Query)
            print("Selecting rows from TABLE_tgju table using cursor.fetchall")
            tgju_records = cursor.fetchall()
            connection.close ()

        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
        tgju_records.reverse()
        tgju_records=np.array(tgju_records)
        tgju_records_date=tgju_records[:,0].tolist()
        # date_time = pd.to_datetime(a[:10], errors = 'coerce')


        font = {'family' : 'DejaVu Sans',
                'weight' : 'bold',
                'size'   : 35}

        matplotlib.rc('font', **font)

        # Create figure and plot space
        fig = plt.figure(figsize=(100,45), dpi=120)
        ax = fig.add_subplot()

        # Add x-axis and y-axis
        plt.title('Daily close prices chart',fontsize=80)
        plt.xlabel('date',fontsize=60)
        plt.ylabel('price',fontsize=60)
        ax.plot(tgju_records_date[-30:],
               tgju_records[:,2].astype(float).tolist()[-30:], 
               'o-', 
               color='red')
        # Set title and labels for axes
        plt.xticks(rotation=45, ha='right')
        plt.savefig(path_output)


    def plot_candels(self,name_database,name_table,path_output):
        tgju_records=[]

        try:
            connection = psycopg2.connect(
              database=name_database, user=self.user, password=self.password, host='127.0.0.1', port= '5432'
             )
            cursor = connection.cursor()
            postgreSQL_select_Query = f"select * from {name_table}"
            cursor.execute(postgreSQL_select_Query)
            print(f"Selecting rows from {name_table} table using cursor.fetchall")
            tgju_records = cursor.fetchall()
            print("Print each row and it's columns values")
            connection.close ()

        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
        tgju_records.reverse()
        tgju_records=tgju_records[-30:]
        #create figure
        plt.figure(figsize=(100,45), dpi=120)
        font = {'family' : 'DejaVu Sans',
                'weight' : 'bold',
                'size'   : 40}
        matplotlib.rc('font', **font)
        #define width of candlestick elements
        width = .7
        width2 = .05
        prices = pd.DataFrame(tgju_records, columns = ['date','open','close','high','low'])
        prices = prices.reset_index() 
        #define colors to use
        col1 = 'green'
        col2 = 'red'
        for index, row in prices.iterrows():
            if row.close>=row.open:
                plt.bar(row.date,row.close-row.open,width,bottom=row.open,color=col1)
                plt.bar(row.date,row.high-row.close,width2,bottom=row.close,color=col1)
                plt.bar(row.date,row.low-row.open,width2,bottom=row.open,color=col1)
            if row.close<row.open:
                plt.bar(row.date,row.close-row.open,width,bottom=row.open,color=col2)
                plt.bar(row.date,row.high-row.close,width2,bottom=row.close,color=col2)
                plt.bar(row.date,row.low-row.open,width2,bottom=row.open,color=col2)

        plt.xticks(rotation=45, ha='right')
        plt.title('Daily candlestick chart',fontsize=80)
        plt.xlabel('date',fontsize=60)
        plt.ylabel('price',fontsize=60)
        #display candlestick chart
        
        plt.savefig(path_output)













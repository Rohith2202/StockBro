import time
import sys
import json
import ast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pyautogui
import nltk
import numpy as np 
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
# nltk.download('vader_lexicon')

analyzer = SentimentIntensityAnalyzer()
months={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
url="https://www.google.com/finance/?hl=en"

def get_prediction(file_name,new_data):
    df = pd.read_csv(file_name)
    df['date_column'] = pd.to_datetime(df['Date'], format='%m-%d-%Y')
    X=df[['date_column',"Volume","News_Score"]]
    Y=df["Value"]
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    X_train['day_of_week'] = X_train['date_column'].dt.dayofweek
    X_train['month'] = X_train['date_column'].dt.month
    X_train['year'] = X_train['date_column'].dt.year
    X_test['day_of_week'] = X_test['date_column'].dt.dayofweek
    X_test['month'] = X_test['date_column'].dt.month
    X_test['year'] = X_test['date_column'].dt.year
    X_train = X_train.drop(['date_column'], axis=1)
    X_test = X_test.drop(['date_column'], axis=1)
    model=LinearRegression()
    model.fit(X_train,y_train)
    new_df = pd.DataFrame([new_data])
    new_df['date_column'] = pd.to_datetime(new_df['date_column'], format='%m-%d-%Y')
    new_df['day_of_week'] = new_df['date_column'].dt.dayofweek
    new_df['month'] = new_df['date_column'].dt.month
    new_df['year'] = new_df['date_column'].dt.year
    new_df = new_df.drop(['date_column'], axis=1)
    new_prediction = model.predict(new_df)
    return new_prediction

def make_dataframe(dates,volume_of_stock,final_score,value,new_data):
    df={'Date':dates,
        "Volume":volume_of_stock,
        'News_Score':final_score,
        "Value":value}
    df=pd.DataFrame(df)
    df.to_csv('data.csv')
    return get_prediction("data.csv",new_data)


def get_data(stock_name,date_to_predict,curr_volume,goodies=0):
    driver=webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)
    send_input = driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz[2]/div/div[3]/div[3]/div/div/div/div[1]/input[2]')
    send_input.send_keys(stock_name)
    send_input.send_keys(Keys.ENTER)
    wait(driver, 3000).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="5yearTab"]/span[2]'))).click()
    x_coordinate = 366
    y_coordinate = 900
    dates=[]
    value=[]
    final_score=[]
    volume_of_stock=[]
    each_score=[]
    news_dates={}
    res=2
    flag=1
    for x_coordinate in range(366,1114):
        if flag==3:
            vals=driver.find_elements(By.CLASS_NAME,"cyDp")
            for val in vals:
                current=val.text 
                for key in months:
                    if key in current:
                        find=current.index(key)
                        current=current[find::]
                        break 
                date_of_news=current[0:12:].split()
                date_of_news[0]=str(months[date_of_news[0]])
                date_of_news[1]=date_of_news[1][:len(date_of_news[1])-1:]
                date_of_news="/".join(date_of_news)
                good_bad=current[13::]
                scores = analyzer.polarity_scores(good_bad)
                pos=0
                if scores['pos']>scores['neg']:
                    pos=1
                else:
                    pos=0
                news_dates[date_of_news]=pos
            flag+=1
        pyautogui.moveTo(x_coordinate, y_coordinate, duration=0) 
        stock_prices=wait(driver, 100000).until(EC.presence_of_element_located((By.CLASS_NAME, 'hSGhwc-SeJRAd'))).text
        stock_prices=stock_prices[5::]
        Dates=wait(driver, 100000).until(EC.presence_of_element_located((By.CLASS_NAME, 'hSGhwc-ZlY4af'))).text
        Dates=Dates.split(" ")
        volume=wait(driver, 100000).until(EC.presence_of_element_located((By.CLASS_NAME, 'hSGhwc-IOpRCf'))).text
        volume=volume.replace("Volume:","")
        volume=volume[:len(volume)-1:]
        volume.strip()
        if res<=0:
            if Dates!=[] and Dates[0]!="":
                Dates[0]=str(months[Dates[0]])
                Dates[1]=Dates[1][0:len(Dates[1])-1:]
                check=False 
                for j in range(int(Dates[1])-5,int(Dates[1])+5):
                    primary="/".join(Dates)
                    if primary in news_dates:
                        final_score.append(news_dates[primary])
                        check=True 
                        break 
                if check==False:
                    final_score.append(0)
                dates.append("-".join(Dates))
                stock_prices.replace(",","")
                value.append(float(stock_prices))
                volume_of_stock.append(float(volume))
        res-=1
        flag+=1
    new_data={'date_column': str(date_to_predict),'Volume': float(curr_volume), 'News_Score': float(goodies)}
    final_df=make_dataframe(dates,volume_of_stock,final_score,value,new_data)
    return final_df
stock_name=str(input("Enter Stock name:"))
date_to_predict=str(input("Enter Date to predict in the format mm-dd-yyyy:"))
curr_volume=float(input("Enter Current volume of stocks:"))
goodies=float(input("Enter 1 if you have good news for stock 0 otherwise:"))
print("DO NOT MOVE MOUSE UNTIL THE CODE OUTPUTS SOMETHING")
print(get_data(stock_name,date_to_predict,curr_volume,goodies=0))
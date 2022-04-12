# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 17:57:37 2022

@author: Weichen
"""
import datetime


def getDate():
    
    # get current & previous date
    Cur_Date = datetime.datetime.today()
    Prev_Date = datetime.datetime.today() - datetime.timedelta(days=1)
    
    # formatting
    cur_date = Cur_Date.strftime("%Y-%m-%d")
    prev_date = Prev_Date.strftime("%Y-%m-%d")
    
    return prev_date, cur_date

def updateNyTimesCFG():
    
    prev_date, cur_date = getDate()

    base_api = "base_api_url=https://www.nytimes.com/sitemap/{year}/{month:0>2}/{day:0>2}/\n\n"
    start_date = "start_date=" + prev_date + "\n\n"
    end_date = "end_date=" + cur_date + "\n\n"
    step_unit = "step_unit=day\n\n"
    step = "step = 1\n\n"
    path = "path=./daily_news/nytimes/\n\n"
    sleep = "sleep=1\n\n"
    
    f = open("settings/nytimes_update.cfg", "w")
    f.write(base_api)
    f.write(start_date)
    f.write(end_date)
    f.write(step_unit)
    f.write(step)
    f.write(path)
    f.write(sleep)
    
    f.close()
    

def updateBBCCFG():
    
    prev_date, cur_date = getDate()

    base_api = "base_api_url=http://dracos.co.uk/made/bbc-news-archive/{year}/{month:0>2}/{day:0>2}/\n\n"
    start_date = "start_date=" + prev_date + "\n\n"
    end_date = "end_date=" + cur_date + "\n\n"
    step_unit = "step_unit=day\n\n"
    step = "step = 1\n\n"
    path = "path=./daily_news/bbc/\n\n"
    sleep = "sleep=0.02\n\n"
    
    f = open("settings/bbc_update.cfg", "w")
    f.write(base_api)
    f.write(start_date)
    f.write(end_date)
    f.write(step_unit)
    f.write(step)
    f.write(path)
    f.write(sleep)
    
    f.close()


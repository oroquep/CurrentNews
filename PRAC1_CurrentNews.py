# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 07:10:36 2019

@author: Oriol Roqué Paniagua
"""
import requests
import numpy as np
from bs4 import BeautifulSoup

def GetDataFromNews(url,title):

    # Apply Request To News Page
    news_response = requests.post(url)
    
    # Check Response Is Valid
    if news_response.status_code == 200:
        
        # Parse Response
        news_soup = BeautifulSoup(news_response.text,"html.parser")
        
        # Get Header Containing Main Data
        header = news_soup.find_all("header")[3]    
        
        # Get News Location
        location = header.find_all("span")[0].get_text()
        
        # Get News Subtitle
        if len(header.find_all("div",{'class': lambda L: L and L.startswith('entrad')})) != 0:
            subtitle = header.find_all("div",{'class': lambda L: L and L.startswith('entrad')})[0].get_text().strip()
        else:
            subtitle=""
        
        # Get Publish Date & Hour
        date = header.find_all("div",{'class': lambda L: L and L.startswith('F-autorData')})
        if len(date) != 0:
            publish_date = date[0].find_all("time")[0].get_text()[:10]
            publish_hour = date[0].find_all("time")[0].get_text()[-5:]
        # Get Update Date & Hour
        if len(date[0].find_all("time")) > 1:
            last_update_date = date[0].find_all("time")[1].get_text()[:10]
            last_update_hour = date[0].find_all("time")[1].get_text()[-5:]
        else:
            last_update_date = ""
            last_update_hour = ""
        
        # Get Number Of Tags
        tags = header.find_all("dl",{'class': lambda L: L and L.startswith('R-nuvolTags')})
        num_tags = len(tags)
        
        if num_tags != 0:
            tag = ""
            for j in range(num_tags):
                if len(tags[0].find_all("a", href=True)) != 0:
                    tag = tag + "|" + tags[0].find_all("a", href=True)[j].get_text()
            tag = tag[1:]
        else:
            tag = ""
            
        array = np.array([url, title, subtitle, location, publish_date, publish_hour, 
                          last_update_date, last_update_hour, tag, num_tags])
        return array
    
# Set Main URL
main_url = "https://www.ccma.cat"

# Set Export csv Path
export_path = r"C:/Users/UserName/Desktop/CurrentNews.csv"

# Set csv Headers
csv_header = np.array(
        ["url", "title", "subtitle", "location", "publish_date", "publish_hour", 
         "last_update_date", "last_update_hour", "tag", "num_tags"])
    
# Apply Request
response = requests.post(main_url + "/324/")

# Check Response Is Valid
if response.status_code == 200:

    # Parse Response
    soup = BeautifulSoup(response.text,"html.parser")
    
    # Get All News
    all_news = soup.find_all("h1", class_ = "titol")
    news_count = 0
    
    # Loop Through All News
    for i in range(len(all_news)):
                
        # Get Link To News Specific Page
        url = main_url + all_news[i].find("a", href= True)["href"]
        
        if url[:len(main_url)+4] == main_url + "/324" and "noticia" in url:
            
            print("Extracting data. Row number " + str(news_count) )
            
            # Get Title
            title = all_news[i].find("a", href=True).get_text()
            
            new_element = GetDataFromNews(url, title)
            
            if news_count == 0:
                dataset = np.array(new_element)
            else:
                dataset = np.vstack((dataset, new_element))
            
            # +1 News Count
            news_count += 1
            
    # Export Result
    if news_count != 0:
        print("Exporting File")
        dataset = np.vstack((csv_header,dataset))
        np.savetxt(export_path, dataset, delimiter=";", fmt='%s')
    else:
        print("No news could be extracted.")
else:
    print("Response not valid: ", response.status_code)


import requests
import json
import pandas as pd
import os
import datetime
import numpy as np
from bs4 import BeautifulSoup



# url to blog post
base_url = 'https://www.lawyered.in/legal-disrupt'





#url to main website
url = 'https://www.lawyered.in'




#file path to json file

json_path = 'data.json'



#dataframe path to scrape only unscraped data

pd_path = r'blog_titles.csv'

################# utlity Functions #####################


#function to make GET request

def get_page(base_url):
        
    headers = {
       "Accept": "application/json"#,
       }
    
    response = requests.request(
       "GET",
       base_url,
       headers=headers,
       verify = False
       )
    
    return response


#tag filter 

def is_para(tag):
    return tag.name == 'p' and tag.span != None


# convert the paras to one string 

def convert_to_complete_para(k):
    # Initialize an empty string to store the concatenated text
    concatenated_text = ""
    
    # Iterate through the <p> tags and concatenate their text
    for paragraph in k:
        concatenated_text += ' \n '
        concatenated_text += paragraph.get_text()
    
    # Print the concatenated text
    print(concatenated_text)
    return concatenated_text
    



# get final content

def get_content(x):
    k = BeautifulSoup(x.text, 'html.parser').findAll(is_para)
    content = convert_to_complete_para(k)
    return content





# Get author details

def get_author(x):
    k = BeautifulSoup(x.text, 'html.parser').findAll('p')
    author_det =  k[0].text.replace('\n', '').strip().split(',')
    
    author_name = author_det[0]
    author_city = author_det[-1]
    
    return author_name, author_city
    
    

# Get json file format

def get_json_file(master_dic ,node_name, node_dic, json_path):
   file_path = json_path
   
   try:
       with open(file_path, "r") as json_file:
        existing_data = json.load(json_file)
    
        # Add new data or modify existing data within the existing_data dictionary
       existing_data[node_name] = node_dic
        
        # Write the updated data back to the JSON file
       with open(file_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)
    
   except:
        with open(file_path, "w") as json_file:
            json.dump(master_dic, json_file, indent=4)
    
        


    
#################### final script ############################

    



response = get_page(base_url)

titles = []
links = []

html_code = response.text
   
soup = BeautifulSoup(html_code, 'html.parser')


page = soup.findAll('h5')
    
for i in page:
    a = i.find('a')
    #link = a.get('href')
    try: 
        try : 
            dd = pd.read_csv(pd_path)
            if a.text not in list(dd['article_title']): 
                titles.append(a.text)
                links.append(a.get('href'))
                print('done')
            else:
                print('no title or link')
        except:
            titles.append(a.text)
            links.append(a.get('href'))      
    except:
        print('no title or link')
        
        

df = pd.DataFrame(titles, columns = ['article_title'])

df['links_to_full_article'] = links

try : 
    dd = pd.read_csv(pd_path)
    indx = len(dd)
    pd.concat([dd,df] , ignore_index = True).to_csv(pd_path, index=False)

except:
    df.to_csv(pd_path, index=False)
    indx = 0




for i in range(len(df)):
    suffix = df['links_to_full_article'][i]
    final_link = url+suffix
    print(final_link)
    x = get_page(final_link)
    content = get_content(x)
    author_name, author_city = get_author(x)
    master_node = {}
    dic = {}
    dic['title'] = df['article_title'][i]
    dic['content'] = content
    dic_auth = {}
    dic_auth['author_name'] = author_name
    dic_auth['author_city'] = author_city
    dic['author_details'] = dic_auth
    master_name = 'Article '+str(i+indx+1)
    master_dic = {}
    master_dic[master_name] = dic
    
    get_json_file(master_dic ,master_name, dic, json_path)
    
    
    
    

    

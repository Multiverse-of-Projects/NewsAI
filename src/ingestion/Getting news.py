#Getting the 100 News with Google News library
from GoogleNews import GoogleNews


from GoogleNews import GoogleNews
import pandas as pd

user_request = input(str("Give me a topic: " ))


googlenews = GoogleNews(period='7d')
googlenews.search(user_request)


all_results = []

for i in range(1, 50):
    googlenews.getpage(i)
    result = googlenews.result()
    
    if result:
        all_results.extend(result)
        

    if len(all_results) >= 100:
        break

df = pd.DataFrame(all_results)


df = df.drop_duplicates(subset=['title'], keep='last')


df = df.head(100)


df.reset_index(drop=True, inplace=True)



data = df.drop(columns = ['media', 'date', 'datetime', 'desc', 'img'])

new_link = []

for i in range(data.shape[0]):
  new_link.append(data.loc[i , "link"])
  
latest_link = []
import re 

for i in range(len(new_link)):
    latest_link.append(re.split("&ved" , new_link[i])[0])
 
data["latest_link"] = latest_link
 


from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import time
import random

description = []


for i in latest_link:

    try:
        response = requests.get(i, timeout=10)

        # Check if the request was successful
        if response.status_code == 200:
            html_content = response.text
        else:
            print(f"Failed to retrieve: {i} (Status code: {response.status_code})")
            description.append("Failed to retrieve the webpage.")
            continue  # Skip to the next link

        soup = BeautifulSoup(html_content, "html.parser")
        paragraphs = soup.find_all("p")

        # Join the text of all paragraphs and store in the description list
        page_description = " ".join([p.get_text() for p in paragraphs])
        description.append(page_description)

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving {i}: {e}")
        description.append("Failed to retrieve the webpage.")
        continue  
    # Introduce a random delay to prevent rate-limiting
    time.sleep(random.uniform(1, 3))


print(description)

data["description"] = description



"""

DataFrame to TEXT file

"""

import pandas as pd
import os


folder_name = "/workspaces/NewsAI/docs/news data"
os.makedirs(folder_name, exist_ok=True)

# Loop through the DataFrame and save each description as a text file
for index, row in data.iterrows():
    description = row['description']
    

    filename = f"description_{index + 1}.txt"
   
    file_path = os.path.join(folder_name, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(description)

print("Descriptions have been saved in the 'NEWS_data' folder.")

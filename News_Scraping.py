import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import json
import re
import hashlib
import time
import openai

translator = Translator()
openai.api_key = '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'

# Function to scrape the recent reports 
def scrapedata():
    # Send an HTTP request to the website
    url = "https://hamal.co.il/%D7%A6%D7%91%D7%90-%D7%95%D7%91%D7%99%D7%98%D7%97%D7%95%D7%9F-40"  
    response = requests.get(url, params={
      'api_key': '9e7b62cb-7f5c-4356-b804-1564a6579c3f',
      'url': 'https://hamal.co.il/main', 
      'render_js': True})
    
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")    
       
        # Extract the desired text
        report_List = soup.find_all('a', class_='styles_action__8YDU4 styles_mail__6E83G') # Modify this to match the actual HTML structure
        
        print("Data successfully scraped")
        for each in report_List:
            each = str(each).replace('חמ"ל', '')
        

    else:
        print("Failed to retrieve the webpage.")
    return(report_List)
    #Print all of the list
   

# Cleans and translate the report from Hebrew to English
def translate_report(report):
    for x in range(len(report)):
        report[x] = translator.translate(re.sub("[^א-ת ]", "", str(report[x]))).text
        
    return report
    
# Creates a unique id for each report
def create_id(translated_report):
    id_list = []
    for x in range(len(translated_report)):
        id_list.insert(x,hashlib.sha1(str.encode(str(translated_report[x]))).hexdigest())
    return id_list

# return the current time and date 
def currentDateTime():
    current_time = time.localtime()
    time_string = time.strftime("%H:%M:%S, %m/%d/%Y" , current_time) # Gets the current date and time
    return(time_string)

# Checks if there are new reports in the update that doesn't exists in the json 
# if there are adding them to the json file
def addTheNew(translated_list, id_list):
    # Reads the reports that already saves in the database 
    with open('Hamal Website/AllNews.json') as f: 
        reportsDict = json.load(f)

    # Checks if there are new reports in the update that doesn't exists in the json 
    # if there are adding them to the json file
    lastReportID = reportsDict['Reports'][0]['Id']

    for x in range(len(translated_list)):
        if lastReportID == id_list[x]:
            print('Done Adding')
            break
        else:
            temp = {
                "Id": id_list[x],
                "Text": translated_list[x],
                "Place": '',
                "Attacker":'',
                "casualties":'',
                "PubilshTime": currentDateTime(),
                "Child_Reports" : []
                }
            reportsDict['Reports'].insert(x,temp)
            print('Added New Report')

    return reportsDict


# Return the instructions for the gpt model
def gpt_instructions():
    messages = [
        {"role": "system", "content":"You are an israeli news worker, you get a war report and you need to return this info (if mention): Where the event took place, what country or organization  did the action and how many injuries or kills there was "},
        {"role": "system", "content":"Pls responde only with the info you understood from the report there no need to be nice or write other things"},
        {"role": "system", "content":"Pls return the info in a JSON format. Here is the expected JSON format: {'Place': the place of the reprot,'Attacker': the army or terror organization that pulled the action,'casualties': how many kills/injured people in number from the report for example 2 killed 0 Injured}"},
        {"role": "system", "content":"Check courfuly that your answer is correct because its an important data"},
        {"role": "system", "content":"If some of the data don't mention just write Not entioned"},
        ]
    return messages

# Get the report information with the chat gpt api and save him in the json file
def save_reportData(savedReports):
    messages = gpt_instructions()

    # Getting information from the reports with gpt
    for x in range(len(savedReports['Reports'])):
        if savedReports['Reports'][x]['Place'] == "":
            messages.append({"role": "user", "content": savedReports['Reports'][x]['Text']})

            complation = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                temperature = 0
            )   
            info = complation.choices[0].message.content
                        
            try:
                dataJson = json.loads(info)
                savedReports['Reports'][x]['Place'] = dataJson['Place']
                savedReports['Reports'][x]['Attacker'] = dataJson['Attacker']
                savedReports['Reports'][x]['casualties'] = dataJson['casualties']
            except:
                print('Didnt find data')
        else:
            break

    # Overide the json file with the new reports
    with open('Hamal Website/AllNews.json', 'w') as f:
        json.dump(savedReports, f,indent=2) 

# Scrap a list of all the recent reports from Hamal website
# Cleans the html from the reports and Translate the reports from Hebrew to English with google translate
translated_list = translate_report(scrapedata())
# Creates a unique id for each report in the list 
id_list = create_id(translated_list) 
# Adding the new repoerts into the json file
savedReports = addTheNew(translated_list,id_list)

# Get the report information with the chat gpt api and save him in the json file
save_reportData(savedReports)


print('Done')
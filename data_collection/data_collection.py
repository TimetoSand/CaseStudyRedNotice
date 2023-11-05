from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
import pika
import json
import os

URL = "https://www.interpol.int/How-we-work/Notices/Red-Notices/View-Red-Notices"

# Set the path to the geckodriver
driver_path = "data_collection/geckodriver"

# Check if geckodriver exists at the specified path
if not os.path.exists(driver_path):
    driver_path = GeckoDriverManager().install()

# Create a new instance of the Firefox driver
service = Service(executable_path=driver_path)
options = webdriver.FirefoxOptions()
options.add_argument("--headless")

# Start the WebDriver and navigate to the page
driver = webdriver.Firefox(service=service, options=options)

driver.get(URL)
time.sleep(12)

# Get the HTML content of the page
content = driver.page_source

# Close the browser window
driver.quit()

#print(content)

soup = BeautifulSoup(content, 'html.parser')

# find all elements that contain a person's information
people = soup.find_all('div', class_='redNoticesList__item notice_red')

people_data = []
for person in people:
    # extract the name for each person
    name_element = person.find('a', class_='redNoticeItem__labelLink')
    name = name_element.get_text(separator=' ') if name_element else 'N/A'

    # extract the age for each person
    age_element = person.find('span', class_='ageCount')
    age = age_element.text if age_element else 'N/A'

    # extract the nationality for each person
    nationality_element = person.find('span', class_='nationalities')
    nationality = nationality_element.text if nationality_element else 'N/A'

    data = {
        'name': name,
        'age': age,
        'nationality': nationality
    }
    people_data.append(data)



filtered_people_data = [data for data in people_data if data['name'] != '']
print(filtered_people_data)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='helloWanted')
message = json.dumps(filtered_people_data)
# send the message
channel.basic_publish(exchange='', routing_key='helloWanted', body=message)

# close the connection
connection.close()

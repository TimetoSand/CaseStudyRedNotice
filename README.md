# CaseStudyRedNotice

This project receives Interpol red notice data by scraping it with Selenium, parses the data, and sends it to a RabbitMQ queue.
Pika is used to send and receive data to and from the queue.The data from the queue is collected in a database, where it is checked
for changes by making comparisons. The application publishes the data on html page. 

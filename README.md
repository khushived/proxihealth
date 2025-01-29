# Disease Outbreak Detection

## Overview

Our project provides a novel approach to perform real-time monitoring of epidemics and give out early warnings by combining various machine learning techniques, natural language processing techniques such as word embedding and web development methods. This involves collection and pre-processing of relevant data from Twitter and then using an LSTM for disease detection and word embedding techniques like Word2Vec to enhance this detection. State-of-the-art techniques are then used to compare and evaluate the designed system. The data generated from this system is then used to create meaningful and visual plots, which are then displayed through dedicated web pages. Monitoring of this data can be done regularly to detect the occurrence of any epidemic. Thus, this approach can be used to effectively monitor the status of different diseases by analyzing data collected from Twitter and then immediately give warnings as soon as any epidemic is detected.


## Project structure

a. driver.py			            --> Driver file of the project  
b. Frontend/static   		      --> Contains all the assets required for the frontend  
c. Frontend/templates		      --> Contains the required html files  
d. Frontend/app.py		         --> It is the controller which is created using flask  
e. LSTM/data			            --> Data reuired for LSTM training  
f. LSTM/train			            --> Contains required files to train LSTM model  
g. Scraper/data			         --> Contains scraped data from twitter  
h. Scraper/twitterScraper.py	   --> Custom twitter scraper  
i. Scraper/scrape.py		         --> Driver file which uses the custom twitter scraper to extract tweets  
j. requirements.txt		         --> Contains all the required libraries to run the project

## Instructions

To run the project, follow these instructions:

### Section 1 : Setup

a. Go to the folder 'LSTM/train' and execute 'preprocessing.py'.

b. In the same folder execute 'train.py' to train the LSTM model.

### Section 2 : Execution

a. Enter the project directory and execute the file 'driver.py':  
   python3 driver.py

b. The data is now generated and to render the webpage, go to the 'Frontend' folder and execute the file 'app.py'.

c. Go to your browser and type 127.0.0.1:5000/ as URL and click enter.

d. You can now see the webpage and access the statistics.



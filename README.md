# how to run 
first you need to install the requirements so type in terminal

pip install -r requirements.txt

type on terminal  
python main.py

for cloning github  : https://github.com/rajashekharkeesari/Test_assignment.git


Solution Approach
Step 1: Setup and Initialization
Import required libraries

Initialize global variables for storing results

Define file paths for input/output

Step 2: Data Preparation
Read input Excel file containing URLs

Create output directory for extracted articles

Step 3: Article Extraction
For each URL in the input file:

Send HTTP request to fetch the webpage

Parse HTML using BeautifulSoup

Extract article title and text (using <article> tag or fallback to <p> tags)

Save extracted text to individual files named by URL_ID

Step 4: Text Processing Setup
Load and clean stopwords from multiple files in the stopwords folder

Handle special characters and formatting

Remove duplicates

Load sentiment words (positive/negative) from sentiment_type folder

Create sentiment dictionary mapping words to their sentiment

Step 5: Text Analysis
For each extracted article:

Text Cleaning:

Remove URLs and special characters

Convert to lowercase

Tokenize words

Basic Metrics:

Count total words and sentences

Calculate average words per sentence

Count syllables per word

Complexity Analysis:

Identify complex words (>2 syllables)

Calculate percentage of complex words

Compute Fog Index (readability metric)

Sentiment Analysis:

Count positive and negative words using sentiment dictionary

Calculate polarity and subjectivity scores

Additional Metrics:

Count personal pronouns

Calculate average word length

Compute syllables per word

Step 6: Output Results
Compile all metrics into a pandas DataFrame

Save results to CSV file (results.csv)

Key Functions
make_stopwords_list(): Processes stopword files

make_sentiment_dict(): Creates sentiment word dictionary

get_article_data(): Extracts article text from URLs

count_syllables(): Syllable counting algorithm

analyze(): Main analysis function that computes all metrics

Notes
The script handles edge cases like missing article tags

It skips invalid URLs gracefully

All text processing is case-insensitive

Stopwords are removed before sentiment analysis

The syllable counter has special handling for common suffixes

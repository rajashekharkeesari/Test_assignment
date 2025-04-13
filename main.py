import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.tokenize import word_tokenize
import os

# Download NLTK data
nltk.download('punkt')

# Initialize global variables
results = []
cleaned_stopwords = []
sentiment_dict = {}

# File paths
input_excel_path = r'Input.xlsx'
output_folder = r'extracted_data'
stopword_folder = r"stopwords"
sentiment_folder = r"sentiment_type"
output_csv_path = 'results.csv'

def make_stopwords_list(filepath):
    with open(filepath, 'r', encoding='latin-1') as f:
        data = f.read()
        data = data.replace('|', "\n")
        data = data.replace('(Former Yug. Rep.)', "")
        data = data.strip().split("\n")
        return [item.strip().lower() for item in data if item.strip()]

def make_sentiment_dict(base_path):
    sentiment_dict = {'positive': [], 'negative': []}
    try:
        files = [f for f in os.listdir(base_path) if f.endswith('.txt')]
        print("Found files:", files)

        for file in files:
            sentiment = 'positive' if 'positive' in file.lower() else 'negative'
            file_path = os.path.join(base_path, file)

            with open(file_path, 'r', encoding='utf-8') as f:
                words = f.read()
                words = words.split("\n")
                words = [word.strip().lower() for word in words if word.strip() and word not in cleaned_stopwords]
                words = list(set(words))
                sentiment_dict[sentiment] = words
        return sentiment_dict

    except FileNotFoundError:
        print("Directory or files not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return sentiment_dict

def get_article_data(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title').get_text(strip=True) if soup.find('title') else "No Title"
        article_tag = soup.find('article')

        if article_tag:
            article_text = article_tag.get_text(strip=True)
        else:
            # Alternative method to extract article text if <article> tag not found
            article_text = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])
            if not article_text:
                article_text = "Article not found"

        return title, article_text

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None

def count_syllables(word):
    vowels = "aeiouy"
    word = word.lower()
    count = 0
    
    # Handle exceptions
    if word.endswith(('es', 'ed')):
        word = word[:-2]
    
    if len(word) == 0:
        return 0
    
    if word[0] in vowels:
        count += 1
    
    for index in range(1, len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count += 1
    
    # Adjust count for words ending with 'e'
    if word.endswith('e'):
        count -= 1
    
    return max(1, count)

def analyze(text, url_id, url):
    # Text cleaning
    positive_words = 0
    negative_words = 0
    
    # Better sentence splitting
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    sentence_count = len(sentences)
    
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s\']', '', text)
    text = text.lower()
    
    # Tokenization
    words = word_tokenize(text)
    
    # Text Analysis Metrics
    word_count = len(words)
    avg_number_of_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
    complex_words = [word for word in words if count_syllables(word) > 2]
    complex_word_count = len(complex_words)
    cleaned_words = [word for word in words if word.isalpha()]
    word_count = len(cleaned_words)
    syllable_counts = [count_syllables(word) for word in cleaned_words]
    syllables_per_word = sum(syllable_counts) / len(syllable_counts) if syllable_counts else 0
    
    pronoun_pattern = re.compile(r'\b(?:i|we|my|ours|us)\b', re.IGNORECASE)
    pronoun_matches = pronoun_pattern.findall(text)
    personal_pronouns = [word for word in pronoun_matches if word.lower() != 'us' or word.islower()]
    personal_pronoun_count = len(personal_pronouns)
    
    total_chars = sum(len(word) for word in cleaned_words)
    avg_word_length = total_chars / word_count if word_count > 0 else 0
    filtered_words = [word for word in words if word.isalpha() and word not in cleaned_stopwords]
    total_words_cleaned = len(filtered_words)
    
    for word in filtered_words:
        if word in sentiment_dict.get('positive', []):
            positive_words += 1
        if word in sentiment_dict.get('negative', []):
            negative_words += 1

    # Calculate scores
    total_sentiment_words = positive_words + negative_words
    polarity_score = (positive_words - negative_words) / (total_sentiment_words + 0.000001)
    subjectivity_score = total_sentiment_words / (total_words_cleaned + 0.000001)

    # Readability metrics
    percentage_complex_words = (complex_word_count / word_count) * 100 if word_count > 0 else 0
    fog_index = 0.4 * (avg_number_of_words_per_sentence + percentage_complex_words)
          
    return {
        'URL_ID': url_id,
        'URL': url,
        'POSITIVE SCORE': positive_words,
        'NEGATIVE SCORE': negative_words,
        'POLARITY SCORE': polarity_score,
        'SUBJECTIVITY SCORE': subjectivity_score,
        'AVG SENTENCE LENGTH': avg_number_of_words_per_sentence,
        'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words,
        'FOG INDEX': fog_index,
        'AVG NUMBER OF WORDS PER SENTENCE': avg_number_of_words_per_sentence,
        'COMPLEX WORD COUNT': complex_word_count,
        'WORD COUNT': word_count,
        'SYLLABLES PER WORD': syllables_per_word,
        'PERSONAL PRONOUNS': personal_pronoun_count,
        'AVG WORD LENGTH': avg_word_length,
    }

def main():
    global cleaned_stopwords, sentiment_dict
    
    # Step 1: Read Excel File
    data = pd.read_excel(input_excel_path)
    
    # Step 2: Create Output Folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Step 3 & 4: Extract and Save Article Texts
    for index, row in data.iterrows():
        url = row.get('URL')
        url_id = row.get('URL_ID')

        if isinstance(url, str) and url.startswith('http'):
            title, article = get_article_data(url)

            if title and article:
                file_path = os.path.join(output_folder, f"{url_id}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"{title}\n{article}")
                print(f"Saved: {file_path}")
            else:
                print(f"Skipped (no data): {url}")
        else:
            print(f"Invalid URL: {url}")
    
    # Step 5: Read and Clean All Stopword Files
    for file in os.listdir(stopword_folder):
        if file.endswith('.txt'):
            file_path = os.path.join(stopword_folder, file)
            page_stopwords = make_stopwords_list(file_path)
            cleaned_stopwords.extend(page_stopwords)

    # Remove duplicates
    cleaned_stopwords = list(set(cleaned_stopwords))
    
    # Step 6: Create Sentiment Dictionary
    sentiment_dict = make_sentiment_dict(sentiment_folder)
    
    # Step 7: Perform Sentiment Analysis
    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        if not file.endswith(".txt"):
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            # Extract URL_ID from the filename
            url_id = file.split(".")[0]
            # Find URL in original data
            url_row = data[data['URL_ID'] == url_id]
            if not url_row.empty:
                url = url_row['URL'].values[0]
                # Perform analysis on the text
                result = analyze(text, url_id, url)
                results.append(result)
    
    # Save the DataFrame to CSV
    dataframe = pd.DataFrame(results)
    dataframe.to_csv(output_csv_path, index=False)
    print(f"Analysis results saved to {output_csv_path}")

if __name__ == "__main__":
    main()
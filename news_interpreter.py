import openai
import pandas as pd
import time

# Load data
news_data = pd.read_csv('News_Data_Final.csv')

openai.api_key = 'xxx'

def send_message(message):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                "role": "system",
                "content": "You are a pre-trained sentiment analysis model."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        max_tokens=5
    )
    return response['choices'][0]['message']['content']

counter = 0

# Loop through DataFrame
for index, row in news_data.iterrows():
    # prompt creation
    
    prompt = (f"Pretend that you are a pre-trained sentiment analysis model that reads and evaluates news articles. You can only output numbers in the range from -1 (meaning negative impact on the stock) up to 1 (meaning positive impact on the stock) for following news article: "
               f"related ticker symbol: {row['ticker']}, title: {row['title']}, summary: {row['summary']}. Please only output the sentiment score number")
    
    # prompt = (f"Pretend that you are a pre-trained sentiment analysis model, which outputs a sentiment score between -1 (downtrend) and 1 (uptrend) for following news article: "
    #           f"related ticker symbol: {row['ticker']}, title: {row['title']}, summary: {row['summary']} Please only output the sentiment score number.")
    
    # Initialize a flag for retrying
    inference_not_done = True
    
    while inference_not_done:
        try:
            # Get sentiment score
            sentiment_score = send_message(prompt)
            
            # Update sentiment column
            news_data.at[index, 'sentiment score'] = sentiment_score
            
            counter += 1
            
            # Print stock and date  
            print(f"Processed row {counter}")
            
            # Mark inference as done
            inference_not_done = False
        except Exception as e:
            print(f"Wait 3 seconds")
            print(f"Error was: {e}")
            time.sleep(3)

# Save to CSV
news_data.to_csv('NEW_SENTIMENTS.csv', index=False)

# dining-concierge-tj2237
A micro service based cloud project utilizing several AWS services like LexV2, S3, Lambda, API Gateway, SQS, DynamoDB, ElasticSearch and SES.

Link to working chatbot:
http://tj2237-clouds23-diningconcierge.s3-website.us-east-2.amazonaws.com/

### Implemented:
- **Greeting Intent** (sample prompts: 'Hi!' / 'Hey')  
- **Thank You Intent** (sample prompts: 'Thank You' / 'Thanks!')  
- **Dining Suggestion Intent** (sample prompts: 'suggest a restaurant' / 'suggest a restaurant in new york serving chinese cuisine')  
  - processing is done in `LF1` -> `DiningSuggestion()`, which logs request in `user-last-request` dynamoDB table (for extra credit), send to SQS (which is later polled in `LF2` to query ES index which is used to query dynamoDB to send email using SES with suggestions based on request)
- *extra credit:* **userHistory** (sample prompts: 'i'm back' / 'this is {phone}' / 'my phone number is {phone}')  
  - confirms if user wants last conversation to be used for suggestions, if user confirms, processing is done in `LF1` -> `userHistory()`

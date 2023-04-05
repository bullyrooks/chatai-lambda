import logging
import logging.config
import boto3
import os
import openai


logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

ssm = boto3.client('ssm', region_name=os.environ["AWS_REGION"])
bottokenresponse = ssm.get_parameter(
    Name='/prod/chatai/chatai.api.key',
    WithDecryption=True
)
openai.api_key = bottokenresponse["Parameter"]["Value"]

model = "gpt-3.5-turbo"

def get_chatai_response(text):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": text}
        ]
    )
    logger.info("completions out: %s", response)

    generated_text = response["choices"][0]["message"]["content"]
    return generated_text

def handler(event, context):
    logger.info("handler request in: %s", event)

    # Extract the text from the event data
    text = event["text"]
    logger.info("text in: %s", text)

    # Get a response from the OpenAI API
    response = get_chatai_response(text)
    logger.info("response out: %s", response)

    return {
        'statusCode': 200,
        'body': response
    }

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

model = "text-davinci-002"

def get_chatai_response(text):
    completions = openai.Completion.create(
        engine=model,
        prompt=text,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    generated_text = completions.choices[0].text
    return generated_text

def handler(event, context):
    logger.info("handler request in")

    # Extract the text from the event data
    text = event.get("text", "")
    logger.info("text in: %s", text)

    # Get a response from the OpenAI API
    response = get_chatai_response(text)
    logger.info("response out: %s", response)

    return {
        'statusCode': 200,
        'body': response
    }

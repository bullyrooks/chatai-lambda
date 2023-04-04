import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway)
from aws_cdk import aws_ssm as ssm
from aws_cdk.aws_apigateway import (
    ApiKey,
    UsagePlan,
    RestApi,
    ThrottleSettings,
    LambdaIntegration)
from aws_cdk.aws_ecr import Repository
from constructs import Construct


class ChatAILambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image_tag = os.getenv("IMAGE_TAG", "latest")
        chatai_lambda_ecr_image = _lambda.DockerImageCode.from_ecr(
            repository=Repository.from_repository_name(self,
                                                       "chatai-lambda-repository",
                                                       "chatai-lambda"),
            tag_or_digest=image_tag
        )
        chatai_lambda_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="chatai-lambda-lambda",
            # Function name on AWS
            function_name="chatai-lambda",
            # Use aws_cdk.aws_lambda.DockerImageCode.from_image_asset to build
            # a docker image on deployment
            code=chatai_lambda_ecr_image,
        )

        chatai_lambda_api = apigateway.LambdaRestApi(self, "chatai-lambda-api",
                                                        rest_api_name="ChatAI Lambda",
                                                        handler=chatai_lambda_lambda,
                                                        proxy=False)

        chatai_lambda_api.root.add_method("GET")

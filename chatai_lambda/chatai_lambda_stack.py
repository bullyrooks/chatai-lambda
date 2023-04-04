import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_certificatemanager as acm,
)
from aws_cdk.aws_apigateway import SecurityPolicy, EndpointType
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

        chatai_lambda_domain_name = "chatai.bullyrooks.com"
        # Create a certificate for the domain name
        chatai_lambda_certificate = acm.Certificate.from_certificate_arn(
            self, "chatai-lambda_certificate",
            certificate_arn="arn:aws:acm:us-west-2:108452827623:certificate/5a47eab5-4c2c-414d-8543-092d305d874e")

        ssm_policy_statement = iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            resources=["arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/*",
                       ],
            effect=iam.Effect.ALLOW
        )

        chatai_lambda_api = apigateway.LambdaRestApi(self, "chatai-lambda-api",
                                                     rest_api_name="ChatAI Lambda",
                                                     handler=chatai_lambda_lambda,
                                                     proxy=False,
                                                     api_key_source_type=apigateway.ApiKeySourceType.HEADER,
                                                     )

        chatai_lambda_api.add_domain_name(
            id="chatai-lambda-domain",
            domain_name=chatai_lambda_domain_name,
            certificate=chatai_lambda_certificate,
            security_policy=SecurityPolicy.TLS_1_2,
            endpoint_type=EndpointType.REGIONAL,
        )

        chatai_lambda_api.root.add_method("POST", api_key_required=True)

        # Create an API key
        chatai_integration_key = ApiKey(self, "Chat AI Integration Key",
                                        api_key_name="chatai-integration-key",
                                        enabled=True)

        # Create a usage plan
        development_usage_plan = UsagePlan(self,
                                           "ChatAI Integration Plan",
                                           throttle=ThrottleSettings(
                                               rate_limit=10,  # requests per second
                                               burst_limit=2  # maximum number of requests in a burst
                                           ),
                                           quota=apigateway.QuotaSettings(
                                               limit=200,  # number of requests
                                               period=apigateway.Period.DAY  # time period
                                           )
                                           )

        # Associate the API key with the usage plan
        development_usage_plan.add_api_key(chatai_integration_key)
        # Associate the API stage with the usage plan
        development_usage_plan.add_api_stage(
            api=chatai_lambda_api,
            stage=chatai_lambda_api.deployment_stage
        )
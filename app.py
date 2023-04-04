import aws_cdk as cdk

from chatai_lambda.chatai_lambda_stack import ChatAILambdaStack


app = cdk.App()
ChatAILambdaStack(app, "ChatAILambdaStack",)
app.synth()

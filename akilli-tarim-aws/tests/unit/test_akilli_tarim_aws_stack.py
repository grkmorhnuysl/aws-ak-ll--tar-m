import aws_cdk as core
import aws_cdk.assertions as assertions

from akilli_tarim_aws.akilli_tarim_aws_stack import AkilliTarimAwsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in akilli_tarim_aws/akilli_tarim_aws_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AkilliTarimAwsStack(app, "akilli-tarim-aws")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

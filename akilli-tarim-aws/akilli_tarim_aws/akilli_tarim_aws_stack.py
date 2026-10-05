from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_sns as sns,
    aws_s3 as s3,
    aws_sns_subscriptions as subs,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_sns as sns,
    aws_s3 as s3,
    aws_sns_subscriptions as subs,
    aws_cognito as cognito
)
from constructs import Construct

class AkilliTarimAwsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

	# --- COGNITO KİMLİK DOĞRULAMA ---
        user_pool = cognito.UserPool(
            self, "TarlaAdminPool",
            user_pool_name="TarlaAdminPool",
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        user_pool_client = user_pool.add_client(
            "TarlaDashboardClient",
            user_pool_client_name="TarlaDashboardClient",
            generate_secret=False, # Next.js frontend için secret kullanılmaz
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True)
        )

        # Terminalde bize lazım olacak ID'leri dışarı yazdırıyoruz
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
        # --------------------------------
        # 1. DynamoDB Tablosu
        sensor_table = dynamodb.Table(
            self, "SensorDataTable",
            partition_key=dynamodb.Attribute(name="sensor_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # 2. S3 Bucket (Arşiv)
        archive_bucket = s3.Bucket(
            self, "SensorDataArchive",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # 3. SNS Topic (Uyarılar)
        alert_topic = sns.Topic(self, "DroughtAlertTopic", display_name="Akilli Tarim Uyarilari")
        # BURAYA KENDİ E-POSTA ADRESİNİ YAZ:
        alert_topic.add_subscription(subs.EmailSubscription("kendi-mail-adresin@gmail.com"))

        # 4. Lambda Fonksiyonu
        ingestion_lambda = _lambda.Function(
            self, "DataIngestionLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.main",
            code=_lambda.Code.from_asset("lambda_src"), 
            environment={
                "TABLE_NAME": sensor_table.table_name,
                "BUCKET_NAME": archive_bucket.bucket_name,
                "TOPIC_ARN": alert_topic.topic_arn
            }
        )

        # İzinler
        sensor_table.grant_read_write_data(ingestion_lambda)
        archive_bucket.grant_read_write(ingestion_lambda)
        alert_topic.grant_publish(ingestion_lambda)

        # 5. API Gateway
        api = apigw.LambdaRestApi(
            self, "SensorApi",
            handler=ingestion_lambda,
            proxy=False 
        )
        
        sensors = api.root.add_resource("sensors")
        sensors.add_method("POST")
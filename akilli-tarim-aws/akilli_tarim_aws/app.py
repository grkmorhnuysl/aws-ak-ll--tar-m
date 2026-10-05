from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_sns as sns,
    aws_s3 as s3,
    aws_sns_subscriptions as subs,
)
from constructs import Construct

class SmartAgriStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. DynamoDB Tablosu (Sıcak Veri - Anlık Okuma/Yazma)
        # Pay-Per-Request modu Free Tier için en güvenlisidir, boşta para yazmaz.
        sensor_table = dynamodb.Table(
            self, "SensorDataTable",
            partition_key=dynamodb.Attribute(name="sensor_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY # Projeyi silince tablo da silinsin (Dev ortamı için)
        )

        # 2. S3 Bucket (Soğuk Veri - Günlük Arşiv / Data Lake)
        archive_bucket = s3.Bucket(
            self, "SensorDataArchive",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # 3. SNS Topic (Kritik Durum Uyarıları)
        alert_topic = sns.Topic(self, "DroughtAlertTopic", display_name="Akilli Tarim Uyarilari")
        # Kendi mail adresini buraya ekleyeceksin
        alert_topic.add_subscription(subs.EmailSubscription("kendi-mail-adresin@gmail.com"))

        # 4. Lambda Fonksiyonu (İşlem Katmanı)
        ingestion_lambda = _lambda.Function(
            self, "DataIngestionLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.main", # lambda_klasoru/handler.py içindeki main fonksiyonu çalışacak
            code=_lambda.Code.from_asset("lambda_src"), # Lambda kodlarının durduğu klasör
            environment={
                "TABLE_NAME": sensor_table.table_name,
                "BUCKET_NAME": archive_bucket.bucket_name,
                "TOPIC_ARN": alert_topic.topic_arn
            }
        )

        sensor_table.grant_read_write_data(ingestion_lambda)
        archive_bucket.grant_read_write(ingestion_lambda)
        alert_topic.grant_publish(ingestion_lambda)

        # 5. API Gateway (Dışarıya Açılan Kapı)
        api = apigw.LambdaRestApi(
            self, "SensorApi",
            handler=ingestion_lambda,
            proxy=False # Sadece belirlediğimiz endpointler çalışsın
        )
        
        # Sadece POST /sensors endpoint'ini oluşturuyoruz
        sensors = api.root.add_resource("sensors")
        sensors.add_method("POST")
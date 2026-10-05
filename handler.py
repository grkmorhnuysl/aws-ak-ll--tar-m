import json
import os
import boto3
from datetime import datetime, timezone

# 1. BEST PRACTICE: Boto3 client'larını fonksiyonun (main) dışında tanımlıyoruz.
# Böylece Lambda "Cold Start" yediğinde bu objeler tekrar tekrar oluşturulmaz, 
# bellek (memory) optimizasyonu sağlanır.
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
s3 = boto3.client('s3')

# CDK'dan enjekte ettiğimiz ortam değişkenleri
TABLE_NAME = os.environ.get('TABLE_NAME')
TOPIC_ARN = os.environ.get('TOPIC_ARN')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def main(event, context):
    try:
        # API Gateway'den gelen POST isteğinin gövdesini (body) al
        body = json.loads(event.get('body', '{}'))
        
        sensor_id = body.get('sensor_id', 'UNKNOWN_SENSOR')
        temperature = body.get('temperature')
        humidity = body.get('humidity')
        ph_level = body.get('ph_level')
        
        # Zaman damgası oluştur (Örn: 2026-10-05T14:30:00+00:00)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # 2. DynamoDB'ye Kayıt (Sıcak Veri - Hızlı Okuma/Yazma)
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                'sensor_id': sensor_id,
                'timestamp': timestamp,
                'temperature': str(temperature), # Decimal hatalarını önlemek için string
                'humidity': str(humidity),
                'ph_level': str(ph_level)
            }
        )
        
        # 3. İş Kuralı (Business Logic): Anomali Kontrolü ve SNS Uyarı
        # Nem %20'nin altındaysa kuraklık alarmı ver
        if humidity is not None and float(humidity) < 20.0:
            alert_message = f"🚨 KRİTİK UYARI: {sensor_id} sensöründe nem seviyesi çok düşük! Mevcut Nem: %{humidity}"
            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="Akıllı Tarım: Kuraklık Uyarısı!",
                Message=alert_message
            )
            
        # 4. S3'e Yedekleme (Data Lake Konsepti)
        # Gelen ham veriyi S3'te bir JSON dosyası olarak arşivle
        s3_key = f"{sensor_id}/{timestamp}.json"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(body),
            ContentType='application/json'
        )

        # API Gateway'e başarılı dönüş yap
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Veri başarıyla işlendi', 
                'sensor': sensor_id,
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        # Hata yakalama: Sistem çökerse 500 dön ve loglara yazdır
        print(f"Sistem Hatası: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Sunucu hatası', 'error': str(e)})
        }
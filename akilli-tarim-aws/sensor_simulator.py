import time
import random
import requests
import json

# CDK deploy komutunu çalıştırdıktan sonra terminalde çıkan API Gateway URL'sini buraya yapıştır.
# Örnek: "https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/sensors"
API_URL = "https://k46in8fflh.execute-api.us-east-1.amazonaws.com/prod/sensors"

SENSOR_ID = "TARLA-01-NODE-A"

def generate_sensor_data():
    """Gerçekçi tarım (sıcaklık, nem, pH) verileri üretir."""
    # SNS alarmını test edebilmek için %25 ihtimalle kuraklık simüle ediyoruz
    is_drought_sim = random.choice([True, False, False, False])
    
    temperature = round(random.uniform(15.0, 38.0), 2)  # Celcius
    # Kuraklık simülasyonu devredeyse nemi %20'nin altında tut ki mail gelsin
    humidity = round(random.uniform(5.0, 19.9) if is_drought_sim else random.uniform(30.0, 80.0), 2)
    ph_level = round(random.uniform(5.5, 7.5), 2)  # Toprak pH
    
    return {
        "sensor_id": SENSOR_ID,
        "temperature": temperature,
        "humidity": humidity,
        "ph_level": ph_level
    }

def main():
    print(f"🌱 {SENSOR_ID} veri simülasyonu başlatıldı...")
    print("Durdurmak için CTRL+C'ye basın.\n")
    
    while True:
        payload = generate_sensor_data()
        print(f"📡 Gönderilen Veri: {json.dumps(payload)}")
        
        try:
            # API Gateway'e veriyi POST ediyoruz
            response = requests.post(
                API_URL, 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ Başarılı: {response.json()}")
            else:
                print(f"❌ Sunucu Hatası ({response.status_code}): {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"🔌 Bağlantı Hatası: API'ye ulaşılamadı. Hata: {e}")
            
        # Test için verileri 10 saniyede bir gönderiyoruz. 
        # Gerçek bir IoT donanımında pil ömrü için bu süre 5-10 dakika arası olur.
        time.sleep(10)

if __name__ == "__main__":
    main()
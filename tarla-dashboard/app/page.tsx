import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, ScanCommand } from "@aws-sdk/lib-dynamodb";
import DashboardClient from "./DashboardClient";

// AWS SDK yapılandırması (Sadece sunucuda çalışır, güvenlidir)
const client = new DynamoDBClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID as string,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY as string,
  },
});
const docClient = DynamoDBDocumentClient.from(client);

// Veritabanından verileri asenkron olarak çeken fonksiyon
async function getSensorData() {
  try {
    const command = new ScanCommand({
      TableName: process.env.DYNAMODB_TABLE_NAME,
    });
    
    const response = await docClient.send(command);
    
    // Verileri zamana göre en yeniden en eskiye sıralıyoruz (Dashboard anlık veriyi ilk sıradan alsın diye)
    const items = (response.Items || []).sort((a, b) => {
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });
    
    return items;
  } catch (error) {
    console.error("DynamoDB Bağlantı Hatası:", error);
    return [];
  }
}

// Next.js 14 için sayfanın cache'lenmesini engelleyip her girişte güncel veri çekmesini sağlıyoruz
export const dynamic = "force-dynamic";

export default async function Home() {
  const data = await getSensorData();

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">🌱 Akıllı Tarım İzleme Merkezi</h1>
          <p className="text-gray-500 mt-2">AWS Serverless ve Next.js tabanlı gerçek zamanlı IoT veri akışı.</p>
        </div>
        
        {/* Veriyi Client Component'e aktarıyoruz */}
        <DashboardClient data={data} />
      </div>
    </main>
  );
}
"use client";

import { useState, useEffect } from "react";
import { Amplify } from "aws-amplify";
import { signIn, signOut, getCurrentUser } from "aws-amplify/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { Thermometer, Droplets, FlaskConical, Activity, LogOut } from "lucide-react";

// AWS Cognito Bağlantı Ayarları
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID as string,
      userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID as string,
    }
  }
});

export default function DashboardClient({ data }: { data: any[] }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");

  // Sayfa açıldığında kullanıcının daha önceden giriş yapıp yapmadığını kontrol et
  useEffect(() => {
    checkUser();
  }, []);

  async function checkUser() {
    try {
      await getCurrentUser();
      setIsAuthenticated(true);
    } catch (err) {
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }

  // AWS Cognito Giriş İşlemi
  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setAuthError("");
    try {
      const { isSignedIn } = await signIn({ username: email, password });
      if (isSignedIn) setIsAuthenticated(true);
    } catch (err: any) {
      setAuthError("Giriş başarısız. Lütfen bilgilerinizi kontrol edin.");
      console.error(err);
    }
  }

  // AWS Cognito Çıkış İşlemi
  async function handleLogout() {
    await signOut();
    setIsAuthenticated(false);
  }

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen"><Activity className="h-10 w-10 text-emerald-500 animate-spin" /></div>;
  }

  // GİRİŞ EKRANI
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="w-[400px] shadow-xl border-t-4 border-t-emerald-500">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Sisteme Giriş</CardTitle>
            <p className="text-sm text-gray-500 mt-2">Akıllı Tarım İzleme Merkezi</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <input 
                type="email" 
                placeholder="E-posta" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" 
                required
              />
              <input 
                type="password" 
                placeholder="Şifre"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" 
                required
              />
              {authError && <p className="text-red-500 text-sm text-center">{authError}</p>}
              <button 
                type="submit"
                className="w-full bg-emerald-600 text-white h-10 rounded-md font-medium hover:bg-emerald-700 transition-colors"
              >
                Giriş Yap
              </button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  // VERİ YOK EKRANI
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col justify-center items-center h-64 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50/50">
        <Activity className="h-10 w-10 text-gray-400 mb-4 animate-pulse" />
        <p className="text-gray-500 font-medium">Sensör verisi bekleniyor...</p>
        <button onClick={handleLogout} className="mt-4 text-sm text-red-500 hover:underline">Çıkış Yap</button>
      </div>
    );
  }

  const latest = data[0];
  const chartData = [...data].reverse();

  // DASHBOARD EKRANI
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <div className="flex items-center gap-3">
          <div className="h-3 w-3 bg-emerald-500 rounded-full animate-pulse"></div>
          <span className="font-semibold text-gray-700">Sistem Aktif | TARLA-01-NODE-A</span>
        </div>
        <button 
          onClick={handleLogout} 
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          <LogOut className="h-4 w-4" /> Çıkış Yap
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-l-4 border-l-orange-500 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-semibold text-gray-600">Sıcaklık</CardTitle>
            <Thermometer className="h-5 w-5 text-orange-500" />
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-extrabold text-gray-900">{latest.temperature}<span className="text-2xl text-gray-400">°C</span></p>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-blue-500 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-semibold text-gray-600">Toprak Nemi</CardTitle>
            <Droplets className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-extrabold text-gray-900"><span className="text-2xl text-gray-400">%</span>{latest.humidity}</p>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-emerald-500 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-semibold text-gray-600">pH Seviyesi</CardTitle>
            <FlaskConical className="h-5 w-5 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-extrabold text-gray-900">{latest.ph_level}</p>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-lg border-0 ring-1 ring-gray-100">
        <CardHeader className="bg-gray-50/50 border-b border-gray-100 pb-4">
          <CardTitle className="text-lg text-gray-700 flex items-center gap-2">
            <Activity className="h-5 w-5 text-indigo-500" />
            24 Saatlik Sensör Trendi
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[450px] pt-6">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorHumidity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={(tick) => new Date(tick).toLocaleTimeString('tr-TR', { hour: '2-digit', minute:'2-digit' })} 
                stroke="#9ca3af"
                fontSize={12}
              />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                labelFormatter={(label) => new Date(label).toLocaleString('tr-TR')}
              />
              <Area type="monotone" dataKey="humidity" stroke="#3b82f6" fillOpacity={1} fill="url(#colorHumidity)" name="Nem (%)" strokeWidth={3} />
              <Line type="monotone" dataKey="temperature" stroke="#f97316" name="Sıcaklık (°C)" strokeWidth={3} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
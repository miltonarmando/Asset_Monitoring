import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8000/api/v1/devices/";

export default function DeviceList() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(API_URL)
      .then((res) => {
        if (!res.ok) throw new Error("Erro ao buscar dispositivos");
        return res.json();
      })
      .then(setDevices)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center p-4">Carregando dispositivos...</div>;
  if (error) return <div className="text-center text-red-600 p-4">{error}</div>;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-4 max-w-4xl mx-auto mt-8">
      <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">Dispositivos Monitorados</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {devices.length === 0 && <div className="col-span-2 text-gray-400">Nenhum dispositivo cadastrado.</div>}
        {devices.map((dev) => (
          <div key={dev.id} className="border rounded p-4 bg-gray-50 dark:bg-gray-800">
            <div className="font-semibold text-lg">{dev.name || dev.hostname}</div>
            <div className="text-sm text-gray-500">IP: {dev.ip_address}</div>
            <div className="text-sm text-gray-500">Status: <span className={dev.status === 'online' ? 'text-green-600' : 'text-red-600'}>{dev.status || 'desconhecido'}</span></div>
            {/* Adicione outras métricas relevantes aqui */}
          </div>
        ))}
      </div>
    </div>
  );
}

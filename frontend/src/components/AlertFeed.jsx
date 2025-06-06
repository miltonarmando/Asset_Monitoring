import React, { useEffect, useState, useRef } from "react";

const WS_URL = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.hostname}:8000/ws/alerts`;

export default function AlertFeed() {
  const [alerts, setAlerts] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new window.WebSocket(WS_URL);
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setAlerts((prev) => [data, ...prev].slice(0, 50));
      } catch (e) {
        // Ignore malformed messages
      }
    };
    ws.current.onclose = () => {
      // Try to reconnect after a delay
      setTimeout(() => {
        ws.current = new window.WebSocket(WS_URL);
      }, 2000);
    };
    return () => ws.current && ws.current.close();
  }, []);

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-4 max-w-xl mx-auto mt-8">
      <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">Alertas em tempo real</h2>
      <ul className="space-y-2 max-h-96 overflow-y-auto">
        {alerts.length === 0 && <li className="text-gray-400">Nenhum alerta recebido ainda.</li>}
        {alerts.map((alert, idx) => (
          <li key={idx} className="border-l-4 pl-2 border-red-500 bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded">
            <span className="font-semibold">{alert.severity || "ALERTA"}:</span> {alert.message || JSON.stringify(alert)}
            <span className="block text-xs text-gray-400 mt-1">{alert.timestamp || ""}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

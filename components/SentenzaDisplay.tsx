import React, { useState, useEffect } from 'react';

interface SentenzaData {
  timestamp: string;
  testo: string;
  status: 'success' | 'error';
  error?: string;
}

export const SentenzaDisplay: React.FC<{ apiUrl: string }> = ({ apiUrl }) => {
  const [data, setData] = useState<SentenzaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSentenza = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/sentenza`);
        if (!response.ok) throw new Error('Errore nel caricamento');
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Errore sconosciuto');
      } finally {
        setLoading(false);
      }
    };
    fetchSentenza();
    const interval = setInterval(fetchSentenza, 60000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  if (loading) return <div className="text-center p-4">Caricamento...</div>;
  if (error) return <div className="text-red-600 p-4">Errore: {error}</div>;
  if (!data) return <div className="text-gray-500 p-4">Nessun dato disponibile</div>;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="text-sm text-gray-500 mb-4">
        Aggiornato: {new Date(data.timestamp).toLocaleDateString('it-IT')}
      </div>
      <div className="prose prose-sm max-w-none">
        {data.status === 'success' ? (
          <p className="whitespace-pre-wrap">{data.testo}</p>
        ) : (
          <p className="text-red-600">Errore: {data.error}</p>
        )}
      </div>
    </div>
  );
};

export default SentenzaDisplay;

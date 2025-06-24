import { useState, useEffect } from 'react';
import './App.css';
import { TextField, Button, Box, Typography, CardContent, CircularProgress, Backdrop } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [tab, setTab] = useState(0);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [longLoading, setLongLoading] = useState(false);
  const [error, setError] = useState(null);

  // Show extended loading message if loading > 10s
  useEffect(() => {
    let timer;
    if (loading) {
      timer = setTimeout(() => setLongLoading(true), 10000);
    } else {
      setLongLoading(false);
    }
    return () => clearTimeout(timer);
  }, [loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // Use backend URL from environment variable for easy deployment
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) throw new Error('Server error');
      const data = await res.json();
      setResults(data);
      setHistory([{ query, timestamp: new Date().toLocaleString() }, ...history]);
    } catch (err) {
      setError('Failed to get response from backend.');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f7f6' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f4f3', px: 8, py: 2, bgcolor: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ width: 24, height: 24, color: '#121615' }}>
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path d="M13.8261 30.5736C16.7203 29.8826 20.2244 29.4783 24 29.4783C27.7756 29.4783 31.2797 29.8826 34.1739 30.5736C36.9144 31.2278 39.9967 32.7669 41.3563 33.8352L24.8486 7.36089C24.4571 6.73303 23.5429 6.73303 23.1514 7.36089L6.64374 33.8352C8.00331 32.7669 11.0856 31.2278 13.8261 30.5736Z" fill="currentColor"></path><path fillRule="evenodd" clipRule="evenodd" d="..." fill="currentColor"></path></svg>
          </Box>
          <Typography sx={{ color: '#121615', fontWeight: 700, fontSize: 18 }}>InsightLens</Typography>
        </Box>
      </Box>

      {/* Main content */}
      <Box sx={{ px: 20, py: 4, display: 'flex', justifyContent: 'center', minHeight: '70vh' }}>
        <Box sx={{ width: '100%', maxWidth: 960, bgcolor: 'white', borderRadius: 4, boxShadow: 2, p: 0, display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ px: 0, position: 'relative' }}>
            <Backdrop open={loading} sx={{ position: 'absolute', zIndex: 10, color: '#1976d2', background: 'rgba(255,255,255,0.6)', flexDirection: 'column' }}>
              <CircularProgress color="primary" />
              {longLoading && (
                <Typography sx={{ mt: 2, color: '#1976d2', fontWeight: 600 }}>
                  Still working, this may take a while...
                </Typography>
              )}
            </Backdrop>

            <Typography sx={{ fontWeight: 700, fontSize: 28,color: '#121615', textAlign: 'center', pt: 5, pb: 2 }}>
              Ask a question about your business data
            </Typography>

            {/* Search bar */}
            <Box sx={{ px: 4, py: 2 }}>
              <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#f1f4f3', borderRadius: 2, height: 48 }}>
                  <Box sx={{ color: '#6a817b', pl: 2 }}>
                    <SearchIcon fontSize="medium" />
                  </Box>
                  <input
                    placeholder="e.g., What were the total sales last quarter?"
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    style={{ border: 'none', outline: 'none', background: 'transparent',color: '#121615', flex: 1, fontSize: 16, padding: '0 12px' }}
                    onKeyDown={e => { if (e.key === 'Enter') handleSubmit(e); }}
                  />
                  <Button
                    type="submit"
                    variant="contained"
                    sx={{ bgcolor: '#121615', color: '#fff', height: 40, borderRadius: 2, ml: 1 }}
                    disabled={!query.trim()}
                  >
                    <SearchIcon fontSize="small" />
                  </Button>
                </Box>
              </form>
            </Box>

            {/* Quick Query Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'center', px: 4, py: 2, gap: 2, flexWrap: 'wrap' }}>
              <Button variant="contained" sx={{ bgcolor: '#f1f4f3', color: '#121615' }} onClick={() => setQuery('What are the top five portfolios of our wealth members?')}>Quick Query 1</Button>
              <Button variant="contained" sx={{ bgcolor: '#f1f4f3', color: '#121615' }} onClick={() => setQuery('Give me the breakup of portfolio values per relationship manager.')}>Quick Query 2</Button>
            </Box>

            {/* Tabs */}
            {/* <Box sx={{ borderBottom: '1px solid #dde3e2', px: 4, pt: 2, display: 'flex', gap: 6 }}>
              <Button onClick={() => setTab(0)} sx={{ borderBottom: tab === 0 ? '3px solid #121615' : '3px solid transparent' }}>Text</Button>
              <Button onClick={() => setTab(1)} sx={{ borderBottom: tab === 1 ? '3px solid #121615' : '3px solid transparent' }}>Table</Button>
              <Button onClick={() => setTab(2)} sx={{ borderBottom: tab === 2 ? '3px solid #121615' : '3px solid transparent' }}>Chart</Button>
            </Box> */}


      <Box sx={{ borderBottom: '1px solid #dde3e2', px: 4, pt: 2, display: 'flex', gap: 2 }}>
              {[
                { label: 'Text', index: 0 },
                { label: 'Table', index: 1 },
                { label: 'Chart', index: 2 }
              ].map(({ label, index }) => (
                <Button
                  key={label}
                  onClick={() => setTab(index)}
                  sx={{
                    backgroundColor: tab === index ? '#e3f2fd' : 'transparent',
                    color: tab === index ? '#1976d2' : '#6a817b',
                    fontWeight: 700,
                    fontSize: 15,
                    borderRadius: 2,
                    px: 3,
                    py: 1,
                    boxShadow: tab === index ? 1 : 'none',
                    textTransform: 'uppercase',
                    transition: '0.3s',
                    '&:hover': {
                      backgroundColor: tab === index ? '#e3f2fd' : '#f0f0f0',
                    }
                  }}
                >
                 {label}
                </Button>
                   ))}
                </Box>


            {/* Results */}
            <Box sx={{ minHeight: 80, px: 4, py: 2 }}>
            {results && tab === 0 && (
  <Typography sx={{ color: '#121615', fontSize: 16 }}>{results.text}</Typography>
)}


              {results && tab === 1 && results.table?.columns && results.table?.rows && (
                <table className="data-table">
                  <thead>
                    <tr>{results.table.columns.map(col => <th key={col}>{col}</th>)}</tr>
                  </thead>
                  <tbody>
                    {results.table.rows.map((row, i) => (
                      <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>
                    ))}
                  </tbody>
                </table>
              )}

              {results && tab === 2 && results.chart?.labels && results.chart?.data ? (
                <div className="chart-container">
                  <Bar
                    data={{
                      labels: results.chart.labels,
                      datasets: [
                        {
                          label: results.chart.label || 'Chart',
                          data: results.chart.data,
                          backgroundColor: '#4f8cff',
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { display: true },
                        title: { display: !!results.chart.label, text: results.chart.label },
                      },
                    }}
                  />
                </div>
              ) : (tab === 2 && <Typography>No chart data available.</Typography>)}

              {!results && <Typography sx={{ color: '#888', pt: 2 }}>Results will be displayed here.</Typography>}
            </Box>

            {/* Query History */}
            <Typography sx={{ fontWeight: 700, fontSize: 18, px: 4, pt: 2 }}>Query History</Typography>
            <Box sx={{ px: 4, pb: 4 }}>
              {history.length === 0 && <Typography>No previous queries yet.</Typography>}
              {history.map((item, i) => (
                <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', bgcolor: '#f9f9f9', borderRadius: 2, px: 2, py: 1, mb: 1 }}>
                  <Typography sx={{ color: '#121615' }}>{item.query}</Typography>

                  <Typography sx={{ color: '#666', fontSize: 12 }}>{item.timestamp}</Typography>

                </Box>
              ))}
            </Box>
          </CardContent>
        </Box>
      </Box>
    </Box>
  );
}

export default App;

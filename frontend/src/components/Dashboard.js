import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format, subDays } from 'date-fns';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './Dashboard.css';

const ANALYTICS_SERVICE_URL = process.env.REACT_APP_ANALYTICS_SERVICE_URL || 'http://localhost:8001';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];

function Dashboard({ token, onLogout }) {
  const [summary, setSummary] = useState(null);
  const [eventTypes, setEventTypes] = useState([]);
  const [dateRangeData, setDateRangeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 7), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd')
  });

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [dateRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);

      // Fetch summary
      const summaryResponse = await axios.get(`${ANALYTICS_SERVICE_URL}/analytics/summary`);
      setSummary(summaryResponse.data);

      // Fetch event types
      const eventTypesResponse = await axios.get(`${ANALYTICS_SERVICE_URL}/analytics/events/by-type`);
      setEventTypes(eventTypesResponse.data);

      // Fetch date range data
      const dateRangeResponse = await axios.get(
        `${ANALYTICS_SERVICE_URL}/analytics/events/date-range`,
        {
          params: {
            start_date: `${dateRange.start}T00:00:00`,
            end_date: `${dateRange.end}T23:59:59`
          }
        }
      );
      setDateRangeData(dateRangeResponse.data);

      setError('');
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDateRangeChange = (e) => {
    setDateRange({
      ...dateRange,
      [e.target.name]: e.target.value
    });
  };

  const pieChartData = eventTypes.map(item => ({
    name: item.event_type,
    value: item.count
  }));

  const barChartData = eventTypes.map(item => ({
    name: item.event_type,
    count: item.count
  }));

  if (loading && !summary) {
    return (
      <div className="dashboard">
        <div className="loading">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Analytics Dashboard</h1>
        <button onClick={onLogout} className="logout-btn">Logout</button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="date-filter">
        <label>
          Start Date:
          <input
            type="date"
            name="start"
            value={dateRange.start}
            onChange={handleDateRangeChange}
          />
        </label>
        <label>
          End Date:
          <input
            type="date"
            name="end"
            value={dateRange.end}
            onChange={handleDateRangeChange}
          />
        </label>
        <button onClick={fetchAnalytics} className="refresh-btn">
          Refresh
        </button>
      </div>

      {summary && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>Total Users</h3>
              <p className="stat-value">{summary.total_users}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-content">
              <h3>Active Users (24h)</h3>
              <p className="stat-value">{summary.active_users_24h}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3>Total Events</h3>
              <p className="stat-value">{summary.total_events}</p>
            </div>
          </div>

          {dateRangeData && (
            <div className="stat-card">
              <div className="stat-icon">📅</div>
              <div className="stat-content">
                <h3>Events in Range</h3>
                <p className="stat-value">{dateRangeData.total_events}</p>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="charts-grid">
        {eventTypes.length > 0 && (
          <>
            <div className="chart-card">
              <h3>Event Distribution (Pie Chart)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Event Counts by Type (Bar Chart)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {dateRangeData && Object.keys(dateRangeData.event_breakdown).length > 0 && (
          <div className="chart-card full-width">
            <h3>Events in Selected Date Range</h3>
            <div className="event-breakdown">
              {Object.entries(dateRangeData.event_breakdown).map(([eventType, count]) => (
                <div key={eventType} className="event-item">
                  <span className="event-name">{eventType}</span>
                  <span className="event-count">{count}</span>
                </div>
              ))}
            </div>
            <p className="date-range-info">
              Unique Users in Range: <strong>{dateRangeData.unique_users}</strong>
            </p>
          </div>
        )}
      </div>

      {eventTypes.length === 0 && (
        <div className="empty-state">
          <p>No analytics data available yet. Start using the platform to generate events!</p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;

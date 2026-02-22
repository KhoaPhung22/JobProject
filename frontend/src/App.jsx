import { useState, useEffect } from 'react'
import { Briefcase, MapPin, Globe, Clock, Search, BarChart2, Filter, LogIn, UserPlus } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Login from './components/Login'
import Register from './components/Register'

function App() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [analyticsData, setAnalyticsData] = useState(null)
  const locationPath = useLocation()

  // Filter States
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')
  const [jobType, setJobType] = useState('')
  const [isRemote, setIsRemote] = useState('all')

  const COLORS = ['#6366f1', '#2dd4bf', '#fbbf24', '#f472b6', '#a78bfa']

  useEffect(() => {
    fetchJobs()
  }, [search, location, jobType, isRemote])

  useEffect(() => {
    if (locationPath.pathname === '/analytics') {
      fetchAnalytics()
    }
  }, [locationPath.pathname])

  const fetchJobs = async () => {
    try {
      setLoading(true)

      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (location) params.append('location', location)
      if (jobType) params.append('type', jobType)
      if (isRemote !== 'all') params.append('remote', isRemote === 'true')

      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiUrl}/jobs?${params.toString()}`)
      if (!response.ok) throw new Error('Failed to fetch jobs')
      const data = await response.json()
      setJobs(data.jobs || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${apiUrl}/analytics`)
      if (!response.ok) throw new Error('Failed to fetch analytics')
      const data = await response.json()
      setAnalyticsData(data)
    } catch (err) {
      console.error('Analytics Error:', err)
      setError('Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }

  const renderBoard = () => (
    <>
      <div className="search-container">
        <div className="search-field">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search job title or company..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="search-field">
          <MapPin size={20} />
          <input
            type="text"
            placeholder="Location (City, State)..."
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>
        <div className="search-field">
          <Filter size={20} />
          <select value={jobType} onChange={(e) => setJobType(e.target.value)}>
            <option value="">All Job Types</option>
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
          </select>
        </div>
        <div className="search-field">
          <Globe size={20} />
          <select value={isRemote} onChange={(e) => setIsRemote(e.target.value)}>
            <option value="all">Remote / On-site</option>
            <option value="true">Remote Only</option>
            <option value="false">On-site Only</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      ) : (
        <div className="job-grid">
          {jobs.map((job) => (
            <div key={job.id} className="job-card">
              <div className="company-name">
                <Briefcase size={18} />
                {job.employer}
              </div>
              <h2 className="job-title">{job.title}</h2>
              <div className="job-info">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <MapPin size={14} />
                  {job.city}, {job.state}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Globe size={14} />
                  {job.country}
                </div>
                {job.is_remote ? <span className="badge">Remote</span> : <span className="badge" style={{ background: 'rgba(148, 163, 184, 0.1)', color: '#94a3b8', borderColor: 'rgba(148, 163, 184, 0.2)' }}>On-site</span>}
              </div>
              <p className="job-description">{job.description}</p>
              <button
                className="apply-btn"
                onClick={() => window.open(job.apply_link, '_blank')}
              >
                Apply Now
              </button>
            </div>
          ))}
          {jobs.length === 0 && (
            <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '4rem', color: '#94a3b8' }}>
              <Search size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
              <h3>No jobs found matching your criteria</h3>
              <p>Try adjusting your filters or search terms</p>
            </div>
          )}
        </div>
      )}
    </>
  )

  const renderAnalytics = () => {
    if (!analyticsData && loading) return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    )

    if (!analyticsData) return <div style={{ textAlign: 'center', padding: '4rem' }}>No data available</div>

    return (
      <div className="analytics-view">
        <div className="analytics-grid">
          <div className="stat-card">
            <div className="stat-label">Total Listings</div>
            <div className="stat-value">{analyticsData.total_jobs}</div>
            <div className="stat-label" style={{ fontSize: '0.9rem' }}>Analyzed with Pandas</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Computer Jobs</div>
            <div className="stat-value">{analyticsData.number_computer_jobs}</div>
            <div className="stat-label" style={{ fontSize: '0.9rem' }}>Analyzed Computer Jobs</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Remote Adoption</div>
            <div className="stat-value">{analyticsData.remote_percent}%</div>
            <div className="stat-label" style={{ fontSize: '0.9rem' }}>Market distribution</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Cities Found</div>
            <div className="stat-value">{analyticsData.top_cities.length}</div>
            <div className="stat-label" style={{ fontSize: '0.9rem' }}>Global footprint</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Job posted in last 24 hours</div>
            <div className="stat-value">{analyticsData.number_of_jobs_today}</div>
            <div className="stat-label" style={{ fontSize: '0.9rem' }}>Today's Jobs</div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '2rem' }}>
          <div className="stat-card chart-container" style={{ textAlign: 'left' }}>
            <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff' }}>
              <MapPin size={20} color="var(--primary)" /> Top Hiring Hubs
            </h3>
            <div style={{ height: '300px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analyticsData.top_cities} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis type="number" stroke="#94a3b8" />
                  <YAxis dataKey="name" type="category" stroke="#94a3b8" width={80} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'var(--bg-color)', border: '1px solid var(--card-border)', borderRadius: '1rem' }}
                    itemStyle={{ color: 'var(--primary)' }}
                  />
                  <Bar dataKey="count" fill="var(--primary)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="stat-card chart-container" style={{ textAlign: 'left' }}>
            <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff' }}>
              <Clock size={20} color="var(--accent)" /> Employment Types
            </h3>
            <div style={{ height: '300px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.employment_types}
                    dataKey="count"
                    nameKey="type"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {analyticsData.employment_types.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: 'var(--bg-color)', border: '1px solid var(--card-border)', borderRadius: '1rem' }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '2rem' }}>
          <div className="stat-card chart-container" style={{ textAlign: 'left' }}>
            <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff' }}>
              <MapPin size={20} color="var(--primary)" /> Number of Jobs By Days
            </h3>
            <div style={{ height: '300px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analyticsData.number_of_jobs_by_days} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis
                    dataKey="name"
                    stroke="#94a3b8"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'var(--bg-color)', border: '1px solid var(--card-border)', borderRadius: '1rem' }}
                    itemStyle={{ color: 'var(--primary)' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="var(--primary)"
                    strokeWidth={3}
                    dot={{ r: 4, fill: 'var(--primary)', strokeWidth: 2, stroke: 'var(--bg-color)' }}
                    activeDot={{ r: 6, strokeWidth: 0 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="chart-placeholder" style={{ marginTop: '2rem' }}>
          <div style={{ textAlign: 'center' }}>
            <BarChart2 size={48} style={{ marginBottom: '1rem', color: 'var(--primary)' }} />
            <h3>Pandas Driven Intelligence</h3>
            <p>Real-time statistical analysis performed directly on the server DataFrame.</p>
          </div>
        </div>
      </div>
    )
  }

  const isAuthPage = locationPath.pathname === '/login' || locationPath.pathname === '/register'

  return (
    <div className="container">
      <header>
        <nav style={{ justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '2rem' }}>
            <Link to="/" className={`nav-link ${locationPath.pathname === '/' ? 'active' : ''}`}>Job Board</Link>
            <Link to="/analytics" className={`nav-link ${locationPath.pathname === '/analytics' ? 'active' : ''}`}>Analytics</Link>
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
            <Link to="/login" className={`nav-link ${locationPath.pathname === '/login' ? 'active' : ''}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <LogIn size={18} /> Sign In
            </Link>
            <Link to="/register" className="apply-btn" style={{ marginTop: 0, padding: '0.6rem 1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <UserPlus size={18} /> Sign Up
            </Link>
          </div>
        </nav>
        {!isAuthPage && (
          <>
            <h1>{locationPath.pathname === '/' ? 'Find Your Flow' : 'Market Insights'}</h1>
            <p className="subtitle">
              {locationPath.pathname === '/' ? 'Curated opportunities for top tech talent' : 'Real-time data from the current job market'}
            </p>
          </>
        )}
      </header>

      {error && !isAuthPage ? (
        <div style={{ textAlign: 'center', color: '#f43f5e', padding: '4rem' }}>
          <p>Error: {error}</p>
          <button onClick={fetchJobs} className="apply-btn" style={{ marginTop: '1rem', width: 'auto', padding: '0.5rem 2rem' }}>
            Try Again
          </button>
        </div>
      ) : (
        <Routes>
          <Route path="/" element={renderBoard()} />
          <Route path="/analytics" element={renderAnalytics()} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      )}
    </div>
  )
}

export default App

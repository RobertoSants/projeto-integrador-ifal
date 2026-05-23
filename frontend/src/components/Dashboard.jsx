import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { workersAPI, servicesAPI, searchAPI, accountsAPI } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [workers, setWorkers] = useState([]);
  const [services, setServices] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterService, setFilterService] = useState('');
  const [minRating, setMinRating] = useState('');
  const [activeTab, setActiveTab] = useState('browse');
  const navigate = useNavigate();

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [workersRes, servicesRes, userRes] = await Promise.all([
          workersAPI.list(),
          servicesAPI.list(),
          accountsAPI.getMe(),
        ]);
        setWorkers(workersRes.data);
        setServices(servicesRes.data);
        setUser(userRes.data);
      } catch (err) {
        console.error('Erro ao carregar dashboard:', err);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, [navigate]);

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const params = {};
      if (searchQuery) params.q = searchQuery;
      if (filterService) params.service = filterService;
      if (minRating) params.rating = minRating;

      const response = await searchAPI.search(params);
      setWorkers(response.data.results || []);
    } catch (err) {
      console.error('Erro ao buscar:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  const resetSearch = async () => {
    setSearchQuery('');
    setFilterService('');
    setMinRating('');
    try {
      const response = await workersAPI.list();
      setWorkers(response.data);
    } catch (err) {
      console.error('Erro ao resetar:', err);
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>💼 Banco de Talentos Comunitário</h1>
          <div className="user-info">
            {user && <span>Bem-vindo, {user.username}!</span>}
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button
          className={`nav-btn ${activeTab === 'browse' ? 'active' : ''}`}
          onClick={() => setActiveTab('browse')}
        >
          Buscar Talentos
        </button>
        <button
          className={`nav-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Meu Perfil
        </button>
      </nav>

      <main className="dashboard-main">
        {activeTab === 'browse' && (
          <section className="browse-section">
            <div className="search-box">
              <h2>Buscar Talentos</h2>
              <form onSubmit={handleSearch}>
                <div className="search-inputs">
                  <input
                    type="text"
                    placeholder="Buscar por nome ou habilidade..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                  />
                  <select
                    value={filterService}
                    onChange={(e) => setFilterService(e.target.value)}
                    className="filter-select"
                  >
                    <option value="">Todas as categorias</option>
                    {services.map((service) => (
                      <option key={service.id} value={service.id}>
                        {service.name}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    placeholder="Avaliação mínima"
                    value={minRating}
                    onChange={(e) => setMinRating(e.target.value)}
                    min="1"
                    max="5"
                    step="0.1"
                    className="filter-input"
                  />
                  <button type="submit" className="search-btn">
                    🔍 Buscar
                  </button>
                  <button
                    type="button"
                    onClick={resetSearch}
                    className="reset-btn"
                  >
                    ↺ Limpar
                  </button>
                </div>
              </form>
            </div>

            <div className="workers-grid">
              {workers.length === 0 ? (
                <p className="no-results">
                  Nenhum talento encontrado com esses critérios.
                </p>
              ) : (
                workers.map((worker) => (
                  <div key={worker.id} className="worker-card">
                    {worker.photo && (
                      <img
                        src={worker.photo}
                        alt={worker.full_name}
                        className="worker-photo"
                      />
                    )}
                    <div className="worker-info">
                      <h3>{worker.full_name}</h3>
                      <p className="worker-bio">{worker.bio}</p>
                      <div className="worker-details">
                        <span className="location">
                          📍 {worker.city}, {worker.state}
                        </span>
                        <span className="rating">
                          ⭐{' '}
                          {worker.avg_rating ? worker.avg_rating.toFixed(1) : 'N/A'}
                        </span>
                      </div>
                      {worker.services && (
                        <div className="services-list">
                          {Array.isArray(worker.services) &&
                          typeof worker.services[0] === 'object'
                            ? worker.services.map((service) => (
                                <span key={service.id} className="service-tag">
                                  {service.name}
                                </span>
                              ))
                            : worker.services.map((service) => (
                                <span key={service} className="service-tag">
                                  {service}
                                </span>
                              ))}
                        </div>
                      )}
                      <p className="worker-phone">📞 {worker.phone}</p>
                      <button
                        className="contact-btn"
                        onClick={() => navigate(`/worker/${worker.id}`)}
                      >
                        Ver Detalhes
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>
        )}

        {activeTab === 'profile' && (
          <section className="profile-section">
            <div className="profile-card">
              <h2>Meu Perfil</h2>
              {user && (
                <div className="profile-info">
                  <div className="profile-field">
                    <label>Username:</label>
                    <p>{user.username}</p>
                  </div>
                  <div className="profile-field">
                    <label>Email:</label>
                    <p>{user.email}</p>
                  </div>
                  <div className="profile-field">
                    <label>Cidade:</label>
                    <p>{user.city}</p>
                  </div>
                  <div className="profile-field">
                    <label>Estado:</label>
                    <p>{user.state}</p>
                  </div>
                  <div className="profile-actions">
                    <button
                      className="edit-btn"
                      onClick={() => navigate('/profile/edit')}
                    >
                      ✏️ Editar Perfil
                    </button>
                    <button
                      className="create-worker-btn"
                      onClick={() => navigate('/worker/create')}
                    >
                      ➕ Criar Perfil de Trabalhador
                    </button>
                  </div>
                </div>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
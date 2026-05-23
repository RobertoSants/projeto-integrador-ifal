import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { workersAPI, servicesAPI } from '../services/api';
import '../styles/WorkerForm.css';

const WorkerForm = () => {
  const navigate = useNavigate();
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    bio: '',
    phone: '',
    city: '',
    state: '',
    photo: '',
    services: [],
  });

  useEffect(() => {
    const loadServices = async () => {
      try {
        const response = await servicesAPI.list();
        setServices(response.data);
      } catch (err) {
        console.error('Erro ao carregar serviços:', err);
      } finally {
        setLoading(false);
      }
    };
    loadServices();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleServiceToggle = (serviceId) => {
    setFormData((prev) => {
      const services = prev.services.includes(serviceId)
        ? prev.services.filter((id) => id !== serviceId)
        : [...prev.services, serviceId];
      return { ...prev, services };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.full_name || !formData.phone || !formData.city || !formData.state) {
      alert('Por favor, preencha todos os campos obrigatórios');
      return;
    }
    if (formData.services.length === 0) {
      alert('Selecione pelo menos um serviço');
      return;
    }

    setSubmitting(true);
    try {
      await workersAPI.create(formData);
      alert('Perfil de trabalhador criado com sucesso!');
      navigate('/dashboard');
    } catch (err) {
      console.error('Erro ao criar perfil:', err);
      alert('Erro ao criar perfil de trabalhador');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="worker-form-container">
      <div className="form-wrapper">
        <button className="back-btn" onClick={() => navigate('/dashboard')}>
          ← Voltar
        </button>
        <h1>Criar Perfil de Trabalhador</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h2>Informações Pessoais</h2>
            <div className="form-group">
              <label>Nome Completo *</label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Bio / Descrição</label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                placeholder="Conte um pouco sobre sua experiência..."
                rows="4"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Telefone/WhatsApp *</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="82999990000"
                  required
                />
              </div>
              <div className="form-group">
                <label>URL da Foto</label>
                <input
                  type="url"
                  name="photo"
                  value={formData.photo}
                  onChange={handleChange}
                  placeholder="https://..."
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Localização</h2>
            <div className="form-row">
              <div className="form-group">
                <label>Cidade *</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  placeholder="Maceió"
                  required
                />
              </div>
              <div className="form-group">
                <label>Estado *</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  placeholder="AL"
                  maxLength="2"
                  required
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Serviços Oferecidos *</h2>
            <p className="info-text">Selecione os serviços que você oferece</p>
            <div className="services-grid">
              {services.map((service) => (
                <label key={service.id} className="service-checkbox">
                  <input
                    type="checkbox"
                    checked={formData.services.includes(service.id)}
                    onChange={() => handleServiceToggle(service.id)}
                  />
                  <span className="service-name">{service.name}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="submit-btn"
          >
            {submitting ? 'Criando...' : 'Criar Perfil'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default WorkerForm;
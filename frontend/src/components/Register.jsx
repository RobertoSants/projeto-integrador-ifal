import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const API_BASE = 'http://localhost:8000/api/';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    city: '',
    state: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: '',
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    if (formData.password !== formData.password_confirm) {
      setErrors({ password_confirm: 'Senhas não coincidem' });
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_BASE}accounts/register/`, formData);
      navigate('/login');
    } catch (err) {
      // Processar erros do backend
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Se é um dicionário de erros por campo
        if (typeof errorData === 'object' && !Array.isArray(errorData)) {
          const processedErrors = {};
          Object.keys(errorData).forEach(key => {
            const value = errorData[key];
            // Pega o primeiro erro se for um array, caso contrário usa o valor diretamente
            processedErrors[key] = Array.isArray(value) ? value[0] : value;
          });
          setErrors(processedErrors);
        } else {
          setErrors({ general: 'Erro no cadastro. Verifique os dados.' });
        }
      } else {
        setErrors({ general: 'Erro no cadastro. Verifique sua conexão.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>📝 Criar Conta</h2>
        <form onSubmit={handleSubmit}>
          {errors.general && <p className="error-message">{errors.general}</p>}
          
          <div className="form-group">
            <label>Username:</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
              style={errors.username ? { borderColor: '#dc3545' } : {}}
            />
            {errors.username && <span className="field-error">{errors.username}</span>}
          </div>
          
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
              style={errors.email ? { borderColor: '#dc3545' } : {}}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>
          
          <div className="form-group">
            <label>Senha:</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              style={errors.password ? { borderColor: '#dc3545' } : {}}
            />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>
          
          <div className="form-group">
            <label>Confirmar Senha:</label>
            <input
              type="password"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              required
              disabled={loading}
              style={errors.password_confirm ? { borderColor: '#dc3545' } : {}}
            />
            {errors.password_confirm && <span className="field-error">{errors.password_confirm}</span>}
          </div>
          
          <div className="form-group">
            <label>Cidade:</label>
            <input
              type="text"
              name="city"
              value={formData.city}
              onChange={handleChange}
              required
              disabled={loading}
              style={errors.city ? { borderColor: '#dc3545' } : {}}
            />
            {errors.city && <span className="field-error">{errors.city}</span>}
          </div>
          
          <div className="form-group">
            <label>Estado (ex: AL):</label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleChange}
              required
              disabled={loading}
              maxLength="2"
              style={errors.state ? { borderColor: '#dc3545' } : {}}
            />
            {errors.state && <span className="field-error">{errors.state}</span>}
          </div>
          
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Criando conta...' : 'Registrar'}
          </button>
        </form>
        <p className="auth-link">
          Já tem conta? <a href="/login">Faça login aqui</a>
        </p>
      </div>
    </div>
  );
};

export default Register;
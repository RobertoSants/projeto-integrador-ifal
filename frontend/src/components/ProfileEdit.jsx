import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { accountsAPI } from '../services/api';
import '../styles/ProfileEdit.css';

const ProfileEdit = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState('profile');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    city: '',
    state: '',
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const loadUserData = async () => {
      try {
        const response = await accountsAPI.getMe();
        setFormData(response.data);
      } catch (err) {
        console.error('Erro ao carregar perfil:', err);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    loadUserData();
  }, [navigate]);

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setError('');
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData({ ...passwordData, [name]: value });
    setError('');
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await accountsAPI.updateMe(formData);
      setSuccess('Perfil atualizado com sucesso!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Erro ao atualizar perfil');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.new_password_confirm) {
      setError('As novas senhas não coincidem');
      return;
    }
    if (passwordData.new_password.length < 6) {
      setError('A nova senha deve ter pelo menos 6 caracteres');
      return;
    }

    setSaving(true);
    try {
      await accountsAPI.changePassword({
        old_password: passwordData.old_password,
        new_password: passwordData.new_password,
      });
      setSuccess('Senha alterada com sucesso!');
      setPasswordData({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      });
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Erro ao alterar senha. Verifique sua senha atual.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="profile-edit-container">
      <div className="edit-wrapper">
        <button className="back-btn" onClick={() => navigate('/dashboard')}>
          ← Voltar
        </button>
        <h1>Editar Perfil</h1>

        <div className="tabs">
          <button
            className={`tab ${tab === 'profile' ? 'active' : ''}`}
            onClick={() => setTab('profile')}
          >
            📝 Perfil
          </button>
          <button
            className={`tab ${tab === 'password' ? 'active' : ''}`}
            onClick={() => setTab('password')}
          >
            🔐 Senha
          </button>
        </div>

        {tab === 'profile' && (
          <form onSubmit={handleProfileSubmit} className="form">
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                disabled
              />
              <small>Username não pode ser alterado</small>
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleProfileChange}
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Cidade</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleProfileChange}
                />
              </div>
              <div className="form-group">
                <label>Estado</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleProfileChange}
                  maxLength="2"
                />
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <button type="submit" disabled={saving} className="submit-btn">
              {saving ? 'Salvando...' : 'Salvar Alterações'}
            </button>
          </form>
        )}

        {tab === 'password' && (
          <form onSubmit={handlePasswordSubmit} className="form">
            <div className="form-group">
              <label>Senha Atual *</label>
              <input
                type="password"
                name="old_password"
                value={passwordData.old_password}
                onChange={handlePasswordChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Nova Senha *</label>
              <input
                type="password"
                name="new_password"
                value={passwordData.new_password}
                onChange={handlePasswordChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Confirmar Nova Senha *</label>
              <input
                type="password"
                name="new_password_confirm"
                value={passwordData.new_password_confirm}
                onChange={handlePasswordChange}
                required
              />
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <button type="submit" disabled={saving} className="submit-btn">
              {saving ? 'Alterando...' : 'Alterar Senha'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default ProfileEdit;
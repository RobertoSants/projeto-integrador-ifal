import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import WorkerDetail from './components/WorkerDetail';
import WorkerForm from './components/WorkerForm';
import ProfileEdit from './components/ProfileEdit';
import './App.css';

function Home() {
  return (
    <div>
      <h1>Bem-vindo ao Banco de Talentos Comunitário</h1>
      <p>Plataforma para conectar contratantes e trabalhadores locais.</p>
      <nav>
        <Link to="/login">Login</Link> | <Link to="/register">Registrar</Link>
      </nav>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/worker/create"
            element={
              <ProtectedRoute>
                <WorkerForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/worker/:id"
            element={
              <ProtectedRoute>
                <WorkerDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile/edit"
            element={
              <ProtectedRoute>
                <ProfileEdit />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workersAPI, reviewsAPI } from '../services/api';
import '../styles/WorkerDetail.css';

const WorkerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [worker, setWorker] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newReview, setNewReview] = useState({ rating: 5, comment: '' });
  const [submitting, setSubmitting] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);

  useEffect(() => {
    const loadWorkerDetails = async () => {
      try {
        const [workerRes, reviewsRes] = await Promise.all([
          workersAPI.get(id),
          workersAPI.getReviews(id),
        ]);
        setWorker(workerRes.data);
        setReviews(reviewsRes.data);
      } catch (err) {
        console.error('Erro ao carregar detalhes:', err);
      } finally {
        setLoading(false);
      }
    };
    loadWorkerDetails();
  }, [id]);

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await reviewsAPI.create({
        worker: id,
        rating: parseInt(newReview.rating),
        comment: newReview.comment,
      });
      setNewReview({ rating: 5, comment: '' });
      setShowReviewForm(false);
      // Reload reviews
      const reviewsRes = await workersAPI.getReviews(id);
      setReviews(reviewsRes.data);
    } catch (err) {
      console.error('Erro ao criar avaliação:', err);
      alert('Erro ao enviar avaliação');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  if (!worker) {
    return (
      <div className="error-container">
        <p>Trabalhador não encontrado</p>
        <button onClick={() => navigate('/dashboard')}>Voltar</button>
      </div>
    );
  }

  return (
    <div className="worker-detail">
      <button className="back-btn" onClick={() => navigate('/dashboard')}>
        ← Voltar
      </button>

      <div className="detail-container">
        <div className="worker-header">
          {worker.photo && <img src={worker.photo} alt={worker.full_name} />}
          <div className="worker-header-info">
            <h1>{worker.full_name}</h1>
            <p className="bio">{worker.bio}</p>
            <div className="header-stats">
              <span className="rating">⭐ {worker.avg_rating ? worker.avg_rating.toFixed(1) : 'N/A'}</span>
              <span className="location">📍 {worker.city}, {worker.state}</span>
              <span className="phone">📞 {worker.phone}</span>
            </div>
          </div>
        </div>

        <div className="services-section">
          <h2>Serviços Oferecidos</h2>
          <div className="services-tags">
            {Array.isArray(worker.services) &&
              worker.services.map((service) => (
                <span key={service.id || service} className="service-badge">
                  {service.name || service}
                </span>
              ))}
          </div>
        </div>

        <div className="reviews-section">
          <div className="reviews-header">
            <h2>Avaliações ({reviews.length})</h2>
            <button
              className="review-btn"
              onClick={() => setShowReviewForm(!showReviewForm)}
            >
              {showReviewForm ? '✕ Cancelar' : '+ Deixar Avaliação'}
            </button>
          </div>

          {showReviewForm && (
            <form className="review-form" onSubmit={handleSubmitReview}>
              <div className="form-group">
                <label>Nota:</label>
                <select
                  value={newReview.rating}
                  onChange={(e) =>
                    setNewReview({ ...newReview, rating: e.target.value })
                  }
                  required
                >
                  <option value="5">⭐⭐⭐⭐⭐ Excelente</option>
                  <option value="4">⭐⭐⭐⭐ Muito Bom</option>
                  <option value="3">⭐⭐⭐ Bom</option>
                  <option value="2">⭐⭐ Satisfatório</option>
                  <option value="1">⭐ Insatisfatório</option>
                </select>
              </div>
              <div className="form-group">
                <label>Comentário:</label>
                <textarea
                  value={newReview.comment}
                  onChange={(e) =>
                    setNewReview({ ...newReview, comment: e.target.value })
                  }
                  placeholder="Compartilhe sua experiência..."
                  rows="4"
                />
              </div>
              <button type="submit" disabled={submitting} className="submit-btn">
                {submitting ? 'Enviando...' : 'Enviar Avaliação'}
              </button>
            </form>
          )}

          <div className="reviews-list">
            {reviews.length === 0 ? (
              <p className="no-reviews">Nenhuma avaliação ainda</p>
            ) : (
              reviews.map((review) => (
                <div key={review.id} className="review-card">
                  <div className="review-header">
                    <span className="rating">
                      {'⭐'.repeat(review.rating)}
                    </span>
                    <span className="date">
                      {new Date(review.created_at).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                  <p className="review-text">{review.comment}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkerDetail;
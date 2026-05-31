/* ==========================================================================
   LÓGICA ASSÍNCRONA E PROCESSAMENTO DE DEPOIMENTOS — DETALHES
   ========================================================================== */

const urlParams = new URLSearchParams(window.location.search);
const workerId = urlParams.get('id');
const profileContent = document.getElementById('profile-content');
const commentsList = document.getElementById('comments-list');

const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

function formatAuthorName(fullName, username) {
    if (!fullName && !username) return "Visitante Anônimo";
    const nameToFormat = fullName ? fullName.trim() : `@${username.trim()}`;
    const parts = nameToFormat.split(" ");
    if (parts.length <= 2) return nameToFormat;
    const filteredParts = parts.filter(p => p.toLowerCase() !== "dos" && p.toLowerCase() !== "da" && p.toLowerCase() !== "de");
    return `${filteredParts[0]} ${filteredParts[1].charAt(0)}.`;
}

async function loadProfile() {
    try {
        const response = await fetch(`http://localhost:8000/api/workers/${workerId}/`, { method: "GET", credentials: "omit" });
        if (!response.ok) throw new Error("Erro ao buscar perfil.");
        
        const w = await response.json();
        const defaultImg = "https://i1-c.pinimg.com/1200x/a8/da/22/a8da222be70a71e7858bf752065d5cc3.jpg";
        const setores = w.services ? w.services.map(s => s.name || s).join(', ') : 'Autônomo';

        const ratingTxt = w.avg_rating !== null && w.avg_rating !== undefined 
            ? parseFloat(w.avg_rating).toFixed(2) 
            : '5.00';

        profileContent.innerHTML = `
            <div class="profile-pic" style="background-image: url('${w.photo_url ? w.photo_url : defaultImg}')"></div>
            <div class="profile-info">
                <span class="card-local" style="position:static; display:inline-block; margin-bottom:10px;">📍 MUNICÍPIO: ${w.city.toUpperCase()}</span>
                <h1 style="margin: 0 0 10px 0; color: var(--cor-al-blue-primary);">${w.full_name}</h1>
                <p style="font-size:16px; color:#444; margin-bottom:15px;"><strong>Eixo de Atuação:</strong> ${setores}</p>
                <p style="font-size:18px; color:var(--cor-al-red-primary); margin-bottom:20px;"><strong>Reputação:</strong> ⭐ ${ratingTxt}</p>
                <div style="border-top:1px solid #eee; padding-top:15px; margin-bottom:25px;">
                    <h3>Apresentação Profissional:</h3>
                    <p style="line-height:1.6; color:#555;">${w.bio || 'Nenhuma biografia informada.'}</p>
                </div>
                <a href="https://wa.me/${w.phone}" target="_blank" class="btn-cta btn-whatsapp" style="display:inline-block; text-align:center; box-shadow:none;">CONTACTAR VIA WHATSAPP</a>
            </div>
        `;
        
        loadReviews();
    } catch (err) {
        profileContent.innerHTML = "<p>Erro ao carregar o perfil profissional.</p>";
    }
}

async function loadReviews() {
    try {
        const res = await fetch(`http://localhost:8000/api/workers/${workerId}/reviews/`, { method: "GET", credentials: "omit" });
        if (res.ok) {
            const reviews = await res.json();
            if(reviews.length > 0) {
                commentsList.innerHTML = reviews.map(r => {
                    const nameDisplay = formatAuthorName(r.author_fullname, r.author_username);
                    const dateDisplay = new Date(r.created_at).toLocaleDateString('pt-BR');

                    return `
                        <div class="comment-item">
                            <div class="comment-header">
                                <span class="comment-author">👤 ${nameDisplay} <span class="comment-date">em ${dateDisplay}</span></span>
                                <div style="color:var(--cor-al-red-primary); font-weight:bold;">Nota: ${'⭐'.repeat(r.rating)}</div>
                            </div>
                            <p style="color:#555; margin:0; padding-left: 5px;">"${r.comment}"</p>
                        </div>
                    `;
                }).join('');
            } else {
                commentsList.innerHTML = `<p style="color:#666;">Nenhum comentário registrado ainda.</p>`;
            }
        }
    } catch (e) { console.error("Erro ao listar depoimentos", e); }
}

document.getElementById('review-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ratingValue = document.getElementById('review-rating').value;
    const commentValue = document.getElementById('review-comment').value;

    try {
        const res = await fetch(`http://localhost:8000/api/workers/${workerId}/reviews/`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rating: parseInt(ratingValue), comment: commentValue })
        });

        if (res.ok) {
            alert("Avaliação e depoimento publicados!");
            document.getElementById('review-comment').value = "";
            loadProfile();
        } else {
            alert("Erro ao salvar avaliação. Certifique-se de preencher os campos corretamente.");
        }
    } catch (err) { alert("Erro de rede ao submeter comentário."); }
});

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('open');
        navMenu.classList.toggle('active');
    });
}

document.querySelectorAll('#nav-menu a').forEach(link => {
    link.addEventListener('click', function() {
        if(hamburger) hamburger.classList.remove('open');
        navMenu.classList.remove('active');
        
        document.querySelectorAll('#nav-menu a').forEach(item => item.classList.remove('active-link'));
        this.classList.add('active-link');
    });
});

const currentPath = window.location.pathname;
if(currentPath.includes("perfil.html")) {
    document.getElementById("menu-perfil").classList.add("active-link");
}

loadProfile();

// ADIÇÃO EXCLUSIVA E TOTALMENTE INTEGRADA: Lógica Smart Header Retrátil
let lastScrollTop = 0;
const headerElement = document.querySelector("header");

window.addEventListener("scroll", () => {
    let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    const isMobileMenuOpen = document.getElementById("hamburger")?.classList.contains("open");

    if (isMobileMenuOpen) {
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
        return;
    }

    if (currentScroll > lastScrollTop && currentScroll > 80) {
        headerElement.classList.add("header-hidden");
    } else {
        headerElement.classList.remove("header-hidden");
    }
    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
});
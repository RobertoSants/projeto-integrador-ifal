/* ==========================================================================
   LÓGICA ASSÍNCRONA E CONTROLE DE COMPONENTES — HOME (INDEX)
   ========================================================================== */

const container = document.getElementById("talents-container");
const capitalContainer = document.getElementById("capital-container");
const capitalDynamicWrapper = document.getElementById("capital");
const countTxt = document.getElementById("results-count");
const capitalCountTxt = document.getElementById("capital-count");
let activeCategory = null;

async function loadCities() {
    try {
        const response = await fetch("https://servicodados.ibge.gov.br/api/v1/localidades/estados/AL/municipios?ordenar=nome");
        const cities = await response.json();
        const select = document.getElementById("city-select");
        cities.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.nome;
            opt.innerText = c.nome;
            select.appendChild(opt);
        });
    } catch (e) { console.error("Erro ao carregar municípios da API do IBGE", e); }
}

async function checkSession() {
    try {
        const response = await fetch("http://localhost:8000/api/auth/refresh/", { method: "POST", credentials: "include" });
        
        // CORREÇÃO DO BUG DO REFRESH ANÔNIMO (ISSUE #11)
        // Só exibe o menu de logout se o status for estritamente 200 (Sessão válida)
        if (response.status === 200) {
            document.getElementById("menu-logout").classList.remove("hidden");
            document.getElementById("menu-cadastrar").classList.add("hidden");
        } else {
            // Se for 204 ou qualquer outro status anônimo, garante que os botões voltem ao estado inicial
            document.getElementById("menu-logout").classList.add("hidden");
            document.getElementById("menu-cadastrar").classList.remove("hidden");
        }
    } catch (e) { console.log("Usuário navegando de forma anônima."); }
}

document.getElementById("menu-logout").addEventListener("click", async (e) => {
    e.preventDefault();
    try {
        const res = await fetch("http://localhost:8000/api/auth/logout/", { method: "POST", credentials: "include" });
        if (res.ok) {
            alert("Sessão encerrada com sucesso.");
            window.location.reload();
        }
    } catch (err) { alert("Erro ao tentar deslogar do servidor."); }
});

const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    navMenu.classList.toggle('active');
});

document.querySelectorAll('#nav-menu a').forEach(link => {
    link.addEventListener('click', function() {
        hamburger.classList.remove('open');
        navMenu.classList.remove('active');
        
        document.querySelectorAll('#nav-menu a').forEach(item => item.classList.remove('active-link'));
        this.classList.add('active-link');
    });
});

async function fetchWorkers() {
    const query = document.getElementById("search-input").value.trim();
    const city = document.getElementById("city-select").value;
    
    let params = [];
    if (query) params.push(`q=${encodeURIComponent(query)}`);
    if (city) {
        params.push(`city=${encodeURIComponent(city)}`);
        params.push(`contratante_city=${encodeURIComponent(city)}`);
    }
    if (activeCategory) params.push(`service=${activeCategory}`);

    const queryString = params.length > 0 ? `?${params.join('&')}` : '';
    const finalUrl = `http://localhost:8000/api/search/${queryString}`;

    try {
        const response = await fetch(finalUrl, { method: "GET", credentials: "include" });
        if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
        
        const data = await response.json();
        const workersList = data.results || [];
        
        if (city) {
            capitalDynamicWrapper.classList.add("hidden");
            renderGroup(workersList, container, countTxt, `profissionais encontrados em ${city.toUpperCase()}`, city);
        } else {
            capitalDynamicWrapper.classList.remove("hidden");
            const localWorkers = workersList.filter(w => w.is_local === true || w.is_local === "true");
            const otherWorkers = workersList.filter(w => w.is_local !== true && w.is_local !== "true");
            
            renderGroup(localWorkers, container, countTxt, "talentos da sua região encontrados", city);
            renderGroup(otherWorkers, capitalContainer, capitalCountTxt, "outros profissionais disponíveis no estado", city);
        }
    } catch (error) {
        console.error("Detalhes do erro de conexão:", error);
        countTxt.innerText = "Erro ao conectar com o servidor backend.";
    }
}

function renderGroup(workers, targetContainer, textElement, message, currentCity) {
    targetContainer.innerHTML = "";
    textElement.innerText = `${workers.length} ${message}`;
    
    if(!workers || workers.length === 0) {
        targetContainer.innerHTML = "<p style='grid-column: 1/-1; color: #666; text-align: center;'>Nenhum trabalhador cadastrado nesta seção.</p>";
        return;
    }

    workers.forEach(w => {
        const defaultImg = "https://i1-c.pinimg.com/1200x/a8/da/22/a8da222be70a71e7858bf752065d5cc3.jpg";
        const card = document.createElement("div");
        card.className = "card";
        
        const setorTxt = Array.isArray(w.services) ? w.services.join(', ') : 'Autônomo';
        const localizacaoTxt = w.city ? w.city.toUpperCase() : 'AL';
        
        const isLocal = w.is_local === true || w.is_local === "true";
        const badgeStyle = isLocal ? `style="background-color: var(--cor-al-red-primary);"` : '';
        const badgeText = isLocal ? '📍 TALENTO LOCAL' : `📍 ${localizacaoTxt}`;
        
        const photoSrc = w.photo_url ? w.photo_url : defaultImg;
        const ratingTxt = w.avg_rating !== null && w.avg_rating !== undefined 
            ? parseFloat(w.avg_rating).toFixed(2) 
            : '5.00';
        
        card.innerHTML = `
            <div class="card-local" ${badgeStyle}>${badgeText}</div>
            <div class="card-img" style="background-image: url('${photoSrc}')"></div>
            <div class="card-body">
                <h3>${w.full_name || 'Profissional Autônomo'}</h3>
                <p><strong>${setorTxt}</strong></p>
                <p class="rating">⭐⭐⭐⭐⭐ ${ratingTxt}</p>
                <a href="https://wa.me/${w.phone}" target="_blank" class="btn-cta btn-whatsapp" style="padding:10px; font-size:12px; text-align:center; display:block; margin-top:15px; box-shadow:none;" onclick="event.stopPropagation();">CONTACTAR VIA WHATSAPP</a>
            </div>
        `;
        
        card.addEventListener('click', () => {
            window.location.href = `detalhes.html?id=${w.id}`;
        });
        
        targetContainer.appendChild(card);
    });
}

document.getElementById("search-button").addEventListener("click", fetchWorkers);

document.getElementById("reset-button").addEventListener("click", () => {
    document.getElementById("search-input").value = "";
    document.getElementById("city-select").value = "";
    activeCategory = null;
    document.querySelectorAll(".sector-card").forEach(c => c.classList.remove("active"));
    document.querySelectorAll('#nav-menu a').forEach(item => item.classList.remove('active-link'));
    fetchWorkers();
});

document.querySelectorAll(".sector-card").forEach(card => {
    card.addEventListener("click", function() {
        const id = this.getAttribute("data-service-id");
        if (activeCategory === id) {
            activeCategory = null;
            this.classList.remove("active");
        } else {
            document.querySelectorAll(".sector-card").forEach(c => c.classList.remove("active"));
            activeCategory = id;
            this.classList.add("active");
        }
        fetchWorkers();
    });
});

loadCities();
checkSession();
fetchWorkers();

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
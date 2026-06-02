/* ==========================================================================
   LÓGICA ASSÍNCRONA E GERENCIAMENTO DE CADASTRO MULTIFÁSICO — CADASTRO
   ========================================================================== */

let isAlreadyLogged = false;
let finalBio = "";
let base64Photo = ""; // Armazena a string Base64 da foto processada

const btnOptimize = document.getElementById('btn-optimize');
const rawBio = document.getElementById('raw-bio');
const aiPreview = document.getElementById('ai-preview');

const step1 = document.getElementById('step-1');
const step2 = document.getElementById('step-2');
const btnNextStep = document.getElementById('btn-next-step');
const btnPrevStep = document.getElementById('btn-prev-step');
const btnSubmitContractor = document.getElementById('btn-submit-contractor');

const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

document.getElementById("phone").addEventListener("input", function(e) {
    let x = e.target.value.replace(/\D/g, "").match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
    e.target.value = !x[2] ? x[1] : "(" + x[1] + ") " + x[2] + (x[3] ? "-" + x[3] : "");
});

// Listener exclusivo para escutar o upload, validar tamanho (1.5MB) e converter para Base64
document.getElementById("photo")?.addEventListener("change", function(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validação estrita de tamanho: 1.5 MB = 1572864 bytes
    if (file.size > 1572864) {
        alert("⚠️ Arquivo muito pesado! Selecione uma foto de perfil menor com no máximo 1.5 MB.");
        e.target.value = "";
        base64Photo = "";
        return;
    }

    const reader = new FileReader();
    reader.onloadend = function() {
        base64Photo = reader.result; // Salva a string Base64 completa pronta para o banco
    };
    reader.readAsDataURL(file);
});

async function loadCities() {
    try {
        const response = await fetch("https://servicodados.ibge.gov.br/api/v1/localidades/estados/AL/municipios?ordenar=nome");
        const cities = await response.json();
        const select = document.getElementById("city");
        cities.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.nome;
            opt.innerText = c.nome;
            select.appendChild(opt);
        });
    } catch (e) { console.error("Erro ao carregar municípios", e); }
}

async function checkInitialSession() {
    try {
        const res = await fetch("https://banco-talentos-api.onrender.com/api/accounts/me/", { method: "GET", credentials: "include" });
        if (res.ok) {
            isAlreadyLogged = true;
            document.getElementById("cadastro-title").innerText = "Complete seu Perfil";
            document.getElementById("cadastro-subtitle").innerText = "Sua conta já está conectada. Preencha seus dados de anúncio profissional abaixo.";
            step1.style.display = "none";
            step2.style.display = "block";
            btnPrevStep.style.display = "none";
            toggleRequiredFields(true);
        } else {
            document.getElementById("username").required = true;
            document.getElementById("email").required = true;
            document.getElementById("password").required = true;
            document.getElementById("consentimento").required = true;
        }
    } catch (e) { console.log("Usuário anônimo."); }
}

function toggleRequiredFields(required) {
    document.getElementById("name").required = required;
    document.getElementById("birth_date").required = required;
    document.getElementById("phone").required = required;
    document.getElementById("city").required = required;
    document.getElementById("service").required = required;
    document.getElementById("raw-bio").required = required;
}

document.querySelectorAll('input[name="user-role"]').forEach(radio => {
    radio.addEventListener('change', function() {
        if (this.value === 'contractor') {
            btnNextStep.classList.add('hidden');
            btnSubmitContractor.classList.remove('hidden');
        } else {
            btnNextStep.classList.remove('hidden');
            btnSubmitContractor.classList.add('hidden');
        }
    });
});

if(document.getElementById('role-contractor') && document.getElementById('role-contractor').checked) {
    btnNextStep.classList.add('hidden');
    btnSubmitContractor.classList.remove('hidden');
}

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('open');
        navMenu.classList.toggle('active');
    });
}

function calculateAge(birthDateString) {
    if (!birthDateString) return 0;
    const today = new Date();
    const birthDate = new Date(birthDateString);
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    return age;
}

function validateStep1() {
    const userVal = document.getElementById("username").value.trim();
    const emailVal = document.getElementById("email").value.trim();
    const passVal = document.getElementById("password").value;

    if (!userVal || !emailVal || !passVal) {
        alert("Por favor, preencha todos os campos da conta de acesso.");
        return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailVal)) {
        alert("Por favor, insira um endereço de e-mail válido.");
        document.getElementById("email").focus();
        return false;
    }
    if (passVal.length < 8 || !/[A-Za-z]/.test(passVal) || !/[0-9]/.test(passVal)) {
        alert("Sua senha está fraca. Crie uma senha com no mínimo 8 caracteres contendo letras e números.");
        return false;
    }
    if (!document.getElementById("consentimento").checked) {
        alert("É obrigatório autorizar o consentimento LGPD para continuar.");
        return false;
    }
    return true;
}

async function submitAccountOnly() {
    if (!validateStep1()) return;
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const consentimento = document.getElementById("consentimento").checked;

    try {
        const regRes = await fetch("https://banco-talentos-api.onrender.com/api/accounts/register/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password, password_confirm: password, city: "Maceió", state: "AL", consentimento })
        });
        if (!regRes.ok) { 
            const errData = await regRes.json();
            alert(`Erro no registro: ${errData.email || errData.username || "Dados inválidos."}`); 
            return; 
        }
        const loginRes = await fetch("https://banco-talentos-api.onrender.com/api/auth/login/", {
            method: "POST", credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        if (loginRes.ok) {
            alert("Sua conta de Contratante foi criada com sucesso!");
            window.location.assign("index.html");
        }
    } catch (err) { alert("Erro de rede com o servidor."); }
}

btnSubmitContractor.addEventListener('click', submitAccountOnly);

btnNextStep.addEventListener('click', () => {
    if (!validateStep1()) return;
    toggleRequiredFields(true);
    step1.style.display = "none";
    step2.style.display = "block";
});

btnPrevStep.addEventListener('click', () => {
    toggleRequiredFields(false);
    step2.style.display = "none";
    step1.style.display = "block";
});

btnOptimize.addEventListener('click', async () => {
    const rawBioVal = rawBio.value.trim();
    const nameVal = document.getElementById("name").value.trim();
    const birthVal = document.getElementById("birth_date").value;
    
    if (!rawBioVal) return;
    if (!nameVal || !birthVal) {
        alert("Por favor, preencha o seu Nome Completo e sua Data de Nascimento para que a IA monte sua apresentação.");
        return;
    }

    const calculatedAge = calculateAge(birthVal);
    if (calculatedAge < 18) {
        alert("É obrigatório ter mais de 18 anos de idade para se cadastrar.");
        return;
    }

    btnOptimize.innerText = 'Processando...';
    try {
        const response = await fetch("https://banco-talentos-api.onrender.com/api/workers/optimize-bio/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bio: rawBioVal, name: nameVal, age: calculatedAge })
        });
        const data = await response.json();
        finalBio = data.optimized_bio;
        
        document.getElementById("raw-bio").value = finalBio;
        
        aiPreview.innerHTML = `<strong>✨ Biografia Otimizada:</strong><br>${finalBio}`;
        aiPreview.style.display = 'block';
        btnOptimize.innerText = 'Texto Otimizado!';
    } catch (e) { btnOptimize.innerText = 'Erro na IA'; }
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const city = document.getElementById("city").value;
    const full_name = document.getElementById("name").value.trim();
    const birth_date = document.getElementById("birth_date").value;
    const phone = document.getElementById("phone").value.trim();
    const service = document.getElementById("service").value;
    const bioText = finalBio || rawBio.value.trim();

    if (!full_name || !birth_date || !phone || !city || !service || !bioText) {
        alert("Por favor, preencha todos os campos obrigatórios do perfil profissional.");
        return;
    }

    if (calculateAge(birth_date) < 18) {
        alert("É obrigatório ser maior de 18 anos.");
        return;
    }

    try {
        if (!isAlreadyLogged) {
            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            const regRes = await fetch("https://banco-talentos-api.onrender.com/api/accounts/register/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password, password_confirm: password, city, state: "AL", consentimento: true, first_name: full_name })
            });
            if (!regRes.ok) {
                alert("Erro ao criar conta de acesso.");
                return;
            }
            await fetch("https://banco-talentos-api.onrender.com/api/auth/login/", {
                method: "POST", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
        }

        // Envio estruturado via JSON contendo a string de texto Base64 da foto
        const payload = {
            full_name: full_name,
            birth_date: birth_date,
            phone: phone.replace(/\D/g, ""),
            city: city,
            state: "AL",
            bio: bioText,
            services: [parseInt(service)],
            photo: base64Photo // String de texto gravada no banco
        };

        const workerRes = await fetch("https://banco-talentos-api.onrender.com/api/workers/", { 
            method: "POST", 
            credentials: "include", 
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload) 
        });
        
        if (workerRes.ok) {
            alert("Perfil profissional publicado com sucesso! Redirecionando...");
            window.location.assign("index.html");
        } else {
            const errDetail = await workerRes.json();
            alert(`Erro ao registrar os dados profissionais: ${JSON.stringify(errDetail)}`);
        }
    } catch (err) { alert("Erro de rede com o servidor."); }
});

loadCities().then(() => checkInitialSession());

let lastScrollTop = 0;
const headerElement = document.querySelector("header");
window.addEventListener("scroll", () => {
    let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    if (document.getElementById("hamburger")?.classList.contains("open")) return;
    if (currentScroll > lastScrollTop && currentScroll > 80) headerElement.classList.add("header-hidden");
    else headerElement.classList.remove("header-hidden");
    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
});
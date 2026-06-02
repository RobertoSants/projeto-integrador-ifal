/* ==========================================================================
   LÓGICA DO PAINEL DO USUÁRIO - MÓDULO PERFIL — VERSÃO BLINDADA CONTRA CRASH
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    let currentProfileId = null;
    let finalBio = "";
    let isWorker = false; // Controla se é atualização (PUT) ou criação (POST)
    
    const loginGate = document.getElementById("login-gate");
    const mainPanel = document.getElementById("main-panel");
    const logoutNav = document.getElementById("panel-logout");
    const workerSection = document.getElementById("worker-data-section");
    const subtitleTxt = document.getElementById("panel-subtitle");
    const workerTitleElement = document.getElementById("worker-section-title");
    const groupEditService = document.getElementById("group-edit-service");
    const btnSaveWorker = document.getElementById("btn-save");

    document.getElementById("edit-phone")?.addEventListener("input", function(e) {
        let x = e.target.value.replace(/\D/g, "").match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
        e.target.value = !x[2] ? x[1] : "(" + x[1] + ") " + x[2] + (x[3] ? "-" + x[3] : "");
    });

    function calculateAge(birthDateString) {
        if (!birthDateString) return 0;
        const today = new Date();
        const birthDate = new Date(birthDateString);
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) age--;
        return age;
    }

    async function loadCities() {
        try {
            const response = await fetch("https://servicodados.ibge.gov.br/api/v1/localidades/estados/AL/municipios?ordenar=nome");
            const cities = await response.json();
            const selects = [document.getElementById("edit-worker-city"), document.getElementById("edit-account-city")];
            selects.forEach(sel => {
                if (!sel) return;
                sel.innerHTML = '<option value="" disabled selected>Escolha sua cidade...</option>';
                cities.forEach(c => {
                    const opt = document.createElement("option");
                    opt.value = c.nome; opt.innerText = c.nome;
                    sel.appendChild(opt);
                });
            });
        } catch (e) { console.error("Erro ao carregar municípios", e); }
    }

    async function fetchMyProfile() {
        try {
            const accountResponse = await fetch("https://banco-talentos-api.onrender.com/api/accounts/me/", { method: "GET", credentials: "include" });
            if (!accountResponse.ok) { showLoginGate(); return; }
            
            const userData = await accountResponse.json();
            
            // OPERADORES DE CHECAGEM SEGURA (?): Evitam o crash se o elemento sumir do HTML
            if (document.getElementById("edit-email")) document.getElementById("edit-email").value = userData.email || ""; 
            if (document.getElementById("edit-username")) document.getElementById("edit-username").value = userData.username || ""; 
            if (document.getElementById("edit-account-city")) document.getElementById("edit-account-city").value = userData.city || "";
            if (document.getElementById("edit-first-name")) document.getElementById("edit-first-name").value = userData.first_name || "";

            const response = await fetch("https://banco-talentos-api.onrender.com/api/workers/me/", { method: "GET", credentials: "include" });
            
            if (response.status === 404) {
                isWorker = false;
                if (subtitleTxt) subtitleTxt.innerText = "Sua conta de Contratante está ativa. Se desejar, ative seu perfil profissional abaixo para anunciar serviços.";
                if (workerSection) workerSection.classList.remove("hidden");
                if (workerTitleElement) workerTitleElement.innerText = "✨ Ativar Meu Perfil de Trabalhador";
                if (groupEditService) groupEditService.classList.remove("hidden"); 
                if (document.getElementById("edit-service")) document.getElementById("edit-service").required = true;
                if (btnSaveWorker) btnSaveWorker.innerText = "CONFIRMAR E ATIVAR PERFIL PROFISSIONAL";
            } else if (response.ok) {
                isWorker = true;
                if (subtitleTxt) subtitleTxt.innerText = "Atualize suas informações públicas ou altere seus parâmetros de acesso.";
                if (workerSection) workerSection.classList.remove("hidden");
                if (workerTitleElement) workerTitleElement.innerText = "Meus Dados Profissionais";
                if (groupEditService) groupEditService.classList.add("hidden"); 
                if (document.getElementById("edit-service")) document.getElementById("edit-service").required = false;
                if (btnSaveWorker) btnSaveWorker.innerText = "SALVAR DADOS PROFISSIONAIS";
                
                const myProfile = await response.json();
                currentProfileId = myProfile.id;
                if (document.getElementById("edit-name")) document.getElementById("edit-name").value = myProfile.full_name || "";
                if (document.getElementById("edit-birth-date")) document.getElementById("edit-birth-date").value = myProfile.birth_date || "";
                if (document.getElementById("edit-phone")) {
                    document.getElementById("edit-phone").value = myProfile.phone || "";
                    document.getElementById("edit-phone").dispatchEvent(new Event('input'));
                }
                if (document.getElementById("edit-worker-city")) document.getElementById("edit-worker-city").value = myProfile.city || "";
                if (document.getElementById("edit-bio")) document.getElementById("edit-bio").value = myProfile.bio || "";
            }
            
            if (loginGate) loginGate.classList.add("hidden");
            if (mainPanel) mainPanel.classList.remove("hidden");
            if (logoutNav) logoutNav.classList.remove("hidden");
        } catch(e) { 
            console.error("Erro ao carregar o painel:", e);
            showLoginGate(); 
        }
    }

    function showLoginGate() {
        if (mainPanel) mainPanel.classList.add("hidden");
        if (logoutNav) logoutNav.classList.add("hidden");
        if (loginGate) loginGate.classList.remove("hidden");
    }

    document.getElementById("btn-edit-optimize")?.addEventListener("click", async () => {
        const rawBioVal = document.getElementById("edit-bio")?.value.trim();
        const nameVal = document.getElementById("edit-name")?.value.trim();
        const birthVal = document.getElementById("edit-birth-date")?.value;
        const aiPreview = document.getElementById("edit-ai-preview");
        const btnAi = document.getElementById("btn-edit-optimize");

        if (!rawBioVal) return;
        if (!nameVal || !birthVal) {
            alert("Preencha o Nome e a Data de Nascimento para gerar a apresentação pessoal.");
            return;
        }

        const age = calculateAge(birthVal);
        if (age < 18) { alert("Menores de 18 anos não são permitidos."); return; }

        btnAi.innerText = "Processando...";
        try {
            const response = await fetch("https://banco-talentos-api.onrender.com/api/workers/optimize-bio/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ bio: rawBioVal, name: nameVal, age: age })
            });
            const data = await response.json();
            finalBio = data.optimized_bio;
            
            if (document.getElementById("edit-bio")) document.getElementById("edit-bio").value = finalBio;
            
            if (aiPreview) {
                aiPreview.innerHTML = `<strong>✨ Biografia Otimizada com Sucesso:</strong><br>${finalBio}`;
                aiPreview.style.display = "block";
            }
            btnAi.innerText = "Texto Otimizado!";
        } catch (e) { btnAi.innerText = "Erro na IA"; }
    });

    document.getElementById("gate-login-form")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("gate-username").value.trim();
        const password = document.getElementById("gate-password").value;
        try {
            const loginRes = await fetch("https://banco-talentos-api.onrender.com/api/auth/login/", {
                method: "POST", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            if (loginRes.ok) {
                setTimeout(fetchMyProfile, 200);
            } else {
                const errData = await loginRes.json();
                alert("Não foi possível entrar. Verifique seu usuário/senha ou limpe os cookies do navegador móvel.");
            }
        } catch(err) { 
            alert("Erro de comunicação com o servidor backend."); 
        }
    });

    logoutNav?.addEventListener("click", async (e) => {
        e.preventDefault();
        const res = await fetch("https://banco-talentos-api.onrender.com/api/auth/logout/", { method: "POST", credentials: "include" });
        if (res.ok) window.location.href = "index.html";
    });

    document.getElementById('hamburger')?.addEventListener('click', () => {
        document.getElementById('hamburger').classList.toggle('open');
        document.getElementById('nav-menu').classList.toggle('active');
    });

    document.getElementById("btn-delete-account")?.addEventListener("click", async () => {
        const confirmacao = confirm("⚠️ ATENÇÃO - AÇÃO IRREVERSÍVEL ⚠️\n\nTem certeza absoluta de que deseja excluir sua conta?\nTodos os seus dados de conta, perfil profissional e depoimentos serão apagados permanentemente das nossas bases de dados.");
        if (!confirmacao) return;
        try {
            const res = await fetch("https://banco-talentos-api.onrender.com/api/accounts/me/", { method: "DELETE", credentials: "include" });
            if (res.ok) {
                alert("Sua conta foi excluída permanentemente de acordo com as diretrizes da LGPD.");
                window.location.href = "index.html";
            } else { alert("Erro ao tentar processar a exclusão."); }
        } catch (err) { alert("Erro de rede com o servidor backend."); }
    });

    document.getElementById("update-account-form")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const btnAcc = document.getElementById("btn-save-account");
        const usernameInput = document.getElementById("edit-username").value.trim();
        const emailInput = document.getElementById("edit-email").value.trim();
        const cityInput = document.getElementById("edit-account-city").value;
        const firstNameInput = document.getElementById("edit-first-name") ? document.getElementById("edit-first-name").value.trim() : usernameInput;

        btnAcc.innerText = "Salvando...";
        try {
            const userRes = await fetch("https://banco-talentos-api.onrender.com/api/accounts/me/", {
                method: "PUT", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    username: usernameInput,
                    email: emailInput, 
                    city: cityInput, 
                    first_name: firstNameInput,
                    state: "AL" 
                })
            });
            
            if(userRes.ok) { 
                alert("Dados de acesso atualizados com sucesso!"); 
                await fetchMyProfile(); 
            } else {
                const errData = await userRes.json();
                if (errData.username) {
                    alert("⚠️ Erro de Validação: Este Nome de Usuário (Login) já está sendo utilizado por outra pessoa. Escolha outro nome.");
                } else {
                    alert("Verifique os dados digitados.");
                }
            }
        } finally { btnAcc.innerText = "ATUALIZAR DADOS"; }
    });

    document.getElementById("update-profile-form")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const birthDate = document.getElementById("edit-birth-date").value;

        if (calculateAge(birthDate) < 18) {
            alert("É obrigatório ser maior de 18 anos de idade.");
            return;
        }

        if (btnSaveWorker) btnSaveWorker.innerText = "Salvando...";
        try {
            const formData = new FormData();
            formData.append("full_name", document.getElementById("edit-name").value);
            formData.append("birth_date", birthDate);
            formData.append("phone", document.getElementById("edit-phone").value.replace(/\D/g, ""));
            formData.append("city", document.getElementById("edit-worker-city").value);
            formData.append("bio", document.getElementById("edit-bio").value.trim());
            
            const photoInput = document.getElementById("edit-photo");
            if(photoInput && photoInput.files.length > 0) formData.append("photo", photoInput.files[0]);

            let url = `https://banco-talentos-api.onrender.com/api/workers/${currentProfileId}/`;
            let method = "PUT";

            if (!isWorker) {
                url = "https://banco-talentos-api.onrender.com/api/workers/";
                method = "POST";
                const serviceVal = document.getElementById("edit-service").value;
                formData.append("services", parseInt(serviceVal));
            }

            const res = await fetch(url, { method: method, credentials: "include", body: formData });
            if(res.ok) { 
                alert(isWorker ? "Perfil profissional atualizado!" : "Perfil de Trabalhador ativado com sucesso!"); 
                window.location.href = "index.html"; 
            } else { alert("Erro ao salvar os dados profissionais."); }
        } catch(err) { alert("Erro de rede com o backend."); }
        finally { if (btnSaveWorker) btnSaveWorker.innerText = isWorker ? "SALVAR DADOS PROFISSIONAIS" : "CONFIRMAR E ATIVAR PERFIL PROFISSIONAL"; }
    });

    document.getElementById("change-password-form")?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const old_password = document.getElementById("pass-old").value;
        const new_password = document.getElementById("pass-new").value;
        const res = await fetch("https://banco-talentos-api.onrender.com/api/accounts/password/change/", {
            method: "POST", credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ old_password, new_password })
        });
        if (res.ok) {
            alert("Senha alterada! Faça login novamente.");
            await fetch("https://banco-talentos-api.onrender.com/api/auth/logout/", { method: "POST", credentials: "include" });
            window.location.reload();
        }
    });

    loadCities().then(fetchMyProfile);

    let lastScrollTop = 0;
    const headerElement = document.querySelector("header");
    window.addEventListener("scroll", () => {
        let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        if (document.getElementById("hamburger")?.classList.contains("open")) return;
        if (currentScroll > lastScrollTop && currentScroll > 80) headerElement.classList.add("header-hidden");
        else headerElement.classList.remove("header-hidden");
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
    });
});
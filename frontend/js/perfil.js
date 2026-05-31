/* ==========================================================================
   LÓGICA DO PAINEL DO USUÁRIO - MÓDULO PERFIL
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    let currentProfileId = null;
    const loginGate = document.getElementById("login-gate");
    const mainPanel = document.getElementById("main-panel");
    const logoutNav = document.getElementById("panel-logout");
    const workerSection = document.getElementById("worker-data-section");
    const subtitleTxt = document.getElementById("panel-subtitle");

    // Máscara para telefone
    const phoneInput = document.getElementById("edit-phone");
    if (phoneInput) {
        phoneInput.addEventListener("input", function(e) {
            let x = e.target.value.replace(/\D/g, "").match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : "(" + x[1] + ") " + x[2] + (x[3] ? "-" + x[3] : "");
        });
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
            const accountResponse = await fetch("http://localhost:8000/api/accounts/me/", { method: "GET", credentials: "include" });
            if (!accountResponse.ok) { showLoginGate(); return; }
            
            const userData = await accountResponse.json();
            document.getElementById("edit-email").value = userData.email || ""; 
            document.getElementById("edit-first-name").value = userData.first_name || ""; 
            document.getElementById("edit-account-city").value = userData.city || "";

            const response = await fetch("http://localhost:8000/api/workers/me/", { method: "GET", credentials: "include" });
            
            if (response.status === 404) {
                subtitleTxt.innerText = "Painel exclusivo para Contratantes. Monitore suas credenciais de acesso abaixo.";
                workerSection.classList.add("hidden");
                document.getElementById("edit-name").required = false;
                document.getElementById("edit-phone").required = false;
                document.getElementById("edit-worker-city").required = false;
                document.getElementById("edit-bio").required = false;
            } else if (response.ok) {
                subtitleTxt.innerText = "Atualize suas informações públicas ou altere seus parâmetros de acesso.";
                workerSection.classList.remove("hidden");
                const myProfile = await response.json();
                currentProfileId = myProfile.id;
                document.getElementById("edit-name").value = myProfile.full_name;
                document.getElementById("edit-phone").value = myProfile.phone;
                document.getElementById("edit-phone").dispatchEvent(new Event('input'));
                document.getElementById("edit-worker-city").value = myProfile.city;
                document.getElementById("edit-bio").value = myProfile.bio || "";
            }
            
            loginGate.classList.add("hidden");
            mainPanel.classList.remove("hidden");
            logoutNav.classList.remove("hidden");
        } catch(e) { showLoginGate(); }
    }

    function showLoginGate() {
        mainPanel.classList.add("hidden");
        logoutNav.classList.add("hidden");
        loginGate.classList.remove("hidden");
    }

    // Formulários e Eventos
    document.getElementById("gate-login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("gate-username").value.trim();
        const password = document.getElementById("gate-password").value;
        try {
            const loginRes = await fetch("http://localhost:8000/api/auth/login/", {
                method: "POST", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            if (loginRes.ok) setTimeout(fetchMyProfile, 150);
            else alert("Usuário ou senha incorretos.");
        } catch(err) { alert("Erro de comunicação com o servidor."); }
    });

    logoutNav.addEventListener("click", async (e) => {
        e.preventDefault();
        try {
            const res = await fetch("http://localhost:8000/api/auth/logout/", { method: "POST", credentials: "include" });
            if (res.ok) window.location.href = "index.html";
        } catch (err) { alert("Erro ao deslogar."); }
    });

    // Atualização de conta (E-mail, Nome, Cidade)
    document.getElementById("update-account-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const btnAcc = document.getElementById("btn-save-account");
        btnAcc.innerText = "Salvando...";
        const emailVal = document.getElementById("edit-email").value.trim();
        const firstNameVal = document.getElementById("edit-first-name").value.trim();
        const cityVal = document.getElementById("edit-account-city").value;

        try {
            const userRes = await fetch("http://localhost:8000/api/accounts/me/", {
                method: "PUT", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: emailVal, first_name: firstNameVal, city: cityVal, state: "AL" })
            });
            if(userRes.ok) { alert("Dados atualizados!"); await fetchMyProfile(); }
            else alert("Erro ao atualizar dados.");
        } catch (err) { alert("Erro de comunicação."); }
        finally { btnAcc.innerText = "ATUALIZAR MEUS DADOS GERAIS"; }
    });

    // Atualização de perfil profissional
    document.getElementById("update-profile-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const btnSave = document.getElementById("btn-save");
        btnSave.innerText = "Salvando...";
        try {
            const formData = new FormData();
            formData.append("full_name", document.getElementById("edit-name").value);
            formData.append("phone", document.getElementById("edit-phone").value.replace(/\D/g, ""));
            formData.append("city", document.getElementById("edit-worker-city").value);
            formData.append("bio", document.getElementById("edit-bio").value);
            const photoInput = document.getElementById("edit-photo");
            if(photoInput.files.length > 0) formData.append("photo", photoInput.files[0]);

            const res = await fetch(`http://localhost:8000/api/workers/${currentProfileId}/`, {
                method: "PUT", credentials: "include", body: formData
            });
            if(res.ok) { alert("Perfil profissional atualizado!"); window.location.href = "index.html"; }
            else alert("Erro ao processar dados profissionais.");
        } catch(err) { alert("Erro de rede com o backend."); }
        finally { btnSave.innerText = "SALVAR DADOS PROFISSIONAIS"; }
    });

    // Alteração de senha
    document.getElementById("change-password-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const old_password = document.getElementById("pass-old").value;
        const new_password = document.getElementById("pass-new").value;
        
        const res = await fetch("http://localhost:8000/api/accounts/password/change/", {
            method: "POST", credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ old_password, new_password })
        });
        
        if (res.ok) {
            alert("Senha alterada! Faça login novamente.");
            await fetch("http://localhost:8000/api/auth/logout/", { method: "POST", credentials: "include" });
            window.location.reload();
        } else alert("Dados inválidos ou senha atual incorreta.");
    });

    // Inicialização segura
    loadCities().then(fetchMyProfile);
});
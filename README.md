# Banco de Talentos Comunitário
Repositório oficial para o desenvolvimento do Projeto Integrador (PINT1123 - 2026.1).
Professor: Leonardo Melo de Medeiros

### Equipe e Funções:
- Roberto dos Santos: Líder Técnico, Gerente de Projeto, Desenvolvedor Front-end e Engenheiro de Qualidade
- João Victhor: Desenvolvedor Backend e Banco de Dados
- Wallex Kaua: Desenvolvedor Front-end
- Marcelo Feitoza: Desenvolvedor de IA (NLP)
- Joberval Magalhães: Tester / QA

---

### O Projeto
Plataforma de impacto social voltada para a visibilidade de trabalhadores informais, utilizando Inteligência Artificial para otimização de perfis profissionais e geração de renda local, com foco especial no fortalecimento dos municípios do interior de Alagoas.

### Tecnologias e Metodologia:
* **Metodologia:** Ágil (Scrum/Kanban).
* **Versionamento:** Git Flow (Pull Requests e Issues).
* **Arquitetura:** Cliente-Servidor (API REST).
* **Interface:** Prototipagem funcional Mobile-First em HTML5 e CSS3 com identidade visual regionalista.
* **Inteligência Artificial:** Processamento de Linguagem Natural (NLP) para profissionalização de biografias (Google Gemini API).

---

## Frontend — Como rodar localmente

Como a interface foi construída em HTML5 puro e CSS3, não há necessidade de gerenciadores de pacotes (como npm/yarn).

### 1. Ajustar a URL da API para ambiente local
Antes de rodar, garanta que os arquivos de script (como `frontend/js/index.js`, `cadastro.js` e `perfil.js`) apontem para o servidor local em vez da URL de produção:
```javascript
const finalUrl = "http://127.0.0.1:8000/api/search/";
```

### 2. Inicializar o servidor estático
Abra a pasta `frontend` no VS Code e utilize uma das seguintes opções para rodar o projeto:
* **Live Server (Recomendado):** Instale a extensão *Live Server* no VS Code, clique com o botão direito no arquivo `index.html` e selecione **Open with Live Server**. O front rodará em `http://127.0.0.1:5500`.
* **Python HTTP Server:** Navegue até a pasta do frontend via terminal e execute:
```bash
  python -m http.server 5500
  ```

---

## Backend — Como rodar localmente

### Pré-requisitos
- Python 3.12+
- Docker Desktop

### 1. Clonar o repositório e entrar na pasta raiz
```bash
git clone https://github.com/RobertoSants/projeto-integrador-ifal.git
cd projeto-integrador-ifal
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar o ambiente
Crie um arquivo chamado `.env` dentro da pasta `backend/core/` (onde fica o `settings.py`) ou use o comando:
```bash
# No Windows:
copy backend\core\.env.example backend\core\.env

# No Linux/Mac:
cp backend/core/.env.example backend/core/.env
```

Conteúdo do `.env` para desenvolvimento local:
```env
SECRET_KEY=django-insecure-ifal-2026-banco-de-talentos-troque-em-producao
DEBUG=True
DB_NAME=banco_talentos
DB_USER=pguser
DB_PASSWORD=pgpass
DB_HOST=localhost
DB_PORT=5432
GEMINI_API_KEY=sua_chave_da_api_aqui
```

### 4. Subir o banco de dados (Docker)
Na raiz do repositório (onde está o arquivo `docker-compose.yml`):
```bash
docker compose up -d
```

### 5. Aplicar migrations e carregar dados da AMA
Entre na pasta do backend para executar os comandos de gerenciamento do Django:
```bash
cd backend
python manage.py migrate
python manage.py loaddata services/fixtures/categorias_iniciais.json
```

### 6. Rodar o servidor backend
```bash
python manage.py runserver
```
API disponível em `http://127.0.0.1:8000`.

---

## Endpoints principais

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/accounts/register/` | Cadastro de usuário | Não |
| POST | `/api/auth/login/` | Login — retorna JWT | Não |
| POST | `/api/auth/refresh/` | Renovar token | Não |
| GET | `/api/accounts/me/` | Perfil do usuário logado | Sim |
| PUT | `/api/accounts/me/` | Atualizar perfil | Sim |
| GET | `/api/workers/` | Listar trabalhadores | Não |
| POST | `/api/workers/` | Cadastrar trabalhador | Sim |
| GET | `/api/workers/<id>/` | Detalhe do trabalhador | Não |
| PUT | `/api/workers/<id>/` | Atualizar trabalhador | Sim (dono) |
| GET | `/api/services/` | Listar eixos setoriais | Não |
| GET | `/api/search/` | Buscar trabalhadores | Não |
| POST | `/api/reviews/` | Avaliar trabalhador | Sim |

### Parâmetros de busca — `GET /api/search/`
| Parâmetro | Exemplo | Descrição |
|-----------|---------|-----------|
| `q` | `?q=pedreiro` | Busca por nome ou bio |
| `city` | `?city=Penedo` | Filtrar por município |
| `service` | `?service=2` | Filtrar por eixo (1=Rural, 2=Construção, 3=Artesanato, 4=Logística) |
| `rating` | `?rating=4` | Nota mínima |
| `contratante_city` | `?contratante_city=Delmiro Gouveia` | Priorizar trabalhadores locais (usado quando não autenticado) |

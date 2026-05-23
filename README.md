# Banco de Talentos Comunitário
Repositório oficial para o desenvolvimento do Projeto Integrador (PINT1123 - 2026.1).
Professor: Leonardo Melo de Medeiros

### Equipe e Funções:
- Roberto dos Santos: Lider Técnico, Gerente de Projeto e Engenheiro de Qualidade
- João Victhor: Desenvolvedor Backend
- Wallex Kaua: Desenvolvedor Front-end
- Thiago Luiz: Desenvolvedor Front-end
- Leonardo Ferro: Banco de Dados
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
* **Inteligência Artificial:** Processamento de Linguagem Natural (NLP) para profissionalização de biografias.

---

## Backend — Como rodar localmente

### Pré-requisitos
- Python 3.12+
- Docker Desktop

### 1. Clonar o repositório
```bash
git clone https://github.com/RobertoSants/projeto-integrador-ifal.git
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```
### 3. Configurar o ambiente
```bash
copy .env.example .env
```

Conteúdo do `.env` para desenvolvimento local:
```
SECRET_KEY=django-insecure-ifal-2026-banco-de-talentos-troque-em-producao
DEBUG=True
DB_NAME=banco_talentos
DB_USER=pguser
DB_PASSWORD=pgpass
DB_HOST=localhost
DB_PORT=5432
```



### 4. Subir o banco de dados
```bash
docker compose up -d
```

### 5. Aplicar migrations e carregar dados iniciais
```bash
cd projeto-integrador-ifal/backend
python manage.py migrate
python manage.py loaddata services/fixtures/categorias_iniciais.json
```

### 6. Rodar o servidor
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
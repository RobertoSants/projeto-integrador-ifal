# ENDPOINTS.md — Documentação da API REST
**Banco de Talentos Comunitário — Projeto Integrador IFAL 2026.1**  
Responsável Backend: João Victhor

---

## Base URL

```
http://localhost:8000/api/
```

Em produção, substituir pelo domínio do servidor.

---

## Autenticação

A API utiliza **JWT (JSON Web Token)** via `djangorestframework-simplejwt`.

O frontend deve:
1. Fazer login em `POST /api/auth/login/` com `username` e `password`
2. Receber `access` (válido por 5 min) e `refresh` (válido por 1 dia)
3. Enviar o token em toda requisição protegida no header:
   ```
   Authorization: Bearer <access_token>
   ```
4. Renovar o `access` quando expirar via `POST /api/auth/refresh/`

### Rotas de Autenticação

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/api/auth/login/` | Login — retorna `access` e `refresh` | Não |
| POST | `/api/auth/refresh/` | Renova o token de acesso | Não |
| POST | `/api/auth/verify/` | Verifica se um token é válido | Não |

#### Exemplo — Login

**Request** `POST /api/auth/login/`
```json
{
  "username": "joao_silva",
  "password": "senha123"
}
```

**Response** `200 OK`
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

| Código | Situação |
|--------|----------|
| 200 | Login bem-sucedido |
| 400 | Campos ausentes |
| 401 | Credenciais inválidas |

---

## Módulo: Accounts (Usuários)

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/api/accounts/register/` | Cadastra novo usuário | Não |
| GET | `/api/accounts/me/` | Retorna dados do usuário logado | ✅ |
| PUT | `/api/accounts/me/` | Atualiza dados do usuário logado | ✅ |
| DELETE | `/api/accounts/me/` | Deleta a própria conta | ✅ |
| POST | `/api/accounts/password/change/` | Troca a senha | ✅ |

#### Exemplo — Cadastro de usuário

**Request** `POST /api/accounts/register/`
```json
{
  "username": "joao_silva",
  "email": "joao@email.com",
  "password": "senha123",
  "password_confirm": "senha123",
  "city": "Maceió",
  "state": "AL"
}
```

> Os campos `city` e `state` são necessários para que o sistema de priorização por município funcione corretamente no endpoint de busca. Ver seção [Módulo: Search](#módulo-search-busca).

**Response** `201 Created`
```json
{
  "id": 1,
  "username": "joao_silva",
  "email": "joao@email.com",
  "city": "Maceió",
  "state": "AL"
}
```

| Código | Situação |
|--------|----------|
| 201 | Usuário criado com sucesso |
| 400 | Dados inválidos (ex: senhas não coincidem, e-mail já cadastrado) |

---

## Módulo: Workers (Trabalhadores / Talentos)

> **Nota de nomenclatura:** O enunciado da issue usa o termo `/talentos` como exemplo. Optou-se por `/workers/` para manter consistência com a terminologia técnica do Django e separar claramente o conceito de "perfil profissional" do conceito de "usuário da plataforma".

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/api/workers/` | Lista todos os trabalhadores | Não |
| POST | `/api/workers/` | Cria perfil de trabalhador | ✅ |
| GET | `/api/workers/<id>/` | Detalhe de um trabalhador | Não |
| PUT | `/api/workers/<id>/` | Edita perfil (somente o dono) | ✅ |
| DELETE | `/api/workers/<id>/` | Remove perfil (somente o dono) | ✅ |
| GET | `/api/workers/<id>/services/` | Serviços oferecidos pelo trabalhador | Não |
| GET | `/api/workers/<id>/reviews/` | Avaliações recebidas pelo trabalhador | Não |

### Campos do objeto Worker

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | int | — | Identificador único (gerado automaticamente) |
| `user` | int | — | ID do usuário vinculado |
| `full_name` | string | ✅ | Nome completo do trabalhador |
| `bio` | string | Não | Descrição/apresentação do trabalhador |
| `phone` | string | ✅ | Telefone ou WhatsApp para contato |
| `city` | string | ✅ | Cidade de atuação |
| `state` | string | ✅ | Estado (ex: `"AL"`) |
| `photo` | url | Não | URL da foto de perfil |
| `services` | array[int] | ✅ | IDs das categorias de serviço oferecidas |
| `avg_rating` | float | — | Média das avaliações (calculado automaticamente) |
| `created_at` | datetime | — | Data de cadastro (gerado automaticamente) |

#### Exemplo — Criar perfil de trabalhador

**Request** `POST /api/workers/`
```json
{
  "full_name": "Carlos Andrade",
  "bio": "Pintor com 10 anos de experiência em residências e comércios.",
  "phone": "82999990000",
  "city": "Maceió",
  "state": "AL",
  "services": [2, 5]
}
```

**Response** `201 Created`
```json
{
  "id": 7,
  "user": 1,
  "full_name": "Carlos Andrade",
  "bio": "Pintor com 10 anos de experiência em residências e comércios.",
  "phone": "82999990000",
  "city": "Maceió",
  "state": "AL",
  "photo": null,
  "services": [2, 5],
  "avg_rating": null,
  "created_at": "2026-04-21T14:00:00Z"
}
```

| Código | Situação |
|--------|----------|
| 201 | Perfil criado com sucesso |
| 400 | Dados inválidos ou campos obrigatórios ausentes |
| 401 | Token ausente ou inválido |

#### Exemplo — Detalhe de trabalhador

**Response** `GET /api/workers/7/` → `200 OK`
```json
{
  "id": 7,
  "user": 1,
  "full_name": "Carlos Andrade",
  "bio": "Pintor com 10 anos de experiência em residências e comércios.",
  "phone": "82999990000",
  "city": "Maceió",
  "state": "AL",
  "photo": "https://exemplo.com/media/fotos/carlos.jpg",
  "services": [
    { "id": 2, "name": "Pintor" },
    { "id": 5, "name": "Gesseiro" }
  ],
  "avg_rating": 4.7,
  "created_at": "2026-04-21T14:00:00Z"
}
```

| Código | Situação |
|--------|----------|
| 200 | Sucesso |
| 404 | Trabalhador não encontrado |

---

## Módulo: Services (Categorias de Serviço)

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/api/services/` | Lista todas as categorias | Não |
| GET | `/api/services/<id>/` | Detalhe de uma categoria | Não |
| GET | `/api/services/<id>/workers/` | Trabalhadores que oferecem essa categoria | Não |

### Campos do objeto Service

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | Identificador único |
| `name` | string | Nome da categoria (ex: `"Eletricista"`) |
| `description` | string | Descrição da categoria |
| `icon` | string | Nome do ícone (ex: `"bolt"`) |

#### Exemplo — Listar categorias

**Response** `GET /api/services/` → `200 OK`
```json
[
  {
    "id": 1,
    "name": "Eletricista",
    "description": "Serviços elétricos residenciais e comerciais",
    "icon": "bolt"
  },
  {
    "id": 2,
    "name": "Pintor",
    "description": "Pintura residencial, comercial e artística",
    "icon": "brush"
  }
]
```

| Código | Situação |
|--------|----------|
| 200 | Sucesso |
| 404 | Categoria não encontrada |

---

## Módulo: Reviews (Avaliações)

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/api/reviews/` | Cria avaliação para um trabalhador | ✅ |
| GET | `/api/reviews/<id>/` | Detalhe de uma avaliação | Não |
| PUT | `/api/reviews/<id>/` | Edita avaliação (somente o autor) | ✅ |
| DELETE | `/api/reviews/<id>/` | Remove avaliação (somente o autor) | ✅ |

### Campos do objeto Review

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | int | — | Identificador único |
| `worker` | int | ✅ | ID do trabalhador avaliado |
| `author` | int | — | ID do usuário que avaliou (preenchido automaticamente) |
| `rating` | int | ✅ | Nota de 1 a 5 |
| `comment` | string | Não | Comentário da avaliação |
| `created_at` | datetime | — | Data da avaliação |

#### Exemplo — Criar avaliação

**Request** `POST /api/reviews/`
```json
{
  "worker": 7,
  "rating": 5,
  "comment": "Excelente serviço, muito pontual e caprichoso!"
}
```

**Response** `201 Created`
```json
{
  "id": 12,
  "worker": 7,
  "author": 1,
  "rating": 5,
  "comment": "Excelente serviço, muito pontual e caprichoso!",
  "created_at": "2026-04-21T14:30:00Z"
}
```

| Código | Situação |
|--------|----------|
| 201 | Avaliação criada com sucesso |
| 400 | Dados inválidos (ex: `rating` fora de 1–5) |
| 401 | Token ausente ou inválido |
| 403 | Usuário tentando editar avaliação de outro |
| 404 | Avaliação ou trabalhador não encontrado |

---

## Módulo: Search (Busca)

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/api/search/` | Busca talentos com filtros e priorização local | Não (mas aceita token) |

### Priorização por Município

> **Requisito:** O endpoint de busca deve priorizar resultados do mesmo município do contratante para fomentar a economia local e reduzir custos de deslocamento.

O endpoint implementa priorização automática de duas formas:

**1. Contratante autenticado (recomendado)**  
Quando o token JWT é enviado no header, o sistema lê automaticamente a `city` do perfil do contratante logado e eleva ao topo os trabalhadores do mesmo município — sem nenhum parâmetro extra necessário.

**2. Contratante não autenticado**  
O frontend pode passar `?contratante_city=Maceió` para ativar a priorização sem login.

Em ambos os casos, o campo `is_local` no response indica se o trabalhador é do mesmo município. Os resultados são ordenados: **locais primeiro**, depois os demais por `avg_rating` decrescente.

### Parâmetros de query

| Parâmetro | Tipo | Obrigatório | Descrição | Exemplo |
|-----------|------|-------------|-----------|---------|
| `q` | string | Não | Busca por texto livre (nome, bio, habilidade) | `q=eletricista` |
| `city` | string | Não | Filtra **exclusivamente** por cidade | `city=Arapiraca` |
| `contratante_city` | string | Não | Cidade do contratante para priorização (usado quando não há login) | `contratante_city=Maceió` |
| `service` | int | Não | ID da categoria de serviço | `service=1` |
| `rating` | float | Não | Nota mínima do trabalhador | `rating=4` |
| `ordering` | string | Não | Ordenação manual (sobrepõe priorização local) | `ordering=-avg_rating` |

> **Diferença entre `city` e `contratante_city`:**  
> - `city` é um **filtro excludente**: retorna apenas trabalhadores daquela cidade.  
> - `contratante_city` é uma **dica de priorização**: trabalhadores de outras cidades ainda aparecem, mas ficam abaixo dos locais.

#### Exemplo 1 — Busca com contratante autenticado (priorização automática)

```
GET /api/search/?q=pintor&rating=4
Authorization: Bearer <access_token>
```

O sistema detecta que o contratante logado é de Maceió e ordena os pintores de Maceió primeiro.

**Response** `200 OK`
```json
{
  "count": 4,
  "contratante_city": "Maceió",
  "results": [
    {
      "id": 7,
      "full_name": "Carlos Andrade",
      "city": "Maceió",
      "state": "AL",
      "avg_rating": 4.7,
      "services": ["Pintor"],
      "phone": "82999990000",
      "is_local": true
    },
    {
      "id": 12,
      "full_name": "Ana Souza",
      "city": "Maceió",
      "state": "AL",
      "avg_rating": 4.5,
      "services": ["Pintor", "Gesseiro"],
      "phone": "82988880000",
      "is_local": true
    },
    {
      "id": 3,
      "full_name": "Pedro Lima",
      "city": "Arapiraca",
      "state": "AL",
      "avg_rating": 4.9,
      "services": ["Pintor"],
      "phone": "82977770000",
      "is_local": false
    }
  ]
}
```

#### Exemplo 2 — Busca sem login com priorização manual

```
GET /api/search/?q=eletricista&contratante_city=Arapiraca
```

**Response** `200 OK`
```json
{
  "count": 3,
  "contratante_city": "Arapiraca",
  "results": [
    {
      "id": 9,
      "full_name": "Marcos Ferreira",
      "city": "Arapiraca",
      "state": "AL",
      "avg_rating": 4.2,
      "services": ["Eletricista"],
      "phone": "82966660000",
      "is_local": true
    },
    {
      "id": 5,
      "full_name": "Luiz Costa",
      "city": "Maceió",
      "state": "AL",
      "avg_rating": 4.8,
      "services": ["Eletricista"],
      "phone": "82955550000",
      "is_local": false
    }
  ]
}
```

#### Exemplo 3 — Filtro exclusivo por cidade (sem priorização)

```
GET /api/search/?city=maceio&service=1
```

Retorna **somente** trabalhadores de Maceió na categoria de serviço 1, sem nenhuma priorização adicional.

| Código | Situação |
|--------|----------|
| 200 | Sucesso (pode retornar lista vazia) |
| 400 | Parâmetro inválido (ex: `rating` não numérico) |

---

## Códigos de Resposta Padrão

| Código | Significado | Quando ocorre |
|--------|-------------|---------------|
| 200 | OK | Requisição GET bem-sucedida |
| 201 | Created | Recurso criado com sucesso (POST) |
| 400 | Bad Request | Dados inválidos, campos faltando ou formato incorreto |
| 401 | Unauthorized | Token ausente, expirado ou inválido |
| 403 | Forbidden | Usuário autenticado, mas sem permissão para aquela ação |
| 404 | Not Found | Recurso não encontrado no banco de dados |
| 500 | Internal Server Error | Erro inesperado no servidor |

### Formato padrão de erro

Todos os erros retornam JSON no seguinte formato:

```json
{
  "error": "Descrição legível do erro",
  "detail": "Informação técnica adicional (opcional)"
}
```

Exemplo de `400 Bad Request`:
```json
{
  "error": "Dados inválidos",
  "detail": {
    "rating": ["Este campo deve ser um número entre 1 e 5."],
    "worker": ["Este campo é obrigatório."]
  }
}
```

---

*Documentação gerada para a issue #3 — Avaliação 1 (Pitch)*  
*Responsável Backend: João Victhor*  
*Arquivo: `/docs/backend/ENDPOINTS.md`*
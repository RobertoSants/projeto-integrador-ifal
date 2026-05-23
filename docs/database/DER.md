# Especificação Técnica do Diagrama Entidade-Relacionamento (DER)
**Banco de Talentos Comunitário — Projeto Integrador IFAL 2026.1**

Este documento detalha a modelagem lógica e conceitual do banco de dados relacional implementado em PostgreSQL para o sistema.

## 1. Entidades Principais e Atributos

### A. Tabela: `accounts_user` (Usuários / Contratantes)
Armazena as informações de autenticação e localização dos usuários gerais do sistema.
- `id` (INT) - **PK** (Chave Primária)
- `username` (VARCHAR) - Único
- `email` (VARCHAR)
- `password` (VARCHAR)
- `city` (VARCHAR) - Município base para cálculo de localidade
- `state` (VARCHAR)

### B. Tabela: `workers_worker` (Trabalhadores / Talentos)
Armazena os perfis profissionais específicos vinculados a um usuário do sistema.
- `id` (INT) - **PK** (Chave Primária)
- `user_id` (INT) - **FK** (Chave Estrangeira referenciando `accounts_user.id`, Relacionamento 1:1)
- `full_name` (VARCHAR)
- `bio` (TEXT) - Espaço para a biografia profissionalizada pela IA
- `phone` (VARCHAR) - WhatsApp de contato direto
- `city` (VARCHAR) - Município de atuação do trabalhador
- `state` (VARCHAR)
- `photo` (VARCHAR) - Caminho da imagem de perfil no diretório de mídia

### C. Tabela: `services_servicecategory` (Eixos Setoriais da AMA)
Armazena as grandes categorias de serviços definidas para os municípios.
- `id` (INT) - **PK** (Chave Primária)
- `name` (VARCHAR) - Ex: Produção Rural, Construção, Artesanato, Logística
- `description` (TEXT)
- `icon` (VARCHAR)

### D. Tabela: `reviews_review` (Avaliações)
Armazena o feedback e notas dadas aos prestadores de serviço.
- `id` (INT) - **PK** (Chave Primária)
- `worker_id` (INT) - **FK** (Chave Estrangeira referenciando `workers_worker.id`, Relacionamento 1:N)
- `author_id` (INT) - **FK** (Chave Estrangeira referenciando `accounts_user.id`, Relacionamento 1:N)
- `rating` (INT) - Valor de 1 a 5
- `comment` (TEXT)
- `created_at` (DATETIME)

## 2. Tabelas de Associação (Relacionamentos N:N)

### E. Tabela Intermediária: `workers_worker_services`
Gerada automaticamente para gerenciar o relacionamento de muitos-para-muitos entre Trabalhadores e Categorias de Serviço.
- `id` (INT) - **PK**
- `worker_id` (INT) - **FK** (referenciando `workers_worker.id`)
- `servicecategory_id` (INT) - **FK** (referenciando `services_servicecategory.id`)

## 3. Mapeamento Lógico dos Relacionamentos
- **User (accounts) 1 : 1 Worker (workers):** Um usuário possui apenas um perfil de trabalhador cadastrado no sistema, enquanto um perfil de trabalhador pertence obrigatoriamente a um único usuário.
- **Worker (workers) 1 : N Review (reviews):** Um trabalhador pode receber múltiplas avaliações de contratantes diferentes, mas cada avaliação é direcionada a apenas um trabalhador.
- **User (accounts) 1 : N Review (reviews):** Um usuário contratante pode realizar diversas avaliações na plataforma, mas cada avaliação possui apenas um autor.
- **Worker (workers) N : N ServiceCategory (services):** Um trabalhador pode se registrar em mais de uma categoria profissional (ex: Construção e Logística), e uma categoria engloba múltiplos trabalhadores do estado.
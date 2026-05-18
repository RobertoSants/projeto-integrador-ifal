# PLANO DE TESTES
Banco de Talentos Comunitário — Projeto Integrador IFAL 2026.1

---

## 1. Estratégia de Garantia de Qualidade

### Objetivo

Garantir que as duas funcionalidades críticas do sistema funcionem corretamente: cadastro de usuários/trabalhadores e busca por profissionais. O foco é validar que os dados são processados corretamente, as validações funcionam e o sistema responde como esperado.

### Escopo

Este plano cobre:
- Testes dos endpoints da API (cadastro e busca)
- Validação de dados de entrada
- Autenticação com JWT
- Integração entre os módulos

Não são escopo deste plano:
- Testes de performance ou carga
- Testes de segurança avançada
- Testes de interface gráfica (frontend)

### Abordagem de Teste

Usaremos testes funcionais focando em:
- Fluxos normais (happy path)
- Casos extremos e limites
- Validações e tratamento de erros
- Combinação de múltiplos filtros

Os testes serão executados manualmente através de Postman/Insomnia e depois automatizados com pytest.

---

## 2. Funcionalidades a Testar

### Funcionalidade 1: Cadastro de Usuário
Endpoint: POST /api/accounts/register/

Permite que novos usuários se registrem. Recebe username, email, senha, cidade e estado. Deve validar todos os dados e rejeitar duplicatas.

### Funcionalidade 2: Cadastro de Trabalhador
Endpoint: POST /api/workers/

Usuários autenticados podem criar um perfil de trabalhador. Recebe nome completo, telefone, cidade, estado, categorias de serviço e bio opcional. Precisa de autenticação JWT.

### Funcionalidade 3: Busca de Trabalhadores
Endpoint: GET /api/search/

Permite buscar trabalhadores usando filtros como texto livre, cidade, categoria de serviço e avaliação mínima. Prioriza resultados pela localidade do contratante se autenticado.

---

## 3. Cenários de Teste

### CADASTRO DE USUÁRIO

**CT-001: Cadastro com Dados Válidos**
- Registrar um novo usuário com todos os dados corretos
- Entrada: POST /api/accounts/register/ com username, email, password, password_confirm, city e state válidos
- Resultado esperado: HTTP 201 Created, resposta contém id, username, email, city, state. Usuário consegue fazer login

**CT-002: Rejeição de Email Duplicado**
- Um email já cadastrado deve ser rejeitado
- Pré-condição: Um usuário com email "joao@email.com" já existe
- Entrada: POST /api/accounts/register/ tentando registrar outro usuário com o mesmo email
- Resultado esperado: HTTP 400 Bad Request com mensagem clara. Novo usuário não é criado

**CT-003: Rejeição de Senhas Não Coincidentes**
- Campos password e password_confirm devem ser iguais
- Entrada: POST /api/accounts/register/ com passwords diferentes
- Resultado esperado: HTTP 400 Bad Request. Usuário não é criado

**CT-004: Rejeição de Campos Obrigatórios Faltando**
- Todos os campos obrigatórios (username, email, password, city, state) são necessários
- Entrada: POST /api/accounts/register/ sem um ou mais campos obrigatórios
- Resultado esperado: HTTP 400 Bad Request listando quais campos faltam. Usuário não é criado

**CT-005: Rejeição de Email Inválido**
- O email deve estar em formato válido
- Entrada: POST /api/accounts/register/ com email no formato "email_invalido" (sem @, domínio, etc)
- Resultado esperado: HTTP 400 Bad Request. Usuário não é criado

**CT-006: Rejeição de Username Duplicado**
- Cada username deve ser único no sistema
- Pré-condição: Um usuário com username "joao_silva" já existe
- Entrada: POST /api/accounts/register/ tentando usar o mesmo username
- Resultado esperado: HTTP 400 Bad Request. Novo usuário não é criado

---

### CADASTRO DE TRABALHADOR

**CT-007: Cadastro de Trabalhador com Dados Válidos**
- Um usuário autenticado deve conseguir criar um perfil de trabalhador
- Pré-condição: Usuário registrado e com JWT válido
- Entrada: POST /api/workers/ com headers Authorization e dados válidos (full_name, phone, city, state, services)
- Resultado esperado: HTTP 201 Created. Worker vinculado corretamente ao usuário autenticado

**CT-008: Rejeição sem Autenticação**
- Cadastro de trabalhador requer que o usuário esteja autenticado (JWT)
- Entrada: POST /api/workers/ sem header Authorization
- Resultado esperado: HTTP 401 Unauthorized. Worker não é criado

**CT-009: Rejeição de Token Inválido**
- Um token JWT inválido ou expirado deve ser rejeitado
- Entrada: POST /api/workers/ com um token malformado ou inválido
- Resultado esperado: HTTP 401 Unauthorized. Worker não é criado

**CT-010: Rejeição de Campos Obrigatórios Faltando**
- Os campos full_name, phone, city, state e services são obrigatórios
- Pré-condição: Usuário autenticado
- Entrada: POST /api/workers/ sem um ou mais campos obrigatórios
- Resultado esperado: HTTP 400 Bad Request indicando quais campos faltam. Worker não é criado

**CT-011: Rejeição de Serviços Inválidos**
- Os service IDs devem existir no banco de dados
- Pré-condição: Usuário autenticado. IDs de serviço válidos estão carregados no banco
- Entrada: POST /api/workers/ com service IDs que não existem (ex: [999, 1000])
- Resultado esperado: HTTP 400 Bad Request indicando que o serviço é inválido. Worker não é criado

---

### BUSCA DE TRABALHADORES

**CT-012: Busca Simples por Texto**
- Buscar trabalhadores usando um termo de texto livre
- Entrada: GET /api/search/?q=pintor
- Resultado esperado: HTTP 200 OK com lista de trabalhadores que contêm "pintor" no nome ou bio

**CT-013: Busca sem Resultado**
- Quando nenhum trabalhador corresponde ao critério de busca
- Entrada: GET /api/search/?q=xyz_nao_existe
- Resultado esperado: HTTP 200 OK com count = 0, results = []

**CT-014: Filtro por Cidade**
- Filtrar trabalhadores por cidade específica
- Entrada: GET /api/search/?city=Maceió
- Resultado esperado: HTTP 200 OK. Todos os resultados têm city = "Maceió"

**CT-015: Filtro por Categoria de Serviço**
- Filtrar trabalhadores pela categoria de serviço
- Entrada: GET /api/search/?service=2
- Resultado esperado: HTTP 200 OK. Todos os resultados oferecem o serviço com ID 2

**CT-016: Filtro por Avaliação Mínima**
- Filtrar apenas trabalhadores com avaliação igual ou acima de um valor mínimo
- Entrada: GET /api/search/?rating=4.0
- Resultado esperado: HTTP 200 OK. Todos os resultados têm avg_rating >= 4.0

**CT-017: Priorização por Localidade**
- Quando um usuário autenticado faz a busca, trabalhadores da mesma cidade aparecem primeiro
- Pré-condição: Usuário autenticado da cidade de Maceió. Existem trabalhadores em Maceió e em Arapiraca
- Entrada: GET /api/search/ (com autenticação JWT do usuário de Maceió)
- Resultado esperado: HTTP 200 OK. Trabalhadores de Maceió aparecem antes dos de outras cidades

**CT-018: Busca Anônima**
- Buscar sem estar autenticado deve funcionar, mas sem priorização por localidade
- Entrada: GET /api/search/?q=pedreiro (sem autenticação)
- Resultado esperado: HTTP 200 OK. Resultados ordenados apenas por rating

**CT-019: Múltiplos Filtros Combinados**
- Filtros devem funcionar juntos com lógica AND
- Entrada: GET /api/search/?q=pintor&city=Maceió&service=2&rating=4.0
- Resultado esperado: HTTP 200 OK. Todos os resultados satisfazem todos os critérios

**CT-020: Rating com Valor Inválido**
- Quando o parâmetro rating recebe um valor que não é um número
- Entrada: GET /api/search/?rating=abc
- Resultado esperado: HTTP 200 OK. Filtro de rating é ignorado e busca continua normalmente

**CT-021: Busca Case-Insensitive**
- A busca não deve ser sensível a maiúsculas/minúsculas
- Entrada: GET /api/search/?q=CARLOS, GET /api/search/?q=carlos
- Resultado esperado: Ambos retornam o mesmo resultado

**CT-022: Parâmetros Desconhecidos Ignorados**
- Parâmetros de query desconhecidos devem ser ignorados, não causando erro
- Entrada: GET /api/search/?q=pintor&unknown_param=value&xyz=123
- Resultado esperado: HTTP 200 OK. Busca funciona normalmente

---

## 4. Critérios de Aceite

### Cadastro de Usuário

| ID | Critério | Validação |
|----|----------|-----------|
| AC-001 | Todos os campos obrigatórios devem ser requeridos | CT-004 |
| AC-002 | Email duplicado deve ser rejeitado | CT-002 |
| AC-003 | Username duplicado deve ser rejeitado | CT-006 |
| AC-004 | Password e password_confirm devem coincidir | CT-003 |
| AC-005 | Email deve ter formato válido | CT-005 |
| AC-006 | Cadastro bem-sucedido retorna HTTP 201 | CT-001 |
| AC-007 | Resposta contém id, username, email, city, state | CT-001 |
| AC-008 | Usuário registrado consegue fazer login | CT-001 |

### Cadastro de Trabalhador

| ID | Critério | Validação |
|----|----------|-----------|
| AC-009 | Autenticação é obrigatória | CT-008 |
| AC-010 | Token inválido é rejeitado | CT-009 |
| AC-011 | Todos os campos obrigatórios são requeridos | CT-010 |
| AC-012 | Service IDs devem existir no banco | CT-011 |
| AC-013 | Worker é vinculado ao usuário autenticado | CT-007 |
| AC-014 | Criação bem-sucedida retorna HTTP 201 | CT-007 |

### Busca

| ID | Critério | Validação |
|----|----------|-----------|
| AC-015 | Parâmetro q busca em full_name e bio | CT-012 |
| AC-016 | Parâmetro city filtra por localidade | CT-014 |
| AC-017 | Parâmetro service filtra por categoria | CT-015 |
| AC-018 | Parâmetro rating filtra por avaliação mínima | CT-016 |
| AC-019 | Trabalhadores da mesma cidade aparecem primeiro | CT-017 |
| AC-020 | Busca anônima não filtra por localidade | CT-018 |
| AC-021 | Múltiplos filtros são aplicados com AND lógico | CT-019 |
| AC-022 | Busca é case-insensitive | CT-021 |
| AC-023 | Nenhum resultado retorna count=0, results=[] | CT-013 |

---

## 5. Padrões de Reporte de Bugs

### Template de Bug Report

```
Título: [Descrição breve do problema]

Severidade:
- [ ] Crítica (aplicação não funciona, bloqueante)
- [ ] Alta (funcionalidade quebrada, sem workaround)
- [ ] Média (funcionalidade impactada, workaround existe)
- [ ] Baixa (cosmético, minor)

Módulo Afetado:
- [ ] Cadastro de Usuário
- [ ] Cadastro de Trabalhador
- [ ] Busca
- [ ] Autenticação
- [ ] Outro

Ambiente:
- URL: http://localhost:8000
- Cliente: Postman / Insomnia / Navegador
- Data/Hora: DD/MM/YYYY HH:MM

Pré-requisitos:
[Qual era o estado do sistema antes do problema?]

Passos para Reproduzir:
1. Passo 1
2. Passo 2
3. [...]

Resultado Esperado:
[O que deveria acontecer?]

Resultado Atual:
[O que aconteceu?]

Evidências:
- Screenshot/Logs: [anexar]
- JSON da Requisição: [cole aqui]
- JSON da Resposta: [cole aqui]
- Erro no Console: [cole aqui]

Impacto no Usuário:
[Como isso afeta o usuário final?]

Observações Adicionais:
[Informações relevantes]

Relatado por: [Nome]
Data: DD/MM/YYYY
Status: Aberto
```

### Níveis de Severidade

| Nível | Exemplos | Prazo para Correção |
|-------|----------|-------------------|
| Crítica | 401 retorna 200, usuário criado 2x, dados perdidos | 24 horas |
| Alta | Busca não retorna resultados válidos, login não funciona | 2 dias |
| Média | Erro na validação de campo, mensagem confusa | 3 dias |
| Baixa | Mensagem em inglês quando deveria ser português, typo | 5 dias |

### Estados de Bug

- Aberto: Novo, não analisado
- Em Análise: Sendo investigado
- Confirmado: Validado como bug real
- Em Desenvolvimento: Dev trabalhando na correção
- Aguardando Teste: Fix pronto, awaiting QA re-test
- Resolvido: Fix verificado e validado
- Rejeitado: Não é bug, comportamento esperado

---

## 6. Checklist de QA

Antes de marcar uma funcionalidade como "Pronto para Produção":

### Cadastro de Usuário
- [ ] Todos os testes CT-001 a CT-006 passam
- [ ] Validações de entrada funcionam
- [ ] Mensagens de erro são claras
- [ ] Usuário consegue fazer login após cadastro
- [ ] Dados persistem corretamente no banco
- [ ] Nenhum bug crítico ou alta aberto

### Cadastro de Trabalhador
- [ ] Todos os testes CT-007 a CT-011 passam
- [ ] Autenticação é obrigatória
- [ ] Worker está vinculado ao user correto
- [ ] Nenhum bug crítico ou alta aberto

### Busca
- [ ] Todos os testes CT-012 a CT-022 passam
- [ ] Filtros funcionam individualmente e combinados
- [ ] Priorização por localidade funciona
- [ ] Ordenação por rating está correta
- [ ] Nenhum bug crítico ou alta aberto

---

## 7. Referências

- README.md — Configuração local
- ENDPOINTS.md — Documentação completa da API
- backend/accounts/models.py — Modelo de usuário
- backend/workers/models.py — Modelo de trabalhador
- backend/search/views.py — Lógica de busca

# Homologação dos Cenários de Busca e Priorização por Localidade #11

## Escopo executado

- CT-012: busca por termo livre
- CT-014: filtro por cidade
- CT-015: filtro por eixo setorial
- CT-016: filtro por rating mínimo
- CT-017: priorização por localidade com sessão ativa
- CT-020: rating inválido tratado sem erro 500
- CT-021: busca case-insensitive
- Smoke visual da Home para o badge `📍 TALENTO LOCAL`

## Ambiente utilizado

- Backend local com Django em `core.test_settings`
- Base de homologação em SQLite, com carga seedada para validação funcional
- Frontend servido em `http://localhost:5500`
- Backend servido em `http://localhost:8000`

## Resultado dos cenários

- CT-012: aprovado
- CT-014: aprovado
- CT-015: aprovado
- CT-016: aprovado
- CT-017: aprovado
- CT-020: aprovado
- CT-021: aprovado

## Evidências verificadas

- Busca por termo livre retornando `Carlos Oliveira` para `q=pintura`
- Filtro por cidade retornando apenas trabalhadores de `Maceió`
- Filtro por eixo setorial retornando apenas registros da categoria `Construção`
- Rating inválido `?rating=abc` retornando HTTP 200 sem quebrar o servidor
- Busca case-insensitive retornando o mesmo resultado para `q=carlos` e `q=CARLOS`
- Priorização por localidade funcionando com sessões de `Maceió`, `Penedo`, `Delmiro Gouveia` e `Santana do Ipanema`
- Badge vermelho `📍 TALENTO LOCAL` exibido na Home quando a sessão autenticada é do mesmo município

## Bug report encontrado

### Título

Requisição de refresh sem sessão gera HTTP 400 no carregamento inicial da Home

### Severidade

- [ ] Crítica
- [ ] Alta
- [ ] Média
- [x] Baixa

### Módulo afetado

- [ ] Cadastro de Usuário
- [ ] Cadastro de Trabalhador
- [ ] Busca
- [x] Autenticação
- [ ] Outro

### Ambiente

- URL: `http://localhost:5500/index.html`
- Backend: `http://localhost:8000`
- Data/Hora: 01/06/2026

### Pré-requisitos

Usuário acessa a Home sem sessão autenticada ativa.

### Passos para reproduzir

1. Abrir a Home em navegador limpo, sem cookies de autenticação.
2. Observar o carregamento inicial da página.
3. Conferir o console do navegador.

### Resultado esperado

Carregamento silencioso da página, sem erro de recurso no console.

### Resultado atual

A chamada `POST /api/auth/refresh/` retorna HTTP 400 e aparece como erro no console, embora a página continue funcional.

### Impacto no usuário

Baixo. Não impede o uso da busca nem a renderização dos cards, mas polui o console e gera ruído de diagnóstico.

### Evidências

- Console do navegador durante o carregamento inicial mostrou `Failed to load resource: the server responded with a status of 400 (Bad Request)` associado ao refresh anônimo.

## Conclusão

A homologação funcional dos cenários de busca e priorização por localidade foi executada com sucesso dentro do ambiente disponível. Os cenários principais passaram e o badge de talento local foi confirmado visualmente na Home.

# Documentação de UX/UI - Banco de Talentos

## Guia de Estilo (Proposta)
- **Cores:** Azul Institucional (Confiança) e Verde (Aprovação/Sucesso).
- **Tipografia:** Sem serifa (Ex: Roboto ou Inter) para facilitar a leitura digital.

## Descrição das Telas (Wireframes Textuais)

### 1. Tela de Busca (Módulo Search)
**Objetivo:** Conectar o contratante ao talento local rapidamente.
- **Header:** Campo de busca com ícone de lupa ("O que você procura?").
- **Filtro de Localidade:** Badge fixo mostrando "Resultados em: [Cidade do Usuário]".
- **Lista de Resultados (Cards):**
    - Tag verde no topo: "📍 Destaque Local" (para `is_local: true`).
    - Nome do Profissional (ex: Carlos Andrade).
    - Avaliação: ⭐ 4.7 (avg_rating).
    - Botão de Ação: "Ver Perfil".

### 2. Tela de Cadastro de Trabalhador (Módulo Workers)
**Objetivo:** Inclusão digital facilitada.
- **Formulário Simples:** Nome, Telefone (WhatsApp) e Cidade.
- **Área de Bio (O diferencial social):**
    - Campo de texto: "Conte sobre sua experiência".
    - **Botão Estilizado:** "✨ Ajustar com IA".
    - **Ação:** Ao clicar, um modal exibe o texto profissionalizado pelo motor de IA do Marcelo.

### 3. Tela de Perfil Detalhado
**Objetivo:** Gerar segurança para a contratação.
- **Topo:** Foto (opcional), Nome e Cidade de atuação.
- **Meio:** Bio profissional gerada pela IA e Lista de Serviços.
- **Rodapé Fixo:** Botão "📲 Entrar em Contato" (Link para WhatsApp).
- **Seção de Prova Social:** Exibição dos comentários do módulo Reviews.

## Elementos de Acessibilidade
- Tipografia legível (mínimo 16px para corpo de texto).
- Botões com área de toque mínima de 44x44px.
- Linguagem simplificada nos rótulos de formulário.
- Alto contraste entre texto e fundo.
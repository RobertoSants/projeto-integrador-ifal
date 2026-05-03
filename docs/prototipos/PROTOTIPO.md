# Documentação de UX/UI - Banco de Talentos Alagoas

## Visão Estratégica e Impacto Regional
O protótipo visual do **Banco de Talentos** foi projetado para ser o ponto de união entre tecnologia de ponta e a necessidade social do interior de Alagoas. Diferente de plataformas genéricas, o design foca na **localidade** e na **identidade cultural**, utilizando as cores da bandeira estadual (Azul, Vermelho e Branco) para gerar confiança e pertencimento no trabalhador e no contratante regional.

## Fidelidade Técnica (Conexão com Backend)
A interface traduz visualmente a lógica de programação estabelecida no `ENDPOINTS.md`:
- **Busca Regionalizada:** Implementa a lógica do endpoint `GET /api/search/`, utilizando o atributo `is_local` para destacar profissionais do mesmo município do contratante, fomentando a economia local.
- **Eixos Setoriais (AMA):** Categorização baseada nos pilares de desenvolvimento da Associação dos Municípios Alagoanos: Construção Civil, Serviços Domésticos, Produção Rural/Artesanato e Logística.
- **Módulo de Perfis:** Interface mapeada para o módulo `/api/workers/`, prevendo a exibição de `full_name`, `city`, `avg_rating` e contato direto via WhatsApp.

## Decisões de Design e Acessibilidade (UX)
1. **Mobile-First & Navegação:** Prioridade total para dispositivos móveis com a implementação de um **Menu Hambúrguer** funcional, garantindo que a navegação seja intuitiva em smartphones.
2. **Didática Simplificada:** Inclusão de uma seção "Como Funciona" em 4 passos com linguagem humana ("Diga o que faz", "Combine tudo no WhatsApp") para reduzir a barreira de entrada de usuários com baixo letramento digital.
3. **Integração com IA (NLP):** O design prevê o suporte assistido para a criação da "Bio", onde a inteligência artificial transforma rascunhos informais em perfis profissionais atraentes.
4. **Elementos Visuais:** 
   - Uso da fonte *Montserrat* para títulos (autoridade) e *Inter* para textos (legibilidade).
   - Badges de destaque "📍 LOCAL" para promover a retenção de renda no município.

## Especificações do Protótipo
- **Tecnologias:** HTML5, CSS3 (Flexbox/Grid) e JavaScript (Lógica de Menu).
- **Responsividade:** Suporte completo para Desktop, Tablet e Mobile através de Media Queries.
- **Identidade:** Estética baseada em Landing Page, adaptada para a paleta tricolor alagoana e fundo temático regional.
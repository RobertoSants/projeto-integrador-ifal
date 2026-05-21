# Documento de Viabilidade Técnica - Motor de IA (NLP)
**Banco de Talentos Comunitário — Projeto Integrador IFAL 2026.1**

## 1. Avaliação de Ferramentas de NLP
Para atender ao requisito de transformar relatos informais de trabalhadores do interior de Alagoas em biografias profissionais atraentes, foram avaliadas três abordagens de Processamento de Linguagem Natural:

* **NLTK (Natural Language Toolkit):** Excelente para tarefas acadêmicas, tokenização e lematização básica. Contudo, carece de modelos prontos e robustos de geração e reestruturação de texto contextualizado em português, exigindo regras manuais excessivas para o nosso escopo.
* **SpaCy:** Altamente eficiente para processamento industrial de texto e Reconhecimento de Entidades Nomeadas (NER) em português. Apesar de sua velocidade na análise sintática, não possui capacidade nativa de geração e reescrita criativa/profissional de texto sem o acoplamento de modelos adicionais complexos.
* **APIs de Grandes Modelos de Linguagem (OpenAI GPT / Google Gemini):** Fornecem a melhor capacidade de interpretação contextual, correção gramatical orgânica e adaptação de tom (transformar termos informais ou gírias em descrições corporativas limpas). Oferecem facilidade de integração via requisições HTTP REST, alinhando-se diretamente com a arquitetura cliente-servidor do nosso projeto.

## 2. Validação da Conversão de Relatos Informais
Os testes conceituais demonstram que as APIs baseadas em LLM conseguem interpretar de forma semântica as variações linguísticas regionais e reestruturar o perfil mantendo a fidelidade das competências informadas:

* *Entrada informal típica:* "Faço serviço de eba de pedreiro, bato laje, reboco parede e faço acabamento em banheiro. Atendo aqui na região de Penedo, só me chamar no zap."
* *Saída profissional gerada:* "Profissional especializado em Construção Civil com ampla experiência em serviços de alvenaria, aplicação de reboco, concretagem de lajes e acabamento fino em ambientes residenciais. Atuação focada no município de Penedo e regiões vizinhas, disponível para orçamentos diretos via WhatsApp."

## 3. Levantamento Teórico para Evolução Futura (Speech-to-Text)
Com foco em mitigar as barreiras do baixo letramento digital em comunidades do interior, foi mapeado o modelo **OpenAI Whisper** para implementações futuras:
* **Viabilidade:** O Whisper é um sistema de reconhecimento automático de fala (ASR) de código aberto com alta precisão para o português brasileiro, inclusive capturando sotaques e variações regionais.
* **Escopo Atual:** Para o MVP atual (com prazo final em 02/06/2026), o desenvolvimento ficará restrito exclusivamente à entrada e processamento de dados por texto. A integração de áudio (Speech-to-Text) permanecerá documentada como proposta de evolução do sistema para versões pós-MVP.

## 4. Tecnologia Base Escolhida
A tecnologia escolhida para o módulo de IA é a **Integração via API REST (Google Gemini / OpenAI)** utilizando engenharia de prompt especializada. Esta escolha garante máxima qualidade na reescrita dos perfis sem inflar o tamanho do repositório nem demandar alto processamento de hardware local (visto que o deploy rodará em servidores leves de desenvolvimento).
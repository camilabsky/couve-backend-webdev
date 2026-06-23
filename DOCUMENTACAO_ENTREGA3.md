# Documento da Entrega 3 - Couve

## Descricao do Sistema

O sistema Couve e uma aplicacao web para gestao colaborativa de atividades, recompensas e acompanhamento de progresso em um contexto comunitario. A proposta e permitir que usuarios autenticados aceitem tarefas, concluam atividades e resgatem recompensas de forma organizada, com regras de negocio claras e controle de acesso.

A solucao possui duas frentes integradas:

1. Interface web para navegacao, autenticacao e operacao do sistema.
2. API REST para integracao e consumo de dados, incluindo autenticacao por JWT.

Com isso, o sistema atende tanto ao uso direto por navegador quanto a integracoes futuras com aplicacoes externas, como app mobile e dashboards.

Objetivos principais:

1. Organizar tarefas e recompensas com fluxo simples e consistente.
2. Garantir seguranca no acesso a dados e operacoes sensiveis.
3. Disponibilizar API padronizada e documentavel.
4. Manter base de codigo modular e preparada para evolucao.

## Requisitos Funcionais

1. O sistema deve exibir uma landing page publica na rota inicial.
2. O sistema deve permitir autenticacao de usuarios por login e senha.
3. O sistema deve permitir logout de usuarios autenticados.
4. O sistema deve restringir paginas privadas a usuarios autenticados (home, tarefas, recompensas e perfil).
5. O sistema deve listar tarefas disponiveis.
6. O sistema deve permitir aceitar tarefa disponivel.
7. O sistema deve permitir concluir tarefa aceita.
8. O sistema deve calcular saldo do perfil com base em moedas obtidas e recompensas resgatadas.
9. O sistema deve listar recompensas disponiveis.
10. O sistema deve permitir resgatar recompensa quando houver saldo e estoque.
11. O sistema deve disponibilizar endpoint para obter dados do usuario autenticado.
12. O sistema deve disponibilizar endpoints de autenticacao JWT (obtencao de token e refresh).
13. O sistema deve disponibilizar endpoint protegido por JWT para validacao de acesso.
14. O sistema deve disponibilizar API REST de recompensas via ViewSet.
15. O sistema deve permitir leitura publica de recompensas e exigir JWT para operacoes de escrita no ViewSet.
16. O sistema deve apresentar mensagens de feedback para sucesso, aviso e erro nas operacoes principais.

## Requisitos Nao Funcionais

1. Seguranca: endpoints sensiveis devem exigir autenticacao e autorizacao adequadas.
2. Seguranca: uso de JWT para autenticacao de API e protecao de escrita em recursos criticos.
3. Usabilidade: interface com navegacao clara e fluxo de uso direto para as operacoes principais.
4. Confiabilidade: validacoes de negocio devem impedir estados invalidos (saldo insuficiente, tarefa ja concluida etc.).
5. Manutenibilidade: organizacao do codigo por camadas (models, views, urls, templates, serializers).
6. Escalabilidade evolutiva: estrutura preparada para ampliar endpoints e entidades sem refatoracoes disruptivas.
7. Portabilidade: execucao local simples com Python, ambiente virtual e banco SQLite.
8. Observabilidade basica: mensagens de sistema e respostas HTTP padronizadas para facilitar testes e debug.
9. Versionamento: historico de alteracoes no GitHub com commits rastreaveis.
10. Compatibilidade: API no padrao REST com JSON para integracao com diferentes clientes.

## Arquitetura Proposta

A arquitetura segue o padrao de aplicacao web em camadas, baseada em Django + Django REST Framework.

Camadas principais:

1. Camada de Apresentacao
- Templates HTML e rotas de interface.
- Controle de exibicao condicional de navegacao conforme autenticacao.
- Formularios de login e acoes de usuario.

2. Camada de Aplicacao
- Views responsaveis por orquestrar casos de uso.
- Controle de autenticacao e permissoes.
- Regras de fluxo (aceitar/concluir tarefa, resgatar recompensa).

3. Camada de API
- Endpoints REST para recursos do sistema.
- ViewSet de recompensas com politica hibrida de acesso (leitura publica, escrita autenticada).
- Endpoints JWT para autenticacao stateless.

4. Camada de Dominio/Persistencia
- Modelos relacionais para perfis, tarefas, recompensas e vinculo de resgates.
- Regras de consulta e agregacao.
- Persistencia em banco relacional (SQLite no ambiente atual).

### Estrategia de Banco de Dados Orientado a Eventos

A arquitetura do banco de dados foi pensada com abordagem orientada a eventos, baseada na captura, armazenamento e processamento de mudancas de estado ao longo do tempo. Nesse contexto, eventos de negocio como:

- tarefa aceita,
- tarefa concluida,
- recompensa resgatada,

representam transicoes relevantes de estado e servem como base para calculos e visoes agregadas.

Para suportar processamentos dinamicos, o saldo do usuario deve ser exposto por meio de uma view de banco dedicada, por exemplo `vw_saldo_usuario`, consolidando ganhos (tarefas concluidas) e gastos (recompensas resgatadas). Essa abordagem melhora consistencia de leitura, facilita auditoria de eventos e simplifica consultas no backend.

Fluxo resumido:

1. Usuario autentica via sessao web para uso das paginas privadas.
2. Cliente API autentica via JWT para acessar endpoints protegidos.
3. Operacoes de negocio validam pre-condicoes antes de persistir alteracoes.
4. Respostas retornam estado atualizado ou erro de negocio de forma explicita.

## Padroes de Projeto Escolhidos

1. MVT (Model-View-Template)
- Estrutura nativa do Django para separar dados, logica e apresentacao.
- Beneficio: clareza estrutural e produtividade no desenvolvimento web.

2. Repository implicito via ORM
- O Django ORM abstrai acesso ao banco com consultas declarativas.
- Beneficio: reducao de SQL acoplado e maior manutencao.

3. Controller/Service style nas views
- Views centralizam o fluxo de casos de uso e regras de operacao.
- Beneficio: regra de negocio aplicada de forma consistente por endpoint.

4. Serializer Pattern (DRF)
- Serializers transformam modelos em JSON e validam entrada de dados.
- Beneficio: padronizacao do contrato da API.

5. Strategy de permissao por metodo HTTP
- No ViewSet, permissoes mudam conforme tipo de operacao (leitura x escrita).
- Beneficio: politica de seguranca flexivel sem duplicar endpoints.

6. Token-Based Authentication (JWT)
- Autenticacao stateless para API com access e refresh token.
- Beneficio: escalabilidade de integracao e desacoplamento da sessao do navegador.

7. Template base com heranca
- Reaproveitamento de layout e componentes comuns.
- Beneficio: consistencia visual e menor duplicacao de codigo.

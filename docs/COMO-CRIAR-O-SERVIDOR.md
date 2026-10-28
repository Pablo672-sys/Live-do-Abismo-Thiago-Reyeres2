# Servidor do Boneco do Abismo — funcionamento pela nuvem

## O que a pessoa que usa o site precisa fazer?

**Só abrir o site no celular.** A pessoa que visita o site não deve precisar instalar Python, abrir o programa do Windows nem deixar o próprio computador ligado — desde que o responsável pelo projeto já tenha publicado o backend numa nuvem e configurado o endereço HTTPS dele no site.

O servidor é configurado **uma vez pelo responsável pelo projeto**, não por cada visitante. Se o backend ainda não estiver hospedado, o site sozinho não consegue executar a IA, gerar voz ou transmitir uma live.

## Como funciona

1. O responsável pelo projeto publica a interface no GitHub Pages.
2. O responsável configura o backend do Boneco do Abismo num servidor de nuvem compatível.
3. O backend recebe uma URL pública HTTPS, com segurança e autenticação adequadas.
4. Essa URL é configurada na interface do site.
5. Depois disso, os visitantes abrem o site pelo Safari ou outro navegador e usam as funções disponíveis sem iniciar um servidor no Windows deles.

## Escolher uma hospedagem compatível

O backend deste projeto usa Python/FastAPI e inclui serviços que podem envolver Ollama, modelos de IA, Coqui XTTS/PyTorch, monitoramento de eventos e transmissão de live. Uma hospedagem estática, como GitHub Pages, não executa esses serviços.

Antes de contratar uma VPS ou outro serviço, confirme que o plano permite:

- executar uma aplicação Python continuamente e reiniciá-la após falhas;
- instalar as dependências do projeto e executar processos em segundo plano;
- fornecer RAM, CPU, armazenamento e, se necessário, GPU suficientes para IA e voz;
- permitir a conexão com os serviços externos necessários à live;
- configurar HTTPS, firewall e autenticação.

Uma VPS costuma ter custo mensal. Planos gratuitos podem suspender aplicações por inatividade, limitar recursos ou não suportar modelos de IA e transmissão contínua. **Não existe garantia de que todo o sistema funcione 24/7 gratuitamente** sem testar uma hospedagem compatível.

## Publicação do backend na nuvem

1. Crie uma máquina/serviço no provedor escolhido, compatível com os requisitos acima.
2. Baixe o repositório privado ou público na máquina e siga o README principal para instalar e configurar o backend.
3. Configure as variáveis de ambiente e credenciais no painel seguro do provedor. Nunca coloque senhas, tokens de live ou chaves privadas no GitHub.
4. Configure o processo para iniciar automaticamente e reiniciar após falhas.
5. Configure domínio, HTTPS válido, firewall e autenticação. Não exponha um painel administrativo sem proteção.
6. Teste cada recurso separadamente: painel, IA, voz, comentários/presentes e transmissão. O fato de a página abrir não prova que todos os recursos estão funcionando.
7. Configure na interface do site o endereço HTTPS público real do backend. Não use `localhost`, `127.0.0.1` nem IPs privados nesse campo para acesso pela internet.

## Como instalar o site no iPhone

1. Abra o endereço do site no Safari.
2. Toque em Compartilhar.
3. Escolha **Adicionar à Tela de Início**.
4. Toque em **Adicionar**.

## Se ainda não estiver funcionando

O endereço do site e o servidor são duas partes diferentes. O GitHub Pages publica a interface, mas não cria automaticamente o backend. Se o responsável ainda não configurou uma hospedagem compatível, as funções de IA, voz e live não ficarão disponíveis apenas por abrir o site.

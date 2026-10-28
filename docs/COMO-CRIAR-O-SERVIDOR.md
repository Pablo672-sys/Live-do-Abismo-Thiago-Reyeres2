# Como criar o servidor do Boneco do Abismo

Este guia explica como ligar o site do Boneco do Abismo ao servidor que executa a IA, a voz e os recursos da live.

> **Importante:** publicar o site no GitHub Pages não cria o servidor da IA. O site é apenas a interface. Para IA local com Ollama, voz XTTS e transmissão de live, o servidor precisa ter recursos e programas compatíveis. Não existe um botão que hospede tudo gratuitamente e para sempre.

## Escolha onde o servidor vai rodar

- **Teste no seu próprio Windows:** não custa hospedagem, mas o computador precisa ficar ligado enquanto alguém usa o servidor. É indicado para testar antes de publicar.
- **Servidor na nuvem (VPS):** fica ligado 24 horas, mesmo com seu computador desligado, mas normalmente custa por mês. Confira RAM, CPU/GPU, armazenamento, limites de tráfego e regras do provedor antes de contratar.
- **Hospedagem gratuita:** pode servir para uma demonstração leve, mas serviços gratuitos podem dormir, limitar recursos ou não aceitar dependências pesadas. Não conte com isso para Ollama, XTTS e transmissão contínua sem testar.

## Opção A — testar no Windows 11

Estes passos são para quem tem o código do projeto no computador.

1. Instale Python 3.12 e Git para Windows.
2. Baixe/clonе o repositório:
   ```powershell
   git clone https://github.com/Pablo672-sys/Live-do-Abismo-Thiago-Reyeres2.git
   cd Live-do-Abismo-Thiago-Reyeres2
   ```
3. Crie e ative um ambiente virtual:
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   Se o PowerShell bloquear a ativação, tente abrir o terminal do VS Code como usuário normal e executar:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```
4. Instale as dependências básicas:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Consulte o README principal e o arquivo `.env.example` para configurar variáveis e serviços opcionais. **Não publique senhas, tokens de live, chaves de API nem arquivos `.env` no GitHub.**
6. Inicie a aplicação seguindo o comando de execução documentado no README principal. Se o README não tiver um comando de inicialização válido para a versão atual, abra uma issue no repositório com o erro completo em vez de adivinhar o comando.
7. Quando o servidor iniciar, teste primeiro no próprio computador. A porta e o endereço exatos devem ser os mostrados no terminal; não presuma que o servidor já está acessível pela internet.

### Para acessar pelo iPhone durante o teste

O iPhone e o computador precisam estar na mesma rede Wi-Fi para um teste local. Use no Safari o endereço de rede local mostrado/configurado no computador. Um endereço como `127.0.0.1` funciona apenas dentro do próprio dispositivo — não serve para acessar o PC pelo iPhone.

**Não exponha a porta do servidor diretamente à internet.** Para acesso remoto, use um serviço de túnel HTTPS confiável com autenticação ou configure o servidor em nuvem com HTTPS, firewall e autenticação. Nunca compartilhe um painel administrativo sem senha.

## Opção B — servidor na nuvem para ficar ligado

1. Escolha um provedor de VPS que permita executar Python, processos em segundo plano e os componentes de que o projeto realmente precisa.
2. Antes de pagar, confira se o plano suporta a memória e o armazenamento exigidos pela IA/voz. Ollama precisa de espaço para baixar o modelo; XTTS/PyTorch também pode consumir bastante RAM e CPU. Transmissão de live pode exigir programas e permissões adicionais.
3. Crie uma máquina Linux ou Windows conforme os requisitos do projeto e mantenha o sistema atualizado.
4. Baixe o repositório na máquina e siga o README principal para instalar dependências e configurar os serviços. Não copie tokens ou senhas para arquivos públicos.
5. Configure o processo para reiniciar após falhas e reinicializações, usando o gerenciador de serviços apropriado ao sistema.
6. Configure um domínio ou subdomínio, HTTPS válido, firewall e autenticação. Abra somente as portas necessárias.
7. Teste separadamente: página do painel, conexão com IA, voz, eventos de chat/presentes e transmissão. Um servidor web respondendo não significa que todos esses componentes estão funcionando.
8. No site do iPhone, informe o **endereço HTTPS público real** do servidor. Não coloque `localhost`, `127.0.0.1` ou um IP privado como `192.168.x.x` nesse campo para acesso pela internet.

## Antes de pedir ajuda

Envie:
- o sistema operacional e o provedor escolhido;
- o passo em que parou;
- o erro completo do terminal (remova tokens, senhas e dados privados);
- quais funções você precisa: painel, IA, voz, chat/presentes ou transmissão.

## O que é necessário para ficar realmente 24/7?

- Uma máquina/serviço ligado continuamente;
- recursos suficientes para o modelo de IA e a voz;
- URL pública com HTTPS;
- configurações seguras e credenciais privadas;
- testes reais de cada recurso.

O GitHub Pages pode continuar hospedando a interface gratuitamente, mas **não executa Ollama, Python, XTTS nem o transmissor de live**. A disponibilidade e o custo do backend dependem do provedor escolhido.

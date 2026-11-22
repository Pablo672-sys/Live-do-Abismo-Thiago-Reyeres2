# Ollama no Boneco do Abismo (Windows 10/11)

Este guia configura a IA de texto local do Boneco do Abismo. A geração de respostas usa o Ollama instalado no próprio computador. Não é necessário criar conta, informar chave de API ou pagar por chamadas de IA.

> Importante: o Ollama substitui somente a IA de texto. A voz/XTTS, os vídeos, o renderer, o monitor do TikTok, Tor e a transmissão continuam sendo componentes separados.

## 1. Requisitos

- Windows 10 ou 11 de 64 bits.
- Ollama instalado.
- Python 3.12 para instalar/executar o Boneco.
- Espaço livre para o modelo (o modelo `llama3.2:3b` ocupa aproximadamente 2 GB, além dos arquivos do programa).

## 2. Instalar o Ollama

1. Abra o site oficial: https://ollama.com/download
2. Baixe o instalador para Windows.
3. Execute o instalador e conclua a instalação.
4. Abra uma nova janela do PowerShell.

Para conferir a instalação:

```powershell
ollama --version
```

Se o comando não for reconhecido, feche e abra o PowerShell novamente. Se continuar, reinicie o Windows e confira se o Ollama foi instalado pelo site oficial.

## 3. Baixar o modelo de IA

No PowerShell, execute:

```powershell
ollama pull llama3.2:3b
```

Espere o download terminar. Depois confira:

```powershell
ollama list
```

A lista deve mostrar `llama3.2:3b`.

## 4. Testar o modelo antes de abrir o Boneco

Execute:

```powershell
ollama run llama3.2:3b
```

Digite uma mensagem, por exemplo:

```text
Responda em português brasileiro: olá, Boneco do Abismo!
```

Para sair do modo de conversa, digite `/bye`.

## 5. Verificar a API local do Ollama

O Boneco acessa o Ollama em `http://127.0.0.1:11434`. Para verificar se o serviço responde:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Se houver erro de conexão, abra outra janela do PowerShell e execute:

```powershell
ollama serve
```

Deixe essa janela aberta enquanto usa o Boneco. Em instalações normais do Ollama para Windows, o aplicativo pode manter o serviço ativo em segundo plano.

## 6. Configuração do Boneco

O código usa estes padrões:

- Provedor: Ollama local.
- Endereço: `http://127.0.0.1:11434`.
- Modelo: `llama3.2:3b`.
- Temperatura: `0.55`.

Opcionalmente, crie o arquivo `private/live_text_ai.json` (a pasta `private` será criada se necessário) com:

```json
{
  "provider": "ollama",
  "ollama_url": "http://127.0.0.1:11434",
  "ollama_model": "llama3.2:3b",
  "temperature": 0.55
}
```

Não coloque senhas, tokens de transmissão ou credenciais privadas nesse arquivo. Ele é uma configuração local e não deve ser enviado para um repositório público.

## 7. Baixar e executar o Boneco

1. Abra o repositório: https://github.com/Pablo672-sys/Live-do-Abismo-Thiago-Reyeres2
2. Clique em **Code** e depois **Download ZIP**.
3. Extraia o ZIP para uma pasta simples, por exemplo `C:\Boneco-do-Abismo`.
4. Instale Python 3.12, se ainda não tiver: https://www.python.org/downloads/
5. Abra a pasta extraída.
6. Execute `INSTALAR.bat` e aguarde a instalação.
7. Para iniciar depois, execute `INICIAR PAINEL.bat`.
8. Abra `http://127.0.0.1:9292` no navegador.

Mantenha o Ollama ativo enquanto o Boneco precisar gerar respostas. A instalação do painel não configura automaticamente XTTS, áudio, Tor, vídeos, chaves do TikTok ou transmissão.

## 8. Diagnóstico rápido

### Erro: connection refused / não foi possível acessar Ollama

- Confira se o Ollama está aberto.
- Teste `Invoke-RestMethod http://127.0.0.1:11434/api/tags`.
- Se necessário, execute `ollama serve` em outra janela.

### Erro: model not found

Execute:

```powershell
ollama pull llama3.2:3b
ollama list
```

O nome do modelo configurado precisa corresponder exatamente a um nome exibido por `ollama list`.

### O Boneco responde com texto de fallback

Confira os arquivos de diagnóstico na pasta `runs`:

- `text_ai.log`
- `text_ai_errors.log`

Eles registram o provedor, modelo, tempo de resposta e falhas de conexão. Não compartilhe logs sem revisar se contêm informações privadas.

### O PC fica lento

Modelos locais usam CPU e memória; o desempenho depende do computador. Feche programas pesados e evite executar vários modelos simultaneamente. É possível trocar o modelo em `private/live_text_ai.json`, desde que ele esteja instalado no Ollama.

## 9. Privacidade e custos

- As solicitações de geração de texto são enviadas ao serviço local do Ollama em `127.0.0.1`.
- Esta integração não envia prompts para a API da OpenAI.
- O download inicial do instalador e do modelo exige internet.
- Depois de baixado, o modelo pode gerar texto localmente sem pagar por uso de API.
- O monitor TikTok, downloads, atualizações e outros serviços podem continuar precisando de internet.

## 10. Voz e transmissão

Esta atualização não troca a voz do Boneco e não inicia uma live automaticamente. O Ollama gera somente o texto; o sistema de voz existente continua responsável por transformar a fala em áudio. Faça os testes de áudio e transmissão separadamente e nunca publique tokens ou chaves no GitHub.

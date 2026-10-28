# Iniciar o Boneco do Abismo no Windows e abrir pelo iPhone

## O que a pessoa precisa fazer

1. No PC Windows, baixe o projeto pelo botão **Code → Download ZIP** no GitHub e extraia a pasta. Também pode usar Git se já estiver instalado.
2. Instale **Python 3.12** para Windows. Durante a instalação, marque **Add Python to PATH**.
3. Dentro da pasta extraída, clique com o botão direito em `start_boneco_windows.ps1` e escolha **Executar com PowerShell**. Se a política do Windows bloquear o script, abra o PowerShell dentro da pasta e execute:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\start_boneco_windows.ps1
   ```
4. Na primeira execução, o script cria o ambiente virtual e instala as dependências. Isso pode demorar e precisa de internet. Mantenha a janela aberta.
5. Quando o servidor iniciar, o terminal mostrará os endereços locais. No próprio PC, teste `http://127.0.0.1:9292`.
6. Conecte o iPhone à mesma rede Wi-Fi do PC. Abra o site do Boneco no Safari e, na seção **Abrir o painel**, digite o endereço de rede mostrado pelo script, por exemplo `http://192.168.1.50:9292). Use o IP real mostrado no seu terminal e toque em **Abrir painel**.

## Se o iPhone não conseguir conectar

- Confirme que os dois aparelhos estão na mesma rede Wi-Fi, não em redes de convidados diferentes.
- No Windows, aceite o aviso do Firewall para permitir Python em **redes privadas**. Se não aparecer aviso, peça ajuda para liberar a porta TCP 9292 somente na rede privada.
- Não use `127.0.0.1` no iPhone: esse endereço aponta para o próprio celular, não para o PC.
- Não abra a porta do servidor diretamente para a internet. Este guia é para rede local confiável.

## Limites importantes

- O PC precisa ficar ligado e a janela do servidor aberta enquanto o celular usa o painel.
- O script prepara o servidor web e as dependências Python básicas. Ele não baixa automaticamente os modelos de IA, não configura credenciais do TikTok, Tor, XTTS ou transmissão RTMP. Esses recursos precisam ser configurados conforme o README principal e os arquivos privados de configuração.
- O GitHub Pages hospeda apenas a página de entrada; não executa o backend Python.
- Não compartilhe tokens de live, senhas nem arquivos privados no GitHub.

# Como Funciona o Remote Desktop

Este documento explica, em linguagem simples, como o sistema funciona por dentro.

---

## Visão Geral

Você quer ver a tela do seu notebook no seu tablet e controlá-lo com toques.
Para isso, o sistema tem **3 partes** que se comunicam:

```
[Tablet Android]  ←→  [Servidor de Sinalização]  ←→  [Notebook Windows]
    Recebe vídeo           (na nuvem, grátis)           Envia vídeo
    Envia toques                                         Recebe toques
```

---

## Parte 1 — O Servidor de Sinalização (Node.js no Render.com)

**O que faz:** É um "matchmaker" — ele apresenta o Android ao Windows para que os dois possam se conectar diretamente depois.

**Por que precisamos disso:** O Android e o Windows não sabem o endereço IP um do outro. O servidor de sinalização fica na internet (URL fixa) e serve como ponto de encontro.

**Como funciona na prática:**
1. O Windows inicia e diz ao servidor: *"Estou na sala 'meu-desktop', aguardando alguém"*
2. O Android abre o app e diz: *"Quero entrar na sala 'meu-desktop'"*
3. O servidor avisa o Windows: *"Chegou alguém!"*
4. O Windows cria uma **oferta WebRTC** (um documento técnico dizendo como ele pode se comunicar) e manda ao Android pelo servidor
5. O Android aceita e manda de volta uma **resposta WebRTC**
6. Os dois trocam **candidatos ICE** (possíveis caminhos de rede para se conectar)
7. A partir daqui, Windows e Android se comunicam **diretamente**, sem passar pelo servidor

**Tecnologia usada:** Socket.IO (biblioteca que permite comunicação em tempo real)

---

## Parte 2 — O Servidor Windows (Python)

É um programa que roda em segundo plano no seu notebook.

### 2a. Captura de Tela (`capture.py`)

**O que faz:** Tira "foto" da tela do Windows dezenas de vezes por segundo e empacota como vídeo.

**Como funciona:**
- Usa a biblioteca `dxcam` que acessa diretamente a placa de vídeo do Windows (muito rápido)
- Cada frame capturado é uma imagem no formato BGR (azul, verde, vermelho)
- O `aiortc` pega essas imagens e as codifica em **H.264** (o mesmo formato de vídeos do YouTube)
- O resultado é um stream de vídeo que vai para o Android

### 2b. Injeção de Input (`input_handler.py`)

**O que faz:** Recebe comandos do Android e simula que você está usando o mouse e o teclado.

**Comandos que recebe (em formato JSON):**
```json
{ "type": "mouse_move", "x": 0.5, "y": 0.25 }
→ Move o cursor para o centro-esquerda da tela

{ "type": "mouse_click", "button": "left" }
→ Clica com o botão esquerdo

{ "type": "key_type", "text": "hello" }
→ Digita "hello"
```

**Por que as coordenadas são 0 a 1 (e não pixels)?**
O Android não sabe a resolução do seu monitor. Então ele manda a posição proporcional (0 = borda esquerda/topo, 1 = borda direita/baixo) e o Windows converte para pixels reais.

**Tecnologia:** `pynput` — biblioteca Python que controla mouse e teclado programaticamente.

### 2c. Conexão WebRTC (`peer.py`)

**O que faz:** Estabelece a conexão de vídeo com o Android e cria um canal para receber os comandos de input.

**Dois canais dentro da mesma conexão WebRTC:**
- **Video Track:** envia a captura de tela como stream de vídeo
- **Data Channel:** canal bidirecional para troca de mensagens (aqui: comandos de input em JSON)

---

## Parte 3 — O App Android (Kotlin)

### 3a. SignalingClient

**O que faz:** Conversa com o servidor de sinalização para configurar a conexão.

Segue o protocolo:
```
Android → servidor: "join meu-desktop"
Windows → servidor: oferece conexão WebRTC
Servidor → Android: "chegou uma oferta"
Android → servidor: resposta WebRTC
Android → servidor: candidatos ICE
Windows → servidor: candidatos ICE
[conexão P2P estabelecida]
```

### 3b. WebRTCManager

**O que faz:** Gerencia a conexão WebRTC com o Windows.

- Configura servidores STUN e TURN para passar pelo roteador/NAT
- Recebe o Video Track (stream da tela) e entrega para a view
- Recebe o Data Channel e entrega para o InputForwarder

### 3c. RemoteSurfaceView

**O que faz:** Exibe o vídeo recebido e captura toques do usuário.

- Herda de `SurfaceViewRenderer` (view especializada do WebRTC SDK para vídeo de baixa latência)
- Quando você toca na tela: captura as coordenadas (X, Y) e converte para proporção 0-1
- Implementa `onCreateInputConnection` para permitir que o teclado Android apareça quando você toca nela

### 3d. InputForwarder

**O que faz:** Converte gestos e teclas em comandos JSON e envia pelo Data Channel.

```
Você toca em (480, 270) numa tela de 960x540
→ normaliza: x = 480/960 = 0.5, y = 270/540 = 0.5
→ manda JSON: {"type":"mouse_move","x":0.5,"y":0.5}
→ Windows recebe e move o cursor para o centro da tela
```

---

## O Que é WebRTC?

WebRTC (Web Real-Time Communication) é uma tecnologia open-source criada pelo Google, usada em:
- Google Meet
- Discord (chamadas de vídeo)
- WhatsApp Web

Ela permite comunicação de vídeo/áudio/dados **ponto a ponto** (sem precisar de servidor no meio) com criptografia automática.

### STUN vs TURN — Passando pelo Roteador

Seu notebook e seu tablet ficam atrás de roteadores que atribuem IPs privados (192.168.x.x). Para se conectar pela internet, precisam descobrir seus IPs públicos:

**STUN (Session Traversal Utilities for NAT):**
- Servidor gratuito do Google: `stun.l.google.com:19302`
- Pergunta: *"Qual é o meu IP público?"*
- Funciona na maioria dos casos

**TURN (Traversal Using Relays around NAT):**
- Usado como fallback quando o P2P falha (redes corporativas, NAT simétrico)
- Serve como relay: o vídeo passa pelo servidor TURN
- Usamos o **Open Relay Project** (20 GB grátis por mês)

---

## Fluxo Completo de Uma Sessão

```
1. Você inicia python main.py no Windows
   → Windows conecta no servidor de sinalização
   → Windows entra na sala "meu-desktop"

2. Você abre o app no tablet
   → Android conecta no servidor de sinalização
   → Android entra na sala "meu-desktop"

3. Servidor avisa o Windows: "peer-ready"
   → Windows cria oferta WebRTC (SDP offer)
   → Windows manda oferta para o Android via servidor

4. Android recebe oferta
   → Android cria resposta (SDP answer)
   → Android manda resposta para o Windows via servidor

5. Windows e Android trocam candidatos ICE
   → Cada um lista formas possíveis de se conectar
   → Testam qual funciona melhor (P2P direto ou via TURN)

6. Conexão estabelecida!
   → Windows começa a capturar tela e enviar como vídeo H.264
   → Android exibe o vídeo na RemoteSurfaceView
   → Seus toques viram comandos JSON que chegam no Windows
   → Windows injeta os comandos como mouse e teclado reais
```

---

## Por Que Essa Abordagem?

| Alternativa | Problema |
|---|---|
| VNC/RDP prontos (AnyDesk, TeamViewer) | Não é do zero, objetivo é aprender |
| WebSocket para vídeo | Teria que implementar buffering, controle de qualidade, criptografia manualmente |
| WebRTC | Cuida de tudo isso automaticamente, é o padrão da indústria para streaming P2P |
| FFmpeg + streaming HTTP | Alta latência, não é interativo |

**WebRTC com aiortc (Python) + Google WebRTC SDK (Android) é o melhor stack** para este caso: baixa latência, P2P, criptografia automática, funciona pela internet.

---

## Estrutura de Arquivos

```
remote-desktop/
├── signaling/           → Servidor Node.js (hospedado no Render.com)
│   └── server.js        → Gerencia salas e repassa SDP/ICE entre pares
├── windows/             → Roda no seu notebook
│   ├── main.py          → Inicia tudo
│   ├── capture.py       → Captura a tela (dxcam)
│   ├── input_handler.py → Injeta mouse/teclado (pynput)
│   └── peer.py          → Conexão WebRTC (aiortc)
└── android/             → App Kotlin
    └── app/src/main/java/com/remotedesktop/
        ├── MainActivity.kt      → Ponto de entrada, inicializa tudo
        ├── SignalingClient.kt   → Conversa com o servidor via Socket.IO
        ├── WebRTCManager.kt     → Gerencia RTCPeerConnection
        ├── RemoteSurfaceView.kt → Exibe vídeo + captura toques
        └── InputForwarder.kt    → Converte gestos em JSON
```

---

## Como Usar (Resumo)

1. **Deploy do servidor de sinalização** no Render.com (Task 10 do plano)
2. **Atualizar a URL** no `main.py` e `MainActivity.kt`
3. No notebook: `python remote-desktop/windows/main.py`
4. No tablet: abrir o app → ver a tela do notebook → controlar com toques

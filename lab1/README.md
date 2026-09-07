# Laboratório 1
## Servidor Web HTTP com Python

Projeto desenvolvido para a disciplina **MC833 - Programação de Redes de Computadores**.

**Aluna:** Ana Carolina de Almeida Cardoso  
**RA:** 246914

### Descrição

O projeto implementa um servidor Web em Python utilizando **sockets TCP** para receber e processar requisições **HTTP GET**.

O servidor é capaz de:

- receber requisições enviadas por um navegador;
- identificar o arquivo solicitado;
- buscar o arquivo no diretório local do servidor;
- responder com `200 OK` quando o arquivo é encontrado;
- responder com `404 Not Found` quando o arquivo não existe;
- atender múltiplas conexões simultaneamente utilizando **threads**.

Cada conexão aceita pelo servidor é atendida em uma thread separada, permitindo que a thread principal continue aguardando novas conexões.

### Estrutura do projeto

```text
lab1/
├── servidor.py
├── index.html
├── pagina2.html
├── style.css
├── imagem1.jpg
├── imagem2.jpg
├── imagem3.jpg
└── README.md
```
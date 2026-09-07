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

### Execução

Execute o servidor:

```python
python3 servidor.py
```

O servidor utiliza a porta 8000.

Para testar na própria máquina, digite no navegador:

```bash
http://localhost:8000/index.html
```

Para acessar a partir de outra máquina na mesma rede, utilize o endereço IP da máquina que está executando o servidor:

```bash
http://<IP_DO_SERVIDOR>:8000/index.html
```

Por exemplo:

```bash
http://192.168.15.56:8000/index.html
```

Para encerrar o servidor, pressione `Ctrl+C`. 
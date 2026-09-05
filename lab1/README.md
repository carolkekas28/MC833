# Servidor Web HTTP com Python

Projeto desenvolvido para a disciplina **MC833 - Programação de Redes de Computadores**.

**Aluna:** Ana Carolina de Almeida Cardoso  
**RA:** 246914

## Descrição

O projeto implementa um servidor Web em Python utilizando **sockets TCP** para receber e processar requisições **HTTP GET**.

O servidor é capaz de:

- receber requisições enviadas por um navegador;
- identificar o arquivo solicitado;
- buscar o arquivo no diretório local;
- responder com `200 OK` quando o arquivo é encontrado;
- responder com `404 Not Found` quando o arquivo não existe;
- atender múltiplas conexões simultaneamente utilizando **threads**.

## Estrutura do projeto

```text
MC833_ServidorWeb/
├── servidor.py
├── index.html
├── pagina2.html
├── style.css
├── imagem1.jpg
├── imagem2.jpg
├── imagem3.jpg
└── README.md
````

## Execução

No terminal, acesse o diretório do projeto e execute:

```bash
python3 servidor.py
```

O servidor utiliza a porta `8000`.

Para testar na própria máquina:

```text
http://localhost:8000/index.html
```

Para testar a partir de outra máquina na mesma rede, utilize o endereço IP do computador servidor:

```text
http://<IP_DO_SERVIDOR>:8000/index.html
```

## Testes realizados

Foram realizados testes de:

* acesso local;
* acesso por outra máquina na mesma rede;
* carregamento de arquivos HTML, CSS e imagens;
* resposta `200 OK`;
* resposta `404 Not Found`;
* atendimento concorrente por meio de múltiplas threads.

## Observação

O projeto foi desenvolvido com finalidade acadêmica para demonstrar conceitos de comunicação cliente-servidor, sockets TCP, protocolo HTTP e concorrência com threads.
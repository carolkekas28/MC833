# IP local da minha máquina: 192.168.15.56
from socket import *
import threading
import os
import mimetypes
import sys

HOST = '0.0.0.0'
PORT = 8000


def atender_cliente(connectionSocket, addr):

    print(f"[CONEXÃO] Cliente conectado: {addr}")

    try:
        # Recebe a requisição HTTP enviada pelo navegador.
        message = connectionSocket.recv(4096).decode('utf-8')

        if not message:
            print(f"[AVISO] Cliente {addr} fechou a conexão sem enviar requisição.")
            return

        print(f"\n[REQUISIÇÃO DE {addr}]")
        print(message)

        # Obtém a primeira linha da requisição HTTP
        # Exemplo: GET /index.html HTTP/1.1
        primeira_linha = message.splitlines()[0]

        partes = primeira_linha.split()

        if len(partes) < 2:
            print(f"[ERRO] Requisição inválida de {addr}: {primeira_linha}")
            return

        metodo = partes[0]
        caminho = partes[1]

        # Processamento de requisições GET
        if metodo != "GET":
            resposta = (
                "HTTP/1.1 405 Method Not Allowed\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                "Connection: close\r\n"
                "\r\n"
                "<html><body><h1>405 Method Not Allowed</h1></body></html>"
            )

            connectionSocket.sendall(resposta.encode('utf-8'))
            return

        # Caso seja acessado apenas http://IP:8000/, entregamos index.html
        if caminho == "/":
            caminho = "/index.html"

        filename = caminho.lstrip("/")

        # Evita acesso a arquivos fora do diretório do servidor
        filename = os.path.normpath(filename)

        if filename.startswith(".."):
            raise FileNotFoundError

        # Tenta abrir o arquivo solicitado
        with open(filename, "rb") as arquivo:
            outputdata = arquivo.read()

        # Identifica o tipo de arquivo
        tipo_conteudo, _ = mimetypes.guess_type(filename)

        if tipo_conteudo is None:
            tipo_conteudo = "application/octet-stream"

        # Cabeçalho HTTP 200 OK
        header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {tipo_conteudo}\r\n"
            f"Content-Length: {len(outputdata)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        # Envia cabeçalho e conteúdo do arquivo
        connectionSocket.sendall(header.encode('utf-8'))
        connectionSocket.sendall(outputdata)

        print(
            f"[RESPOSTA DE {addr}] "
            f"200 OK: {filename} entregue com sucesso."
        )

    except (FileNotFoundError, IOError):

        # Caso o arquivo não seja encontrado, envia uma resposta 404 Not Found
        resposta = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>404</title>
        </head>
        <body>
            <h1>404 Not Found</h1>
            <p>O arquivo solicitado não foi encontrado.</p>
        </body>
        </html>
        """

        corpo = resposta.encode('utf-8')

        header = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(corpo)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        connectionSocket.sendall(header.encode('utf-8'))
        connectionSocket.sendall(corpo)

        print(
            f"[RESPOSTA DE {addr}] "
            f"404 Not Found: arquivo não encontrado."
        )

    except Exception as erro:
        print(
            f"[ERRO] Ocorreu um erro ao processar "
            f"a requisição de {addr}: {erro}"
        )

    finally:
        # Fecha somente a conexão deste cliente
        connectionSocket.close()
        print(f"[DESCONECTADO] Cliente desconectado: {addr}")


def iniciar_servidor():

    # Cria o socket TCP
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    serverSocket.bind((HOST, PORT))

    serverSocket.listen(10)

    print("=" * 50)
    print("SERVIDOR WEB MC833")
    print(f"[INICIADO] Servidor HTTP iniciado na porta {PORT}")
    print(f"Acesse: http://<IP_DO_SERVIDOR>:{PORT}/index.html")
    print("=" * 50)

    try:
        while True:

            print("\nReady to serve...")

            # Espera uma nova conexão
            connectionSocket, addr = serverSocket.accept()

            # Cria uma thread para atender o cliente
            thread_cliente = threading.Thread(
                target=atender_cliente,
                args=(connectionSocket, addr)
            )

            thread_cliente.start()

            print(
                f"[THREAD] Cliente {addr} atendido pela "
                f"{thread_cliente.name}"
            )

    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")

    finally:
        serverSocket.close()


if __name__ == "__main__":
    iniciar_servidor()
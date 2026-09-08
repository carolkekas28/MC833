# Import socket module
from socket import *
import sys
import threading

HOST = '0.0.0.0'
PORT = 8000

def atender_cliente(connectionSocket, addr):
    '''''
    Atende uma requisição HTTP de um cliente.
    Cada cliente executa esta função em uma thread separada.
    '''
    print(f"[CONEXÃO] Cliente conectado: {addr}")

    try:
        # Recebe a requisição HTTP enviada pelo navegador. 
        message = connectionSocket.recv(4096).decode('utf-8')

        print(f"[REQUISIÇÃO] Recebida do cliente {addr}:\n{message}")

        # Extrai e lê o conteúdo do arquivo, por exemplo, GET /index.html HTTP/1.1
        filename = message.split()[1]
        f = open(filename[1:], "rb")
        outputdata = f.read()
        f.close()

        # Envia o cabeçalho HTTP de sucesso.
        connectionSocket.send(
            "HTTP/1.1 200 OK\r\n\r\n".encode('utf-8')
        )

        # Envia o conteúdo do arquivo para o cliente.
        connectionSocket.sendall(outputdata)

        print(
            f"[RESPOSTA DE {addr}] "
            f"200 OK: {filename[1:]} enviado com sucesso."
        )

    except IOError:
        # Envia resposta HTTP para arquivo não encontrado.
        resposta = (
            "HTTP/1.1 404 Not Found\r\n\r\n"
            "<html>"
            "<body>"
            "<h1>404 Not Found</h1>"
            "<p>O arquivo solicitado não foi encontrado no servidor.</p>"
            "</body>"
            "</html>"
        )

        connectionSocket.send(resposta.encode('utf-8'))

        print(
            f"[RESPOSTA DE {addr}] "
            "404 Not Found: arquivo não encontrado."
        )

    finally:
        # Fecha o socket deste cliente.
        connectionSocket.close()

        print(f"[DESCONECTADO] Cliente desconectado: {addr}")


def main():
    # Cria o socket TCP do servidor.
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((HOST, PORT))
    serverSocket.listen(10)

    print("=" * 50)
    print("SERVIDOR WEB MC833")
    print(f"[INICIADO] Servidor web iniciado em {HOST}:{PORT}")
    print(f"Acesse em: http://<IP_DO_SERVIDOR>:{PORT}/index.html")
    print("=" * 50)

    try: 
        while True:
            # Aguarda uma nova conexão de um cliente.
            print("\nReady to serve...")

            connectionSocket, addr = serverSocket.accept()

            # Cria uma nova thread para atender o cliente.
            thread_cliente = threading.Thread(
                target = atender_cliente,
                args = (connectionSocket, addr)
            )

            thread_cliente.start()

            print(f"[THREAD] Cliente {addr} atendido pela {thread_cliente.name}")

    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Servidor encerrado pelo usuário.")
        
        # Fecha o socket principal.
        serverSocket.close()
        
        sys.exit(0)

if __name__ == "__main__":
    main()
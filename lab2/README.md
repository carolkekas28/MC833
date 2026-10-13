# Lab 2 — Análise de tráfego TCP e UDP

Projeto da disciplina **MC833 — Programação de Redes de Computadores**, do Instituto de Computação da Unicamp.

**Autora:** Ana Carolina de Almeida Cardoso — RA 246914.

## Objetivo

Analisar tráfego real capturado com o Wireshark e relacionar os campos e o comportamento dos protocolos TCP e UDP à teoria de redes de computadores.

- **TCP:** upload de `alice.txt` para `gaia.cs.umass.edu`, utilizando HTTP.
- **UDP:** consultas DNS realizadas com `nslookup` para três domínios.

O script utiliza **Scapy** para ler as capturas, **NumPy** para auxiliar os cálculos e **matplotlib** para gerar os gráficos. Essa abordagem permite reproduzir os resultados e sobrepor a curva de EstimatedRTT com o parâmetro solicitado no laboratório.

## Arquivos de entrada

Coloque estes arquivos na mesma pasta:

| Arquivo | Descrição |
| --- | --- |
| `analise_redes.py` | Script de análise em Python. |
| `tcp-capture-anacarolina.pcapng` | Captura da conexão TCP do upload. |
| `udp-capture-anacarolina.pcapng` | Captura das consultas e respostas DNS. |

O relatório em LaTeX apresenta a metodologia, a interpretação dos cinco gráficos e as conclusões. As capturas e o código devem acompanhar o relatório na entrega.

## Requisitos

- Python 3.
- Bibliotecas `scapy`, `numpy` e `matplotlib`.
- Wireshark para inspecionar as capturas ou realizar novos experimentos.

A análise é feita offline: não exige iniciar uma nova captura, conectar-se aos servidores ou executar o script com privilégios de administrador.

## Execução

No Terminal, entre na pasta `lab2` do repositório.

### 1. Criar o ambiente virtual

    python3 -m venv .venv

### 2. Ativar o ambiente

No macOS ou Linux:

    source .venv/bin/activate

No Windows, usando PowerShell:

    .venv\Scripts\Activate.ps1

### 3. Instalar as dependências

    python -m pip install scapy numpy matplotlib

### 4. Executar o script

    python analise_redes.py

O programa cria a pasta `results` ao lado do script e salva os resultados nela. Os gráficos são gravados em PNG, sem abrir janelas.

Arquivos de saída com os mesmos nomes são substituídos nas execuções seguintes.

## Configuração do experimento

A conexão TCP analisada utiliza:

| Parâmetro | Valor |
| --- | --- |
| IPv4 local do cliente | `192.168.15.85` |
| Porta temporária do cliente | `52628` |
| IPv4 do servidor | `128.119.245.12` |
| Porta HTTP do servidor | `80` |
| Peso da nova amostra no EstimatedRTT | `ALPHA = 0.125` |
| Intervalo de throughput | `THROUGHPUT_INTERVAL = 0.1` s |

Os endereços e a porta temporária correspondem a esta captura. Para analisar outra conexão, confira e ajuste `SERVER_IP`, `CLIENT_PORT`, `SERVER_PORT` e os nomes dos arquivos no início do script.

As consultas DNS consideradas são:

- `www.ic.unicamp.br`
- `www.cs.umass.edu`
- `www.u-tokyo.ac.jp`

O script exige um par válido de consulta e resposta por domínio. Caso os domínios sejam alterados, atualize também a lista `DOMAINS`.

## Gráficos obrigatórios

| Arquivo | Conteúdo |
| --- | --- |
| `01_tcp_sequence.png` | Número de sequência relativo versus tempo, no estilo Stevens, para observar os fleets. |
| `02_tcp_rtt.png` | RTT por segmento e curva de EstimatedRTT com α = 0,125. |
| `03_tcp_throughput.png` | Throughput do cliente em bytes/s, calculado em intervalos de 0,1 s. |
| `04_udp_dns_rtt.png` | Comparação dos tempos de resposta das três consultas DNS. |
| `05_udp_tcp_headers.png` | Comparação dos campos UDP com o cabeçalho do primeiro segmento TCP com dados. |

Cada gráfico é acompanhado de uma discussão no relatório.

## Dados exportados

| Arquivo | Conteúdo |
| --- | --- |
| `tcp_packets.csv` | Campos dos pacotes da conexão TCP selecionada. |
| `tcp_rtt.csv` | Associação entre segmentos e ACKs, amostras de RTT e EstimatedRTT. |
| `tcp_throughput.csv` | Bytes por intervalo, bytes acumulados e throughput. |
| `dns.csv` | Pares de consulta/resposta, RTT, endereços e portas DNS. |
| `header_fields.csv` | Tamanho dos campos dos cabeçalhos UDP e TCP. |

A versão sem resumo textual não cria nem atualiza `summary.txt`. Um arquivo desse nome gerado por uma versão anterior pode permanecer na pasta.

## Critérios de análise

### TCP

- O tempo é contado desde o SYN do cliente.
- A sequência relativa é calculada a partir do número de sequência inicial do cliente.
- O RTT é medido entre o envio do segmento e o primeiro ACK cumulativo observado que confirma todos os seus bytes.
- Intervalos de sequência repetidos são usados para identificar possíveis retransmissões. Amostras de RTT ambíguas associadas a esses intervalos são excluídas.
- O EstimatedRTT começa com a primeira amostra válida e é atualizado em ordem de envio dos segmentos:

    EstimatedRTT = 0.875 × previous_estimate + 0.125 × current_sample

- O throughput corresponde à diferença dos bytes acumulados de payload TCP dividida pela duração do intervalo. Inclui dados HTTP e eventuais retransmissões; não corresponde exclusivamente ao conteúdo útil de `alice.txt`.

### UDP/DNS

- Consultas e respostas são associadas por endereços, portas invertidas, identificador da transação, nome, tipo e classe da pergunta.
- O RTT DNS mede o tempo entre a consulta e a resposta do resolvedor utilizado.
- Na consulta, a porta de destino é 53; na resposta, a porta de origem é 53 e a de destino é a porta temporária do cliente.
- O cabeçalho UDP contém quatro campos de dois bytes: porta de origem, porta de destino, comprimento e checksum.

## Limites de interpretação

A captura não registra diretamente a janela de congestionamento (`cwnd`) ou o limiar `ssthresh`. Os fleets permitem discutir indícios de slow start e congestion avoidance, mas não determinar inequivocamente as fases nesta conexão.

Um mesmo ACK pode confirmar vários segmentos, de modo que as amostras de RTT correspondentes não são independentes. A curva calculada pelo script não representa necessariamente a estimativa interna do sistema operacional.

As consultas DNS podem ser respondidas a partir de cache. Seus tempos não medem diretamente a distância até as instituições associadas aos domínios. Uma medição por domínio caracteriza esta execução, sem demonstrar uma diferença permanente de desempenho.

## Compilação do relatório

No Overleaf, envie o arquivo `.tex` e os cinco gráficos PNG referenciados por ele para a mesma pasta do projeto. Compile com **pdfLaTeX**.

Os logos são opcionais. Para exibi-los na capa, adicione:

- `UNICAMP_logo.png`
- `logo_instituto_de_computacao.png`

Compile novamente caso apareçam referências ainda não resolvidas, como `[?]`.

## Referências

- [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293.html)
- [RFC 5681 — TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681.html)
- [RFC 768 — User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768.html)
- [Documentação do Scapy](https://scapy.readthedocs.io/)

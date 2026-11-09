# Dados pré-processados – MC833 Trabalho 3

Fonte: MAWI Working Group Traffic Archive, samplepoint-F (https://mawi.wide.ad.jp/mawi/).
Cada trace tem ~15 minutos, a partir das 14:00 no horário do Japão (JST = UTC+9).
Os endereços IP já vêm anonimizados pela MAWI e o payload dos pacotes foi removido na captura.

Convenções:
* `tamanho` = tamanho real do quadro no fio (wirelen), em bytes, incluindo o cabeçalho Ethernet.
* `tipo` ∈ {TCP, UDP, ICMP (inclui ICMPv6), Outro IP, Não IP}.
* `t_s` = segundos desde o primeiro pacote do trace; `timestamp` em UTC.

## <id>_serie_10ms.parquet  (todos os pacotes)
t_s, timestamp, bytes, pacotes, bytes_tcp, pacotes_tcp, bytes_udp, pacotes_udp, bytes_icmp, pacotes_icmp,
bytes_outro, pacotes_outro, bytes_ipv4, bytes_ipv6
-> Para outra resolução: df.groupby(df.t_s // 1).sum()  (1 s), df.groupby((df.t_s * 10) // 1).sum()  (100 ms) etc.

## <id>_serie_1s.parquet  (todos os pacotes)
t_s, timestamp, bytes, pacotes, ips_origem_unicos, ips_destino_unicos, fluxos_unicos, tcp_syn (SYN sem ACK)

## <id>_pacotes_amostra.parquet  (amostra aleatória uniforme; fração em resumo.json)
timestamp, t_s, tamanho, caplen (bytes efetivamente capturados), ip_len (campo de tamanho do IP),
versao_ip (4/6/0), protocolo (nº IANA), tipo, ip_origem, ip_destino, porta_origem, porta_destino, flags_tcp
(bits: FIN=1, SYN=2, RST=4, PSH=8, ACK=16, URG=32)

## <id>_fluxos.parquet  (os maiores fluxos em bytes; total de fluxos em resumo.json)
ip_origem, ip_destino, porta_origem, porta_destino, protocolo, tipo, versao_ip, pacotes, bytes, inicio_s, fim_s
Fluxo = 5-tupla unidirecional.

## <id>_hist_fluxos.parquet  (todos os fluxos)
limite_inferior (bins logarítmicos), fluxos_por_pacotes, fluxos_por_bytes

## <id>_portas.parquet  (todos os pacotes TCP/UDP)
tipo, porta_servico (= menor porta entre origem e destino), pacotes, bytes

## <id>_hist_tamanhos.parquet  (todos os pacotes)
versao_ip, tipo, tamanho, pacotes  -> histograma exato

## <id>_recorte.pcap
Primeiros segundos do pcap original (formato pcap clássico), para o exercício opcional de parsing.

## <id>_resumo.json
Metadados: início, duração, totais, vazão média, distribuição por protocolo, nº de fluxos, fração amostrada.

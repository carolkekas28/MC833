from pathlib import Path
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scapy.all import rdpcap, IP, IPv6, TCP, UDP, DNS

BASE_DIR = Path(__file__).resolve().parent
TCP_FILE = BASE_DIR / "tcp-capture-anacarolina.pcapng"
UDP_FILE = BASE_DIR / "udp-capture-anacarolina.pcapng"
OUTPUT_DIR = BASE_DIR / "results"

SERVER_IP = "128.119.245.12"
CLIENT_PORT = 52628
SERVER_PORT = 80

DOMAINS = [
    "www.ic.unicamp.br",
    "www.cs.umass.edu",
    "www.u-tokyo.ac.jp"
]

ALPHA = 0.125
THROUGHPUT_INTERVAL = 0.1 # Seconds per interval.

def get_addresses(packet):
    if IP in packet:
        return packet[IP].src, packet[IP].dst
    elif IPv6 in packet:
        return packet[IPv6].src, packet[IPv6].dst
    return None, None

def save_csv(filename, columns, rows):
    with (OUTPUT_DIR / filename).open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)

def save_plot(filename):
    plt.grid(alpha=0.25, axis="y")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=200)
    plt.close()

def overlaps(first_range, second_range):
    return (
        first_range[0] < second_range[1]
        and second_range[0] < first_range[1]
    )

def analyze_tcp():
    capture = rdpcap(str(TCP_FILE))
    connection = []

    # Select only the upload connection.
    for packet_number, packet in enumerate(capture, start=1):
        if TCP not in packet:
            continue

        src, dst = get_addresses(packet)
        tcp = packet[TCP]

        is_client = (
            dst == SERVER_IP
            and int(tcp.sport) == CLIENT_PORT
            and int(tcp.dport) == SERVER_PORT
        )
        is_server = (
            src == SERVER_IP
            and int(tcp.sport) == SERVER_PORT
            and int(tcp.dport) == CLIENT_PORT
        )

        if is_client or is_server:
            connection.append((packet_number, packet, is_client))

    if not connection:
        raise ValueError(
            "TCP connection not found. Check the IP address and ports."
        )

    syn_packets = [
        item for item in connection
        if item[2]
        and (int(item[1][TCP].flags) & 0x02)
        and not (int(item[1][TCP].flags) & 0x10)
    ]
    if not syn_packets:
        raise ValueError("Client SYN not found in the capture.")

    syn_number, syn, _ = syn_packets[0]
    initial_sequence_number = int(syn[TCP].seq)
    start_time = float(syn.time)

    synack_packets = [
        item for item in connection
        if not item[2]
        and (int(item[1][TCP].flags) & 0x12) == 0x12
    ]
    if not synack_packets:
        raise ValueError("Server SYNACK not found.")

    synack_number, synack, _ = synack_packets[0]
    rows = []
    segments = []
    retransmissions = []
    pending_segments = []
    rtt_samples = []

    for packet_number, packet, is_client in connection:
        tcp = packet[TCP]
        elapsed_time = float(packet.time) - start_time
        payload_size = len(bytes(tcp.payload))
        header_size = int(tcp.dataofs) * 4

        rows.append([
            packet_number,
            elapsed_time,
            "client" if is_client else "server",
            int(tcp.seq),
            int(tcp.ack),
            str(tcp.flags),
            payload_size,
            header_size,
        ])

        if is_client and payload_size:
            # Sequence numbers relative to the SYN, as in Wireshark.
            sequence = (
                int(tcp.seq) - initial_sequence_number
            ) % (2 ** 32)
            sequence_range = (sequence, sequence + payload_size)

            previous_segments = [
                segment for segment in segments
                if overlaps(
                    sequence_range,
                    (segment["seq"], segment["end"]),
                )
            ]

            if previous_segments:
                retransmissions.append(packet_number)

                # Avoid ambiguous RTT measurements for retransmitted bytes.
                for segment in pending_segments:
                    if overlaps(
                        sequence_range,
                        (segment["seq"], segment["end"]),
                    ):
                        segment["ambiguous"] = True

            segment = {
                "packet": packet_number,
                "time": elapsed_time,
                "seq": sequence,
                "end": sequence + payload_size,
                "bytes": payload_size,
                "ambiguous": bool(previous_segments),
            }
            segments.append(segment)
            pending_segments.append(segment)

        elif not is_client and (int(tcp.flags) & 0x10):
            acknowledgement = (
                int(tcp.ack) - initial_sequence_number
            ) % (2 ** 32)

            acknowledged_segments = [
                segment for segment in pending_segments
                if segment["end"] <= acknowledgement
            ]

            for segment in acknowledged_segments:
                if not segment["ambiguous"]:
                    rtt_ms = (
                        elapsed_time - segment["time"]
                    ) * 1000

                    rtt_samples.append([
                        segment["packet"],
                        packet_number,
                        segment["time"],
                        rtt_ms,
                    ])

            pending_segments = [
                segment for segment in pending_segments
                if segment["end"] > acknowledgement
            ]

    if not segments:
        raise ValueError("No data segments sent by the client.")

    save_csv(
        "tcp_packets.csv",
        [
            "packet", "time_s", "direction", "seq_raw", "ack_raw",
            "flags", "payload_bytes", "header_bytes",
        ],
        rows,
    )

    # Sequence versus time: vertical segments, Stevens style.
    plt.figure(figsize=(10, 5))
    for segment in segments:
        plt.vlines(
            segment["time"],
            segment["seq"],
            segment["end"],
            color="tab:blue",
        )
    plt.title("TCP: sequence versus time — Stevens style")
    plt.xlabel("Time since the client SYN (s)")
    plt.ylabel("Relative sequence number (bytes)")
    save_plot("01_tcp_sequence.png")

    # Per-segment RTT and EstimatedRTT.
    # A cumulative ACK may produce samples for multiple segments.
    rtt_samples.sort(key=lambda sample: (sample[2], sample[0]))
    estimated_rtt = None
    rtt_rows = []

    for packet_number, ack_number, elapsed_time, rtt in rtt_samples:
        estimated_rtt = (
            rtt if estimated_rtt is None
            else (1 - ALPHA) * estimated_rtt + ALPHA * rtt
        )
        rtt_rows.append([
            packet_number,
            ack_number,
            elapsed_time,
            rtt,
            estimated_rtt,
        ])

    save_csv(
        "tcp_rtt.csv",
        [
            "data_packet", "ack_packet", "send_time_s",
            "rtt_ms", "estimated_rtt_ms",
        ],
        rtt_rows,
    )

    plt.figure(figsize=(10, 5))
    if rtt_rows:
        data = np.asarray(rtt_rows, dtype=float)
        plt.scatter(
            data[:, 2],
            data[:, 3],
            s=15,
            label="Per-segment RTT",
        )
        plt.plot(
            data[:, 2],
            data[:, 4],
            color="tab:orange",
            label="EstimatedRTT (α = 0.125)",
        )
        plt.legend()
    else:
        plt.text(
            0.5,
            0.5,
            "No valid RTT samples",
            ha="center",
            transform=plt.gca().transAxes,
        )
    plt.title("TCP: RTT and EstimatedRTT")
    plt.xlabel("Send time since the SYN (s)")
    plt.ylabel("RTT (ms)")
    save_plot("02_tcp_rtt.png")

    # Throughput: differences in cumulative bytes per interval.
    # Count observed TCP payload, including retransmissions.
    duration = max(
        float(packet.time) - start_time
        for _, packet, _ in connection
    )
    bin_edges = np.arange(
        0,
        duration + THROUGHPUT_INTERVAL,
        THROUGHPUT_INTERVAL,
    )
    if len(bin_edges) < 2:
        bin_edges = np.array([0, THROUGHPUT_INTERVAL])

    bytes_per_interval, _ = np.histogram(
        [segment["time"] for segment in segments],
        bins=bin_edges,
        weights=[segment["bytes"] for segment in segments],
    )
    cumulative_bytes = np.cumsum(bytes_per_interval)
    rates = (
        np.diff(np.r_[0, cumulative_bytes]) / np.diff(bin_edges)
    )
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    save_csv(
        "tcp_throughput.csv",
        [
            "start_s", "end_s", "interval_bytes",
            "cumulative_bytes", "throughput_bytes_s",
        ],
        zip(
            bin_edges[:-1],
            bin_edges[1:],
            bytes_per_interval,
            cumulative_bytes,
            rates,
        ),
    )

    plt.figure(figsize=(10, 5))
    plt.step(bin_centers, rates, where="mid")
    plt.title(
        f"TCP: client throughput — "
        f"{THROUGHPUT_INTERVAL:g} s intervals"
    )
    plt.xlabel("Time since the SYN (s)")
    plt.ylabel("Throughput (bytes/s)")
    save_plot("03_tcp_throughput.png")

    # Compare header fields using the first captured data segment.
    reference = next(
        row for row in rows if row[0] == segments[0]["packet"]
    )
    return reference[0], reference[-1]

def analyze_dns():
    queries = {}
    results = []
    retransmitted_queries = set()

    for packet_number, packet in enumerate(
        rdpcap(str(UDP_FILE)), start=1
    ):
        if UDP not in packet or DNS not in packet:
            continue

        dns = packet[DNS]
        if not dns.qd:
            continue

        question = dns.qd[0]
        domain = (
            question.qname.decode(errors="replace")
            .rstrip(".")
            .lower()
        )
        if domain not in DOMAINS:
            continue

        src, dst = get_addresses(packet)
        udp = packet[UDP]
        question_key = (
            int(dns.id),
            domain,
            int(question.qtype),
            int(question.qclass),
        )

        if int(dns.qr) == 0:
            key = (
                src, dst, int(udp.sport), int(udp.dport)
            ) + question_key
            if key in queries:
                retransmitted_queries.add(key)
            else:
                queries[key] = (float(packet.time), packet_number)
        else:
            key = (
                dst, src, int(udp.dport), int(udp.sport)
            ) + question_key
            if key in queries:
                query_time, query_number = queries.pop(key)
                if key not in retransmitted_queries:
                    results.append([
                        domain,
                        query_number,
                        packet_number,
                        (float(packet.time) - query_time) * 1000,
                        dst,
                        int(udp.dport),
                        src,
                        int(udp.sport),
                    ])
                retransmitted_queries.discard(key)

    save_csv(
        "dns.csv",
        [
            "domain", "query_packet", "response_packet", "rtt_ms",
            "client_ip", "client_port", "dns_ip", "dns_port",
        ],
        results,
    )

    # Require one pair per domain instead of silently choosing a query.
    for domain in DOMAINS:
        count = sum(result[0] == domain for result in results)
        if count != 1:
            raise ValueError(
                f"{domain}: found {count} valid DNS pairs. "
                "The expected capture contains one query and one "
                "response per domain; check dns.csv."
            )

    results.sort(key=lambda result: DOMAINS.index(result[0]))
    plt.figure(figsize=(9, 5))
    bars = plt.bar(
        [result[0] for result in results],
        [result[3] for result in results],
        color=["tab:blue", "tab:orange", "tab:green"],
    )
    plt.bar_label(
        bars,
        labels=[f"{result[3]:.3f} ms" for result in results],
    )
    plt.ylim(0, max(result[3] for result in results) * 1.2)
    plt.ylabel("DNS response time (ms)")
    plt.title("UDP/DNS: time between query and response")
    save_plot("04_udp_dns_rtt.png")

def compare_headers(packet_number, tcp_header_size):
    fields = [
        "Source port",
        "Destination port",
        "Length",
        "Checksum",
        "Sequence number",
        "Acknowledgement number",
        "Data offset",
        "Reserved",
        "Flags",
        "Window",
        "Urgent pointer",
        "Options/padding",
    ]

    udp_sizes = [2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0]

    # Fractions represent fields smaller than one byte.
    # Data offset: 4 bits; reserved: 3 bits; flags: 9 bits.
    tcp_sizes = [
        2, 2, 0, 2, 4, 4, 4 / 8, 3 / 8, 9 / 8,
        2, 2, tcp_header_size - 20,
    ]

    save_csv(
        "header_fields.csv",
        ["field", "udp_bytes", "tcp_bytes"],
        zip(fields, udp_sizes, tcp_sizes),
    )

    positions = np.arange(len(fields))
    plt.figure(figsize=(12, 6))
    plt.bar(
        positions - 0.2,
        udp_sizes,
        width=0.4,
        label="UDP — total: 8 bytes",
    )
    plt.bar(
        positions + 0.2,
        tcp_sizes,
        width=0.4,
        label=f"TCP — packet {packet_number}: {tcp_header_size} bytes",
    )
    plt.xticks(positions, fields, rotation=45, ha="right")
    plt.ylabel("Size (bytes; fractions represent bits)")
    plt.title("UDP and TCP header field comparison")
    plt.legend()
    save_plot("05_udp_tcp_headers.png")

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    packet_number, header_size = analyze_tcp()
    analyze_dns()
    compare_headers(packet_number, header_size)

    print(f"Plots and CSV files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

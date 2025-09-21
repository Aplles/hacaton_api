import concurrent.futures
import socket
import threading
import time
from typing import Union

from p2pnetwork.node import Node

BROADCAST_PORT = 12000
TCP_PORT = 10001
DISCOVERY_TIMEOUT = 2


def get_my_ip():
    """Универсальный способ узнать свой LAN IP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_network_prefix():
    """Получаем префикс сети (первые 3 октета)"""
    my_ip = get_my_ip()
    parts = my_ip.split(".")
    if len(parts) == 4:
        return ".".join(parts[:3]) + "."
    return None


def scan_local_network(tcp_port=TCP_PORT):
    my_ip = get_my_ip()
    parts = my_ip.split('.')
    if len(parts) != 4:
        print('[WARN] Невалидный IP-адрес')
        return set()

    prefix2 = f"{parts[0]}.{parts[1]}."
    my_third = int(parts[2])
    third_range = range(max(0, my_third - 2), min(255, my_third + 3))
    active_peers = set()
    target_ips = [f"{prefix2}{third}.{fourth}"
                  for third in third_range
                  for fourth in range(1, 255)
                  if f"{prefix2}{third}.{fourth}" != my_ip]
    print(f'[SCAN] TCP-скан {len(third_range)} подсетей по {len(target_ips)} адресов...')

    def check_peer(ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, tcp_port))
            sock.close()
            if result == 0:
                active_peers.add((ip, tcp_port))
                print(f"[SCAN] Найден активный узел: {ip}:{tcp_port}")
        except Exception:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        list(executor.map(check_peer, target_ips))
    return active_peers


def discover_peers(
    my_tcp_port=TCP_PORT, broadcast_port=BROADCAST_PORT, timeout=DISCOVERY_TIMEOUT
):
    """Автообнаружение других пиров через UDP broadcast."""
    my_ip = get_my_ip()
    peers = set()
    stop_flag = threading.Event()

    def listen():
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.bind(("", broadcast_port))
        udp_sock.settimeout(0.5)
        while not stop_flag.is_set():
            try:
                msg, addr = udp_sock.recvfrom(1024)
                if msg.startswith(b"MESH_DISCOVERY:"):
                    sender_port = int(msg.decode().split(":")[1])
                    peer_ip = addr[0]
                    peer = (peer_ip, sender_port)
                    if peer != (my_ip, my_tcp_port):
                        peers.add(peer)
                        print(f"[DISCOVERY] Обнаружен пир через broadcast: {peer}")
            except socket.timeout:
                continue
        udp_sock.close()

    listen_thread = threading.Thread(target=listen, daemon=True)
    listen_thread.start()

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    my_msg = f"MESH_DISCOVERY:{my_tcp_port}".encode()
    end = time.time() + timeout

    while time.time() < end:
        udp_sock.sendto(my_msg, ("<broadcast>", broadcast_port))
        time.sleep(1)

    stop_flag.set()
    listen_thread.join()
    udp_sock.close()
    scanned_peers = scan_local_network()
    all_peers = peers.union(scanned_peers)
    return {p for p in all_peers if p != (my_ip, my_tcp_port)}


class MeshNode(Node):
    def __init__(self, host, port, name):
        super().__init__(host, port, None)
        self.name = name
        self.connected_peers = set()

    def node_message(self, connected_node, data):
        print(data, type(data))
        from models_app.models import Alarm, User

        current_user = User.objects.first()
        if (
            data.get("from") in current_user.codes
                and data.get("type") == "create_alarm"
        ):
            print("Other peer data: ", data.get("data"))
            Alarm.objects.create(
                speed=data["info"]["speed"],
                magnetic=data["info"]["magnetic"],
                scatter_area=data["info"]["scatter_area"],
                other_user_grade=data["info"]["grade"],
                user_id=data["info"]["user_id"],
            )
        print(f"\n[RECV][{connected_node.host}:{connected_node.port}] -> {data}")

    def node_connect_with_node(self, node):
        print(f"[CONNECT] -> {node.host}:{node.port}")
        self.connected_peers.add((node.host, node.port))

    def node_disconnect_with_node(self, node):
        print(f"[DISCONN] -> {node.host}:{node.port}")
        if (node.host, node.port) in self.connected_peers:
            self.connected_peers.remove((node.host, node.port))

    def node_request_to_stop(self):
        print(f"[STOP] Node {self.name} остановлен.")

    def auto_connect_to_peers(self, peers):
        """Автоматическое подключение к найденным пирам"""
        my_ip = get_my_ip()
        for peer_ip, peer_port in peers:
            if (peer_ip, peer_port) != (my_ip, self.port) and (
                peer_ip,
                peer_port,
            ) not in self.connected_peers:
                print(f"[AUTO-CONNECT] Подключаемся к {peer_ip}:{peer_port}...")
                try:
                    self.connect_with_node(peer_ip, peer_port)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"[ERROR] Ошибка подключения к {peer_ip}:{peer_port}: {e}")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


_mesh_node_instance: Union[MeshNode, None] = None


def get_mesh_node() -> Union["MeshNode", None]:
    return _mesh_node_instance


def start_mesh_node(user_code):
    global _mesh_node_instance
    if _mesh_node_instance is not None:
        return _mesh_node_instance

    host = "0.0.0.0"
    port = TCP_PORT
    found_peers = discover_peers(my_tcp_port=port)
    node = MeshNode(host, port, user_code)
    node.start()
    if found_peers:
        node.auto_connect_to_peers(found_peers)
    _mesh_node_instance = node
    return node

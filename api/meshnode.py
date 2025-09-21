import socket
import threading
import time
import uuid
from typing import Union

from p2pnetwork.node import Node

BROADCAST_PORT = 12000
TCP_PORT = 10001
DISCOVERY_TIMEOUT = 3


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def get_network_prefix():
    my_ip = get_my_ip()
    parts = my_ip.split('.')
    if len(parts) == 4:
        return '.'.join(parts[:3]) + '.'
    return None


def scan_local_network():
    network_prefix = get_network_prefix()
    if not network_prefix:
        print("[WARN] Не удалось определить префикс сети")
        return set()
    active_peers = set()

    def check_peer(ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, TCP_PORT))
            sock.close()
            if result == 0:
                active_peers.add((ip, TCP_PORT))
                print(f"[SCAN] Найден активный узел: {ip}:{TCP_PORT}")
        except:
            pass

    print(f"[SCAN] Сканируем сеть {network_prefix}1-99...")
    threads = []
    for i in range(1, 100):
        ip = f"{network_prefix}{i}"
        if ip != get_my_ip():
            thread = threading.Thread(target=check_peer, args=(ip,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join(timeout=0.5)
    return active_peers


def discover_peers(my_tcp_port=TCP_PORT, broadcast_port=BROADCAST_PORT, timeout=DISCOVERY_TIMEOUT):
    my_ip = get_my_ip()
    peers = set()
    stop_flag = threading.Event()

    def listen():
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.bind(('', broadcast_port))
        udp_sock.settimeout(0.5)
        while not stop_flag.is_set():
            try:
                msg, addr = udp_sock.recvfrom(1024)
                if msg.startswith(b'MESH_DISCOVERY:'):
                    sender_port = int(msg.decode().split(':')[1])
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
        udp_sock.sendto(my_msg, ('<broadcast>', broadcast_port))
        time.sleep(1)
    stop_flag.set()
    listen_thread.join()
    udp_sock.close()
    scanned_peers = scan_local_network()
    all_peers = peers.union(scanned_peers)
    return {p for p in all_peers if p != (my_ip, my_tcp_port)}


class MeshNode(Node):
    def __init__(self, host, port, name, unique_id=None):
        super().__init__(host, port, None)
        self.name = name
        self.unique_id = unique_id or str(uuid.uuid4())
        self.connected_peers = set()
        # peer_id -> {"connection": NodeConnection, "ip":..., "port":..., "name":...}
        self.peer_info = {}
        print(f"[INFO] Мой peer_id: {self.unique_id}")

    def node_connect_with_node(self, node):
        print(f"[CONNECT] -> {node.host}:{node.port}")
        self.connected_peers.add((node.host, node.port))
        # Всегда отправляем свой peer_id первому же подключенному peer
        self.send({
            "type": "whoami",
            "peer_id": self.unique_id,
            "name": self.name,
        }, node)

    def node_message(self, connected_node, data):
        if isinstance(data, dict) and data.get("type") == "whoami":
            peer_id = data["peer_id"]
            peer_name = data.get("name", "")
            self.peer_info[peer_id] = {
                "connection": connected_node,
                "ip": connected_node.host,
                "port": connected_node.port,
                "name": peer_name,
            }
            print(
                f"[PEER] Новый peer_id зарегистрирован: {peer_id} [{peer_name}] @ {connected_node.host}:{connected_node.port}")
            return

        peer_already_known = False
        for peer_id, info in self.peer_info.items():
            if info["ip"] == connected_node.host and info["port"] == connected_node.port:
                peer_already_known = True
                break

        if not peer_already_known:
            print(
                f"[AUTODISCOVERY] Peer на {connected_node.host}:{connected_node.port} не идентифицирован, просим whoami...")
            self.send({
                "type": "whoami",
                "peer_id": self.unique_id,
                "name": self.name
            }, connected_node)

        print(f"\n[RECV][{connected_node.host}:{connected_node.port}] -> {data}")

    def node_disconnect_with_node(self, node):
        print(f"[DISCONN] -> {node.host}:{node.port}")
        if (node.host, node.port) in self.connected_peers:
            self.connected_peers.remove((node.host, node.port))
        # Чистим peer_info по ip:port (peer_id не узнаём, но бывает совпадение)
        for peer_id, info in list(self.peer_info.items()):
            if info["ip"] == node.host and info["port"] == node.port:
                del self.peer_info[peer_id]
                print(f"[PEER_INFO] peer_id {peer_id} удалён из peer_info (disconnect)")

    def node_request_to_stop(self):
        print(f"[STOP] Node {self.name} остановлен.")

    def auto_connect_to_peers(self, peers):
        my_ip = get_my_ip()
        for peer_ip, peer_port in peers:
            if (peer_ip, peer_port) != (my_ip, self.port) and \
                    (peer_ip, peer_port) not in self.connected_peers:
                print(f"[AUTO-CONNECT] Подключаемся к {peer_ip}:{peer_port}...")
                try:
                    self.connect_with_node(peer_ip, peer_port)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"[ERROR] Ошибка подключения к {peer_ip}:{peer_port}: {e}")

    def send_to_peer_ids(self, peer_id_list, message):
        """Отправить сообщение только указанным по peer_id."""
        found = 0
        for peer_id in peer_id_list:
            info = self.peer_info.get(peer_id)
            if info:
                self.send(message, info["connection"])
                found += 1
                print(f"[SEND] Сообщение отправлено в peer_id {peer_id}: {info['ip']}:{info['port']} [{info['name']}]")
            else:
                print(f"[WARN] Неизвестный peer_id: {peer_id}")
        return found

    def send_mesh_message(self, message, peer_ids=None):
        """
        Отправить сообщение выбранным peer_id, или всем если не указано или пусто.
        :param message: dict
        :param peer_ids: list/tuple/set или None
        """
        if not peer_ids:
            self.send_to_nodes(message)
            print(f"[SEND] Сообщение отправлено всем peer.")
            return "all"
        else:
            found = 0
            for peer_id in peer_ids:
                info = self.peer_info.get(peer_id)
                if info:
                    self.send(message, info["connection"])
                    found += 1
                    print(
                        f"[SEND] Сообщение отправлено в peer_id {peer_id}: {info['ip']}:{info['port']} [{info['name']}]")
                else:
                    print(f"[WARN] Неизвестный peer_id: {peer_id}")
            return found


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


_mesh_node_instance: Union[MeshNode, None] = None


def get_mesh_node() -> Union['MeshNode', None]:
    return _mesh_node_instance


def start_mesh_node():
    global _mesh_node_instance
    if _mesh_node_instance is not None:
        return _mesh_node_instance
    host = "0.0.0.0"
    port = TCP_PORT
    my_ip = get_my_ip()
    unique_id = str(uuid.uuid4())
    name = f"Peer_{my_ip}:{port}"
    found_peers = discover_peers(my_tcp_port=port)
    node = MeshNode(host, port, name, unique_id)
    node.start()
    if found_peers:
        node.auto_connect_to_peers(found_peers)
    _mesh_node_instance = node
    return node

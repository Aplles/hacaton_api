import socket
import threading
import time
from p2pnetwork.node import Node

BROADCAST_PORT = 12000  # UDP порт для discovery
TCP_PORT = 10001  # TCP порт для Mesh-сервера/клиента
DISCOVERY_TIMEOUT = 3  # Как долго слушаем сеть, сек


def get_my_ip():
    """ Универсальный способ узнать свой LAN IP. """
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
    """Получаем префикс сети (первые 3 октета)"""
    my_ip = get_my_ip()
    parts = my_ip.split('.')
    if len(parts) == 4:
        return '.'.join(parts[:3]) + '.'
    return None


def scan_local_network():
    """Сканируем локальную сеть на наличие активных узлов"""
    network_prefix = get_network_prefix()
    if not network_prefix:
        print("[WARN] Не удалось определить префикс сети")
        return set()

    active_peers = set()

    def check_peer(ip):
        """Проверяем доступность узла"""
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

    # Создаем потоки для проверки каждого IP
    threads = []
    for i in range(1, 100):  # Проверяем IP с 1 до 99
        ip = f"{network_prefix}{i}"
        if ip != get_my_ip():  # Не проверяем себя
            thread = threading.Thread(target=check_peer, args=(ip,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join(timeout=0.5)

    return active_peers


def discover_peers(my_tcp_port=TCP_PORT, broadcast_port=BROADCAST_PORT, timeout=DISCOVERY_TIMEOUT):
    """ Автообнаружение других пиров через UDP broadcast. """
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

    # Запускаем слушатель бродкастов
    listen_thread = threading.Thread(target=listen, daemon=True)
    listen_thread.start()

    # Параллельно бродкастим свой порт
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

    # Добавляем результаты сканирования сети
    scanned_peers = scan_local_network()
    all_peers = peers.union(scanned_peers)

    # Не включаем себя
    return {p for p in all_peers if p != (my_ip, my_tcp_port)}


class MeshNode(Node):
    def __init__(self, host, port, name):
        super().__init__(host, port, None)
        self.name = name
        self.connected_peers = set()

    def node_message(self, connected_node, data):
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
            if (peer_ip, peer_port) != (my_ip, self.port) and \
                    (peer_ip, peer_port) not in self.connected_peers:
                print(f"[AUTO-CONNECT] Подключаемся к {peer_ip}:{peer_port}...")
                try:
                    self.connect_with_node(peer_ip, peer_port)
                    time.sleep(0.1)  # Небольшая задержка между подключениями
                except Exception as e:
                    print(f"[ERROR] Ошибка подключения к {peer_ip}:{peer_port}: {e}")


def send_mesh_messages(node):
    try:
        while True:
            print("\n" + "=" * 50)
            print("Команды:")
            print("1. Введите сообщение для отправки")
            print("2. 'scan' - повторно сканировать сеть")
            print("3. 'list' - показать подключенные узлы")
            print("4. 'exit' - выйти")
            print("=" * 50)

            msg = input('\nВведите сообщение или команду: ')

            if msg == 'exit':
                print("[INFO] Mesh node останавливается...")
                node.stop()
                break
            elif msg == 'scan':
                print("[INFO] Повторное сканирование сети...")
                new_peers = scan_local_network()
                if new_peers:
                    print(f"[SCAN] Найдено новых узлов: {len(new_peers)}")
                    node.auto_connect_to_peers(new_peers)
                else:
                    print("[SCAN] Новых узлов не найдено")
            elif msg == 'list':
                print("📋 Подключенные узлы:")
                if node.connected_peers:
                    for peer in node.connected_peers:
                        print(f"  - {peer[0]}:{peer[1]}")
                else:
                    print("  Нет подключенных узлов")
            else:
                node.send_to_nodes({
                    "type": "message",
                    "msg": msg,
                    "from": node.name,
                    "timestamp": time.time()
                })
                print(f"[SEND] Сообщение отправлено!")

    except (EOFError, KeyboardInterrupt):
        node.stop()


if __name__ == "__main__":
    host = "0.0.0.0"
    port = TCP_PORT
    my_ip = get_my_ip()
    name = f"Peer_{my_ip}:{port}"

    print(f"[INFO] Мой IP: {my_ip}")
    print(f"[INFO] Порт: {port}")
    print(f"[INFO] Имя узла: {name}")
    print(f"[INFO] Автопоиск mesh-пиров ... (ждём {DISCOVERY_TIMEOUT}с)")

    # Обнаруживаем пиров (broadcast + сканирование сети)
    found_peers = discover_peers(my_tcp_port=port)

    if found_peers:
        print(f"[INFO] Найденные пиры: {len(found_peers)}")
        for peer in found_peers:
            print(f"  - {peer[0]}:{peer[1]}")
    else:
        print("[INFO] Пиров не найдено — вы первый в сети!")
    print("#" * 50)

    # Запускаем узел
    node = MeshNode(host, port, name)
    node.start()
    print(f"[INFO] Mesh node {name} стартовал на {host}:{port}")

    # Автоматически подключаемся к найденным пирам
    if found_peers:
        node.auto_connect_to_peers(found_peers)

    # Запускаем интерактивный интерфейс
    sender = threading.Thread(target=send_mesh_messages, args=(node,))
    sender.daemon = True
    sender.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Останавливаем узел...")
        node.stop()

    print("[INFO] Node завершил работу.")
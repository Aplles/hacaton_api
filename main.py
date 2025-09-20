from p2pnetwork.node import Node
import threading
import time

class AlarmNode(Node):
    def __init__(self, host, port, name, peers=None):
        super().__init__(host, port, None)
        self.name = name
        self.peers_list = peers or []

    def node_message(self, connected_node, data):
        print(f"\n[RECV] from {connected_node}: {data}")
        if data.get("type") == "alarm":
            print(f"[ALARM] - {data.get('msg')}")
        else:
            print(f"[INFO ] - {data}")

    def node_connect_with_node(self, node):
        print(f"\n[INFO] Connected with peer: {node}")

    def node_disconnect_with_node(self, node):
        print(f"\n[INFO] Disconnected from peer: {node}")

    def node_request_to_stop(self):
        print(f"\n[INFO] Node {self.name} stopping...")

# Функция для рассылки тестовых тревог
def send_alarm(node):
    while True:
        cmd = input('\nEnter "alarm" to send, "exit" to stop: ')
        if cmd == "alarm":
            alarm_msg = {"type": "alarm", "msg": f'Опасность обнаружена на {node.name}!'}
            node.send_to_nodes(alarm_msg)
            print("[SEND ] Alarm message sent to peers!")
        elif cmd == "exit":
            node.stop()
            break

if __name__ == "__main__":
    import sys
    host = "0.0.0.0"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    name = f"peer_{port}"

    # Запуск узла
    node = AlarmNode(host, port, name)
    node.start()
    print(f"[INFO] Node {name} started on {host}:{port}")

    # Можно указать пиров для коннекта при запуске
    for peer_addr in sys.argv[2:]:
        host_, port_ = peer_addr.split(":")
        node.connect_with_node(host_, int(port_))

    # Запуск CLI для отправки тревог
    sender_thread = threading.Thread(target=send_alarm, args=(node,))
    sender_thread.daemon = True
    sender_thread.start()
    sender_thread.join()

    print("[INFO] Node stopped.")
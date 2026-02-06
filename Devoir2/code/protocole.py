# code/protocole.py
# Implémentation Selective Repeat (SR) avec CRC-16 (CCITT)
# Logs horodatés: ENVOI, RECEPTION, ACK, TIMEOUT, RETRANSMISSION
# Segmentation: 100 octets max (hors en-tête/CRC)
# Usage:
#   python -m code.protocole 2       # ex: scénario 2 (canal bruité)
#   python -m code.protocole 1       # scénario 1 (canal parfait)
#   python -m code.protocole 3       # scénario 3 (canal instable)

import sys, os, time, threading, binascii, platform
from datetime import datetime
from pathlib import Path
from code.Canal import Canal
from code import stuffing


# Paramètres protocole 
MAX_PAYLOAD = 100
MOD = 8          # numérotation modulo 8
W   = 4           # fenêtre SR 8 
TIMEOUT_MS = 260   # DOIT être > delaiMax pour scénarios 1 & 2



# Utilitaires 
def ts():
    # Horodatage compact pour les logs
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def crc16_ccitt(data: bytes) -> int:
    # CRC-16-CCITT (init 0xFFFF), binascii.crc_hqx
    return binascii.crc_hqx(data, 0xFFFF) & 0xFFFF

# Structure de trame 
class Frame:
    """
    La classe Frame :

    Emballe les données et les informations de contrôle (type, numéros, CRC).

    Permet au canal de simuler des erreurs en modifiant donnees.

    Détecte les corruptions via verify_crc().

    Affiche des logs lisibles dans le terminal.
    """
    __slots__ = ("seq", "acknum", "is_ack", "payload", "length", "crc", "donnees")

    def __init__(self, seq: int, acknum: int, is_ack: bool, payload: bytes):
        self.seq     = seq % MOD
        self.acknum  = acknum % MOD
        self.is_ack  = is_ack
        self.payload = payload or b""
        self.length  = len(self.payload)
        # CRC calculé sur: type|seq|ack|len|payload
        hdr = bytes([1 if self.is_ack else 0, self.seq, self.acknum, self.length])
        self.crc = crc16_ccitt(hdr + self.payload)
        # Copie "lisible" pour le canal (“simuler une erreur”, si besoin)
        try:
            self.donnees = self.payload.decode("latin1")  
        except Exception:
            self.donnees = ""



    # Sérialisation binaire non-stuffée: header|payload|crc(2 bytes big-endian)
    def to_raw_bytes(self) -> bytes:
        hdr = bytes([1 if self.is_ack else 0, self.seq, self.acknum, self.length])
        crc_bytes = self.crc.to_bytes(2, 'big')
        return hdr + self.payload + crc_bytes

    # Applique le bit-stuffing et encadre par flags 0x7E
    def to_stuffed_bytes(self) -> bytes:
        raw = self.to_raw_bytes()
        bits = stuffing.bytes_to_bits(raw)
        stuffed = stuffing.bit_stuff(bits)
        body = stuffing.bits_to_bytes(stuffed)
        # Flags HDLC = 0x7E
        return bytes([0x7E]) + body + bytes([0x7E])

    @classmethod
    def from_stuffed_bytes(cls, data: bytes):
        """Reconstruit une Frame depuis un flux d'octets encadré par flags.
        Retourne une Frame (avec payload) même si CRC incorrect — le caller
        devra vérifier via verify_crc()."""
        if not data or data[0] != 0x7E or data[-1] != 0x7E:
            raise ValueError("Absence de flags ou flux malformé")
        body = data[1:-1]
        bits = stuffing.bytes_to_bits(body)
        destuffed = stuffing.bit_destuff(bits)
        raw = stuffing.bits_to_bytes(destuffed)
        # raw = hdr(4) + payload + crc(2)
        if len(raw) < 6:
            raise ValueError("Trame trop courte après destuffing")
        hdr = raw[0:4]
        t_is_ack = bool(hdr[0])
        seq = hdr[1]
        acknum = hdr[2]
        length = hdr[3]
        payload = raw[4:4+length]
        crc_bytes = raw[4+length:4+length+2]
        if len(crc_bytes) < 2:
            # CRC absent ou tronqué
            crc_val = 0
        else:
            crc_val = int.from_bytes(crc_bytes, 'big')
        fr = cls(seq=seq, acknum=acknum, is_ack=t_is_ack, payload=payload)
        # Overwrite computed CRC with the one extracted (to allow detection)
        fr.crc = crc_val
        # Keep payload as donnees for channel simulation
        try:
            fr.donnees = payload.decode('latin1')
        except Exception:
            fr.donnees = ""
        return fr

    
    
    def header_bytes(self) -> bytes:
        return bytes([1 if self.is_ack else 0, self.seq, self.acknum, self.length])

    #Au moment où le récepteur reçoit la trame, on recalcule le CRC :
    #Si le canal a altéré donnees, le CRC recalculé different de  CRC original -> erreur détectée (FAIL).
    #Sinon, le CRC correspond -> trame correcte (OK).
    def verify_crc(self) -> bool:
        hdr = self.header_bytes()
        # Si le canal a corrompu .donnees, reconstruire payload depuis donnees:
        payload = self.donnees.encode("latin1") if self.donnees else self.payload
        return crc16_ccitt(hdr + payload) == self.crc

    def __repr__(self):
        t = "ACK" if self.is_ack else "DATA"
        return f"<{t} seq={self.seq} ack={self.acknum} len={self.length} crc={self.crc:04X}>"

#  Récepteur 
class Receiver:
    def __init__(self, canal: Canal, stats):
        self.canal = canal
        self.expected = 0           # prochain en-ordre attendu
        self.buf = [None]*W         # buffer SR
        self.rebuilt = bytearray()  # message reconstruit
        self.stats = stats          # dict comptage

    def on_from_sender(self, frame: Frame):
        # Accept either Frame objects or raw bytes (stuffed) from the canal.
        if isinstance(frame, (bytes, bytearray)):
            try:
                frame = Frame.from_stuffed_bytes(bytes(frame))
            except Exception as e:
                print(f"{ts()} | RX  | ERREUR parsing bitstream: {e}")
                return
        if frame.is_ack:
            # Le RX ne traite pas d'ACK
            return
        ok = frame.verify_crc()
        print(f"{ts()} | RX  | RECEPTION {frame} | CRC={'OK' if ok else 'FAIL'}")
        if not ok:
            # Trame ignorée (CRC invalide)
            return

        s = frame.seq
        # Est-ce dans la fenêtre?
        if self._in_window(self.expected, s):
            idx = (s - self.expected) % MOD
            if idx < W and self.buf[idx] is None:
                self.buf[idx] = frame

            # Délivrer tout préfixe continu
            while self.buf[0] is not None:
                f0 = self.buf[0]
                # prendre le payload éventuellement corrompu si "donnees" a changé
                data = f0.donnees.encode("latin1") if f0.donnees else f0.payload
                self.rebuilt.extend(data)
                # shift du buffer
                for i in range(W-1):
                    self.buf[i] = self.buf[i+1]
                self.buf[W-1] = None
                self.expected = (self.expected + 1) % MOD

        # Envoi d'un ACK cumulatif: dernier in-ordre est expected-1
        acknum = (self.expected - 1) % MOD
        ack = Frame(seq=0, acknum=acknum, is_ack=True, payload=b"")
        print(f"{ts()} | RX  | ACK-> {ack}")
        self.canal.transmettre(ack, self._to_sender)

    def _to_sender(self, ack_frame: Frame):
        # Raccourci pour livrer vers le côté émetteur (callback lié au Sender)
        if hasattr(self, "_sender_ack_cb"):
            self._sender_ack_cb(ack_frame)

    def _in_window(self, start, x):
        return ((x - start) % MOD) < W

    def bind_sender_ack(self, ack_cb):
        self._sender_ack_cb = ack_cb

    def message_bytes(self) -> bytes:
        return bytes(self.rebuilt)

# Émetteur 
class Sender:
    def __init__(self, canal: Canal, timeout_ms: int, stats):
        self.canal = canal
        self.timeout_ms = timeout_ms
        self.base = 0
        self.next_seq = 0
        self.window = {}              # seq -> Frame
        self.timers = {}              # seq -> Timer
        self.lock = threading.Lock()
        self.stats = stats            # dict de compteurs

    def send_message(self, data: bytes, receiver: Receiver):
        # Lier la route des ACK du RX vers le TX
        receiver.bind_sender_ack(self.on_ack_from_rx)

        # Segmentation en morceaux ≤ 100 o
        chunks = [data[i:i+MAX_PAYLOAD] for i in range(0, len(data), MAX_PAYLOAD)]

        t0 = time.time()
        off = 0
        MAX_DURATION = 10 
       # boucle principale: envoyer, puis attendre vidage de fenêtre
        while off < len(chunks) or self.window:
            # arrêter si la simulation dépasse la durée limite
            if time.time() - t0 > MAX_DURATION:
                print(f"{ts()} | SYS | Durée limite {MAX_DURATION}s atteinte — arrêt du protocole.")
                break

            # remplir la fenêtre
            while off < len(chunks) and self._free_slots() > 0:
                payload = chunks[off]
                acknum = (self.base - 1) % MOD if self.window else ((self.next_seq - 1) % MOD)
                fr = Frame(seq=self.next_seq, acknum=acknum, is_ack=False, payload=payload)
                self.window[self.next_seq] = fr
                self._send_with_timer(fr)
                self.stats["frames_envoyees"] += 1
                self.next_seq = (self.next_seq + 1) % MOD
                off += 1

            time.sleep(0.002)

        t1 = time.time()
        self.stats["duree_s"] = round(t1 - t0, 3)
        
        # Cancel outstanding timers to avoid background retransmissions after exit
        for tm in list(self.timers.values()):
            try:
                tm.cancel()
            except Exception:
                pass
        self.timers.clear()

    def _free_slots(self):
        used = (self.next_seq - self.base) % MOD
        return W - used

    def _send_with_timer(self, frame: Frame):
        # Sérialiser + stuffing avant envoi
        try:
            out_bytes = frame.to_stuffed_bytes()
            print(f"{ts()} | TX  | ENVOI {frame} -> {len(out_bytes)} octets (timeout={self.timeout_ms} ms)")
            self.canal.transmettre(out_bytes, self._to_receiver)
        except Exception:
            # Fallback : envoyer l'objet trame comme avant
            print(f"{ts()} | TX  | ENVOI (fallback) {frame} (timeout={self.timeout_ms} ms)")
            self.canal.transmettre(frame, self._to_receiver)
        # (Ré)armer le timer
        seq = frame.seq
        if seq in self.timers:
            self.timers[seq].cancel()
        tm = threading.Timer(self.timeout_ms/1000.0, self._on_timeout, args=(seq,))
        self.timers[seq] = tm
        tm.start()

    def _on_timeout(self, seq: int):
        with self.lock:
            if seq in self.window:
                print(f"{ts()} | TX  | TIMEOUT seq={seq} → RETRANSMISSION")
                self.stats["frames_retransmises"] += 1
                self._send_with_timer(self.window[seq])

    def on_ack_from_rx(self, ack_frame: Frame):
        # Le canal appelle ceci quand un ACK revient
        if not ack_frame.is_ack:
            return
        self.stats["acks_recus"] += 1
        a = ack_frame.acknum
        print(f"{ts()} | TX  | ACK RECU a={a}")
        # Avancer base cumulativement
        while self.base != (a + 1) % MOD and self.window:
            if self.base in self.timers:
                self.timers[self.base].cancel()
                del self.timers[self.base]
            if self.base in self.window:
                del self.window[self.base]
            self.base = (self.base + 1) % MOD

        # Edge case: si l'ACK pointe exactement sur base-1 (fenêtre entièrement validée)
        if self.base == (a + 1) % MOD and self.base in self.timers:
            self.timers[self.base].cancel()
            del self.timers[self.base]

    def _to_receiver(self, frame: Frame):
        # Callback pour livrer vers le RX
        if hasattr(self, "_receiver_from_tx_cb"):
            self._receiver_from_tx_cb(frame)

    def bind_receiver(self, rx_cb):
        self._receiver_from_tx_cb = rx_cb

# main 
SCENARIOS = {
    1: {"nom": "Canal parfait", "probErreur": 0.0,  "probPerte": 0.0,  "delaiMax": 0},
    2: {"nom": "Canal bruité",  "probErreur": 0.05, "probPerte": 0.10, "delaiMax": 200},
    3: {"nom": "Canal instable","probErreur": 0.10, "probPerte": 0.15, "delaiMax": 300},
}

def run_scenario(num_scn: int):
    params = SCENARIOS[num_scn]
    print(f"\n=== SCÉNARIO {num_scn}: {params['nom']} ===")
    # Timeout recommandé: > delaiMax (sauf test 4 de l’énoncé)
    # - scénario 3: on force un timeout adapté
    base_timeout = TIMEOUT_MS
    rtt_based = 2 * params["delaiMax"] + 100   # marge 100 ms
    timeout_ms = max(base_timeout, rtt_based)

    # Canal
    canal = Canal(probErreur=params["probErreur"], probPerte=params["probPerte"], delaiMax=params["delaiMax"])

    # Stats
    stats = {
        "frames_envoyees": 0,
        "frames_retransmises": 0,
        "acks_recus": 0,
        "duree_s": 0.0
    }

    # Entités
    rx = Receiver(canal, stats)
    tx = Sender(canal, timeout_ms, stats)

    # Lier callbacks croisés
    tx.bind_receiver(rx.on_from_sender)   # DATA TX->RX
    rx.bind_sender_ack(tx.on_ack_from_rx) # ACK  RX->TX

    # Charger message.txt
    msg_path = Path("message.txt")
    if not msg_path.exists():
        # message par défaut pour ne pas planter si absent
        data = ("Hello, SR over noisy canal! " * 300).encode("ascii", errors="ignore")
    else:
        data = msg_path.read_bytes()

    print(f"{ts()} | SYS | Python={platform.python_version()} | OS={platform.system()}-{platform.release()}")
    print(f"{ts()} | SYS | Message: {len(data)} octets | timeout={timeout_ms} ms | W={W} | MOD={MOD}")

    # Lancer l’envoi
    tx.send_message(data, rx)

    # Comparer message reconstruit
    rebuilt = rx.message_bytes()
    ok = (rebuilt == data)
    print("\nTransmission terminée.")
    print(f"Frames envoyées : {stats['frames_envoyees']}")
    print(f"Frames retransmises : {stats['frames_retransmises']}")
    print(f"ACK reçus : {stats['acks_recus']}")
    print(f"Durée totale : {stats['duree_s']} s")
    print(f"Intégrité message : {'OK' if ok else 'ECHEC'}")

if __name__ == "__main__":
    # Choix du scénario via argument CLI (1, 2, 3)
    try:
        scn = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        if scn not in SCENARIOS: raise ValueError
    except ValueError:
        print("Usage: python -m code.protocole [1|2|3]")
        sys.exit(1)
    run_scenario(scn)

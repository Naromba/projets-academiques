import random
import threading

class Canal:
    """
    Canal de transmission générique simulant un lien non fiable.
    Les paramètres probErreur, probPerte et delaiMax sont configurables
    pour reproduire différents scénarios.
    """

    def __init__(self, probErreur=0.0, probPerte=0.0, delaiMax=0):
        """
        Initialise le canal.
        probErreur : probabilité de corruption d'une trame (0.0 à 1.0)
        probPerte  : probabilité de perte d'une trame
        delaiMax   : délai maximal (en ms)
        """
        self.probErreur = probErreur
        self.probPerte = probPerte
        self.delaiMax = delaiMax
        self._fifo = []  # File FIFO pour garder l’ordre; stocke des tuples (trame, callback)
        print(f"[Canal] Initialisé → erreur={probErreur}, perte={probPerte}, delaiMax={delaiMax} ms")

    def transmettre(self, trame, callback_reception):
        """
        Simule la transmission d'une trame ou d'un ACK via le canal.
        Le callback est appelé quand la trame arrive au récepteur.
        """
        tirage = random.random()

        #  Trame perdue
        if tirage < self.probPerte:
            print(f"[Canal]  Trame perdue : {trame}")
            return

        #  Trame corrompue
        if tirage < self.probPerte + self.probErreur:
            trame = self._corrompre(trame)
            print(f"[Canal] Trame corrompue : {trame}")

        # Délai simulé
        delai = random.randint(0, self.delaiMax) if self.delaiMax > 0 else 0
        # Stocker la paire (trame, callback) pour garantir que la trame
        # soit livrée au callback qui l'a envoyée (évite mismatch entre
        # DATA/ACK quand les timers arrivent dans un autre ordre).
        self._fifo.append((trame, callback_reception))
        print(f"[Canal]  Transmission (+{delai} ms) : {trame}")
        threading.Timer(delai / 1000, self._livrer).start()

    def _livrer(self):
        """Livre la trame la plus ancienne (ordre préservé).
        Cette méthode est appelée par un Timer—elle récupère la paire
        (trame, callback) dans la FIFO et appelle le callback associé.
        """
        if not self._fifo:
            return
        trame, callback_reception = self._fifo.pop(0)
        print(f"[Canal]  Trame livrée : {trame}")
        try:
            callback_reception(trame)
        except Exception:
            # Ne pas laisser une exception de callback casser le canal
            # (les threads qui échouent sont visibles dans les logs).
            raise

    def _corrompre(self, trame):
        """Altère la trame. Supporte objets Frame (modifie .donnees)
        ou flux d'octets (flip d'un bit aléatoire).
        """
        # Bit-level corruption for raw bytes
        if isinstance(trame, (bytes, bytearray)):
            ba = bytearray(trame)
            if len(ba) == 0:
                return bytes(ba)
            # choisir un octet puis un bit à inverser
            byte_idx = random.randint(0, len(ba) - 1)
            bit_idx = random.randint(0, 7)
            ba[byte_idx] ^= (1 << bit_idx)
            return bytes(ba)

        # Fallback: try to corrupt .donnees if present (Frame objects)
        if hasattr(trame, "donnees") and trame.donnees:
            pos = random.randint(0, len(trame.donnees) - 1)
            c = trame.donnees[pos]
            trame.donnees = trame.donnees[:pos] + chr((ord(c) + 1) % 256) + trame.donnees[pos+1:]
        return trame

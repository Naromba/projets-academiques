"""Bit-stuffing HDLC — helpers bytes<->bits + stuffing/destuffing."""

from typing import List


def bytes_to_bits(data: bytes, msb_first: bool = True) -> List[int]:
    """Convertit octets -> liste de bits.

    Par défaut `msb_first=True` (ordre MSB-first par octet). Si
    `msb_first=False`, l'ordre LSB-first est utilisé (utile pour
    reproduire certaines conventions de l'énoncé).
    """
    bits: List[int] = []
    if msb_first:
        for b in data:
            for i in range(8):
                bits.append((b >> (7 - i)) & 1)
    else:
        for b in data:
            for i in range(8):
                bits.append((b >> i) & 1)
    return bits


def bits_to_bytes(bits: List[int], msb_first: bool = True) -> bytes:
    """Convertit liste de bits -> octets (pad 0 si besoin).

    `msb_first` doit correspondre à l'option utilisée pour
    `bytes_to_bits` afin d'obtenir une conversion inverse correcte.
    """
    if len(bits) % 8 != 0:
        bits = bits + [0] * (8 - (len(bits) % 8))
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        if msb_first:
            for j in range(8):
                byte = (byte << 1) | (bits[i + j] & 1)
        else:
            # LSB-first: bits[i] is least-significant bit
            for j in range(7, -1, -1):
                byte = (byte << 1) | (bits[i + j] & 1)
        out.append(byte)
    return bytes(out)


def bit_stuff(bits: List[int]) -> List[int]:
    """Insère un '0' après cinq '1' consécutifs."""
    out: List[int] = []
    consec = 0
    for b in bits:
        out.append(b)
        if b == 1:
            consec += 1
            if consec == 5:
                out.append(0)
                consec = 0
        else:
            consec = 0
    return out

def bit_destuff(bits: List[int]) -> List[int]:
    """Supprime les '0' insérés après cinq '1'."""
    out: List[int] = []
    consec = 0
    i = 0
    n = len(bits)
    while i < n:
        b = bits[i]
        out.append(b)
        if b == 1:
            consec += 1
            if consec == 5:
                nxt = i + 1
                if nxt < n and bits[nxt] == 0:
                    i += 1
                consec = 0
        else:
            consec = 0
        i += 1
    return out


if __name__ == '__main__':
    sample = bytes([0b11111000, 0b11111111, 0b00011111])
    print("Octets exemple:", sample)
    bits = bytes_to_bits(sample)
    print("Bits:", ''.join(str(b) for b in bits))
    s = bit_stuff(bits)
    print("Stuffed:", ''.join(str(b) for b in s))
    d = bit_destuff(s)
    print("Restauré?", d == bits)



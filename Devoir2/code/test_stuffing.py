from code import stuffing
import random
import binascii

def bits_to_str(bits):
    return ''.join(str(b) for b in bits)

def test_vector_example():
    """Test déterministe : vérifie stuffing/destuffing."""
    # Construire des octets qui produisent des runs de 1
    data = bytes([0b11111000, 0b01111110, 0b11111111])
    bits = stuffing.bytes_to_bits(data)
    stuffed = stuffing.bit_stuff(bits)
    destuffed = stuffing.bit_destuff(stuffed)
    print("Bits originaux :", bits_to_str(bits))
    print("Bits après stuffing :", bits_to_str(stuffed))
    print("Bits après destuffing :", bits_to_str(destuffed))
    assert destuffed == bits
    print("Test vecteur déterministe : OK")

def test_random_roundtrip(count=100):
    """Tests aléatoires : vérifie round-trip."""
    for i in range(count):
        size = random.randint(1, 20)
        data = bytes(random.getrandbits(8) for _ in range(size))
        bits = stuffing.bytes_to_bits(data)
        stuffed = stuffing.bit_stuff(bits)
        destuffed = stuffing.bit_destuff(stuffed)
        if destuffed != bits:
            print("Échec roundtrip aléatoire #", i)
            print("originaux:", bits_to_str(bits))
            print("stuffed :", bits_to_str(stuffed))
            print("destuff :", bits_to_str(destuffed))
            raise AssertionError("Roundtrip failed")
    print(f"Roundtrip aléatoire ({count} cas) : OK")


def test_assignment_vector():
    """Test demandé dans l'énoncé : affiche avant/après/destuffing + CRC."""
    input_bits_str = '011111101111101111110111110'
    bits = [int(c) for c in input_bits_str]
    stuffed = stuffing.bit_stuff(bits)
    destuffed = stuffing.bit_destuff(stuffed)

    # Convert to bytes (MSB-first) for CRC
    orig_bytes = stuffing.bits_to_bytes(bits, msb_first=True)
    dest_bytes = stuffing.bits_to_bytes(destuffed, msb_first=True)
    crc_orig = binascii.crc_hqx(orig_bytes, 0xFFFF)
    crc_dest = binascii.crc_hqx(dest_bytes, 0xFFFF)

    print('\nTest énoncé :')
    print('Input bits:    ', ''.join(str(b) for b in bits))
    print('Stuffed bits:  ', ''.join(str(b) for b in stuffed))
    print('Destuffed bits:', ''.join(str(b) for b in destuffed))
    print('Expected stuffed (énoncé): 01111101011111001111100111110101111100')
    print('CRC orig:  0x%04X' % crc_orig)
    print('CRC dest:  0x%04X' % crc_dest)
    print('CRC equal:', crc_orig == crc_dest)

    assert destuffed == bits
    assert crc_orig == crc_dest
    print('Test énoncé : OK')

if __name__ == '__main__':
    print("Tests stuffing:")
    test_vector_example()
    test_random_roundtrip(200)
    test_assignment_vector()
    print("OK: stuffing tests")

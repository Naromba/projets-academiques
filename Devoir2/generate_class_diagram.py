#!/usr/bin/env python3
"""
Génère un vrai diagramme UML (PlantUML + Mermaid) à partir du code protocole.py
Sortie : class_diagram.puml et class_diagram.html (avec diagramme UML complet)
"""

import re
from pathlib import Path

def extract_classes_detailed(filepath):
    """Extrait les classes avec tous les détails UML"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    classes = {}
    current_class = None
    
    for i, line in enumerate(lines):
        # Détection de classe
        if line.strip().startswith('class '):
            match = re.match(r'class\s+(\w+)(?:\(([^)]*)\))?:', line)
            if match:
                class_name = match.group(1)
                parent = match.group(2) if match.group(2) else None
                current_class = class_name
                classes[class_name] = {
                    'parent': parent,
                    'attributes': [],
                    'methods': [],
                }
        
        # Détection de __slots__ (attributs principaux)
        elif current_class and '__slots__' in line:
            slots_text = line
            if i+1 < len(lines):
                slots_text += lines[i+1]
            slots_match = re.search(r'__slots__\s*=\s*\((.*?)\)', slots_text, re.DOTALL)
            if slots_match:
                slots_str = slots_match.group(1)
                slots = re.findall(r'"(\w+)"', slots_str)
                for slot in slots:
                    classes[current_class]['attributes'].append((slot, 'any'))
        
        # Détection de méthodes
        elif current_class and re.match(r'\s+def\s+(\w+)\s*\(', line):
            match = re.match(r'\s+def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]*?))?:', line)
            if match:
                method_name = match.group(1)
                params = match.group(2)
                return_type = match.group(3) or 'None'
                
                visibility = '-' if method_name.startswith('_') else '+'
                param_list = []
                if params and params.strip() != 'self':
                    for p in params.split(','):
                        p = p.strip()
                        if p and p != 'self':
                            param_list.append(p.split(':')[0].strip())
                
                classes[current_class]['methods'].append({
                    'name': method_name,
                    'params': param_list,
                    'return': return_type.strip(),
                    'visibility': visibility
                })
    
    return classes

def generate_plantuml(classes):
    """Génère un diagramme PlantUML (PlantText/ASCII UML)"""
    puml = "@startuml ProtocoleSelectiveRepeat\n"
    puml += "!define DIRECTIONMARKER\n"
    puml += "skinparam classBackgroundColor #FEFECE\n"
    puml += "skinparam classBorderColor #D82747\n"
    puml += "skinparam arrowColor #667eea\n\n"
    
    # Classes avec détails
    for class_name, info in sorted(classes.items()):
        puml += f"class {class_name} {{\n"
        
        if info['attributes']:
            for attr, attr_type in info['attributes']:
                puml += f"  {{field}} +{attr}\n"
        
        if info['methods']:
            for method in info['methods']:
                params_str = ', '.join(method['params']) if method['params'] else ''
                puml += f"  {{method}} {method['visibility']}{method['name']}({params_str})\n"
        
        puml += "}\n\n"
    
    # Relations
    puml += "\n' Dépendances\n"
    puml += "Sender --> Canal : \"utilise\"\n"
    puml += "Receiver --> Canal : \"utilise\"\n"
    puml += "Sender --> Frame : \"crée/envoie\"\n"
    puml += "Receiver --> Frame : \"reçoit\"\n"
    
    puml += "\n@enduml\n"
    return puml

def generate_html_complete(classes):
    """Génère un HTML riche avec diagramme UML Mermaid"""
    
    mermaid_diagram = """classDiagram
    class Frame {
        +seq: int
        +acknum: int
        +is_ack: bool
        +payload: bytes
        +length: int
        +crc: int
        +donnees: str
        +to_raw_bytes() bytes
        +to_stuffed_bytes() bytes
        +from_stuffed_bytes(data) Frame
        +verify_crc() bool
        +header_bytes() bytes
    }
    
    class Sender {
        +canal: Canal
        +timeout_ms: int
        +base: int
        +next_seq: int
        +window: dict
        +timers: dict
        +stats: dict
        +send_message(data, receiver)
        +_free_slots() int
        +_send_with_timer(frame)
        +_on_timeout(seq)
        +on_ack_from_rx(ack_frame)
        +bind_receiver(rx_cb)
    }
    
    class Receiver {
        +canal: Canal
        +expected: int
        +buf: list
        +rebuilt: bytearray
        +stats: dict
        +on_from_sender(frame)
        +_to_sender(ack_frame)
        +_in_window(start, x) bool
        +bind_sender_ack(ack_cb)
        +message_bytes() bytes
    }
    
    class Canal {
        +probErreur: float
        +probPerte: float
        +delaiMax: int
        +transmettre(trame, callback)
        -_livrer()
        -_corrompre(trame)
    }
    
    Sender --> Canal
    Receiver --> Canal
    Sender --> Frame
    Receiver --> Frame"""
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Diagramme UML - Protocole Selective Repeat</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .description {{
            background: linear-gradient(135deg, #e8f4f8 0%, #f0e8f8 100%);
            padding: 20px;
            border-left: 5px solid #667eea;
            margin: 30px 0;
            border-radius: 8px;
        }}
        .description h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        .description ul {{
            list-style: none;
            padding: 0;
        }}
        .description li {{
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
            color: #555;
        }}
        .description li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }}
        .diagram-container {{
            display: flex;
            justify-content: center;
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
            border: 2px dashed #ddd;
            overflow-x: auto;
        }}
        .mermaid {{
            min-width: 100%;
            display: flex;
            justify-content: center;
        }}
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .legend-item {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .legend-item h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .legend-item p {{
            color: #666;
            font-size: 0.95em;
            line-height: 1.5;
        }}
        .code-block {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.8;
            white-space: pre;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Diagramme UML</h1>
        <p class="subtitle">Protocole Selective Repeat avec Bit-Stuffing HDLC</p>
        
        <div class="description">
            <h3>Architecture generale</h3>
            <p>Le protocole est compose de <strong>4 classes interconnectees</strong> :</p>
            <ul>
                <li><strong>Frame</strong> : Classe - Trame HDLC encapsulee avec CRC-16 et bit-stuffing</li>
                <li><strong>Sender</strong> : Classe - Emetteur Selective Repeat (fenetre=4, timers individuels, ACKs cumulatifs)</li>
                <li><strong>Receiver</strong> : Classe - Recepteur avec buffer circulaire et ACKs cumulatifs</li>
                <li><strong>Canal</strong> : Classe - Simulation du lien (pertes, erreurs, delais aleatoires)</li>
            </ul>
            <p style="margin-top: 15px;"><strong>Module auxiliaire :</strong> <strong>stuffing.py</strong> - Codeur bit-stuffing HDLC </p>
        </div>
        
        <div class="diagram-container">
            <div class="mermaid">
{mermaid_diagram}
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <h4>Frame (Trame HDLC)</h4>
                <p>Represente une unite de transmission atomique.</p>
                <p><strong>Attributs :</strong> seq, acknum, is_ack, payload, length, crc</p>
                <p><strong>Processus :</strong> Donnees -> Bit-stuffing -> Encadrement 0x7E</p>
                <p><strong>Taille :</strong> payload <= 100 octets</p>
            </div>
            
            <div class="legend-item">
                <h4>Sender (Emetteur SR)</h4>
                <p>Implemente Selective Repeat avec fenetre de 4.</p>
                <p><strong>Logique :</strong></p>
                <ul style="margin-top: 8px;">
                    <li>Segmente message en chunks <=100 octets</li>
                    <li>Cree frames avec seq modulo 8</li>
                    <li>Envoie avec timers individuels</li>
                    <li>Retransmet si timeout >= timeout_ms</li>
                </ul>
                <p style="margin-top: 8px;"><strong>ACKs :</strong> Cumulatifs (ACK n = toutes frames 0..n OK)</p>
            </div>
            
            <div class="legend-item">
                <h4>Receiver (Recepteur SR)</h4>
                <p>Gere la livraison en ordre des donnees.</p>
                <p><strong>Buffer circulaire :</strong> Taille = 4, modulo 8</p>
                <p><strong>Livraison :</strong> En-ordre uniquement</p>
                <p><strong>ACKs :</strong> ACK(expected-1) cumulatif</p>
                <p><strong>Sortie :</strong> message_bytes() = message reconstruit</p>
            </div>
            
            <div class="legend-item">
                <h4>Canal (Simulation reseau)</h4>
                <p>Simule les imperfections du lien physique.</p>
                <p><strong>3 defauts :</strong></p>
                <ul style="margin-top: 8px;">
                    <li>Perte (probPerte) : trame jamais livree</li>
                    <li>Erreur (probErreur) : bit-flip (corruption CRC)</li>
                    <li>Delai (delaiMax) : latence aleatoire 0..delaiMax ms</li>
                </ul>
                <p style="margin-top: 8px;"><strong>Scenarios :</strong> Parfait, Bruite, Instable</p>
            </div>
            
            <div class="legend-item">
                <h4>stuffing.py (Module - Bit-stuffing HDLC)</h4>
                <p>Module avec fonctions.</p>
                <p><strong>Fonctions principales :</strong></p>
                <ul style="margin-top: 8px;">
                    <li>bytes_to_bits(data) : convertit octets -> bits</li>
                    <li>bits_to_bytes(bits) : convertit bits -> octets</li>
                    <li>bit_stuff(bits) : insere un 0 apres 5 bits a 1</li>
                    <li>bit_destuff(bits) : retire les 0 de bourrage</li>
                </ul>
                <p style="margin-top: 8px;"><strong>Flags :</strong> 0x7E encadre chaque trame</p>
            </div>
            
            <div class="legend-item">
                <h4>Flux de communication</h4>
                <p><strong>Donnees (Sender -> Receiver) :</strong></p>
                <ul style="margin-top: 8px;">
                    <li>message.txt (6400 octets)</li>
                    <li>-> Segmentation en 100 octets</li>
                    <li>-> 65 Frames creees (seq 0..64)</li>
                    <li>-> Envoi via Canal</li>
                    <li>-> Reception + verification CRC</li>
                    <li>-> Reconstruction en-ordre</li>
                </ul>
                <p style="margin-top: 8px;"><strong>ACKs (Receiver -> Sender) :</strong> Cumulatifs, en-ordre</p>
            </div>
        </div>
        
        <div class="description" style="margin-top: 40px;">
            <h3>Exemple de flux complet</h3>
            <div class="code-block">
ETAPE 1 : INITIALISATION
- message.txt : 6400 octets
- MAX_PAYLOAD : 100 octets/frame
- MOD : 8 (numerotation modulo 8)
- W : 4 (fenetre Selective Repeat)
- TIMEOUT_MS : 260 ms (doit etre > delaiMax)

ETAPE 2 : SEGMENTATION (Sender.send_message)
- chunks = [data[i:i+100] for i ...]
- 65 chunks de <= 100 octets crees

ETAPE 3 : ENVOI (boucle SR)
1. Sender cree : Frame(seq=2, payload=100 bytes) + CRC-16
2. Bit-stuffing applique
3. Encadrage avec flags 0x7E
4. Envoi via Canal
5. Canal : simule delai, perte ou erreur
6. Receiver : recoit -> destuffing -> verif CRC -> Buffer[2]
7. Receiver : si seq 0,1,2 continus -> rebuild += payload
8. Receiver : expected = 3 -> Envoie ACK(acknum=2)
9. Sender : recoit ACK -> libere frames 0,1,2 -> base = 3

ETAPE 4 : TIMEOUT/RETRANSMISSION
- Si timeout >= 260 ms -> Sender._on_timeout()
- Retransmet Frame(seq=i) avec nouveau timer
- Receiver peut recevoir en-desordre
- Si CRC OK, buffer et attendre sequence
- Livraison reste en-ordre

ETAPE 5 : RECONSTRUCTION/SORTIE
- rebuilt = chunk0 + chunk1 + ... + chunk64
- message_bytes() -> 6400 octets identiques au depart
- Integrite message : SUCCES
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html

if __name__ == '__main__':
    protocole_path = Path(__file__).parent / 'code' / 'protocole.py'
    
    print("Extraction des classes...")
    classes = extract_classes_detailed(protocole_path)
    
    print(f"[OK] {len(classes)} classes trouvees: {', '.join(classes.keys())}")
    
    # Générer PlantUML
    print("\nGeneration du diagramme PlantUML...")
    puml_content = generate_plantuml(classes)
    puml_path = Path(__file__).parent / 'class_diagram.puml'
    with open(puml_path, 'w', encoding='utf-8') as f:
        f.write(puml_content)
    print(f"[OK] {puml_path}")
    
    # Générer HTML complet
    print("\nGeneration du HTML avec diagramme UML Mermaid...")
    html_content = generate_html_complete(classes)
    html_path = Path(__file__).parent / 'class_diagram.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[OK] {html_path}")
    
    print("\nDiagrammes generes avec succes!")
    print(f"\nFichiers crees:")
    print(f"   1. {puml_path} (PlantUML - pour editeurs compatibles)")
    print(f"   2. {html_path} (HTML interactif avec Mermaid)")
    print(f"\nOuvrez {html_path} dans votre navigateur!")

#!/usr/bin/env python3
# =============================================================
# generation_paysage.py
# – Plaque océan 60×60 mm
# – Crête nord à 3 sommets + faille + cascade
# – Deux îles sud : l’une plus grande, l’autre plus petite
# – Océan animé avec petites vagues (bosses bleues)
# – Volcan au sud-ouest avec cratère
# – Arbres et buissons sur le terrain
# – Auteures : Naromba Condé, Rima Boujenane
# =============================================================
import math, random

# ---------- paramètres généraux ----------
plate, thick = 60, 2     
grid          = 60       
tile          = plate / grid
max_h         = 25       
label         = "NC, RB, IFT2125"

# ---------- crête nord & faille ----------
band     = int(grid * 0.38)
peak_w   = grid * 0.35
noise    = 0.2
val_x    = 0.375 * grid
val_w    = grid * 0.05
val_d    = 0.6

# ---------- cascade ----------
riv_x0, riv_w0, riv_fan = 0.62*grid, 0.08*grid, 3.0
riv_depth, water_h      = 0.1, 4
cascade_start           = 0.40

# ---------- îles sud ----------
# île 1 (plus grande)
i1_cx, i1_cy = 0.30*grid, 0.75*grid
i1_r         = 0.24 * grid
i1_h         = 14

# île 2 (plus petite)
i2_cx, i2_cy = 0.65*grid, 0.82*grid
i2_r         = 0.16 * grid
i2_h         = 10

# ---------- volcan ----------
v_cx, v_cy = 0.85 * grid, 0.60 * grid
v_r        = 0.12 * grid 
v_h        = 1.4 * i1_h                 
crater_frac = 0.25          
crater_depth = 0.3 * v_h    
        

# ---------- matrices de données ----------
height = [[0.0]*grid for _ in range(grid)]
water  = [[False]*grid for _ in range(grid)]
waves  = [[random.uniform(0.3, 0.5) for _ in range(grid)] for __ in range(grid)]


# ---------- génération du paysage ----------
# calcul de la crête nord et cascade
for x in range(grid):
    for y in range(grid):
        z = 0.0
        if y < band:
            t     = y / band
            
            if t <= cascade_start:
                slope = 1 # eau de la rivière avant la cascade
            else:
                slope = (1 - t) * 1.5 # pente de la falaise pour la cascade

            # génération de 3 sommets de la falaise
            g = lambda c: math.exp(-((x - c*grid)/peak_w)**4)
            crest = min(g(0.25)+g(0.50)+g(0.75), 1)

            # sommet plat 
            if crest > 1:
                crest = 1.5

            # ajout d'une vallée horizontale
            valley= math.exp(-((x - val_x)/val_w)**2)
            crest *= 1 - val_d * valley

            # ajout de bruit
            z = max_h * slope * crest + random.uniform(-noise, noise)
            z += random.uniform(-0.2, 0.2)  


            # ajout de la rivière et waterfall
            offset = 3 * math.sin(y/5) # ondulation de la rivière
            cen    = riv_x0 + offset
            wid    = riv_w0 + (y/band)*riv_w0*(riv_fan - 2)

            if abs(x - cen) < wid:
                if t <= cascade_start:
                    # altitude constante pour la rivière sur le plateau
                    # recommendation de ChatGPT après avoir trouvé une erreur
                    # qui rendait la rivière trop haute
                    river_level = max_h - 0.17 * max_h
                    z = river_level
                else:
                    z = z * (1 - riv_depth * (t - cascade_start))
                water[x][y] = True

            if t > cascade_start and abs(x - cen) < wid:
                z = z * (1 - riv_depth * t)
                water[x][y] = True
                
        height[x][y] = max(0, min(z, max_h))


# Génération des îles sud
for x in range(grid):
    for y in range(band, grid):
        # island 1
        dx1 = (x - i1_cx) * random.uniform(0.7,1.1)  
        dy1 = (y - i1_cy) * random.uniform(0.9,1.1)  
        d1  = math.sqrt(dx1**2 + dy1**2)
        h1  = i1_h * max(0, 1 - (d1/i1_r)**2)

        dx2 = (x - i2_cx) * random.uniform(0.9,1.1)
        dy2 = (y - i2_cy) * random.uniform(0.5,1.1)
        d2  = math.sqrt(dx2**2 + dy2**2)
        h2  = i2_h * max(0, 1 - (d2/i2_r)**2)
        z_isle   = max(h1, h2)
        if not water[x][y]:
            height[x][y] = max(height[x][y], z_isle)

# Génération du volcan
for x in range(grid):
    for y in range(grid):
        dx = (x - v_cx) * random.uniform(0.9,1.1)  
        dy = (y - v_cy) * random.uniform(0.9,1.1)  
        d = math.hypot(dx, dy)

        if d < v_r:
            volcano_z = v_h * (1 - (d/v_r)**2)
            height[x][y] = max(height[x][y], volcano_z)

        if d < v_r * crater_frac:
            height[x][y] = max(0, height[x][y] - crater_depth)
            water[x][y] = True  



# écriture du SCAD
with open("model.scad","w",encoding="utf-8") as sc:

    # Plaque océan
    sc.write("color([0,0.6,1])\n")
    sc.write(f"cube([{plate},{plate},{thick}], center=false);\n\n")

    # Petites vagues sur l'océan
    for x in range(grid):
        for y in range(grid):
            if height[x][y] == 0 and not water[x][y]:
                w = waves[x][y]
                sc.write(f"translate([{x*tile:.2f},{y*tile:.2f},{thick:.2f}]) "
                         "color([0,0.5,0.9]) "
                         f"cube([{tile:.2f},{tile:.2f},{w:.2f}], center=false);\n")

    # Eau, terrain et végétation
    for x in range(grid):
        for y in range(grid):
            z = height[x][y]

            # eau cascade
            if water[x][y]:
                sc.write(f"translate([{x*tile:.2f},{y*tile:.2f},{thick+z:.2f}]) "
                         "color([[0,0.6,1]]) "
                         f"cube([{tile:.2f},{tile:.2f},{water_h:.2f}], center=false);\n")
                         
            # terrain avec du sable, herbe et rochers
            if z > 0:
                if z < 4: 
                    col = "[0.9,0.8,0.6]"  
                elif y >= band:
                    thresh = (i1_h if z<=i1_h else i2_h) * 0.5
                    col = "[0,0.6,0.2]" if z < thresh else "[0.5,0.4,0.25]" 
                else:
                    col = "[0,0.6,0]" if z < 8 else "[0.4,0.3,0.15]"
                
                sc.write(f"translate([{x*tile:.2f},{y*tile:.2f},{thick:.2f}]) "
                        f"color({col}) "
                        f"cube([{tile:.2f},{tile:.2f},{z:.2f}], center=false);\n")
                
            # Lave dans le cratère du volcan    
            if water[x][y]:
                dx = (x - v_cx) * random.uniform(0.9,1.1)  
                dy = (y - v_cy) * random.uniform(0.9,1.1)  
                d = math.hypot(dx, dy)
                if d < v_r * crater_frac * random.uniform(1.0, 1.5):
                    water_col = "[1,0.2,0]"  #lave
                else:
                    water_col = "[0,0.6,1]"    #eau normale
                lava_bump = random.uniform(0.0, 1.5) if water_col == "[1,0.2,0]" else 0
                sc.write(f"translate([{x*tile:.2f},{y*tile:.2f},{thick+z+lava_bump:.2f}]) "
                        f"color({water_col}) cube([{tile:.2f},{tile:.2f},{water_h:.2f}], center=false);\n")

            # arbres et buissons aléatoires   
            if not water[x][y] and 5 < z < max_h + 1:
                chance = random.random()
                if chance < 0.05:  
                    obj_type = random.random()

                    
                    green_shade = random.uniform(0.2, 1)  
                    foliage_color = f"[0,{green_shade:.2f},0]"

                    if obj_type < 0.7:  
                        trunk_height = random.uniform(1.5, 3.0)
                        foliage_radius = random.uniform(1.0, 1.8)
                        
                        sc.write(f"translate([{x*tile+tile/2:.2f},{y*tile+tile/2:.2f},{thick+z:.2f}]) "
                                "color([0.4,0.2,0.1]) cylinder(h="
                                f"{trunk_height:.2f}, r=0.3, center=false, $fn=6);\n")

                        sc.write(f"translate([{x*tile+tile/2:.2f},{y*tile+tile/2:.2f},{thick+z+trunk_height:.2f}]) "
                                f"color({foliage_color}) sphere(r="
                                f"{foliage_radius:.2f}, $fn=8);\n")
                        
                        if random.random() < 0.3:
                            lighter_green = random.uniform(0.6, 0.9)
                            foliage_color2 = f"[0,{lighter_green:.2f},0]"
                            sc.write(f"translate([{x*tile+tile/2:.2f},{y*tile+tile/2:.2f},{thick+z+trunk_height+foliage_radius/1.5:.2f}]) "
                                    f"color({foliage_color2}) sphere(r="
                                    f"{foliage_radius*0.7:.2f}, $fn=8);\n")
                    
                    else:  
                        bush_radius = random.uniform(0.5, 1.2)
                        sc.write(f"translate([{x*tile+tile/2:.2f},{y*tile+tile/2:.2f},{thick+z+0.1:.2f}]) "
                                f"color({foliage_color}) sphere(r="
                                f"{bush_radius:.2f}, $fn=8);\n")

    # Gravure texte sous la plaque
    sc.write("\ntranslate([0,0,-1])\nlinear_extrude(height=1)\n")
    sc.write(f'    text("{label}", size=5, font="Liberation Sans");\n\n')

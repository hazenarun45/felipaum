# -*- coding: utf-8 -*-
"""Builds the multi-page motorhome electrical schematic PDF."""
from reportlab.pdfgen import canvas
from diagram_lib import (Sheet, COL, PW, PH, MARGIN, FONT, FONTB, tint,
                         page_frame, legend)


# ---- small inline icons -----------------------------------------------------
def ic_battery(s, x, y, w, hh):
    bx, by = x + w - 58, y + hh + 10
    s.rect(bx, by, 40, 22, stroke=COL["battery"], lw=1.2, r=2)
    s.rect(bx + 40, by + 6, 4, 10, fill=COL["battery"])
    for i in range(3):
        s.line(bx + 10 + i * 10, by + 4, bx + 10 + i * 10, by + 18,
               COL["battery"], 1)


def ic_vents(col):
    def f(s, x, y, w, hh):
        bx, by = x + w - 52, y + hh + 12
        for i in range(5):
            s.line(bx, by + i * 4, bx + 36, by + i * 4, tint(COL[col], 0.4), 1.4)
    return f


# ============================================================ PAGE 1
def page1(c, total):
    s = Sheet(c)
    page_frame(s, 1, total, "Visão Geral — Baterias & Cadeia Lynx",
               "Power In → BMS NG 500A → Lynx Distributor 1 → Lynx Distributor 2",
               COL["lynx"])

    # batteries (purple) left
    bx = 70
    b1 = s.device(bx, 150, 250, "battery", "Lithium NG 25.6V 300Ah",
                  ["Bateria #1 · 7.68 kWh", "Terminais M10 · 20–25 Nm"],
                  subtitle="Victron Lithium Smart NG", icon=ic_battery)
    b2 = s.device(bx, 340, 250, "battery", "Lithium NG 25.6V 300Ah",
                  ["Bateria #2 · 7.68 kWh", "Terminais M10 · 20–25 Nm"],
                  subtitle="Victron Lithium Smart NG", icon=ic_battery)

    s.note(bx, 510, 250, "BANCO 24V — PARALELO EM ESTRELA",
           ["2x 300Ah = 600Ah / 15.36 kWh",
            "Cabos de comprimento idêntico",
            "(star point) p/ balanceamento",
            "Cabo de banco: 50mm²"], COL["battery"])

    # star point
    spx, spy = 360, 280
    s.dot(spx, spy, 5, COL["battery"])
    s.text(spx - 4, spy + 12, "STAR", size=8, color=COL["battery"], font=FONTB)
    # battery cables to star (50mm²)
    s.cable([(b1[0] + b1[2], 200), (spx, 200), (spx, spy)], "50mm²",
            COL["battery"], tag_at=0.5)
    s.cable([(b2[0] + b2[2], 390), (spx, 390), (spx, spy)], "50mm²",
            COL["battery"], tag=False)

    # ---- Lynx horizontal chain (teal) ----
    row_y = 250
    mod_w = 230
    gap = 56
    x0 = 430
    xs = [x0 + i * (mod_w + gap) for i in range(4)]

    pin = s.device(xs[0], row_y, mod_w, "lynx", "Lynx Power In",
                   ["Barramento de entrada", "Conexão do banco 24V",
                    "M8 · busbar comum"], subtitle="Lynx Distributor base")
    bms = s.device(xs[1], row_y, mod_w, "lynx", "BMS NG 500A",
                   ["Shunt + SOC integrado", "Contator 500A failsafe",
                    "Pré-carga integrada", "ATC / ATD (contatos secos)",
                    "DVCC · AUX 24V 1.1A"], subtitle="Victron Lynx Smart BMS NG")
    d1 = s.device(xs[2], row_y, mod_w, "lynx", "Lynx Distributor 1",
                  ["4 slots CARREGADORES", "S1 MEGA 300A · S2 100A",
                   "S3 livre · S4 MEGA 60A"], subtitle="Lado de geração")
    d2 = s.device(xs[3], row_y, mod_w, "lynx", "Lynx Distributor 2",
                  ["4 slots CARGAS", "S1 40A · S2 40A", "S3 50A · S4 livre"],
                  subtitle="Lado de consumo")

    midy = row_y + 60
    # star -> power in (50mm²)
    s.cable([(spx, spy), (spx, midy), (xs[0], midy)], "50mm²", COL["lynx"],
            tag_at=0.55)
    # chain busbar links 50mm²
    for a, b in [(pin, bms), (bms, d1), (d1, d2)]:
        s.cable([(a[0] + a[2], midy), (b[0], midy)], "50mm²", COL["lynx"],
                tag=False)
        s.text((a[0] + a[2] + b[0]) / 2, midy - 12, "busbar 500A", size=8,
               color=COL["lynx"], font=FONTB, align="c")

    # arrows of flow
    for b in [pin, bms, d1]:
        ax = b[0] + b[2] + gap / 2
        s.polyline([(ax - 7, midy - 5), (ax + 5, midy), (ax - 7, midy + 5)],
                   COL["lynx"], 2)

    # downstream pointers
    s.text(d1[0] + d1[2] / 2, d1[1] + d1[3] + 16,
           "→ Detalhe na Folha 2 (carregadores + alternador)", size=9,
           color=COL["lynx"], font=FONTB, align="c")
    s.text(d2[0] + d2[2] / 2, d2[1] + d2[3] + 16,
           "→ Detalhe na Folha 3 (cargas + Battery Protect)", size=9,
           color=COL["lynx"], font=FONTB, align="c")

    # DVCC / comms note under BMS
    s.note(xs[1] - 10, 470, 250, "BMS NG — CONTROLE INTEGRADO",
           ["DVCC controla MultiPlus, MPPTs", "e Orion XS via Cerbo GX",
            "ATD → Battery Protect (Folha 3)", "VE.Can → Cerbo (Folha 5)"],
           COL["lynx"])

    legend(s, PW - MARGIN - 230, PH - MARGIN - 56 - 196,
           [("MultiPlus / Inversor", "multiplus"),
            ("Solar (MPPT)", "solar"),
            ("Baterias 24V", "battery"),
            ("Cadeia Lynx", "lynx"),
            ("Alternador (Orion XS)", "alt"),
            ("Battery Protect", "bp"),
            ("AC 230V", "ac"),
            ("DC 12V", "dc12")])
    c.showPage()


# ============================================================ PAGE 2
def page2(c, total):
    s = Sheet(c)
    page_frame(s, 2, total, "Lynx Distributor 1 — Carregadores & Alternador",
               "4 slots de geração + circuito do alternador 210A via Orion XS",
               COL["solar"])

    # Distributor 1 busbar block on the left, vertical slots
    dx, dy, dw = 70, 150, 250
    dist = s.device(dx, dy, dw, "lynx", "Lynx Distributor 1",
                    ["Barramento 24V positivo", "4 slots fusíveis MEGA",
                     "Conecta BMS NG ← → D2"], subtitle="Lado de geração",
                    minh=560)
    # slot anchor points on right edge
    slot_y = [dy + 100, dy + 230, dy + 360, dy + 500]
    slot_lbl = ["S1", "S2", "S3", "S4"]
    busx = dx + dw
    for sy, sl in zip(slot_y, slot_lbl):
        s.chip(busx - 44, sy - 8, sl, COL["lynx"], w=34, size=9)

    colx = 470          # fuse column
    devx = 720          # device column
    devw = 300

    # S1 -> MultiPlus (300A MEGA, 50mm²)
    s.cable([(busx, slot_y[0]), (colx - 34, slot_y[0])], "50mm²",
            COL["multiplus"])
    s.fuse(colx, slot_y[0], "MEGA 300A", big=True, w=86)
    s.cable([(colx + 43, slot_y[0]), (devx, slot_y[0])], "50mm²",
            COL["multiplus"], tag=False)
    s.device(devx, slot_y[0] - 36, devw, "multiplus",
             "MultiPlus II 24/5000/120",
             ["Inversor/Carregador 5kVA 230V", "Cabo CC 50mm² (<1.5 m)",
              "VE.Bus → Cerbo GX"], subtitle="Victron MultiPlus-II",
             icon=ic_vents("multiplus"))

    # S2 -> MPPT 150/85 (100A MEGA, 16mm²)
    s.cable([(busx, slot_y[1]), (colx - 34, slot_y[1])], "16mm²", COL["solar"])
    s.fuse(colx, slot_y[1], "MEGA 100A", big=True, w=86)
    s.cable([(colx + 43, slot_y[1]), (devx, slot_y[1])], "16mm²",
            COL["solar"], tag=False)
    s.device(devx, slot_y[1] - 34, devw, "solar", "MPPT 150/85",
             ["Solar teto 2240 Wp", "VE.Direct → Cerbo GX"],
             subtitle="SmartSolar MPPT", icon=ic_vents("solar"))

    # S3 -> LIVRE (placa solar flexível removida)
    s.cable([(busx, slot_y[2]), (colx - 34, slot_y[2])], "", COL["lynx"],
            tag=False)
    s.rect(colx - 34, slot_y[2] - 20, 300, 40, fill=COL["panel"],
           stroke=COL["lynx"], lw=1, r=6, dash=(4, 3))
    s.text(colx + 116, slot_y[2] - 7, "SLOT 3 — LIVRE (expansão futura)",
           size=9.5, color=COL["lynx"], font=FONTB, align="c")
    s.text(colx + 116, slot_y[2] + 7, "reservado p/ novo carregador solar",
           size=8.5, color=COL["muted"], align="c")

    # S4 -> 2x Orion XS (60A MEGA, 16mm² each, inline 30A). Detail is in the
    # alternator band below; here we only show the slot + pointer.
    s.cable([(busx, slot_y[3]), (colx - 34, slot_y[3])], "16mm²", COL["alt"])
    s.fuse(colx, slot_y[3], "MEGA 60A", big=True, w=78)
    s.cable([(colx + 39, slot_y[3]), (606, slot_y[3])], "16mm²",
            COL["alt"], tag=False)
    s.fuse(644, slot_y[3], "inline 30A", w=70)
    s.cable([(680, slot_y[3]), (devx, slot_y[3])], "16mm²", COL["alt"],
            tag=False)
    s.chip(devx, slot_y[3] - 10, "2x Orion XS 1400  →  ver circuito abaixo",
           COL["alt"], size=10, h=20)
    # dashed connector down to the alternator band
    s.polyline([(devx + 150, slot_y[3] + 10), (devx + 150, 752)],
               COL["alt"], 1.6, dash=(5, 3))
    s.text(devx + 158, 730, "entrada do alternador", size=8.5,
           color=COL["alt"], font=FONTB)

    # ---- Alternator circuit (bottom band) ----
    ay = 760
    s.rect(60, ay, PW - 120, 300, fill=tint(COL["alt"], 0.95),
           stroke=COL["alt"], lw=1, r=8, dash=(4, 3))
    s.text(80, ay + 14, "CIRCUITO DO ALTERNADOR (entra no Slot 4 do Distributor 1)",
           size=11, color=COL["alt"], font=FONTB)

    alt = s.device(90, ay + 60, 260, "alt", "Alternador 12V 210A",
                   ["Iveco Daily 65-180 4x4", "Saída 25mm² → ANL fuses"],
                   subtitle="Chassi / motor")
    anly = [ay + 90, ay + 200]
    fx = 430
    s.cable([(alt[0] + alt[2], alt[1] + 30), (fx - 40, alt[1] + 30),
             (fx - 40, anly[0])], "25mm²", COL["alt"])
    s.cable([(alt[0] + alt[2], alt[1] + 30), (fx - 40, alt[1] + 30),
             (fx - 40, anly[1])], "25mm²", COL["alt"], tag=False)
    s.fuse(fx, anly[0], "ANL 80A", big=True, w=72)
    s.fuse(fx, anly[1], "ANL 80A", big=True, w=72)
    ox = 560
    oa = s.device(ox, anly[0] - 30, 240, "alt", "Orion XS 1400 #1",
                  ["50A @12V in · 600W", "~23A @24V out"], subtitle="DC-DC")
    ob = s.device(ox, anly[1] - 30, 240, "alt", "Orion XS 1400 #2",
                  ["50A @12V in · 600W", "~23A @24V out"], subtitle="DC-DC")
    s.cable([(fx + 36, anly[0]), (ox, anly[0])], "16mm²", COL["alt"], tag=False)
    s.cable([(fx + 36, anly[1]), (ox, anly[1])], "16mm²", COL["alt"], tag=False)
    # orion outputs -> inline 30A -> D1 S4
    ix = 900
    s.cable([(oa[0] + oa[2], anly[0]), (ix - 34, anly[0])], "16mm²",
            COL["alt"])
    s.cable([(ob[0] + ob[2], anly[1]), (ix - 34, anly[1])], "16mm²",
            COL["alt"], tag=False)
    s.fuse(ix, anly[0], "inline 30A", w=70)
    s.fuse(ix, anly[1], "inline 30A", w=70)
    s.cable([(ix + 35, anly[0]), (1060, anly[0]), (1060, ay + 130),
             (1180, ay + 130)], "16mm²", COL["alt"], tag=False)
    s.cable([(ix + 35, anly[1]), (1060, anly[1]), (1060, ay + 130)], "16mm²",
            COL["alt"], tag=False)
    s.chip(1185, ay + 122, "→ Distributor 1 · Slot 4", COL["lynx"], size=9.5)
    s.note(1185, ay + 160, 380, "OBS — ALTERNADOR",
           ["Saída @24V dos 2x Orion XS retorna ao",
            "Distributor 1 Slot 4 (MEGA 60A) e",
            "carrega o banco junto com o solar."], COL["alt"])
    c.showPage()


# ============================================================ PAGE 3
def page3(c, total):
    s = Sheet(c)
    page_frame(s, 3, total, "Lynx Distributor 2 — Cargas & Battery Protect",
               "4 slots de consumo · Battery Protect 100A no Slot 3 (cargas não-DVCC)",
               COL["bp"])

    dx, dy, dw = 70, 150, 250
    s.device(dx, dy, dw, "lynx", "Lynx Distributor 2",
             ["Barramento 24V positivo", "4 slots fusíveis MEGA",
              "Recebe do Distributor 1"], subtitle="Lado de consumo", minh=560)
    busx = dx + dw
    slot_y = [dy + 110, dy + 220, dy + 360, dy + 500]
    for sy, sl in zip(slot_y, ["S1", "S2", "S3", "S4"]):
        s.chip(busx - 44, sy - 8, sl, COL["lynx"], w=34, size=9)

    colx = 470
    devx = 700

    # S1 AC HENT #1 (40A MEGA, 35mm²)
    s.cable([(busx, slot_y[0]), (colx - 34, slot_y[0])], "35mm²", COL["ac"])
    s.fuse(colx, slot_y[0], "MEGA 40A", big=True, w=78)
    s.cable([(colx + 39, slot_y[0]), (devx, slot_y[0])], "35mm²", COL["ac"],
            tag=False)
    s.device(devx, slot_y[0] - 30, 300, "ac", "Ar-Cond. HENT #1",
             ["Inversor 24V · ~35A máx", "Conexão direta (sem BP)"],
             subtitle="HENT 24V Inverter", icon=ic_vents("ac"))

    # S2 AC HENT #2
    s.cable([(busx, slot_y[1]), (colx - 34, slot_y[1])], "35mm²", COL["ac"])
    s.fuse(colx, slot_y[1], "MEGA 40A", big=True, w=78)
    s.cable([(colx + 39, slot_y[1]), (devx, slot_y[1])], "35mm²", COL["ac"],
            tag=False)
    s.device(devx, slot_y[1] - 30, 300, "ac", "Ar-Cond. HENT #2",
             ["Inversor 24V · ~35A máx", "Conexão direta (sem BP)"],
             subtitle="HENT 24V Inverter", icon=ic_vents("ac"))

    # S3 -> Battery Protect chain
    s.cable([(busx, slot_y[2]), (colx - 34, slot_y[2])], "10mm²", COL["bp"])
    s.fuse(colx, slot_y[2], "MEGA 50A", big=True, w=78)
    s.cable([(colx + 39, slot_y[2]), (devx, slot_y[2])], "10mm²", COL["bp"],
            tag=False)
    bp = s.device(devx, slot_y[2] - 36, 230, "bp", "Battery Protect 100A",
                  ["IN ← D2-S3 · OUT → cargas", "Remote H/L ← ATD do BMS NG"],
                  subtitle="Smart BatteryProtect 24V")
    # BP remote control dashed from BMS ATD
    s.cable([(bp[0] + bp[2] / 2, bp[1]), (bp[0] + bp[2] / 2, 120),
             (1280, 120)], "", COL["lynx"], tag=False)
    s.polyline([(bp[0] + bp[2] / 2, bp[1]), (bp[0] + bp[2] / 2, 120),
                (1280, 120)], COL["lynx"], 1.4, dash=(5, 3))
    s.chip(1285, 112, "ATD · BMS NG (bateria baixa → desliga)", COL["lynx"],
           size=9)

    # BP OUT split -> 3 inline fuses
    spx = bp[0] + bp[2]
    spy = slot_y[2]
    s.dot(spx + 30, spy, 4, COL["bp"])
    out_y = [spy - 90, spy, spy + 90]
    fx2 = 1110
    s.polyline([(spx, spy), (spx + 30, spy)], COL["bp"], 2)
    # Orion 24/12
    s.cable([(spx + 30, spy), (spx + 30, out_y[0]), (fx2 - 34, out_y[0])],
            "10mm²", COL["bp"])
    s.fuse(fx2, out_y[0], "inline 50A", w=70)
    s.cable([(fx2 + 35, out_y[0]), (1240, out_y[0])], "10mm²", COL["bp"],
            tag=False)
    s.device(1240, out_y[0] - 30, 300, "dc12", "Orion 24/12 70A",
             ["12.2V regulado · 840W", "→ Barramento 12V (Folha 4)"],
             subtitle="Orion-Tr Smart 24/12")
    # Fridge 1
    s.cable([(spx + 30, spy), (spx + 30, out_y[1]), (fx2 - 34, out_y[1])],
            "4mm²", COL["bp"], tag=False)
    s.fuse(fx2, out_y[1], "inline 15A", w=70)
    s.cable([(fx2 + 35, out_y[1]), (1240, out_y[1])], "4mm²", COL["bp"],
            tag=False)
    s.device(1240, out_y[1] - 24, 300, "bp", "Geladeira TopRV #1",
             ["Compressor 24V"], subtitle="TopRV")
    # Fridge 2
    s.cable([(spx + 30, spy), (spx + 30, out_y[2]), (fx2 - 34, out_y[2])],
            "4mm²", COL["bp"], tag=False)
    s.fuse(fx2, out_y[2], "inline 15A", w=70)
    s.cable([(fx2 + 35, out_y[2]), (1240, out_y[2])], "4mm²", COL["bp"],
            tag=False)
    s.device(1240, out_y[2] - 24, 300, "bp", "Geladeira TopRV #2",
             ["Compressor 24V"], subtitle="TopRV")

    # S4 free
    s.cable([(busx, slot_y[3]), (colx - 34, slot_y[3])], "", COL["lynx"],
            tag=False)
    s.rect(colx - 34, slot_y[3] - 18, 240, 36, fill=COL["panel"],
           stroke=COL["lynx"], lw=1, r=6, dash=(4, 3))
    s.text(colx + 86, slot_y[3] - 6, "SLOT 4 — LIVRE (expansão futura)",
           size=9.5, color=COL["lynx"], font=FONTB, align="c")
    s.text(colx + 86, slot_y[3] + 6, "som · 3ª bateria · etc.", size=8.5,
           color=COL["muted"], align="c")

    s.note(70, 740, 470, "POR QUE BATTERY PROTECT SÓ NO SLOT 3?",
           ["ACs HENT ficam FORA do BP: 70A + 42A (Orion+gelas) = 112A > 100A.",
            "Dispositivos DVCC (MultiPlus, MPPTs, Orion XS) param via software.",
            "BP desconecta graciosamente cargas não-DVCC quando ATD abre."],
           COL["bp"])
    c.showPage()


# ============================================================ PAGE 4
def page4(c, total):
    s = Sheet(c)
    page_frame(s, 4, total, "Barramento 12V DC",
               "Orion 24/12 70A → busbar 12.2V · bitolas, fusíveis e queda de tensão",
               COL["dc12"])

    orion = s.device(70, 150, 250, "dc12", "Orion 24/12 70A",
                     ["Saída 12.2V regulada", "840W · queda ≤ 2.1%"],
                     subtitle="Orion-Tr Smart")
    # positive busbar (vertical)
    busx = 360
    bus_top, bus_bot = 150, 1040
    s.cable([(orion[0] + orion[2], 195), (busx, 195), (busx, bus_top)],
            "10mm²", COL["dc12"], tag_at=0.5)
    s.rect(busx - 8, bus_top, 16, bus_bot - bus_top, fill=COL["dc12"], r=4)
    s.text(busx, bus_top - 12, "+ BUSBAR 12V", size=9, color=COL["dc12"],
           font=FONTB, align="c")
    s.rect(busx + 760, bus_top, 16, bus_bot - bus_top,
           fill=tint(COL["ink"], 0.3), r=4)
    s.text(busx + 768, bus_top - 12, "– BUSBAR", size=9,
           color=tint(COL["ink"], 0.2), font=FONTB, align="c")

    circuits = [
        ("Shelly 1 — quarto teto 4000K", "4mm²", "ATO 10A", "~5A", "1.8%"),
        ("Shelly 1 — sala teto 4000K", "4mm²", "ATO 10A", "~5A", "1.4%"),
        ("Shelly 1 — banheiro teto 4000K", "4mm²", "ATO 10A", "~4A", "1.4%"),
        ("Shelly 1 — spots mesa sala", "2.5mm²", "ATO 5A", "~2A", "0.9%"),
        ("Shelly 1 — COB indiretas banheiro", "4mm²", "ATO 10A", "~3A", "1.3%"),
        ("Shelly 1 — COB rodapé cozinha", "2.5mm²", "ATO 10A", "~4A", "1.4%"),
        ("Shelly 1 — COB bancada cozinha", "2.5mm²", "ATO 10A", "~4A", "1.4%"),
        ("Shelly 1 — COB armários cozinha", "2.5mm²", "ATO 10A", "~3A", "1.0%"),
        ("Shelly 1 — COB ext. banheiro", "4mm²", "ATO 10A", "~3A", "1.3%"),
        ("Shelly 1 — COB indiretas quarto", "4mm²", "ATO 10A", "~4A", "1.4%"),
        ("2x Shelly 1 — toldo motor", "4mm²", "ATO 15A", "~8A", "1.4%"),
        ("2x Shelly 1 — escada motor", "4mm²", "ATO 15A", "~6A", "1.0%"),
        ("2x Shelly 1 — mesa elétrica", "4mm²", "ATO 15A", "~6A", "1.0%"),
        ("Câmeras 360° + NVR", "6mm²", "ATO 10A", "~5A", "1.4%"),
        ("Starlink Mini", "2.5mm²", "ATO 10A", "~5A", "1.7%"),
        ("Router GL-X2000", "2.5mm²", "ATO 3A", "~1A", "<1%"),
        ("Tomadas 12V / USB", "10mm²", "ATO 15A", "~10A", "1.4%"),
    ]
    n = len(circuits)
    y0, y1 = bus_top + 16, bus_bot - 16
    step = (y1 - y0) / (n - 1)
    fx = busx + 230
    namex = busx + 270
    for i, (name, g, fu, cur, drop) in enumerate(circuits):
        yy = y0 + i * step
        s.cable([(busx + 8, yy), (fx - 26, yy)], g, COL["dc12"], tag=False)
        s.fuse(fx, yy, fu, w=64, h=15)
        s.cable([(fx + 32, yy), (namex - 6, yy)], g, COL["dc12"], tag=False)
        # negative return (thin) to neg busbar
        s.line(busx + 752, yy, busx + 760, yy, tint(COL["ink"], 0.3), 1)
        s.line(namex + 400, yy, busx + 752, yy, tint(COL["ink"], 0.45), 0.7,
               dash=(2, 2))
        # label row
        s.text(namex, yy - 5.5, name, size=9.4, color=COL["ink"], font=FONTB)
        s.chip(namex + 268, yy - 8, g, COL["dc12"], w=52, size=8)
        s.text(namex + 330, yy - 5.5, cur, size=8.8, color=COL["muted"])
        s.text(namex + 380, yy - 5.5, "Δ " + drop, size=8.8,
               color=COL["multiplus"] if drop.endswith("8%") else COL["muted"])

    # header row
    s.text(namex, y0 - 26, "CIRCUITO", size=9, color=COL["dc12"], font=FONTB)
    s.text(namex + 268, y0 - 26, "BITOLA", size=9, color=COL["dc12"],
           font=FONTB)
    s.text(namex + 330, y0 - 26, "I", size=9, color=COL["dc12"], font=FONTB)
    s.text(namex + 380, y0 - 26, "QUEDA", size=9, color=COL["dc12"], font=FONTB)
    c.showPage()


# ============================================================ PAGE 5
def page5(c, total):
    s = Sheet(c)
    page_frame(s, 5, total, "Quadro AC 230V & Comunicação / Rede",
               "Saída MultiPlus II 230V · portas Cerbo GX · rede WiFi e BLE",
               COL["multiplus"])

    # --- AC panel (left) ---
    s.text(70, 130, "QUADRO AC 230V (saída MultiPlus II)", size=12,
           color=COL["ac"], font=FONTB)
    mp = s.device(70, 160, 230, "multiplus", "MultiPlus II 24/5000",
                  ["Saída AC 230V 50Hz", "Disjuntor geral bipolar 25A"],
                  subtitle="Inversor/Carregador")
    acbus = 330
    s.cable([(mp[0] + mp[2], 205), (acbus, 205), (acbus, 230)], "4mm²",
            COL["ac"], tag=False)
    s.rect(acbus - 7, 230, 14, 470, fill=COL["ac"], r=4)
    s.text(acbus, 218, "BARRA AC 230V", size=8.5, color=COL["ac"],
           font=FONTB, align="c")
    ac = [
        ("Cooktop indução", "2000W", "4mm² 3-vias", "Bipolar 16A"),
        ("Brastemp Gourmand 31L", "~2100W (16A)", "4mm² 3-vias", "Bipolar 16A"),
        ("Tomadas 220V gerais", "variável", "2.5mm² 3-vias", "Bipolar 10A"),
        ("Monitor 27\" + eletrônicos", "~100W", "2.5mm² 3-vias", "Bipolar 6A"),
    ]
    yy = 270
    for name, p, cab, dj in ac:
        s.cable([(acbus + 7, yy), (acbus + 70, yy)],
                "4mm²" if "4mm" in cab else "2.5mm²", COL["ac"], tag=False)
        s.fuse(acbus + 100, yy, dj.replace("Bipolar ", ""), big=True, w=54)
        d = s.device(acbus + 140, yy - 22, 300, "ac", name, [f"{p} · {cab}"],
                     subtitle=None, hh=22)
        yy += 110

    # --- Communication (right) ---
    s.text(900, 130, "COMUNICAÇÃO — CERBO GX", size=12, color=COL["comm"],
           font=FONTB)
    cerbo = s.device(900, 160, 230, "comm", "Cerbo GX",
                     ["Gateway / DVCC", "Modo CLIENTE WiFi"],
                     subtitle="Victron Cerbo GX", minh=360)
    ports = [
        ("VE.Bus", "MultiPlus II", "RJ45 UTP", "multiplus"),
        ("VE.Direct 1", "MPPT 150/85", "VE.Direct 5m", "solar"),
        ("VE.Can", "BMS NG (+term. azul)", "RJ45", "lynx"),
        ("USB 1", "GX Touch 70", "USB incluído", "comm"),
        ("USB 2", "TP-Link UB500 BT", "RuuviTag/Mopeka BLE", "comm"),
    ]
    px = 1130
    yy = 190
    for port, dev, cab, key in ports:
        s.chip(px - 36, yy - 8, port, COL["comm"], w=84, size=8)
        s.cable([(px + 48, yy), (px + 120, yy)], "2.5mm²", COL[key], tag=False)
        s.device(px + 120, yy - 16, 330, key, dev, [cab], hh=20)
        yy += 80

    # --- WiFi / network band ---
    ny = 740
    s.rect(60, ny, PW - 120, 250, fill=tint(COL["comm"], 0.95),
           stroke=COL["comm"], lw=1, r=8, dash=(4, 3))
    s.text(80, ny + 14, "REDE WiFi & BLE", size=11, color=COL["comm"],
           font=FONTB)
    sl = s.device(90, ny + 50, 220, "comm", "Starlink Mini",
                  ["Internet satélite", "Ethernet → roteador"], subtitle="WAN")
    rt = s.device(390, ny + 50, 220, "comm", "GL.iNet GL-X2000",
                  ["Roteador principal", "WAN ← Starlink"], subtitle="Spitz AX")
    s.cable([(sl[0] + sl[2], ny + 80), (rt[0], ny + 80)], "2.5mm²",
            COL["comm"], tag=False)
    s.text((sl[0] + sl[2] + rt[0]) / 2, ny + 64, "ethernet", size=8,
           color=COL["comm"], font=FONTB, align="c")
    s.device(690, ny + 50, 240, "comm", "Rede local WiFi",
             ["16x Shelly · Cerbo (cliente)", "Echo Dot · Tablet · Celulares",
              "NVR câmeras 360°"], subtitle="SSID único")
    s.device(1000, ny + 50, 240, "comm", "Sensores BLE",
             ["3–5x RuuviTag (temp/umid)", "3x Mopeka Pro (nível tanque)"],
             subtitle="via TP-Link UB500")
    s.polyline([(rt[0] + rt[2], ny + 80), (685, ny + 80)], COL["comm"], 1.4,
               dash=(5, 3))
    s.note(1300, ny + 50, 320, "OBS — REDE",
           ["Cerbo GX em modo CLIENTE (não AP).",
            "Todos na mesma rede do roteador.",
            "VRM via 4G/Starlink."], COL["comm"])
    c.showPage()


# ============================================================ PAGE 6
def page6(c, total):
    s = Sheet(c)
    page_frame(s, 6, total, "Esquema de Ligação Shelly & Iluminação",
               "Shelly 1 (iluminação) e 2x Shelly 1 (motorização) com interruptores",
               COL["dc12"])

    # Lighting wiring (left)
    s.text(70, 130, "ILUMINAÇÃO — 1x Shelly 1 por zona (10 zonas)", size=12,
           color=COL["dc12"], font=FONTB)
    s.rect(60, 150, 760, 340, fill=tint(COL["dc12"], 0.96),
           stroke=COL["dc12"], lw=1, r=8)
    bx = 110
    s.chip(bx, 220, "12V +", COL["dc12"], w=70, size=10, h=22)
    s.fuse(bx + 150, 231, "ATO", w=56)
    sh = s.device(bx + 230, 190, 200, "dc12", "Shelly 1",
                  ["Relé WiFi", "L · N · O · SW · I"], subtitle="Gen3")
    s.cable([(bx + 70, 231), (bx + 122, 231)], "4mm²", COL["dc12"], tag=False)
    s.cable([(bx + 178, 231), (sh[0], 231)], "4mm²", COL["dc12"], tag=False)
    s.text(sh[0] - 30, 215, "→ L", size=8.5, color=COL["dc12"], font=FONTB)
    # output to LED
    led = s.device(bx + 520, 190, 180, "dc12", "Fita LED / COB",
                   ["3000K / 4000K", "zona iluminação"], subtitle=None, hh=22)
    s.cable([(sh[0] + sh[2], 220), (led[0], 220)], "4mm²", COL["dc12"],
            tag=False)
    s.text((sh[0] + sh[2] + led[0]) / 2, 205, "O →", size=8.5,
           color=COL["dc12"], font=FONTB, align="c")
    # switch to SW
    s.rect(bx + 250, 360, 120, 60, fill=COL["white"], stroke=COL["dc12"],
           lw=1.2, r=6)
    s.text(bx + 310, 382, "Interruptor", size=9, color=COL["dc12"],
           font=FONTB, align="c")
    s.polyline([(sh[0] + 100, sh[1] + sh[3]), (sh[0] + 100, 360)],
               COL["dc12"], 1.4, dash=(4, 3))
    s.text(sh[0] + 108, 345, "SW", size=8.5, color=COL["dc12"], font=FONTB)

    s.note(70, 510, 760, "10 ZONAS DE ILUMINAÇÃO (sem RGB)",
           ["Teto 4000K+perfil: quarto · sala · banheiro   |   Spots 3000K: mesa sala",
            "COB 5mm 3000K: indiretas banheiro · rodapé cozinha · bancada · armários",
            "             · ext. banheiro · indiretas quarto"], COL["dc12"])

    # Motorization wiring (right)
    s.text(900, 130, "MOTORIZAÇÃO — 2x Shelly 1 por item (interlock script)",
           size=12, color=COL["bp"], font=FONTB)
    s.rect(880, 150, 740, 340, fill=tint(COL["bp"], 0.96), stroke=COL["bp"],
           lw=1, r=8)
    shA = s.device(930, 200, 190, "bp", "Shelly A (UP)",
                   ["O → central UP", "Rocker → SW"], subtitle="Gen3")
    shB = s.device(930, 330, 190, "bp", "Shelly B (DOWN)",
                   ["O → central DOWN", "Rocker → SW"], subtitle="Gen3")
    motor = s.device(1280, 250, 220, "bp", "Central do motor",
                     ["Toldo / Escada / Mesa", "UP · DOWN · COMUM"],
                     subtitle="12V DC motor")
    s.cable([(shA[0] + shA[2], 235), (motor[0], 285)], "4mm²", COL["bp"],
            tag=False)
    s.cable([(shB[0] + shB[2], 365), (motor[0], 320)], "4mm²", COL["bp"],
            tag=False)
    s.text(1200, 250, "UP", size=9, color=COL["bp"], font=FONTB)
    s.text(1200, 345, "DOWN", size=9, color=COL["bp"], font=FONTB)
    # rocker switch
    s.rect(1130, 430, 160, 48, fill=COL["white"], stroke=COL["bp"], lw=1.2,
           r=6)
    s.text(1210, 446, "Rocker (centro = OFF)", size=8.5, color=COL["bp"],
           font=FONTB, align="c")
    s.polyline([(shA[0] + 95, shA[1] + shA[3]), (shA[0] + 95, 430)],
               COL["bp"], 1.4, dash=(4, 3))
    s.polyline([(shB[0] + 95, shB[1] + shB[3]), (shB[0] + 95, 412),
                (1180, 412), (1180, 430)], COL["bp"], 1.4, dash=(4, 3))

    s.note(880, 510, 740, "3 ITENS MOTORIZADOS",
           ["Toldo · Escada · Mesa elétrica — cada um com 2x Shelly 1.",
            "Interlock por script: impede UP e DOWN simultâneos.",
            "Rocker switch de 3 posições, centro = desligado."], COL["bp"])

    # combined note bottom
    s.note(70, 720, PW - 140, "RESUMO DE LIGAÇÃO SHELLY",
           ["Iluminação (1x Shelly 1):  12V+ → [ATO] → Shelly L  |  Shelly O → fita LED  |  Interruptor → SW",
            "Motorização (2x Shelly 1):  Shelly A: O → central UP  |  Shelly B: O → central DOWN  |  Rocker → SW de cada"],
           COL["ink"])
    c.showPage()


def build(path, pages, total):
    c = canvas.Canvas(path, pagesize=(PW, PH))
    c.setTitle("Diagrama Elétrico Motorhome v10")
    for fn in pages:
        fn(c, total)
    c.save()
    print("PDF gerado:", path)


def main():
    full = [page1, page2, page3, page4, page5, page6]
    # Versão COM a lógica dos Shellys (inclui a Folha 6)
    build("Diagrama_Eletrico_Motorhome_v10_com_Shelly.pdf", full, 6)
    # Versão SEM a lógica dos Shellys (sem a Folha 6)
    build("Diagrama_Eletrico_Motorhome_v10_sem_Shelly.pdf", full[:5], 5)


if __name__ == "__main__":
    main()

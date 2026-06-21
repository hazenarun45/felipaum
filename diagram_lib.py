# -*- coding: utf-8 -*-
"""
Drawing engine for the motorhome electrical schematic.
Victron-style vector blocks, precise top-left coordinate control, no overlaps.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------------------------------------------------------------- page geometry
# A2 landscape in points (lots of room to avoid overlaps)
PW, PH = 1684.0, 1191.0
MARGIN = 46

# ----------------------------------------------------------------- color system
COL = {
    "multiplus": HexColor("#C8102E"),   # vermelho
    "solar":     HexColor("#0072CE"),   # azul
    "ac":        HexColor("#E5197F"),   # rosa
    "dc12":      HexColor("#2E8B2E"),   # verde
    "battery":   HexColor("#7B2FBF"),   # roxo
    "lynx":      HexColor("#0E9C9C"),   # teal
    "alt":       HexColor("#6E6E6E"),   # cinza
    "bp":        HexColor("#F5821F"),   # laranja Battery Protect
    "comm":      HexColor("#5A4FCF"),   # roxo-azulado comunicacao
    "victron":   HexColor("#0066B3"),
    "ink":       HexColor("#1C2B36"),
    "muted":     HexColor("#5B6B77"),
    "line":      HexColor("#B7C2CB"),
    "fuse":      HexColor("#FFD21F"),
    "fusebig":   HexColor("#F5A21F"),
    "white":     HexColor("#FFFFFF"),
    "panel":     HexColor("#F4F7F9"),
}

# cable widths (pt) proportional to gauge, scaled for the big canvas
CABLE_SCALE = 1.7
GAUGE_PT = {
    "50mm²": 4.0, "35mm²": 3.0, "25mm²": 2.5, "16mm²": 2.0,
    "10mm²": 1.5, "6mm²": 1.2, "4mm²": 1.0, "2.5mm²": 0.8,
}

FONT = "Helvetica"
FONTB = "Helvetica-Bold"


def tint(c, f):
    """lighten color c toward white by factor f (0..1)"""
    return Color(c.red + (1 - c.red) * f,
                 c.green + (1 - c.green) * f,
                 c.blue + (1 - c.blue) * f)


class Sheet:
    """Canvas wrapper using TOP-LEFT origin (y grows downward)."""

    def __init__(self, c):
        self.c = c

    def Y(self, y):
        return PH - y

    # --------------------------------------------------------------- primitives
    def rect(self, x, y, w, h, fill=None, stroke=None, lw=1, r=0, dash=None):
        c = self.c
        c.saveState()
        if dash:
            c.setDash(dash)
        if lw:
            c.setLineWidth(lw)
        if stroke is not None:
            c.setStrokeColor(stroke)
        if fill is not None:
            c.setFillColor(fill)
        yb = self.Y(y + h)
        if r:
            c.roundRect(x, yb, w, h, r, stroke=1 if stroke is not None else 0,
                        fill=1 if fill is not None else 0)
        else:
            c.rect(x, yb, w, h, stroke=1 if stroke is not None else 0,
                   fill=1 if fill is not None else 0)
        c.restoreState()

    def line(self, x1, y1, x2, y2, color, lw=1, dash=None, cap=1):
        c = self.c
        c.saveState()
        c.setLineWidth(lw)
        c.setStrokeColor(color)
        c.setLineCap(cap)
        if dash:
            c.setDash(dash)
        c.line(x1, self.Y(y1), x2, self.Y(y2))
        c.restoreState()

    def polyline(self, pts, color, lw=1, dash=None):
        c = self.c
        c.saveState()
        c.setLineWidth(lw)
        c.setStrokeColor(color)
        c.setLineCap(1)
        c.setLineJoin(1)
        if dash:
            c.setDash(dash)
        p = c.beginPath()
        p.moveTo(pts[0][0], self.Y(pts[0][1]))
        for (x, y) in pts[1:]:
            p.lineTo(x, self.Y(y))
        c.drawPath(p)
        c.restoreState()

    def text(self, x, y, s, size=10, color=None, font=FONT, align="l"):
        c = self.c
        c.saveState()
        c.setFont(font, size)
        c.setFillColor(color if color is not None else COL["ink"])
        yy = self.Y(y) - size * 0.72
        if align == "l":
            c.drawString(x, yy, s)
        elif align == "c":
            c.drawCentredString(x, yy, s)
        else:
            c.drawRightString(x, yy, s)
        c.restoreState()

    def dot(self, x, y, rad, color):
        c = self.c
        c.saveState()
        c.setFillColor(color)
        c.circle(x, self.Y(y), rad, stroke=0, fill=1)
        c.restoreState()

    # -------------------------------------------------------------- composites
    def device(self, x, y, w, key, title, lines, subtitle=None,
               icon=None, hh=30, minh=None):
        """Professional Victron-style device block. Returns (x,y,w,h) rect."""
        color = COL[key]
        line_h = 15
        body_h = 14 + line_h * len(lines) + (16 if subtitle else 6)
        h = hh + body_h
        if minh and h < minh:
            h = minh
        # shadow
        self.rect(x + 3, y + 3, w, h, fill=tint(COL["ink"], 0.86), r=8)
        # body
        self.rect(x, y, w, h, fill=COL["white"], stroke=color, lw=1.6, r=8)
        # header
        self.c.saveState()
        self.c.setFillColor(color)
        self.c.roundRect(x, self.Y(y + hh), w, hh, 8, stroke=0, fill=1)
        self.c.rect(x, self.Y(y + hh), w, hh / 2, stroke=0, fill=1)
        self.c.restoreState()
        self.text(x + 12, y + hh / 2 - 7, title, size=12.5, color=COL["white"],
                  font=FONTB)
        # victron tag
        self.text(x + w - 10, y + hh / 2 - 6, "VICTRON", size=7.5,
                  color=tint(COL["white"], 0.0), font=FONTB, align="r")
        ty = y + hh + 12
        if subtitle:
            self.text(x + 12, ty, subtitle, size=9.5, color=color, font=FONTB)
            ty += 16
        for ln in lines:
            self.text(x + 12, ty, ln, size=9.3, color=COL["muted"])
            ty += line_h
        if icon:
            icon(self, x, y, w, hh)
        return (x, y, w, h)

    def fuse(self, cx, cy, label, big=False, w=None, h=18):
        """Inline fuse drawn as a yellow/orange rounded rectangle."""
        fw = w if w else max(46, stringWidth(label, FONTB, 8.5) + 16)
        col = COL["fusebig"] if big else COL["fuse"]
        self.rect(cx - fw / 2, cy - h / 2, fw, h, fill=col,
                  stroke=COL["ink"], lw=0.8, r=4)
        self.text(cx, cy - 4.5, label, size=8.5, color=COL["ink"],
                  font=FONTB, align="c")
        return fw

    def cable(self, pts, gauge, color, tag_at=0.5, tag_dy=-11, tag=True):
        lw = GAUGE_PT.get(gauge, 1.0) * CABLE_SCALE
        # casing
        self.polyline(pts, tint(color, 0.55), lw + 2.4)
        self.polyline(pts, color, lw)
        if tag and gauge:
            # tag on first segment
            (x1, y1), (x2, y2) = pts[0], pts[1]
            mx = x1 + (x2 - x1) * tag_at
            my = y1 + (y2 - y1) * tag_at
            tw = stringWidth(gauge, FONTB, 8.5) + 10
            horiz = abs(x2 - x1) >= abs(y2 - y1)
            if horiz:
                self.rect(mx - tw / 2, my + tag_dy - 8, tw, 14,
                          fill=COL["white"], stroke=color, lw=0.7, r=3)
                self.text(mx, my + tag_dy - 4.5, gauge, size=8.5,
                          color=color, font=FONTB, align="c")
            else:
                self.rect(mx + 8, my - 7, tw, 14, fill=COL["white"],
                          stroke=color, lw=0.7, r=3)
                self.text(mx + 8 + tw / 2, my - 3.5, gauge, size=8.5,
                          color=color, font=FONTB, align="c")
        return lw

    def chip(self, x, y, label, color, w=None, size=9, h=16):
        cw = w if w else stringWidth(label, FONTB, size) + 16
        self.rect(x, y, cw, h, fill=tint(color, 0.86), stroke=color,
                  lw=0.9, r=4)
        self.text(x + cw / 2, y + h / 2 - size * 0.42, label, size=size,
                  color=color, font=FONTB, align="c")
        return cw

    def note(self, x, y, w, title, lines, color):
        h = 22 + 14 * len(lines)
        self.rect(x, y, w, h, fill=tint(color, 0.93), stroke=color,
                  lw=1, r=6, dash=(3, 2))
        self.text(x + 12, y + 8, title, size=9.5, color=color, font=FONTB)
        yy = y + 26
        for ln in lines:
            self.text(x + 12, yy, ln, size=8.6, color=COL["ink"])
            yy += 14
        return h


# ---------------------------------------------------------------- page chrome
def page_frame(s, pageno, total, title, subtitle, accent):
    # border
    s.rect(MARGIN - 10, MARGIN - 10, PW - 2 * (MARGIN - 10),
           PH - 2 * (MARGIN - 10), stroke=COL["line"], lw=1.2, r=4)
    # title bar
    s.rect(MARGIN, MARGIN, PW - 2 * MARGIN, 52, fill=tint(accent, 0.90),
           stroke=accent, lw=1.2, r=6)
    s.rect(MARGIN, MARGIN, 10, 52, fill=accent, r=0)
    s.text(MARGIN + 26, MARGIN + 14, title, size=20, color=COL["ink"],
           font=FONTB)
    s.text(MARGIN + 26, MARGIN + 37, subtitle, size=10.5, color=COL["muted"])
    s.text(PW - MARGIN - 16, MARGIN + 14, "MOTORHOME IVECO DAILY 65-180 4x4",
           size=10.5, color=accent, font=FONTB, align="r")
    s.text(PW - MARGIN - 16, MARGIN + 33,
           "Sistema Victron 24V  ·  600Ah / 15.36kWh  ·  v10",
           size=9, color=COL["muted"], align="r")
    # title block bottom-right
    bx, by, bw, bh = PW - MARGIN - 360, PH - MARGIN - 56, 360, 56
    s.rect(bx, by, bw, bh, fill=COL["panel"], stroke=COL["line"], lw=1, r=4)
    s.line(bx, by + 28, bx + bw, by + 28, COL["line"], 0.8)
    s.line(bx + 250, by, bx + 250, by + bh, COL["line"], 0.8)
    s.text(bx + 12, by + 8, "Diagrama Elétrico — Motorhome", size=9.5,
           color=COL["ink"], font=FONTB)
    s.text(bx + 12, by + 34, "Desenho: Claude Code", size=8.5, color=COL["muted"])
    s.text(bx + 262, by + 8, "Data: 2026-06-21", size=8.5, color=COL["muted"])
    s.text(bx + 262, by + 22, f"Folha {pageno}/{total}", size=11,
           color=accent, font=FONTB)
    s.text(bx + 262, by + 40, "Rev. 10", size=8.5, color=COL["muted"])


def legend(s, x, y, items):
    s.rect(x, y, 230, 26 + 18 * len(items), fill=COL["white"],
           stroke=COL["line"], lw=1, r=6)
    s.text(x + 12, y + 8, "LEGENDA — SUBSISTEMAS", size=8.5,
           color=COL["ink"], font=FONTB)
    yy = y + 28
    for (lab, key) in items:
        s.line(x + 14, yy + 6, x + 40, yy + 6, COL[key], 3.4)
        s.text(x + 48, yy + 1, lab, size=8.6, color=COL["muted"])
        yy += 18

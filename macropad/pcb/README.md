# Macropad PCB

## Files
- `macropad.kicad_sch` — KiCad schematic
- `macropad.net` — KiCad netlist (import into PCB editor)

## Opening in KiCad

1. Install **KiCad 7+** from https://www.kicad.org/
2. Install the **MX_Alps_Hybrid** footprint library:
   - KiCad > Plugin and Content Manager > search "MX Alps Hybrid" > Install
   - Or manually: https://github.com/ai03-2725/MX_Alps_Hybrid
3. Open `macropad.kicad_sch` in the Schematic Editor
4. File > Export > Netlist → save as `macropad.net`
5. Open PCB Editor → File > Import Netlist → select `macropad.net`
6. Run auto-placer, then manually arrange, then route

## Board Layout Guide

```
┌─────────────────────────────────────┐
│  [OLED 128x64]          [ENC1]      │  ← top strip
├─────────────────────────────────────┤
│  [SW1] [SW2] [SW3] [SW4]            │
│  [SW5] [SW6] [SW7] [SW8]            │  ← 4x4 switch grid
│  [SW9] [SW10][SW11][SW12]           │     19.05mm spacing
│  [SW13][SW14][SW15][SW16]           │
├─────────────────────────────────────┤
│  [Raspberry Pi Pico]  [RESET]       │  ← bottom strip
│  (castellated, USB-left)            │
└──●────────────────────────────────●─┘
   M3                              M3   ← 4x mounting holes
```

## PCB Dimensions (estimated)
- Width:  ~105mm  (4 keys × 19.05mm + margins)
- Height: ~130mm  (keys + OLED strip + Pico strip)
- Mounting holes: M3, 3mm from each corner

## Ordering from JLCPCB / PCBWay
- 2-layer PCB
- 1.6mm thickness
- HASL or ENIG finish
- Min trace width: 0.2mm
- Min clearance: 0.2mm

## Required Libraries
- `MX_Alps_Hybrid` — switch footprints
- `Rotary_Encoder` — EC11 footprint (built into KiCad)
- `Connector_PinHeader_2.54mm` — OLED header (built into KiCad)
- `Button_Switch_THT` — reset button (built into KiCad)
- `Diode_THT` — 1N4148 (built into KiCad)
- `MCU_RaspberryPi` — Pico (built into KiCad 7+)

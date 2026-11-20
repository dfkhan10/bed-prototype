# Bed prototype: pneumatic and cell-mount architecture review

6 November 2026. **Engineering proposal for the next revision, not a manufacturing release.** The existing assembled/exploded CAD remains the previous nominal-geometry baseline. This review adds the requirements that were missing from that baseline.

## Confirmed requirements

- 12 cells: A–C across, 1–4 down; one Arduino/controller assembly.
- Heat-welded TPU film bladders, not FDM-printed pressure chambers.
- Approximately 20–30 mm movement, with smooth motion preferred over speed. Exact stroke timing and working pressure have not been selected.
- Some cells must inflate while others deflate; selected other cells must be able to hold.
- Four small mounting screws per cell are acceptable. Screws must remain outside the pressure boundary.
- A thin moving printed cap above each bladder is acceptable. Raised caps should stop flush with the fixed pump cover.
- A common bottom support plane, plus a visually continuous top chassis extending through the pump-cover area. **Printed sections, bonded and finished to hide their joints**, is the confirmed production route.
- Commercial fittings are acceptable. Pump count must follow gas demand and installed performance, not cell count.

## What the photos establish, and what they do not

The supplied listing explicitly describes a **two-pump breathing simulation kit** and shows two DC pumps, one small blue solenoid assembly, tubing, and a controller/expansion board. The photo does not provide model codes, pump curves, motor voltage markings, a valve circuit symbol or dimensioned drawings. The two-pump pressure/suction interpretation is plausible, but **the exact kit plumbing is not proven by these photographs**.

The small processor board appears to be Nano-format on a larger carrier, rather than a bare Uno. Arduino lists the classic Nano nominally as 45×18 mm; its carrier, motor/valve drivers, connectors and cables require a much larger envelope. This observation does not identify the exact carrier or establish its mounting-hole pattern. [Arduino Nano documentation](https://docs.arduino.cc/hardware/nano).

The old 68 mm pump length, Ø31 head, 22×12×30 valve and 69×54 controller reservation remain estimates, **not checked dimensions of this kit**. A listing montage is not a calibrated photograph: different product cutouts can have different scales. Final rigid pockets should use the actual components/drawings; provisional mounting should use adjustable cradles and straps.

A manufacturer-sold **example**, DYX DQB370-A, is advertised with 1.0–2.3 L/min **without load**, but it is not identified as this kit. Its numbers cannot be assigned to the photographed pumps or used as installed pressure/vacuum performance. [DYX manufacturer listing](https://dyxminipump.en.made-in-china.com/product/zCWnLIsVChkR/China-DC6V-Mini-Air-Pump-370-Motor-Pump-for-Fish-Tank-Aquarium.html).

The engineer's referenced prompt/skill was not included in the three attachments and has not been evaluated.

## Circuit recommendation

Use two independently managed pneumatic buses: pressure and suction. The pressure pump takes ambient air and feeds the pressure bus. The evacuation pump draws from the suction bus and discharges to ambient. Each cell connects to both buses through independently shuttable paths, while retaining one physical hose to the cell.

```text
Filtered ambient → pressure pump(s) → pressure bus → fill valve i ─┐
                                                                  ├→ tee → one hose → cell i
Muffled ambient ← evacuation pump(s) ← suction bus ← drain valve i ┘
```

| Cell command | Fill valve | Drain valve |
|---|---|---|
| Rise | Open/modulated as the hardware permits | Closed |
| Hold | Closed | Closed |
| Lower | Closed | Open/modulated as the hardware permits |

Both paths must never be open for the same cell: that would connect the pressure and suction buses together. Use a close-before-open interlock. Other cells may independently take different states.

The straightforward component implementation is **24 normally closed two-way valves**, two per cell. An alternative is **12 suitable three-position, closed-centre valve assemblies**. A plain two-position 3/2 valve chooses between two paths but does not supply a third independent closed/hold state by itself. The little blue kit valve has not yet been classified.

A published soft-actuator implementation uses separate inflation and extraction pumps and separate branch valves for each actuator; this supports the circuit concept, not the choice of hardware or dimensions here. [Yao et al., China Mechanical Engineering, 2020](https://www.cmemo.org.cn/fileup/HTML/20201609.shtml).

The valves must be compatible with the low differential pressures and the intended vacuum. Many pilot-operated compressed-air valves require a minimum supply pressure; verify the actual valve rather than assuming any metal solenoid will work. Ordinary valves also leak to some degree, so closed/hold is not indefinite position locking. [SMC selection guidance](https://content2.smcetech.com/pdf/BPvol6_selection.pdf), [SMC application precautions](https://ca01.smcworld.com/catalog/Clean-en/vq100_en/spdfdata/vq100_en_11sp.htm).

One Arduino can control the system through appropriate I/O expansion and power drivers. It must not directly power pumps or coils from GPIO. Allow space for driver channels, flyback suppression appropriate to the chosen valves, connectors, power distribution and pressure sensing, in addition to the Arduino itself. Two-valve-per-cell control already means 24 valve outputs before pumps and auxiliary functions.

## Pump mechanism

A motor rotates an eccentric, which reciprocates a diaphragm. Inlet and outlet check valves cause suction on one stroke and discharge on the other. The same pump therefore has a suction side and a pressure side. Reversing motor polarity does not establish reversible pneumatic flow through those check valves. The ports must be identified on the actual unit. [Boxer pump mechanism](https://www.boxerpumps.com/de/knowledge/diaphragm-pumps-for-gas/).

The recommended two-bus arrangement uses different pumps for the two roles so demand on one side can be managed independently of the other. It is not a claim that two pumps are the theoretical minimum: passive exhaust or a single transfer pump with extra switching/venting can support other architectures. Those alternatives change unloaded retraction and pressure/flow coupling and are not the baseline for this review.

## Preliminary sizing

The calculation reads the present nominal **56 mm active width** from `bed_params.json`; this is a sensitivity study, not confirmation of the final bladder dimensions.

- Height: 20–30 mm, user target.
- Volume estimate: `width² × height × shape factor`; shape factor 0.5–1.0 is an unmeasured scenario range.
- Central scenario: 25 mm rise and factor 0.7 → **54.88 mL/cell**.
- Low/upper scenarios: **31.36–94.08 mL/cell**. The upper value is a rectangular-envelope estimate, not a measured pillow volume.
- Pressure scenario: 10 kPa gauge, **not a selected operating pressure or film rating**.
- Hose scenario: 0.6 m of 4 mm ID hose per cell → 7.54 mL line volume. A line already full of atmospheric air needs only the extra compression mass when filling; adding its entire volume as fresh fill demand would overcount.
- Reserve factor: 1.5, provisional. It is not based on measured leakage.

At the same reference temperature, ambient-equivalent air demand per cell is:

`[(Pfinal_abs × Vfinal − Pinitial_abs × Vinitial) + (Pfinal_abs − Pinitial_abs) × Vline] / Pambient`

`required flow = simultaneous cells × air demand / stroke time × reserve`

| Cells inflating together | Central flow, 10 s stroke | Central flow, 20 s stroke | 20 s low–upper scenario |
|---:|---:|---:|---:|
| 3 | 1.65 L/min | 0.82 L/min | 0.48–1.41 L/min |
| 6 | 3.30 L/min | 1.65 L/min | 0.95–2.81 L/min |
| 12 | 6.59 L/min | 3.30 L/min | 1.90–5.62 L/min |

These values are **required ambient-equivalent installed flow**, not the kit's advertised flow. Pressure-flow curves are required because free flow is not the flow delivered against the working pressure and valve restrictions. [Parker sizing catalog](https://www.parker.com/content/dam/Parker-com/Literature/Precision-Fluidics/Miniature-Diaphragm-Pumps/PPF_Pumps_Catalog.pdf).

For each bank separately, the first estimate is `ceil(required flow / effective flow of one pump at the operating point)`. Verify parallel-pump behaviour, check valves, drive voltage, duty cycle, manifold losses and the actual performance curve. Vacuum ratings may report inlet volume flow; convert to the same air-mass reference before comparing them with this demand.

**Example, not a selected count:** six rising and six lowering cells over 20 seconds, with the central volume assumption, require about 1.65 L/min per bank using an equal air-removal budget as a placeholder. If each pump genuinely provides 2 L/min at its bank's operating conditions, one pressure plus one evacuation pump could suffice. At 1 L/min effective flow, use two per bank, four total. At the upper-volume scenario, a 2 L/min pump would need help or a slower stroke. Actual evacuation must be verified from its start/end pressure and volume, suction curve and desired final collapse.

**Proposal:** begin with a smooth 20 s stroke for six-cell groups as an adjustable development target, and reserve modular expansion. All 12 inflating together approximately doubles that bank's demand. Do not freeze either a two-pump or eight-pump tray yet.

More parallel pumps mainly improve filling speed. Static support follows pressure, effective area, bladder/weld strength and the structural load path. At 10 kPa over 56×56 mm, `pA` is 31.4 N per cell; that is a force scale, **not a load rating**. Increasing pressure is not an accepted shortcut to more support.

Reproduction: `python3 design/analysis/2026-11-06_pump_sizing.py`. Full assumptions and cases: `work/2026-11-06_pump_sizing_scenarios.json`.

## Cell attachment and support

Use a replaceable cell cassette with these separate functions:

1. A rigid lower cup supports the bladder's entire lower surface and the port area. The cup transfers load to ribs/posts and the common bottom base, rather than hanging from the service-module joint.
2. The airtight TPU envelope is heat-welded before installation. A gusset, preformed/oversized film or another deliberate bladder construction must provide the 20–30 mm travel; a flat membrane of the same width cannot be assumed to rise that far without stretch or footprint contraction.
3. A non-inflating flange extends **outside the closed weld line**. A removable rigid ring clamps this flange. Four M2.5 screws pass through that outer dry flange into rigid bosses; screw holes do not intersect the chamber or weld land. Rounded edges and compression stops avoid cutting or over-compressing the film.
4. A moving printed cap spreads the contact load and provides a flat visible square. Guidance limits tilt; upper and lower mechanical stops define travel. The raised stop sets the cap's top flush with the fixed top fascia. A soft covering can bridge contact gaps while allowing independent motion.

```text
fixed top fascia ══════ [ moving cap at upper stop ] ═════ pump cover
                                  ↓ 20–30 mm
                         heat-welded TPU bladder
                     clamp ring / outer dry flange
                     supported lower cup + air port
                          ribs / support posts
common bottom base ══════════════════════════════════════════════════
```

The present 60 mm pitch is not a validated package for a 56 mm active region, a weld land, four separate corner screws, cap guides and a removable clamp. The next model must dimension that stack first, then derive pitch. Preserving the 56 mm active region may grow pitch into roughly the 76–90 mm range, depending on guide design; this is a packaging study range, not a selected dimension. Do not silently shrink the bladder simply to preserve the old 60 mm number.

The cap can be flush with a fixed cover at a chosen reference position, here the raised stop. Lowered cells will sit below it. A fixed cover cannot be flush with a moving cell at every height.

## TPU-to-hose interface

A metal fitting is acceptable as a **commercial hose connection**; it is a different component from the solenoid that selects cell flow.

Prefer a TPU-compatible weldable flange/port with the metal barb or adapter supported by the rigid cup. An alternative mechanical port uses a reinforced film patch, appropriate gasket surfaces and load-spreading backing, with its tightening/strain loads reacted by the cassette. A metal threaded fitting screwed directly into unsupported thin film is not the attachment design.

Commercial inflation hardware demonstrates both weld-compatible urethane flanges and clamped flange systems. Its material, bore, opening pressure and seal arrangement must match this application; those example products are not a parts recommendation. [Halkey-Roberts urethane weld flange](https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/HRC/Molded-Manifold-Tech-Sheet.pdf), [clamped flange example](https://www.halkeyroberts.com/Products/molded-flange).

Use an open flow path for controlled inflation **and** evacuation. A tyre-style self-closing valve or check valve may obstruct the evacuation path unless deliberately actuated or bypassed. Confirm hose bore and material: a 4 mm ID barb specification is not the same interface as a 4 mm OD push-in fitting.

## Tube and housing layout

- Keep the valves and commercial pressure/suction distribution hardware serviceable in the foot bay. Two valves tee to one dedicated hose per cell: there are still **12 long cell hoses**, not 24 long hoses.
- Route three labelled column bundles A/B/C under the supported cups. Within each bundle, keep row numbers 1–4 in a fixed order. Provide removable retainers, strain relief and radiused through-seam openings, without closed printed pressure passages.
- Arrange the valve pairs by cell ID near the bundle entries. Lay out actual ports/connectors and their keep-outs before deciding the bank pitch. Nominal body boxes alone do not reserve fitting bends or wire exits.
- Determine each hose centre-line from its port, bend clearance, bundle lane and valve tee. Hose lengths need not be equal by default; measure/calibrate their dynamic effects. Add only the service loop needed for removal and strain relief.
- Mount pumps on removable, vibration-isolated cradles. Reserve nozzle bends, wire exits, motor ventilation and access to straps/clamps. Provide a dry electronics lane for the single Arduino, driver boards and connectors.
- Support both the cell region and pump region on a **common bottom base**. Provide posts under the cell grid and clear corridors for the hose bundles. The four cell/service joint screws should not be the load path for a long cantilevered cell deck.
- Keep underside access panels. The visible fixed top should have one outer contour and no separately rounded interior tile edges. Upper guide stops, cap clearances and the uninterrupted pump fascia are designed together.

The previous assembly is approximately 388 mm long even before a flange/guide-driven pitch increase. It cannot become a single-piece print on a 252 mm usable bed simply by changing software. Options are printed structural sections with a bonded/finished top joint, a continuous manufactured face sheet over printed supports, or a sufficiently large printer. The confirmed route is **printed sections, bonded and finished to hide the joints**, with service access from below. Model the top as an integrated whole before splitting it for printing; internal split faces stay square and coplanar, without the separately rounded tile edges visible in the current screenshot. This achieves a finished continuous assembly rather than a single printer-sized extrusion.

## Method and next decision

The quality work is: requirements and valve state table; gas-demand sizing against measured pressure/vacuum curves; component/fitting keep-outs; interference and tool-access checks; one-cell seal/guide/port coupon; slicing; then full assembly. A direct-STL workflow can implement good geometry, but changing output format does not establish those checks. Keep the JSON parameter model and editable solids while evaluating the missing engineer prompt; a second full modeling stack is not needed to prove this concept.

Recommended next revision: dual pneumatic buses, per-cell inflate/hold/deflate control, supported welded-film cassettes with four dry-flange screws, moving caps flush at the raised stop, one common base and a continuous visible top. First resolve the single-cell flange/guide envelope and verify one real pump/valve circuit; then size the complete housing and freeze pump count. Exact kit identification, measured installed flow, the flange/guide envelope and the resulting footprint remain open. The moving caps and bonded/finished top sections are approved directions.

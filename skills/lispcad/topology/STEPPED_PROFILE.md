# LISPCAD Topology — Stepped / Notched Profile

Source: approved V4.3 production baseline.

The general contour-topology rule remains in `../core/DATUM_DIMENSION.md`.

### 4.9 Stepped / Notched Flanges *(restored from V1)*
For flanges stepping inward before joining the body:
- $Y_{\text{flange\_flat}} = L_{\text{flange\_nominal}} - N_y$
- $Y_{\text{bend}} = Y_{\text{flange\_flat}}$
- $Y_{\text{notch}} = Y_{\text{flange\_flat}} + L_{\text{notch\_gap}}$
- $Y_{\text{body\_flat}} = L_{\text{body\_nominal}}$ (untouched)

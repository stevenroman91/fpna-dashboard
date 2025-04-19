# visuals.py

import plotly.io as pio
import plotly.graph_objects as go

# 1) Définition du layout “green‑blue blend”
finance_layout = go.Layout(
    font=dict(
        family="Helvetica, Arial, sans-serif",
        size=12,
        color="#2c3e50"
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    # Palette verte & bleue
    colorway=[
        "#0B3D91",  # bleu nuit
        "#238B45",  # vert forêt
        "#74C476",  # vert clair
        "#6BAED6",  # bleu pastel
        "#2171B5",  # bleu ciel soutenu
    ],
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor="#E1E1E1",
        ticks="outside",
        tickcolor="#E1E1E1",
        tickfont=dict(size=11)
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#F2F2F2",
        zeroline=False,
        showline=True,
        linecolor="#E1E1E1",
        ticks="outside",
        tickcolor="#E1E1E1",
        tickfont=dict(size=11)
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11)
    ),
    margin=dict(l=60, r=60, t=80, b=60)
)

# 2) Enregistrement du template et ajout des defaults Waterfall
finance_template = go.layout.Template(
    layout=finance_layout,
    data={
        "waterfall": [
            go.Waterfall(
                # Couleur des impacts positifs
                increasing=dict(marker=dict(color="#2171B5")),
                # Couleur des impacts négatifs
                decreasing=dict(marker=dict(color="#238B45")),
                connector=dict(line=dict(color="#E1E1E1"))
            )
        ]
    }
)

pio.templates["finance_gb_blend"] = finance_template
pio.templates.default = "finance_gb_blend"

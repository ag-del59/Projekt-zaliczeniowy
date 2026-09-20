import tkinter as tk
from tkinter import ttk
from database import (
    get_variant_labels,
    get_comparison_by_rs,
    get_all_comparisons
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()

root.title("Analiza wariantów BRCA1 / BRCA2")
root.geometry("1200x700")
root.minsize(1100, 650)

title_label = ttk.Label(
    root,
    text="Analiza wariantów BRCA1 / BRCA2",
    font=("Arial", 18, "bold")
)

title_label.pack(pady=20)

# ------------------------------------------------
# PRZEŁĄCZANIE WIDOKÓW
# ------------------------------------------------

view_buttons_frame = ttk.Frame(root)

view_buttons_frame.pack(
    pady=(0, 10)
)

single_view = ttk.Frame(root)

single_view.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)

all_view = ttk.Frame(root)

def show_single_view():

    all_view.pack_forget()

    single_view.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )


def show_all_view():

    single_view.pack_forget()

    all_view.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

single_view_button = ttk.Button(
    view_buttons_frame,
    text="Analiza pojedynczego wariantu",
    command=show_single_view
)

single_view_button.pack(
    side="left",
    padx=5
)


all_view_button = ttk.Button(
    view_buttons_frame,
    text="Porównanie wszystkich wariantów",
    command=show_all_view
)

all_view_button.pack(
    side="left",
    padx=5
)
all_view_title = ttk.Label(
    all_view,
    text="Porównanie wszystkich wariantów",
    font=("Arial", 16, "bold")
)

all_view_title.pack(
    pady=20
)
# ------------------------------------------------
# FILTRY - WSZYSTKIE WARIANTY
# ------------------------------------------------

all_controls_frame = ttk.Frame(all_view)

all_controls_frame.pack(
    pady=10
)

ttk.Label(
    all_controls_frame,
    text="Gen:"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


gene_all_combobox = ttk.Combobox(
    all_controls_frame,
    values=[
        "Wszystkie",
        "BRCA1",
        "BRCA2"
    ],
    state="readonly",
    width=25
)

gene_all_combobox.set("Wszystkie")

gene_all_combobox.grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)

ttk.Label(
    all_controls_frame,
    text="Populacja:"
).grid(
    row=1,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


population_all_combobox = ttk.Combobox(
    all_controls_frame,
    values=[
        "Global",
        "European (non-Finnish)",
        "Finnish"
    ],
    state="readonly",
    width=25
)

population_all_combobox.set(
    "European (non-Finnish)"
)

population_all_combobox.grid(
    row=1,
    column=1,
    padx=5,
    pady=5
)

ttk.Label(
    all_controls_frame,
    text="Skala:"
).grid(
    row=2,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


scale_all_combobox = ttk.Combobox(
    all_controls_frame,
    values=[
        "Liniowa",
        "Logarytmiczna"
    ],
    state="readonly",
    width=25
)

scale_all_combobox.set(
    "Logarytmiczna"
)

scale_all_combobox.grid(
    row=2,
    column=1,
    padx=5,
    pady=5
)


# ------------------------------------------------
# WYKRES WSZYSTKICH WARIANTÓW
# ------------------------------------------------

all_chart_frame = ttk.LabelFrame(
    all_view,
    text="Porównanie AF"
)

all_chart_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)

all_chart_info = ttk.Label(
    all_chart_frame,
    text="Wybierz parametry i kliknij „Pokaż porównanie”."
)

all_chart_info.pack(
    pady=50
)

# Lewa strona
left_frame = ttk.LabelFrame(
    single_view,
    text="Wybór danych"
)

left_frame.grid(
    row=0,
    column=0,
    sticky="ns",
    padx=(0, 15)
)

# Prawa strona
right_frame = ttk.Frame(
    single_view
)

right_frame.grid(
    row=0,
    column=1,
    sticky="nsew"
)

single_view.columnconfigure(
    1,
    weight=1
)

variant_labels = get_variant_labels()
variant_combobox = ttk.Combobox(
    left_frame,
    values=variant_labels,
    width=65,
    state="readonly"
)

variant_combobox.pack(
    padx=15,
    pady=10
)

population_combobox = ttk.Combobox(
    left_frame,
    values=[
        "Global",
        "European (non-Finnish)",
        "Finnish"
    ],
    state="readonly",
    width=30
)

population_combobox.set(
    "European (non-Finnish)"
)

population_combobox.pack(
    padx=15,
    pady=10
)

controls_frame = ttk.Frame(
    left_frame
)

controls_frame.pack(
    padx=15,
    pady=15
)
chart_frame = ttk.LabelFrame(
    left_frame,
    text="Porównanie AF"
)

chart_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(5, 15)
)

results_frame = ttk.Frame(
    right_frame
)

results_frame.pack(
    fill="both",
    expand=True
)

variant_frame = ttk.LabelFrame(
    results_frame,
    text="Wariant"
)

variant_frame.grid(
    row=0,
    column=0,
    columnspan=2,
    sticky="ew",
    padx=10,
    pady=10
)


ttk.Label(
    variant_frame,
    text="Gen:"
).grid(row=0, column=0, sticky="w", padx=10, pady=5)

gene_value = ttk.Label(
    variant_frame,
    text="-"
)

gene_value.grid(row=0, column=1, sticky="w")


ttk.Label(
    variant_frame,
    text="rsID:"
).grid(row=1, column=0, sticky="w", padx=10, pady=5)

rs_value = ttk.Label(
    variant_frame,
    text="-"
)

rs_value.grid(row=1, column=1, sticky="w")


ttk.Label(
    variant_frame,
    text="HGVS:"
).grid(row=2, column=0, sticky="w", padx=10, pady=5)

hgvs_value = ttk.Label(
    variant_frame,
    text="-"
)

hgvs_value.grid(row=2, column=1, sticky="w")

lab_frame = ttk.LabelFrame(
    results_frame,
    text="Laboratorium"
)

lab_frame.grid(
    row=1,
    column=0,
    sticky="nsew",
    padx=10,
    pady=10
)


lab_labels = [
    "Liczba przebadanych:",
    "Heterozygoty:",
    "Homozygoty:",
    "AC:",
    "AN:",
    "AF:"
]

for i, text in enumerate(lab_labels):

    ttk.Label(
        lab_frame,
        text=text
    ).grid(
        row=i,
        column=0,
        sticky="w",
        padx=10,
        pady=4
    )


tested_value = ttk.Label(lab_frame, text="-")
tested_value.grid(row=0, column=1, padx=10)

hetero_value = ttk.Label(lab_frame, text="-")
hetero_value.grid(row=1, column=1, padx=10)

homo_value = ttk.Label(lab_frame, text="-")
homo_value.grid(row=2, column=1, padx=10)

lab_ac_value = ttk.Label(lab_frame, text="-")
lab_ac_value.grid(row=3, column=1, padx=10)

lab_an_value = ttk.Label(lab_frame, text="-")
lab_an_value.grid(row=4, column=1, padx=10)

lab_af_value = ttk.Label(lab_frame, text="-")
lab_af_value.grid(row=5, column=1, padx=10)

# -------- gnomAD --------

ref_frame = ttk.LabelFrame(
    results_frame,
    text="gnomAD"
)

ref_frame.grid(
    row=1,
    column=1,
    sticky="nsew",
    padx=10,
    pady=10
)


ref_labels = [
    "Populacja:",
    "AC:",
    "AN:",
    "AF:"
]

for i, text in enumerate(ref_labels):

    ttk.Label(
        ref_frame,
        text=text
    ).grid(
        row=i,
        column=0,
        sticky="w",
        padx=10,
        pady=4
    )


population_value = ttk.Label(ref_frame, text="-")
population_value.grid(row=0, column=1, padx=10)

ref_ac_value = ttk.Label(ref_frame, text="-")
ref_ac_value.grid(row=1, column=1, padx=10)

ref_an_value = ttk.Label(ref_frame, text="-")
ref_an_value.grid(row=2, column=1, padx=10)

ref_af_value = ttk.Label(ref_frame, text="-")
ref_af_value.grid(row=3, column=1, padx=10)


# -------- PORÓWNANIE --------

comparison_frame = ttk.LabelFrame(
    results_frame,
    text="Porównanie"
)

comparison_frame.grid(
    row=2,
    column=0,
    columnspan=2,
    sticky="ew",
    padx=10,
    pady=10
)


ttk.Label(
    comparison_frame,
    text="Różnica częstości:"
).grid(row=0, column=0, padx=10, pady=10)


ratio_value = ttk.Label(
    comparison_frame,
    text="-",
    font=("Arial", 11, "bold")
)

ratio_value.grid(row=0, column=1, padx=10, pady=10)


status_value = ttk.Label(
    results_frame,
    text=""
)

status_value.grid(
    row=3,
    column=0,
    columnspan=2,
    pady=5
)
ttk.Label(
    comparison_frame,
    text="Odds ratio:"
).grid(row=1, column=0, padx=10, pady=5, sticky="w")

odds_ratio_value = ttk.Label(
    comparison_frame,
    text="-"
)
odds_ratio_value.grid(row=1, column=1, padx=10, pady=5)


ttk.Label(
    comparison_frame,
    text="p-value (test Fishera):"
).grid(row=2, column=0, padx=10, pady=5, sticky="w")

p_value_value = ttk.Label(
    comparison_frame,
    text="-"
)
p_value_value.grid(row=2, column=1, padx=10, pady=5)


ttk.Label(
    comparison_frame,
    text="Istotność statystyczna:"
).grid(row=3, column=0, padx=10, pady=5, sticky="w")

significance_value = ttk.Label(
    comparison_frame,
    text="-",
    font=("Arial", 10, "bold")
)
significance_value.grid(row=3, column=1, padx=10, pady=5)


def show_af_chart(lab_af, ref_af, population, rs_id):
    # Usuwamy poprzedni wykres
    for widget in chart_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(
        figsize=(4.5, 3.5)
    )

    names = [
        "Laboratorium",
        f"gnomAD\n{population}"
    ]

    values = [
        lab_af,
        ref_af
    ]

    bars = ax.bar(
        names,
        values
    )
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:.4f}%",
            ha="center",
            va="bottom"
        )

    # Pobranie wybranej skali
    scale = scale_combobox.get()

    if scale == "Logarytmiczna":
        ax.set_yscale("log")

    ax.set_ylabel("Częstość allelu [%]")
    ax.set_title(
        f"{rs_id}\nAF: laboratorium vs gnomAD"
    )

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(
        fig,
        master=chart_frame
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )

    plt.close(fig)

def show_all_variants_chart():

    population = population_all_combobox.get()
    gene = gene_all_combobox.get()

    # Pobranie danych z bazy
    df = get_all_comparisons(
        population,
        gene
    )

    # Usunięcie poprzedniego wykresu / komunikatu
    for widget in all_chart_frame.winfo_children():
        widget.destroy()

    if df.empty:

        message = ttk.Label(
            all_chart_frame,
            text="Brak danych dla wybranych parametrów."
        )

        message.pack(pady=50)

        return

    # Etykiety wariantów
    labels = df["rs_id"]

    # Wartości AF
    lab_values = df["lab_af_percent"]
    ref_values = df["ref_af_percent"]

    # Pozycje wariantów na osi Y
    y = range(len(df))

    fig, ax = plt.subplots(
        figsize=(9, 5)
    )

    # Słupki LAB
    ax.barh(
        [i - 0.2 for i in y],
        lab_values,
        height=0.4,
        label="Laboratorium"
    )

    # Słupki gnomAD
    ax.barh(
        [i + 0.2 for i in y],
        ref_values,
        height=0.4,
        label="gnomAD"
    )

    ax.set_yticks(
        list(y)
    )

    ax.set_yticklabels(
        labels
    )

    ax.set_xlabel(
        "Częstość allelu [%]"
    )

    ax.set_ylabel(
        "Wariant"
    )

    ax.set_title(
        f"LAB vs gnomAD — {population}"
    )

    ax.legend()

    # Wybrana skala
    scale = scale_all_combobox.get()

    if scale == "Logarytmiczna":
        ax.set_xscale("log")

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(
        fig,
        master=all_chart_frame
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )

    plt.close(fig)

show_all_button = ttk.Button(
    all_controls_frame,
    text="Pokaż porównanie",
    command=show_all_variants_chart
)

show_all_button.grid(
    row=3,
    column=0,
    columnspan=2,
    pady=15
)

def show_statistics():

    selected = variant_combobox.get()
    population = population_combobox.get()

    if not selected or not population:
        return

    # np. BRCA1 — rs80357906 — NM_007294.4:c.5266dupC
    parts = selected.split(" — ")
    rs_id = parts[1]

    df = get_comparison_by_rs(
        rs_id,
        population
    )

    if df is None:
        status_value.config(
            text="Brak danych referencyjnych dla wybranej populacji."
        )
        return

    row = df.iloc[0]

    # -------------------------
    # INFORMACJE O WARIANCIE
    # -------------------------

    gene_value.config(
        text=row["gene"]
    )

    rs_value.config(
        text=row["rs_id"]
    )

    hgvs_value.config(
        text=row["hgvs_c"]
    )

    # -------------------------
    # LABORATORIUM
    # -------------------------

    tested_value.config(
        text=f"{int(row['tested_n'])}"
    )

    hetero_value.config(
        text=f"{int(row['heterozygous_n'])}"
    )

    homo_value.config(
        text=f"{int(row['homozygous_n'])}"
    )

    lab_ac_value.config(
        text=f"{int(row['lab_ac'])}"
    )

    lab_an_value.config(
        text=f"{int(row['lab_an'])}"
    )

    lab_af_value.config(
        text=f"{row['lab_af_percent']:.4f}%"
    )

    # -------------------------
    # gnomAD
    # -------------------------

    population_value.config(
        text=row["population"]
    )

    ref_ac_value.config(
        text=f"{int(row['ref_ac'])}"
    )

    ref_an_value.config(
        text=f"{int(row['ref_an'])}"
    )

    ref_af_value.config(
        text=f"{row['ref_af_percent']:.4f}%"
    )

    # -------------------------
    # PORÓWNANIE
    # -------------------------

    ratio = row["frequency_ratio"]

    if ratio is None:
        ratio_value.config(
            text="Nie można obliczyć"
        )

    elif ratio >= 1:
        ratio_value.config(
            text=f"{ratio:.2f} × częściej w laboratorium"
        )

    elif ratio > 0:
        ratio_value.config(
            text=f"{1 / ratio:.2f} × rzadziej w laboratorium"
        )

    else:
        ratio_value.config(
            text="Wariant niewykryty w laboratorium"
        )

    status_value.config(text="")




    # -------------------------
    # TEST STATYSTYCZNY
    # -------------------------

    odds_ratio = row["odds_ratio"]
    p_value = row["p_value"]
    significant = row["significant"]

    odds_ratio_value.config(
        text=f"{odds_ratio:.2f}"
    )

    # zapis naukowy, np. 1.14e-84
    p_value_value.config(
        text=f"{p_value:.3e}"
    )

    if significant:
        significance_value.config(
            text="Tak (p < 0,05)"
        )
    else:
        significance_value.config(
            text="Nie (p ≥ 0,05)"
        )
    show_af_chart(
        row["lab_af_percent"],
        row["ref_af_percent"],
        row["population"],
        row["rs_id"]
    )

show_button = ttk.Button(
    controls_frame,
    text="Pokaż statystyki",
    command=show_statistics
)

show_button.pack()

ttk.Label(
    controls_frame,
    text="Skala wykresu:"
).pack(pady=(10, 2))

scale_combobox = ttk.Combobox(
    controls_frame,
    values=[
        "Liniowa",
        "Logarytmiczna"
    ],
    state="readonly",
    width=18
)

scale_combobox.set("Liniowa")
scale_combobox.pack()

def change_scale(event=None):
    show_statistics()


scale_combobox.bind(
    "<<ComboboxSelected>>",
    change_scale
)

root.mainloop()
import tkinter as tk
from tkinter import ttk

from database import get_variant_labels, get_comparison_by_rs

root = tk.Tk()

root.title("Analiza wariantów BRCA1 / BRCA2")
root.geometry("850x650")

title_label = ttk.Label(
    root,
    text="Analiza wariantów BRCA1 / BRCA2",
    font=("Arial", 18, "bold")
)

title_label.pack(pady=20)

variant_labels = get_variant_labels()
variant_combobox = ttk.Combobox(
    root,
    values=variant_labels,
    width=65,
    state="readonly"
)

variant_combobox.pack(pady=10)

population_combobox = ttk.Combobox(
    root,
    values=[
        "Global",
        "European (non-Finnish)",
        "Finnish"
    ],
    state="readonly",
    width=30
)

population_combobox.set("European (non-Finnish)")
population_combobox.pack(pady=5)

controls_frame = ttk.Frame(root)
controls_frame.pack(pady=10)

results_frame = ttk.Frame(root)
results_frame.pack(pady=15)

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

    else:
        ratio_value.config(
            text=f"{1 / ratio:.2f} × rzadziej w laboratorium"
        )

    status_value.config(text="")

show_button = ttk.Button(
    controls_frame,
    text="Pokaż statystyki",
    command=show_statistics
)

show_button.pack()


root.mainloop()
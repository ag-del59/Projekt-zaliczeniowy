import tkinter as tk
from tkinter import ttk

from database import get_variant_labels, get_comparison_by_rs

root = tk.Tk()

root.title("Analiza wariantów BRCA1 / BRCA2")
root.geometry("700x500")

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

def show_statistics():

    selected = variant_combobox.get()

    if not selected:
        return


    parts = selected.split(" — ")

    rs_id = parts[1]

    population = population_combobox.get()

    df = get_comparison_by_rs(
        rs_id,
        population
    )

    if df is None:
        return

    row = df.iloc[0]

    gene_value.config(
        text=row["gene"]
    )

    rs_value.config(
        text=row["rs_id"]
    )

    tested_value.config(
        text=row["tested_n"]
    )

    hetero_value.config(
        text=row["heterozygous_n"]
    )

    homo_value.config(
        text=row["homozygous_n"]
    )

    af_value.config(
        text=f"{row['lab_af_percent']:.3f}%"
    )

show_button = ttk.Button(
    root,
    text="Pokaż statystyki",
    command=show_statistics
)

show_button.pack(pady=10)


results_frame = ttk.Frame(root)
results_frame.pack(pady=20)

ttk.Label(
    results_frame,
    text="Gen:"
).grid(row=0, column=0, sticky="w", padx=10, pady=5)

gene_value = ttk.Label(
    results_frame,
    text="-"
)

gene_value.grid(
    row=0,
    column=1,
    sticky="w"
)

ttk.Label(
    results_frame,
    text="rsID:"
).grid(row=1, column=0, sticky="w", padx=10, pady=5)

rs_value = ttk.Label(
    results_frame,
    text="-"
)

rs_value.grid(
    row=1,
    column=1,
    sticky="w"
)

ttk.Label(
    results_frame,
    text="Liczba przebadanych:"
).grid(row=2, column=0, sticky="w", padx=10, pady=5)

tested_value = ttk.Label(
    results_frame,
    text="-"
)

tested_value.grid(
    row=2,
    column=1,
    sticky="w"
)

ttk.Label(
    results_frame,
    text="Heterozygoty:"
).grid(row=3, column=0, sticky="w", padx=10, pady=5)

hetero_value = ttk.Label(
    results_frame,
    text="-"
)

hetero_value.grid(
    row=3,
    column=1,
    sticky="w"
)

ttk.Label(
    results_frame,
    text="Homozygoty:"
).grid(row=4, column=0, sticky="w", padx=10, pady=5)

homo_value = ttk.Label(
    results_frame,
    text="-"
)

homo_value.grid(
    row=4,
    column=1,
    sticky="w"
)

ttk.Label(
    results_frame,
    text="Częstość allelu:"
).grid(row=5, column=0, sticky="w", padx=10, pady=5)

af_value = ttk.Label(
    results_frame,
    text="-"
)

af_value.grid(
    row=5,
    column=1,
    sticky="w"
)

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

root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
from database import (
    get_variant_labels,
    get_comparison_by_rs,
    get_all_comparisons,
    get_cancer_group_af
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()

root.title("Analiza wariantów BRCA1 / BRCA2")
root.geometry("1100x700")
root.minsize(650, 450)

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

# Przewijane obszary obu widoków. Canvas przewija całą zawartość,
# natomiast wewnętrzne ramki zachowują dotychczasowy układ pack/grid.
def create_scrollable_view(parent):
    outer = ttk.Frame(parent)
    canvas = tk.Canvas(outer, highlightthickness=0, borderwidth=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content = ttk.Frame(canvas)
    window_id = canvas.create_window((0, 0), window=content, anchor="nw")

    def update_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def resize_content(event):
        # Nie zwężamy zawartości poniżej minimalnej szerokości układu.
        canvas.itemconfigure(window_id, width=max(event.width, 1000))
        update_region()

    content.bind("<Configure>", update_region)
    canvas.bind("<Configure>", resize_content)
    return outer, content, canvas


single_outer, single_view, single_canvas = create_scrollable_view(root)
all_outer, all_view, all_canvas = create_scrollable_view(root)
single_outer.pack(fill="both", expand=True, padx=10, pady=5)


def show_single_view():
    all_outer.pack_forget()
    single_outer.pack(fill="both", expand=True, padx=10, pady=5)


def show_all_view():
    single_outer.pack_forget()
    all_outer.pack(fill="both", expand=True, padx=10, pady=5)


def scroll_active_view(event):
    # Obsługa Windows/macOS oraz Linux; tylko widoczny widok.
    canvas = single_canvas if single_outer.winfo_ismapped() else all_canvas
    if getattr(event, "num", None) == 4:
        amount = -1
    elif getattr(event, "num", None) == 5:
        amount = 1
    else:
        amount = -int(event.delta / 120) if event.delta else 0
        if amount == 0 and event.delta:
            amount = -1 if event.delta > 0 else 1
    canvas.yview_scroll(amount, "units")


root.bind_all("<MouseWheel>", scroll_active_view)
root.bind_all("<Button-4>", scroll_active_view)
root.bind_all("<Button-5>", scroll_active_view)

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


# Filtry pacjentów — widok wszystkich wariantów
ttk.Label(all_controls_frame, text="Wiek od:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
age_min_all_entry = ttk.Entry(all_controls_frame, width=12)
age_min_all_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

ttk.Label(all_controls_frame, text="Wiek do:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
age_max_all_entry = ttk.Entry(all_controls_frame, width=12)
age_max_all_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

ttk.Label(all_controls_frame, text="Nowotwór:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
cancer_all_combobox = ttk.Combobox(
    all_controls_frame, values=["Wszystkie", "Tak", "Nie"],
    state="readonly", width=23
)
cancer_all_combobox.set("Wszystkie")
cancer_all_combobox.grid(row=5, column=1, padx=5, pady=5)


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

# Filtry pacjentów — pojedynczy wariant
patient_filters_frame = ttk.LabelFrame(left_frame, text="Filtry pacjentów")
patient_filters_frame.pack(fill="x", padx=15, pady=5)

ttk.Label(patient_filters_frame, text="Wiek od:").grid(row=0, column=0, padx=5, pady=5)
age_min_entry = ttk.Entry(patient_filters_frame, width=8)
age_min_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(patient_filters_frame, text="Wiek do:").grid(row=0, column=2, padx=5, pady=5)
age_max_entry = ttk.Entry(patient_filters_frame, width=8)
age_max_entry.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(patient_filters_frame, text="Nowotwór:").grid(row=1, column=0, padx=5, pady=5)
cancer_combobox = ttk.Combobox(
    patient_filters_frame, values=["Wszystkie", "Tak", "Nie"],
    state="readonly", width=15
)
cancer_combobox.set("Wszystkie")
cancer_combobox.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")


controls_frame = ttk.Frame(
    left_frame
)

controls_frame.pack(
    padx=15,
    pady=15
)
chart_frame = ttk.LabelFrame(
    left_frame,
    text="Częstość wariantu a występowanie nowotworu"
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


def show_cancer_chart(rs_id, age_min=None, age_max=None):
    """Porównuje AF w grupach z nowotworem i bez, w wybranym wieku."""
    for widget in chart_frame.winfo_children():
        widget.destroy()

    df = get_cancer_group_af(rs_id, age_min, age_max)
    groups = [("tak", "Z nowotworem"), ("nie", "Bez nowotworu")]
    values, sizes = [], []
    for code, label in groups:
        subset = df[df["has_cancer"] == code] if not df.empty else df
        if subset.empty:
            values.append(0.0)
            sizes.append(0)
        else:
            values.append(float(subset.iloc[0]["af_percent"]))
            sizes.append(int(subset.iloc[0]["tested_n"]))

    if not any(sizes):
        ttk.Label(chart_frame, text="Brak pacjentów w wybranym zakresie wieku.").pack(pady=30)
        return

    fig, ax = plt.subplots(figsize=(5.3, 3.6))
    labels = [label for _, label in groups]
    bars = ax.bar(labels, values)
    max_value = max(values)
    logarithmic = scale_combobox.get() == "Logarytmiczna"
    positive_values = [v for v in values if v > 0]
    if logarithmic and positive_values:
        ax.set_yscale("log")
        minimum = min(positive_values)
        ax.set_ylim(max(minimum / 10, 1e-8), max(max_value * 3, minimum * 2))
    else:
        ax.set_ylim(0, max(max_value * 1.3, 0.01))
    for bar, value, size in zip(bars, values, sizes):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            (value * 1.18 if logarithmic and positive_values and value > 0
             else value + max(max_value * 0.035, 0.0003)),
            f"{value:.4f}%\\n(n={size})" if size else "Brak pacjentów",
            ha="center", va="bottom", fontsize=9
        )
    if logarithmic and not positive_values:
        ax.text(0.5, 0.5, "AF = 0 w obu grupach — skala liniowa",
                transform=ax.transAxes, ha="center", va="center", fontsize=9)
    elif logarithmic and any(v == 0 for v in values):
        ax.text(0.5, 0.96, "AF = 0 nie jest widoczne na skali logarytmicznej",
                transform=ax.transAxes, ha="center", va="top", fontsize=8)
    ax.set_ylabel("Częstość allelu (AF) [%]")
    ax.set_title(f"{rs_id} — grupy według statusu nowotworu")
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

    ttk.Label(
        chart_frame,
        text="Obie grupy porównywane są w tym samym zakresie wieku.\\n"
             "Wykres pokazuje dane syntetyczne, nie dowodzi związku przyczynowego.",
        justify="center"
    ).pack(pady=(0, 6))


def read_patient_filters(age_min_entry, age_max_entry, cancer_combobox):
    """Odczytuje i sprawdza filtry pacjentów."""
    text_min = age_min_entry.get().strip()
    text_max = age_max_entry.get().strip()
    try:
        age_min = int(text_min) if text_min else None
        age_max = int(text_max) if text_max else None
    except ValueError:
        raise ValueError("Wiek musi być liczbą całkowitą.")

    if age_min is not None and not 0 <= age_min <= 120:
        raise ValueError("Wiek od musi mieścić się w zakresie 0–120.")
    if age_max is not None and not 0 <= age_max <= 120:
        raise ValueError("Wiek do musi mieścić się w zakresie 0–120.")
    if age_min is not None and age_max is not None and age_min > age_max:
        raise ValueError("Wiek od nie może być większy niż wiek do.")

    selection = cancer_combobox.get()
    has_cancer = {"Tak": "tak", "Nie": "nie"}.get(selection)
    return age_min, age_max, has_cancer


def show_all_variants_chart():

    population = population_all_combobox.get()
    gene = gene_all_combobox.get()

    try:
        age_min, age_max, has_cancer = read_patient_filters(
            age_min_all_entry, age_max_all_entry, cancer_all_combobox
        )
    except ValueError as error:
        messagebox.showerror("Nieprawidłowe filtry", str(error))
        return

    df = get_all_comparisons(
        population, gene,
        age_min=age_min, age_max=age_max, has_cancer=has_cancer
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
    row=6,
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

    try:
        age_min, age_max, has_cancer = read_patient_filters(
            age_min_entry, age_max_entry, cancer_combobox
        )
    except ValueError as error:
        messagebox.showerror("Nieprawidłowe filtry", str(error))
        return

    df = get_comparison_by_rs(
        rs_id, population,
        age_min=age_min, age_max=age_max, has_cancer=has_cancer
    )

    # Wykres grup nowotworowych nie zależy od dostępności danych gnomAD.
    # Celowo porównuje obie grupy niezależnie od filtra "Nowotwór".
    show_cancer_chart(rs_id, age_min, age_max)

    if df is None:
        status_value.config(
            text="Brak danych referencyjnych lub pacjentów dla wybranych filtrów."
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

show_button = ttk.Button(
    controls_frame,
    text="Pokaż statystyki",
    command=show_statistics
)

show_button.pack()

ttk.Label(controls_frame, text="Skala wykresu:").pack(pady=(10, 2))
scale_combobox = ttk.Combobox(
    controls_frame, values=["Liniowa", "Logarytmiczna"],
    state="readonly", width=18
)
scale_combobox.set("Liniowa")
scale_combobox.pack()


def change_scale(event=None):
    if variant_combobox.get():
        show_statistics()


scale_combobox.bind("<<ComboboxSelected>>", change_scale)

root.mainloop()

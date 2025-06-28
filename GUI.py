import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog

class VerticalReraViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("RERA CSV Viewer (with Dynamic Filters)")
        self.root.geometry("1000x700")

        self.df = None
        self.filtered_df = None
        self.current_index = 0
        self.available_filters = {}

        # Upload button
        upload_btn = ttk.Button(root, text="Upload CSV", command=self.load_csv)
        upload_btn.pack(pady=10)

        # Filter frame
        self.filter_frame = tk.Frame(root)
        self.filter_frame.pack()

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.state_var = tk.StringVar()
        self.district_var = tk.StringVar()

        # Search bar (always visible)
        tk.Label(self.filter_frame, text="RERA No:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(self.filter_frame, textvariable=self.search_var, width=20).grid(row=0, column=1, padx=5, pady=5)

        # Button placeholder (actual buttons placed later)
        self.button_frame = tk.Frame(self.filter_frame)
        self.button_frame.grid(row=0, column=4, rowspan=2, padx=10, pady=5)

        # Scrollable frame for data
        container = tk.Frame(root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(container)
        scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # Navigation buttons
        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=10)
        ttk.Button(nav_frame, text="Previous", command=self.show_previous).pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="Next", command=self.show_next).pack(side=tk.LEFT, padx=10)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        self.df = pd.read_csv(path, low_memory=False)
        self.filtered_df = self.df.copy()
        self.current_index = 0

        # Clean filter area
        for widget in self.filter_frame.winfo_children():
            if widget != self.button_frame and not isinstance(widget, ttk.Entry):
                widget.destroy()

        # RERA No Label and Entry again (after clearing others)
        tk.Label(self.filter_frame, text="RERA No:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(self.filter_frame, textvariable=self.search_var, width=20).grid(row=0, column=1, padx=5, pady=5)

        # Determine available filters dynamically
        self.available_filters = {}

        row = 1
        col = 0
        if 'projectStatus' in self.df.columns:
            self.available_filters['projectStatus'] = self.status_var
            self.status_cb = ttk.Combobox(self.filter_frame, textvariable=self.status_var, width=20, state="readonly")
            self.status_cb['values'] = sorted(self.df['projectStatus'].dropna().unique())
            tk.Label(self.filter_frame, text="Status:").grid(row=row, column=col, padx=5, pady=5, sticky='w')
            self.status_cb.grid(row=row, column=col + 1, padx=5, pady=5)
            col += 2

        if 'state' in self.df.columns:
            self.available_filters['state'] = self.state_var
            self.state_cb = ttk.Combobox(self.filter_frame, textvariable=self.state_var, width=20, state="readonly")
            self.state_cb['values'] = sorted(self.df['state'].dropna().unique())
            tk.Label(self.filter_frame, text="State:").grid(row=row, column=col, padx=5, pady=5, sticky='w')
            self.state_cb.grid(row=row, column=col + 1, padx=5, pady=5)
            col += 2

        if 'district' in self.df.columns:
            self.available_filters['district'] = self.district_var
            self.district_cb = ttk.Combobox(self.filter_frame, textvariable=self.district_var, width=20, state="readonly")
            self.district_cb['values'] = sorted(self.df['district'].dropna().unique())
            tk.Label(self.filter_frame, text="District:").grid(row=row, column=col, padx=5, pady=5, sticky='w')
            self.district_cb.grid(row=row, column=col + 1, padx=5, pady=5)

        # Buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        ttk.Button(self.button_frame, text="Apply Filter", command=self.apply_filters).pack(pady=2)
        ttk.Button(self.button_frame, text="Clear Filters", command=self.clear_filters).pack(pady=2)

        self.show_record()

    def apply_filters(self):
        if self.df is None:
            return

        df_filtered = self.df.copy()

        # Apply RERA search
        if self.search_var.get().strip():
            df_filtered = df_filtered[df_filtered['reraNo'].astype(str).str.contains(self.search_var.get().strip(), case=False, na=False)]

        # Apply other filters if their columns exist
        for column, var in self.available_filters.items():
            if var.get():
                df_filtered = df_filtered[df_filtered[column] == var.get()]

        self.filtered_df = df_filtered
        self.current_index = 0
        self.show_record()

    def clear_filters(self):
        self.search_var.set("")
        for var in self.available_filters.values():
            var.set("")

        if self.df is not None:
            self.filtered_df = self.df.copy()
            self.current_index = 0
            self.show_record()

    def show_record(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if self.filtered_df is None or self.filtered_df.empty:
            tk.Label(self.scrollable_frame, text="No records found.", font=("Arial", 14)).pack()
            return

        record = self.filtered_df.iloc[self.current_index]
        for col, val in record.items():
            row = tk.Frame(self.scrollable_frame)
            row.pack(anchor='w', fill='x', pady=2)
            tk.Label(row, text=f"{col}:", font=("Arial", 10, "bold"), width=25, anchor='w').pack(side=tk.LEFT)
            tk.Label(row, text=str(val), font=("Arial", 10), wraplength=1000, justify="left").pack(side=tk.LEFT, fill='x', expand=True)

        count_text = f"Showing {self.current_index + 1} of {len(self.filtered_df)} result(s)"
        tk.Label(self.scrollable_frame, text=count_text, font=("Arial", 10, "italic"), pady=10).pack()

    def show_previous(self):
        if self.filtered_df is not None and self.current_index > 0:
            self.current_index -= 1
            self.show_record()

    def show_next(self):
        if self.filtered_df is not None and self.current_index < len(self.filtered_df) - 1:
            self.current_index += 1
            self.show_record()

if __name__ == "__main__":
    root = tk.Tk()
    app = VerticalReraViewer(root)
    root.mainloop()

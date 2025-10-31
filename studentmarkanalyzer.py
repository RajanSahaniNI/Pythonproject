import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import pandas as pd
import matplotlib.pyplot as plt

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 32
        y = y + cy + self.widget.winfo_rooty() + 22
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#232939", foreground="white", relief='solid', borderwidth=1,
                         font=("Segoe UI", 10, "normal"), padx=9, pady=3)
        label.pack()
    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

ICON_PATH = "icon.ico"  # You can remove or replace this with your own icon

selected_file = None
df = None
subject_stats = None
theme = "light"

def calc_grade(mark):
    if mark >= 90:
        return 'A'
    elif mark >= 80:
        return 'B'
    elif mark >= 70:
        return 'C'
    elif mark >= 60:
        return 'D'
    else:
        return 'F'

def select_file(lbl_file):
    global selected_file, df, subject_stats
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        selected_file = file_path
        lbl_file.config(text=f"Selected File: {file_path}")
        try:
            df = pd.read_csv(selected_file)
            for subject in ['Math', 'Science', 'English']:
                df[subject + '_Grade'] = df[subject].apply(calc_grade)
            df['Total'] = df[['Math', 'Science', 'English']].sum(axis=1)
            df['Average'] = df[['Math', 'Science', 'English']].mean(axis=1)
            subject_stats = df[['Math', 'Science', 'English']].agg(['mean', 'min', 'max'])
        except Exception as e:
            messagebox.showerror("Error", f"Could not process file:\n{e}")

def show_results(output_area):
    global df, subject_stats
    if df is None:
        messagebox.showwarning("No file selected", "Please select a CSV file first.")
        return
    top_student = df.loc[df['Total'].idxmax(), 'Name']
    top_scorers = {sub: df.loc[df[sub].idxmax(), 'Name'] for sub in ['Math', 'Science', 'English']}
    output = []
    output.append("Per-student results:")
    output.append(df[['Name', 'Math', 'Math_Grade', 'Science', 'Science_Grade', 'English', 'English_Grade', 'Total', 'Average']].to_string(index=False))
    output.append("\nOverall Top Scorer: " + str(top_student))
    output.append("Subject-wise Top Scorers: " + str(top_scorers))
    output.append("\nSubject statistics (mean/min/max):\n" + str(subject_stats))
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, "\n".join(output))
    output_area.config(state='disabled')

def plot_avg_marks():
    global subject_stats
    if subject_stats is None:
        messagebox.showwarning("No data", "Please select and process a CSV file first.")
        return
    plt.figure(figsize=(7,5))
    avg_marks = subject_stats.loc['mean']
    plt.bar(['Math', 'Science', 'English'], avg_marks, color=['skyblue','salmon','limegreen'])
    plt.title('Average Marks per Subject')
    plt.ylabel('Average Marks')
    plt.xlabel('Subject')
    plt.tight_layout()
    plt.show()

def plot_total_marks():
    global df
    if df is None:
        messagebox.showwarning("No data", "Please select and process a CSV file first.")
        return
    plt.figure(figsize=(8,5))
    plt.barh(df['Name'], df['Total'], color='orchid')
    plt.title('Total Marks per Student')
    plt.xlabel('Total Marks')
    plt.tight_layout()
    plt.show()

def plot_pie_chart(subj):
    global df
    if df is None:
        messagebox.showwarning("No data", "Please select and process a CSV file first.")
        return
    plt.figure(figsize=(6,6))
    grade_counts = df[f'{subj}_Grade'].value_counts()
    plt.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title(f'Grade Distribution in {subj}')
    plt.tight_layout()
    plt.show()

def reset_ui(lbl_file, output_area, dropdown):
    global selected_file, df, subject_stats
    selected_file = None
    df = None
    subject_stats = None
    lbl_file.config(text="Selected File: None")
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.config(state='disabled')
    dropdown.set("Math")

def toggle_theme(root, banner, frame_buttons, frame_pie, lbl_file, output_area):
    global theme
    theme = "dark" if theme == "light" else "light"
    colors = {
        "dark": {
            "bg": "#232939",
            "fg": "#e2eefd",
            "banner_bg": "#185a9d",
            "banner_fg": "#e2eefd",
            "btn_bg": "#2d4156",
            "btn_fg": "#d2faf3",
            "label_fg": "#e2eefd",
            "output_bg": "#2d4156",
        },
        "light": {
            "bg": "#f2f6fb",
            "fg": "#185a9d",
            "banner_bg": "#43cea2",
            "banner_fg": "#185a9d",
            "btn_bg": "#43cea2",
            "btn_fg": "white",
            "label_fg": "#348f50",
            "output_bg": "#e6f7f9",
        }
    }
    color = colors[theme]
    root.config(bg=color["bg"])
    banner.config(bg=color["banner_bg"], fg=color["banner_fg"])
    frame_buttons.config(bg=color["bg"])
    frame_pie.config(bg=color["bg"])
    lbl_file.config(bg=color["bg"], fg=color["label_fg"])
    output_area.config(background=color["output_bg"], fg=color["fg"])

def export_summary():
    global df, subject_stats
    if df is None:
        messagebox.showwarning("No data", "Please select and process a CSV file first.")
        return
    top_student = df.loc[df['Total'].idxmax(), 'Name']
    top_scorers = {sub: df.loc[df[sub].idxmax(), 'Name'] for sub in ['Math', 'Science', 'English']}
    output = []
    output.append("Per-student results:")
    output.append(df[['Name', 'Math', 'Math_Grade', 'Science', 'Science_Grade', 'English', 'English_Grade', 'Total', 'Average']].to_string(index=False))
    output.append("\nOverall Top Scorer: " + str(top_student))
    output.append("Subject-wise Top Scorers: " + str(top_scorers))
    output.append("\nSubject statistics (mean/min/max):\n" + str(subject_stats))
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")])
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(output))
            messagebox.showinfo("Export Successful", f"Summary exported to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export summary:\n{e}")

root = tk.Tk()
root.title("Student Marks Analyzer")
try:
    root.iconbitmap(ICON_PATH)
except Exception:
    pass

root.geometry("1000x680")
root.configure(bg="#f2f6fb")

banner = tk.Label(
    root, text="🎓 Student Marks Analyzer", font=("Segoe UI", 26, "bold"),
    bg="#43cea2", fg="#185a9d", pady=10
)
banner.pack(fill="x", pady=0)

tk.Label(
    root, text="Select a CSV file containing marks, view results, and generate charts.",
    font=("Segoe UI", 13), bg="#f2f6fb", fg="#236977"
).pack()

lbl_file = tk.Label(root, text="Selected File: None", fg="#348f50", bg="#f2f6fb", font=("Segoe UI", 11))
lbl_file.pack(pady=5)

output_area = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, width=118, height=17, font=("Consolas", 10), background="#e6f7f9"
)
output_area.pack(pady=8)
output_area.config(state='disabled')

frame_buttons = tk.Frame(root, bg="#f2f6fb")
frame_buttons.pack(pady=7)

btn_select = tk.Button(
    frame_buttons, text="Select CSV File", command=lambda: select_file(lbl_file),
    font=("Segoe UI", 13, "bold"), bg="#43cea2", fg="white", width=15, relief=tk.RAISED, bd=3
)
btn_select.grid(row=0, column=0, padx=7, pady=7)
ToolTip(btn_select, "Choose a CSV file to analyze.")

btn_results = tk.Button(
    frame_buttons, text="Show Results", command=lambda: show_results(output_area),
    font=("Segoe UI", 13, "bold"), bg="#37c978", fg="white", width=15, relief=tk.RAISED, bd=3
)
btn_results.grid(row=0, column=1, padx=7, pady=7)
ToolTip(btn_results, "Display statistics and grades in the panel below.")

btn_avg = tk.Button(
    frame_buttons, text="Average Marks Chart", command=plot_avg_marks,
    font=("Segoe UI", 12, "bold"), bg="#4f8cff", fg="white", width=17, relief=tk.RAISED, bd=3
)
btn_avg.grid(row=0, column=2, padx=7, pady=7)
ToolTip(btn_avg, "Show bar chart of subject averages.")

btn_total = tk.Button(
    frame_buttons, text="Total Marks Chart", command=plot_total_marks,
    font=("Segoe UI", 12, "bold"), bg="#c86dd7", fg="white", width=17, relief=tk.RAISED, bd=3
)
btn_total.grid(row=0, column=3, padx=7, pady=7)
ToolTip(btn_total, "Show total marks per student.")

btn_reset = tk.Button(
    frame_buttons, text="Reset", command=lambda: reset_ui(lbl_file, output_area, subj_dropdown),
    font=("Segoe UI", 12, "bold"), bg="#e44f4f", fg="white", width=15, relief=tk.RAISED, bd=3
)
btn_reset.grid(row=0, column=4, padx=7, pady=7)
ToolTip(btn_reset, "Clear all results and selections.")

btn_theme = tk.Button(
    frame_buttons, text="Dark/Light Mode", command=lambda: toggle_theme(root, banner, frame_buttons, frame_pie, lbl_file, output_area),
    font=("Segoe UI", 12, "bold"), bg="#232939", fg="#e2eefd", width=15, relief=tk.RAISED, bd=3
)
btn_theme.grid(row=0, column=5, padx=7, pady=7)
ToolTip(btn_theme, "Toggle between dark and light UI themes.")

btn_export = tk.Button(
    frame_buttons, text="Export Summary", command=export_summary,
    font=("Segoe UI", 12, "bold"), bg="#185a9d", fg="white", width=15, relief=tk.RAISED, bd=3
)
btn_export.grid(row=0, column=6, padx=7, pady=7)
ToolTip(btn_export, "Export analysis results and statistics to a file.")

frame_pie = tk.Frame(root, bg="#f2f6fb")
frame_pie.pack(pady=7)
tk.Label(frame_pie, text="Grade Distribution Pie Chart: ", font=("Segoe UI", 12), bg="#f2f6fb", fg="#236977").grid(row=0, column=0, columnspan=2, pady=3)

subj_dropdown = ttk.Combobox(frame_pie, values=["Math", "Science", "English"], font=("Segoe UI", 12), width=13, state="readonly")
subj_dropdown.grid(row=1, column=0, padx=12, pady=6)
subj_dropdown.set("Math")
ToolTip(subj_dropdown, "Select subject for pie chart.")

btn_plot_pie = tk.Button(
    frame_pie, text="Show Pie Chart", command=lambda: plot_pie_chart(subj_dropdown.get()),
    font=("Segoe UI", 11, "bold"), bg="#43cea2", fg="white", width=15, relief=tk.RAISED, bd=3
)
btn_plot_pie.grid(row=1, column=1, padx=8, pady=2)
ToolTip(btn_plot_pie, "Generate grade distribution pie chart for selected subject.")

root.mainloop()

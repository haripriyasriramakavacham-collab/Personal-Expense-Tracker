#!/usr/bin/env python
# coding: utf-8

# In[4]:


import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
class ExpenseDatabase:
    FILE_NAME = "expenses.csv"
    HEADERS = ["ID", "Date", "Category", "Price", "Description"]
    def __init__(self):
        self.initialize_database()
    def initialize_database(self):
        if not os.path.exists(self.FILE_NAME):
            with open(self.FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
                writer=csv.writer(file)
                writer.writerow(self.HEADERS)
    def read_all(self):
        if not os.path.exists(self.FILE_NAME):
            return []
        with open(self.FILE_NAME, mode="r", encoding="utf-8") as file:
            return list(csv.reader(file))
    def write_all(self, rows):
        with open(self.FILE_NAME, mode="w", newline="", encoding="utf-8") as file:
            writer=csv.writer(file)
            writer.writerows(rows)
    def generate_next_id(self):
        rows=self.read_all()
        if len(rows)<=1:
            return 1
        existing_ids=[]
        for row in rows[1:]:
            try:
                existing_ids.append(int(row[0]))
            except (ValueError, IndexError):
                continue
        return max(existing_ids) + 1 if existing_ids else 1
class ExpenseOperations(ExpenseDatabase):
    def add_expense_record(self, date_val, category_val, price_val, desc_val):
        next_id=self.generate_next_id()
        with open(self.FILE_NAME, mode="a", newline="", encoding="utf-8") as file:
            writer=csv.writer(file)
            writer.writerow([next_id, date_val, category_val, price_val, desc_val])
        return next_id
    def edit_expense_record(self, target_id, new_date, new_category, new_price, new_desc):
        rows=self.read_all()
        target_row_index=None
        for idx, row in enumerate(rows[1:], start=1):
            if row[0]==str(target_id):
                target_row_index=idx
                break
        if target_row_index is None:
            return False
        current_record=rows[target_row_index]
        if new_date:
            current_record[1]=new_date
        if new_category:
            current_record[2]=new_category.title()
        if new_price:
            current_record[3]=str(new_price)
        if new_desc:
            current_record[4]=new_desc
        rows[target_row_index]=current_record
        self.write_all(rows)
        return True
    def delete_expense_record(self, target_id):
        rows=self.read_all()
        if len(rows)<=1:
            return False
        updated_list=[rows[0]]
        deleted_flag=False
        for row in rows[1:]:
            if row[0]==str(target_id):
                deleted_flag=True
            else:
                updated_list.append(row)
        if deleted_flag:
            self.write_all(updated_list)
            return True
        return False
class ExpenseReporter(ExpenseOperations):
    def calculate_summary_data(self):
        rows=self.read_all()
        if len(rows)<=1:
            return 0.0, {}
        total_sum=0.0
        category_map={}
        for row in rows[1:]:
            try:
                val=float(row[3])
                cate=row[2]
                total_sum+=val
                category_map[cate]=category_map.get(cate, 0.0) + val
            except (ValueError, IndexError):
                continue
        return total_sum, category_map
class ExpenseTrackerGUI(ExpenseReporter):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.title("Personal Expense Tracker System")
        self.root.geometry("800x650")
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)
        self.setup_ui()
        self.refresh_table()
    def setup_ui(self):
        input_frame=ttk.LabelFrame(self.root, text=" Expense Details ", padding=10)
        input_frame.pack(fill="x", padx=15, pady=10)
        ttk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Category:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_entry = ttk.Entry(input_frame, width=15)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Price:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.price_entry = ttk.Entry(input_frame, width=15)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Description:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=25)
        self.desc_entry.grid(row=1, column=3, padx=5, pady=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Add Expense", command=self.add_gui).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="View Record", command=self.view_record_gui).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.edit_gui).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_gui).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_entries).pack(side="left", padx=5)

        search_frame = ttk.LabelFrame(self.root, text=" Search Records ", padding=10)
        search_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(search_frame, text="Query (Category or Date):").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(search_frame, text="Search", command=self.search_gui).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Reset Table", command=self.refresh_table).pack(side="left", padx=5)

        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=self.HEADERS, show="headings")
        for col in self.HEADERS:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.column("ID", width=50)
        self.tree.column("Description", width=250, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill="x", padx=15, pady=5)
        ttk.Button(bottom_frame, text="Generate Summary Report", command=self.show_summary_gui).pack(side="left")
        self.total_label = ttk.Label(bottom_frame, text="Gross Spend: $0.00", font=("Arial", 11, "bold"))
        self.total_label.pack(side="right")

    def refresh_table(self, rows_to_display=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = rows_to_display if rows_to_display is not None else self.read_all()
        if len(rows) > 1:
            for row in rows[1:]:
                self.tree.insert("", "end", values=row)
        total, _ = self.calculate_summary_data()
        self.total_label.config(text=f"Gross Spend: ${total:.2f}")

    def add_gui(self):
        date_val = self.date_entry.get().strip()
        category_val = self.category_entry.get().strip().title()
        price_str = self.price_entry.get().strip()
        desc_val = self.desc_entry.get().strip()

        try:
            datetime.strptime(date_val, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Use YYYY-MM-DD format for date.")
            return

        try:
            price_val = float(price_str)
            if price_val <= 0:
                messagebox.showerror("Invalid Price", "Price must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Invalid Number", "Enter a valid numerical price.")
            return

        assigned_id = self.add_expense_record(date_val, category_val, price_val, desc_val)
        self.refresh_table()
        self.clear_entries()
        messagebox.showinfo("Success", f"Expense logged successfully (Assigned ID: {assigned_id})")

    def view_record_gui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Select a record from table to view.")
            return
        values = self.tree.item(selected[0], "values")
        details = f"Record ID: {values[0]}\nDate: {values[1]}\nCategory: {values[2]}\nPrice: ${float(values[3]):.2f}\nDescription: {values[4]}"
        messagebox.showinfo("Expense Record Details", details)

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clear_entries()
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, values[1])
            self.category_entry.insert(0, values[2])
            self.price_entry.insert(0, values[3])
            self.desc_entry.insert(0, values[4])

    def edit_gui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Select a row from table to edit.")
            return

        target_id = self.tree.item(selected[0], "values")[0]
        date_val = self.date_entry.get().strip()
        category_val = self.category_entry.get().strip()
        price_str = self.price_entry.get().strip()
        desc_val = self.desc_entry.get().strip()

        try:
            datetime.strptime(date_val, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Use YYYY-MM-DD format for date.")
            return

        try:
            price_val = float(price_str)
            if price_val <= 0:
                messagebox.showerror("Invalid Price", "Price must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Invalid Number", "Enter a valid numerical price.")
            return

        if self.edit_expense_record(target_id, date_val, category_val, price_val, desc_val):
            self.refresh_table()
            self.clear_entries()
            messagebox.showinfo("Success", f"Record ID {target_id} updated successfully!")

    def delete_gui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Select a record from table to delete.")
            return
        target_id = self.tree.item(selected[0], "values")[0]
        if self.delete_expense_record(target_id):
            self.refresh_table()
            self.clear_entries()

            messagebox.showinfo("Success", "Record removed successfully!")

    def search_gui(self):
        query = self.search_entry.get().strip().lower()
        rows = self.read_all()
        if len(rows) <= 1:
            return
        matches = [rows[0]] + [row for row in rows[1:] if query in row[1].lower() or query in row[2].lower()]
        self.refresh_table(matches)

    def show_summary_gui(self):
        total, category_map = self.calculate_summary_data()
        if not category_map:
            messagebox.showinfo("Summary Report", "No transaction records available.")
            return

        report = [
            f"Overall Gross Spend: ${total:.2f}\n",
            "Category Distribution Summary:",
            "-" * 40,
        ]
        for cate, amt in category_map.items():
            report.append(f"{cate:<12}: ${amt:.2f}")

        messagebox.showinfo("Financial Summary Report", "\n".join(report))

    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.category_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()


# In[ ]:





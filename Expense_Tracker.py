from tkinter import *
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import csv
import os

transactions = []
filename = "expenses.csv"

def load_data():
    global transactions
    if os.path.exists(filename):
        with open(filename, newline="") as f:
            reader = csv.reader(f)
            transactions = list(reader)
    update_table()
    update_balance()

def save_data():
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(transactions)

def add_transaction():
    t_type = type_var.get()
    category = category_var.get().strip()
    amount = amount_var.get().strip()

    if not category or not amount:
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        amt = float(amount)
    except:
        messagebox.showerror("Error", "Amount must be a number")
        return

    transactions.append([t_type, category, f"{amt:.2f}"])
    update_table()
    update_balance()
    save_data()

def delete_selected():
    selected = table.selection()
    if not selected:
        messagebox.showinfo("Info", "Select a transaction to delete")
        return
    for item in selected:
        values = table.item(item, "values")
        for t in transactions:
            if t[0] == values[0] and t[1] == values[1] and t[2] == values[2]:
                transactions.remove(t)
                break
    update_table()
    update_balance()
    save_data()

def update_table():
    for row in table.get_children():
        table.delete(row)
    for t in transactions:
        tag = "income" if t[0] == "Income" else "expense"
        table.insert("", "end", values=t, tags=(tag,))

def update_balance():
    balance = 0
    for t in transactions:
        amt = float(t[2])
        if t[0] == "Income":
            balance += amt
        else:
            balance -= amt
    balance_label.config(text=f"Balance: ₹{balance:.2f}", 
                         fg="green" if balance >=0 else "red")

def show_pie_chart():
    expense_data = {}
    for t in transactions:
        if t[0] == "Expense":
            category = t[1]
            amt = float(t[2])
            expense_data[category] = expense_data.get(category, 0) + amt

    if not expense_data:
        messagebox.showinfo("Info", "No expense data to show chart")
        return

    categories = list(expense_data.keys())
    amounts = list(expense_data.values())

    plt.pie(amounts, labels=categories, autopct="%1.1f%%")
    plt.title("Expenses by Category")
    plt.show()

def new_list():
    global transactions
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all transactions?"):
        transactions = []
        save_data()
        update_table()
        update_balance()

window = Tk()
window.title("Ankit's Expense Tracker")
window.geometry("750x600")
window.config(bg="#282c34")

type_var = StringVar(value="Expense")
category_var = StringVar()
amount_var = StringVar()

Label(window, text="Expense Tracker", font=("Arial", 20), bg="#282c34", fg="white").pack(pady=10)

form = Frame(window, bg="#282c34")
form.pack(pady=10)

Label(form, text="Type:", bg="#282c34", fg="white").grid(row=0, column=0, padx=5, pady=5)
OptionMenu(form, type_var, "Income", "Expense").grid(row=0, column=1, padx=5, pady=5)

Label(form, text="Category:", bg="#282c34", fg="white").grid(row=0, column=2, padx=5, pady=5)
Entry(form, textvariable=category_var).grid(row=0, column=3, padx=5, pady=5)

Label(form, text="Amount:", bg="#282c34", fg="white").grid(row=0, column=4, padx=5, pady=5)
Entry(form, textvariable=amount_var).grid(row=0, column=5, padx=5, pady=5)

Button(form, text="Add", command=add_transaction, bg="#61afef", width=10).grid(row=0, column=6, padx=5)
Button(form, text="Delete Selected", command=delete_selected, bg="#e06c75", width=15).grid(row=0, column=7, padx=5)
Button(form, text="New List", command=new_list, bg="#d19a66", width=10).grid(row=0, column=8, padx=5)

table_frame = Frame(window)
table_frame.pack(pady=10)

table = ttk.Treeview(table_frame, columns=("Type", "Category", "Amount"), show="headings", height=12)
table.heading("Type", text="Type")
table.heading("Category", text="Category")
table.heading("Amount", text="Amount")
table.tag_configure("income", foreground="green")
table.tag_configure("expense", foreground="red")
table.pack()

balance_label = Label(window, text="Balance: ₹0.00", font=("Arial", 16), bg="#282c34", fg="#98c379")
balance_label.pack(pady=10)

Button(window, text="Show Expense Chart", command=show_pie_chart, bg="#e5c07b", width=20).pack(pady=5)

footer = Label(window, text="Developed by Ankit", font=("Arial", 10), fg="gray", bg="#282c34")
footer.pack(side="bottom")

load_data()
window.mainloop()
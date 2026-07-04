import tkinter as tk

def open_expense_tracker():
    dashboard.withdraw()

    expense_win = tk.Toplevel()
    expense_win.title("Expense Tracker")
    expense_win.geometry("500x400")
    expense_win.config(bg="white")

    tk.Label(expense_win, text="EXPENSE TRACKER", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    header_frame = tk.Frame(expense_win, bg="gray")
    header_frame.pack(fill="x", padx=10)

    tk.Label(header_frame, text="EXPENSE TYPE", bg="lightgray", bd=1, relief="solid").grid(row=0, column=0, sticky="nsew")
    tk.Label(header_frame, text="AMOUNT", bg="lightgray", bd=1, relief="solid").grid(row=0, column=1, sticky="nsew")
    tk.Label(header_frame, text="ADD EXPENSE", bg="lightgray", bd=1, relief="solid").grid(row=0, column=2, sticky="nsew")

    header_frame.grid_columnconfigure(0, weight=1)
    header_frame.grid_columnconfigure(1, weight=1)
    header_frame.grid_columnconfigure(2, weight=1)

    input_frame = tk.Frame(expense_win, bg="white")
    input_frame.pack(fill="x", padx=10, pady=5)

    expense_type_entry = tk.Entry(input_frame)
    expense_type_entry.grid(row=0, column=0, sticky="ew", padx=2)

    amount_entry = tk.Entry(input_frame)
    amount_entry.grid(row=0, column=1, sticky="ew", padx=2)

    def add_expense():
        expense_type = expense_type_entry.get()
        amount = amount_entry.get()
        if expense_type and amount:
            expense_list.insert(tk.END, f"{expense_type} - ${amount}")
            expense_type_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)

    add_button = tk.Button(input_frame, text="Add", command=add_expense)
    add_button.grid(row=0, column=2, sticky="ew", padx=2)

    input_frame.grid_columnconfigure(0, weight=1)
    input_frame.grid_columnconfigure(1, weight=1)
    input_frame.grid_columnconfigure(2, weight=1)

    expense_list = tk.Listbox(expense_win, height=10)
    expense_list.pack(fill="both", expand=True, padx=10, pady=10)

    def on_close():
        expense_win.destroy()
        dashboard.deiconify()

    expense_win.protocol("WM_DELETE_WINDOW", on_close)

def open_dashboard():
    login_win.destroy()

    global dashboard
    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry("700x500")
    dashboard.config(bg="white")

    sidebar = tk.Frame(dashboard, bg="plum1", width=150, height=500)
    sidebar.pack(side="left", fill="y")

    tk.Label(sidebar, text="USER", bg="plum1", fg="black", font=("Arial", 12, "bold")).pack(pady=20)

    tk.Button(sidebar, text="HOME", bg="white", width=12).pack(pady=5)
    tk.Button(sidebar, text="EXPENSES", bg="white", width=12, command=open_expense_tracker).pack(pady=5)
    tk.Button(sidebar, text="GOALS", bg="white", width=12).pack(pady=5)
    tk.Button(sidebar, text="HELP", bg="white", width=12).pack(pady=5)

    main_frame = tk.Frame(dashboard, bg="white")
    main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    tk.Label(main_frame, text="Welcome to the Dashboard!", font=("Arial", 18), bg="white").pack(pady=20)

    dashboard.mainloop()

login_win = tk.Tk()
login_win.title("Login Page")
login_win.geometry("400x300")
login_win.config(bg="white")

tk.Label(login_win, text="LOGIN PAGE", bg="plum1", fg="black", font=("Arial", 14, "bold"), width=25).pack(pady=10)

tk.Label(login_win, text="Name:", bg="white").pack()
tk.Entry(login_win).pack(pady=5)

tk.Label(login_win, text="Email:", bg="white").pack()
tk.Entry(login_win).pack(pady=5)

tk.Label(login_win, text="Password:", bg="white").pack()
tk.Entry(login_win, show="*").pack(pady=5)

tk.Button(login_win, text="Login", bg="plum1", command=open_dashboard).pack(pady=20)

login_win.mainloop()
TKP.py
Displaying TKP.py

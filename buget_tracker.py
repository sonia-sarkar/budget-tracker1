import csv
from datetime import datetime
import os
import matplotlib.pyplot as plt
import termplotlib as tpl
DATA_FILE = "data/expenses.tsv"
import sqlite3
import openai


def categorize_expense_with_ai(description):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that classifies expenses into one of the following categories: Food, Transportation, Entertainment, Housing, Misc."
                },
                {
                    "role": "user",
                    "content": f"Classify this expense: {description}"
                }
            ],
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        print(f"❌ AI categorization failed: {e}")
        return None
    
DB_FILE = "data/budget.db"

VALID_CATEGORIES = ['Food', 'Transportation', 'Entertainment', 'Housing', 'Misc']

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')
def categorize_description(description):
    try:
        prompt = (
            f"What category does this expense fall into: '{description}'?\n"
            f"Categories: {', '.join(VALID_CATEGORIES)}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that classifies expenses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        category = response['choices'][0]['message']['content'].strip()

        if category not in VALID_CATEGORIES:
            print(f"⚠️ Category '{category}' not recognized. Defaulting to 'Misc'.")
            return "Misc"
        return category
    except Exception as e:
        print(f"❌ Error categorizing expense: {e}")
        return "Misc"
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
    ''')
    return conn

CATEGORIES = ["Food", "Transportation", "Entertainment", "Housing", "Misc"]

def add_expense(conn):
    from datetime import datetime

    date_input = input("Date (YYYY-MM-DD, leave blank for today): ").strip()
    date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")

    use_ai = input("Do you want to auto-categorize based on description? (y/n): ").strip().lower()
    if use_ai == 'y':
        description = input("Enter a short description of the expense: ")
        category = categorize_description(description)
        print(f"✅ Category detected: {category}")
    else:
        category = input(f"Enter a category ({', '.join(CATEGORIES)}): ").strip()
        if category not in CATEGORIES:
            print(f"❌ Invalid category. Please choose from: {', '.join(CATEGORIES)}")
            return

    try:
        amount = float(input("Amount: $"))
    except ValueError:
        print("❌ Invalid amount.")
        return

    conn.execute(
        "INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
        (date, category, amount)
    )
    conn.commit()
    print("✅ Expense added.")


def list_expenses(conn):
    cursor = conn.execute("SELECT id, date, category, amount FROM expenses")
    for row in cursor:
        print(f"{row[0]}: {row[1]} | {row[2]} | ${row[3]:.2f}")

def summary(conn):
    # Get total spent
    total_spent = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0
    print(f"Total spent: ${total_spent:.2f}")

    # Get total budget (if set)
    cursor = conn.execute("SELECT amount FROM budgets WHERE category = '__total__'")
    row = cursor.fetchone()
    if row:
        total_budget = row[0]
        diff = total_budget - total_spent
        status = "✅ Under budget" if diff >= 0 else "❌ Over budget"
        print(f"Total budget: ${total_budget:.2f} ({status}, ${abs(diff):.2f} {'left' if diff >= 0 else 'over'})")

    print()

    # Get spending per category
    cursor = conn.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_spending = {row[0]: row[1] for row in cursor}

    # Get category budgets
    cursor = conn.execute("SELECT category, amount FROM budgets WHERE category != '__total__'")
    category_budgets = {row[0]: row[1] for row in cursor}

    for category, spent in category_spending.items():
        line = f"  {category}: ${spent:.2f}"
        if category in category_budgets:
            budget = category_budgets[category]
            diff = budget - spent
            status = "✅ Under budget" if diff >= 0 else "❌ Over budget"
            line += f" / ${budget:.2f} ({status}, ${abs(diff):.2f} {'left' if diff >= 0 else 'over'})"
        print(line)


'''def graph_expenses_text(conn):
    cursor = conn.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    if not data:
        print("No expenses to graph.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    fig = tpl.figure()
    fig.barh(amounts, categories, force_ascii=True)
    fig.show()'''



def graph_expenses(conn):
    cursor = conn.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    if not data:
        print("No expenses to graph.")
        return

    # Fetch budget data
    budgets = dict(conn.execute("SELECT category, amount FROM budgets").fetchall())

    categories = [row[0] for row in data]
    spent = [row[1] for row in data]
    budgeted = [budgets.get(cat, 0) for cat in categories]
    remaining = [max(budgeted[i] - spent[i], 0) for i in range(len(categories))]

    bar_width = 0.35
    x = range(len(categories))

    fig, ax = plt.subplots()
    ax.bar(x, budgeted, bar_width, label='Budget', color='lightgray')
    ax.bar(x, spent, bar_width, label='Spent', color='tomato')

    ax.set_xlabel('Category')
    ax.set_ylabel('Amount ($)')
    ax.set_title('Spending vs Budget')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.savefig('expenses_graph.png')  # Optional: saves to file
    plt.show()  # This shows the graph in a pop-up window


def edit_expense(conn):
    list_expenses(conn)
    try:
        exp_id = int(input("\nEnter the ID of the expense to edit: "))
    except ValueError:
        print("❌ Invalid ID.")
        return

    cursor = conn.execute("SELECT date, category, amount FROM expenses WHERE id = ?", (exp_id,))
    row = cursor.fetchone()
    if row is None:
        print("❌ Expense not found.")
        return

    old_date, old_category, old_amount = row

    print("Leave input blank to keep the existing value.")

    new_date = input(f"Date [{old_date}]: ") or old_date
    new_category = input(f"Category [{old_category}]: ") or old_category
    try:
        new_amount_str = input(f"Amount [{old_amount}]: ")
        new_amount = float(new_amount_str) if new_amount_str.strip() else old_amount
    except ValueError:
        print("❌ Invalid amount.")
        return

    conn.execute(
        "UPDATE expenses SET date = ?, category = ?, amount = ? WHERE id = ?",
        (new_date, new_category, new_amount, exp_id)
    )
    conn.commit()
    print("✅ Expense updated.")
def set_budget(conn):
    print("\nSet a budget:")
    print("1. Total budget")
    print("2. Category-specific budget")
    choice = input("Choose an option (1 or 2): ").strip()

    if choice == '1':
        try:
            amount = float(input("Enter total budget amount: $"))
            conn.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", ('__total__', amount))
            conn.commit()
            print("✅ Total budget set.")
        except ValueError:
            print("❌ Invalid amount.")
    elif choice == '2':
        while True:
            category = input(f"Category ({', '.join(VALID_CATEGORIES)}): ").strip().title()
            if category in VALID_CATEGORIES:
                break
            print("❌ Invalid category. Please choose from:", ", ".join(VALID_CATEGORIES))

        try:
            amount = float(input(f"Enter budget for {category}: $"))
            conn.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (category, amount))
            conn.commit()
            print(f"✅ Budget for {category} set.")
        except ValueError:
            print("❌ Invalid amount.")
    else:
        print("❌ Invalid option.")

def main():
    conn = get_connection()
    while True:
        command = input("\nCommand (add/budget/list/summary/graph/edit/exit): ").lower()

        if command == "add":
            add_expense(conn)
        elif command == "list":
            list_expenses(conn)
        elif command == "summary":
            summary(conn)
        elif command == "graph":
            graph_expenses(conn)
        elif command == "edit":
            edit_expense(conn)
        elif command == "budget":
            set_budget(conn)
        elif command == "exit":
            conn.close()
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()

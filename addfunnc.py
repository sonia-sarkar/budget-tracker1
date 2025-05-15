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











    def add_expense(conn):
    from datetime import datetime

    date_input = input("Date (YYYY-MM-DD, leave blank for today): ").strip()
    date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
    print("\nCategories:")
    print("1. Food")
    print("2. Transportation")
    print("3. Entertainment")
    print("4. Housing")
    print("5. Misc")
    choice = input("Choose an option #: ").strip()

    if choice == '1':
        category = Food 
    if choice == '2':
        category = Transportation 
    if choice == '3':
        category = Entertainment 
    if choice == '4':
        category = Housing 
    if choice == '5':
        category = Misc
    else:
        print(f"❌ Invalid category. Please choose from: 1, 2, 3, 4, or 5")
    '''while True:
        category = input(f"Category ({', '.join(VALID_CATEGORIES)}): ").capitalize()
        if category in VALID_CATEGORIES:
            break
        else:
            print(f"❌ Invalid category. Please choose from: {', '.join(VALID_CATEGORIES)}")'''

    # Ask for the expense amount
    try:
        amount = float(input("Amount: $"))
    except ValueError:
        print("❌ Invalid amount. Please enter a valid number.")
        return

    # Insert the expense into the database
    conn.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
    conn.commit()
    print("✅ Expense added.")


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


    #WORKING ADDEXPENSE
    '''def add_expense(conn):
    from datetime import datetime

    date_input = input("Date (YYYY-MM-DD, leave blank for today): ").strip()
    date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")

    while True:
        category = input(f"Category ({', '.join(VALID_CATEGORIES)}): ").capitalize()
        if category in VALID_CATEGORIES:
            break
        else:
            print(f"❌ Invalid category. Please choose from: {', '.join(VALID_CATEGORIES)}")

    # Ask for the expense amount
    try:
        amount = float(input("Amount: $"))
    except ValueError:
        print("❌ Invalid amount. Please enter a valid number.")
        return

    # Insert the expense into the database
    conn.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
    conn.commit()
    print("✅ Expense added.")'''

def add_book():
    print("\n➕ Add a New Book")

    title = input("Enter the book title: ").strip()

    # Step 1: Pull existing authors/categories before asking for them
    existing_authors = get_existing_values(2)  # Column B: Authors
    existing_categories = get_existing_values(3)  # Column C: Categories

    # Check if title already exists
    existing_titles = get_existing_values(1)  # Column A: Titles
    if title.lower() in [t.lower() for t in existing_titles]:
        print("⚠️ This book already exists in your library.\n")
        return

    # --- Step 3: Prompt for author and category ---

    # Show existing authors and prompt
    print("\nExisting Authors:")
    for a in existing_authors:
        print(f" - {a}")
    author = input(
        "Enter author name (type exactly if selecting an existing one): ").strip()

    # Show existing categories and prompt
    print("\nExisting Categories:")
    for c in existing_categories:
        print(f" - {c}")
    category = input(
        "Enter category (e.g. fiction, non-fiction, memoir): ").strip()

    # --- Step 4: Prompt for genre, owned, and completed ---

    genre = input("Enter genre (e.g. sci-fi, romance, historical): ").strip()

    # Owned (Yes/No)
    owned = input("Do you own this book? (Y/N): ").strip().lower()
    if owned == "y":
        owned = "Yes"
    else:
        owned = "No"

    # Completed (Yes/No)
    completed = input("Have you completed this book? (Y/N): ").strip().lower()
    if completed == "y":
        completed = "Yes"
    else:
        completed = "No"

    # --- Step 5: log timestamp ---
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Step 6: Append new row to Books sheet ---
    new_row = [title, author, category, genre, owned, completed, timestamp]
    books_sheet.append_row(new_row)
    print(f"✔️ '{title}' by {author} added to the Books sheets.\n")

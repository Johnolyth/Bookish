# -------------------------------------------
# -------------------------------------------
# ----------------BOOKISH APP----------------
# -------------------------------------------
# -------------------------------------------
# -------------------------------------------
# -------------------Setup-------------------


import json
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"
         ]
creds = Credentials.from_service_account_file(
    "charged-sector-283120-2e2e126eaf3d.json",
    scopes=scope)

gc = gspread.authorize(creds)

# Open workbook and worksheets
spreadsheet = gc.open("bookish_test")
books_sheet = spreadsheet.worksheet("Books")
logs_sheet = spreadsheet.worksheet("Logs")
# -----------------FUNCTIONS-----------------


def get_existing_values(column_index):
    values = books_sheet.col_values(column_index)[1:]
    return list(set(v.strip() for v in values if v.strip()))


def add_book():
    print("\nAdd a New Book")

    title = input("Enter the book title: ").strip()

    # Step 1: Pull existing authors/categories before asking for them
    existing_authors = get_existing_values(2)  # Column B: Authors
    existing_categories = get_existing_values(3)  # Column C: Categories

    # Check if title already exists
    existing_titles = get_existing_values(1)  # Column A: Titles
    if title.lower() in [t.lower() for t in existing_titles]:
        print("This book already exists in your library.\n")
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
    print(f"'{title}' by {author} added to the Books sheets.\n")


def edit_book_at_row(row_num):
    row = books_sheet.row_values(row_num)

    print(f"\nEditing: {row[0]} by {row[1]}")
    print("Leave input blank to keep the current value.\n")

    new_title = input(f"Title [{row[0]}]: ").strip()
    if new_title:
        books_sheet.update_cell(row_num, 1, new_title)

    new_author = input(f"Author [{row[1]}]: ").strip()
    if new_author:
        books_sheet.update_cell(row_num, 2, new_author)

    new_category = input(f"Category [{row[2]}]: ").strip()
    if new_category:
        books_sheet.update_cell(row_num, 3, new_category)

    new_genre = input(f"Genre [{row[3]}]: ").strip()
    if new_genre:
        books_sheet.update_cell(row_num, 4, new_genre)

    new_owned = input(f"Owned? (Yes/No) [{row[4]}]: ").strip().capitalize()
    if new_owned in ["Yes", "No"]:
        books_sheet.update_cell(row_num, 5, new_owned)

    new_read = input(f"Completed? (Yes/No) [{row[5]}]: ").strip().capitalize()
    if new_read in ["Yes", "No"]:
        books_sheet.update_cell(row_num, 6, new_read)

    print("Book info updated!\n")


def save_workbook():
    workbook.save(workbook_path)
    print("Changes saved to workbook.\n")


def log_note(title):

    print(f"Logging a note for: {title}")

    page = input("Enter page number (optional): ").strip()
    if not page:
        page = "--"

    note = input(f"Enter your note for '{title}': ").strip()
    if not note:
        print("No note entered.\n")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs_sheet.append_row([title, page, note, timestamp])
    print(f"Note logged for '{title}' at {timestamp}.\n")


def mark_owned(title):

    all_rows = books_sheet.get_all_values()

    for i, row in enumerate(all_rows[1:], start=2):
        cell_title = row[0].strip().lower()
        if cell_title == title.strip().lower():
            books_sheet.update_cell(i, 5, "Yes")

            print(f"'{title}' marked as owned.\n")
            return

    print(f"Title '{title}' not found in Books sheet.\n")


def mark_read(title):
    all_rows = books_sheet.get_all_values()

    for i, row in enumerate(all_rows[1:], start=2):
        cell_title = row[0].strip().lower()
        if cell_title == title.strip().lower():
            books_sheet.update_cell(i, 6, "Yes")
            print(f"'{title}' marked as read.\n")
            return

    print(f"Title '{title}' not found in Books sheet.\n")


def search_by_title():
    search_term = input("Enter a book title (or part of it): ").strip().lower()

    print("\nResults:")
    found = False

    rows = books_sheet.get_all_values()[1:]  # Skip header
    for idx, row in enumerate(rows, start=2):  # start=2 to account for header
        title = row[0].strip().lower()

        if search_term in title:
            found = True
            print(f"- {row[0]} by {row[1]}")

            choice = input(
                "\nWould you like to (L)og a note, mark as (O)wned, mark as (R)ead, (E)dit, or (S)kip? ").strip().lower()

            if choice == "l":
                log_note(row[0])

            elif choice == "o":
                mark_owned(row[0])

            elif choice == "r":
                mark_read(row[0])

            elif choice == "e":
                edit_book_at_row(idx + 1)

            elif choice == "s":
                print("Skipped.\n")
            else:
                print("Invalid choice.\n")

    if not found:
        print("No matches found")


def search_by_author():
    search_term = input(
        "Enter an author name (or part of it): ").strip().lower()

    rows = books_sheet.get_all_values()[1:]

    matching_books = []

    # start=2 to match spreadsheet row numbers
    for idx, row in enumerate(rows, start=2):
        author = row[1].strip().lower()
        if search_term in author:
            matching_books.append((idx, row))  # Store row number and row data

    if not matching_books:
        print("No books found by that author.\n")
        return

    print("\nBooks by matching author(s):")
    for i, (row_num, row) in enumerate(matching_books, start=1):
        print(f"{i}. {row[0]} by {row[1]}")

    selection = input(
        "\nSelect a book by number or press Enter to cancel: ").strip()
    if selection == "":
        print("Selection cancelled.\n")
        return

    try:

        selection = int(selection)
        if 1 <= selection <= len(matching_books):
            row_num, selected_row = matching_books[selection - 1]
            selected_title = selected_row[0]

            print(f"\nYou selected: {selected_title} by {selected_row[1]}")

            choice = input(

                "Would you like to (L)og a note, mark as (O)wned, mark as (R)ead, (E)dit, or (S)kip? ").strip().lower()

            if choice == "l":
                log_note(selected_title)

            elif choice == "o":
                mark_owned(selected_title)

            elif choice == "r":
                mark_read(selected_title)

            elif choice == "e":
                edit_book_at_row(row_num)

            elif choice == "s":
                print("Skipped.\n")

            else:
                print("Invalid choice.\n")

        else:
            print("Invalid selection.\n")

    except ValueError:
        print("Invalid input. Please enter a number.\n)")


def XXsearch_by_authorXX():
    search_term = input(
        "Enter an author name (or part of it): ").strip().lower()
    print("\nBooks by matching authos:")

    found = False
    for row in books_sheet.iter_rows(min_row=2, values_only=True):
        author = str(row[1]).lower()
        title = row[0]
        if search_term in author:
            found = True
            print(f"- {title} by {row[1]}")
    if not found:
        print("No matches found.")


def main_menu():
    print("--- Main Menu ---")
    print("\n-Search\n-Add\n-Quit")


def search_menu():
    print("--- Search Menu ---")
    print("\nAuthor (search by author)\nTitle (search by title)\nBack")

# -------------------------------------------


main_command = ""
filename = "book_notes.json"

if os.path.exists(filename):
    with open(filename, "r") as file:
        book_notes = json.load(file)

else:
    book_notes = {}


# -----------------MAIN BLOCK----------------

while main_command.strip().lower() != "quit":
    main_menu()
    main_command = input("> ")

    if main_command.strip().lower() == "search":

        while main_command.strip().lower() != "back":
            search_menu()
            main_command = input("> ")

            if main_command.strip().lower() == "title":
                search_by_title()

            elif main_command.strip().lower() == "author":
                search_by_author()
    elif main_command.strip().lower() == "add":
        add_book()

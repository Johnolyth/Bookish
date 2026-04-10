author_list = ["Toni Morrison", "bell hooks",
               "James Baldwin", "Octavia Butler", "Zora Neale Hurston"]

current_input = ""
while True:
    next_letter = input(f"Search (so far: '{current_input}'): ")

    if next_letter == "":
        break  # Exit on Enter with no new character

    current_input += next_letter
    matches = [a for a in author_list if current_input.lower() in a.lower()]

    print("\nMatches:")
    for match in matches:
        print(f"  - {match}")
    print("\n---")

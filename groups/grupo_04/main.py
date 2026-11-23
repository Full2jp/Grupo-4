"""
PhotoCensus - Group 04 (Module 2)
"""
import os
import sys
import json

# Lets this file find black_box.py in /kit (do not remove these lines)
GROUP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(GROUP_DIR, "..", "..", "kit"))
from black_box import *  # noqa: E402,F401,F403[cite: 2, 3]

REPORT_FILE = os.path.join(GROUP_DIR, "report.txt")

print("PhotoCensus - Group 04")

#Returns True if text is a number (int or float), else False
def number_check(text):
    cleaned = text.replace(",", ".").strip()
    if not cleaned:
        return False
    try:
        float(cleaned)
        return True
    except ValueError:
        return False

#Universal error handler for inputs
def read_input(
    prompt,
    kind="str",
    *,
    allowed=None,
    min_val=None,
    max_val=None,
    check_fn=None,
    error_msg="ERROR. Invalid input. Try again.",
    lowercase=False,
    block_numbers=True,
):
    while True:
        raw = input(prompt).strip()

#Int type
        if kind == "int":
            try:
                value = int(raw)
            except ValueError:
                print(error_msg)
                continue

#Float type
        elif kind == "float":
            try:
                value = float(raw.replace(",", "."))
            except ValueError:
                print(error_msg)
                continue

#String type
        elif kind == "str":
            value = raw.lower() if lowercase else raw
            if not value:
                print(error_msg)
                continue
            if block_numbers and number_check(value):
                print(error_msg)
                continue
        else:
            raise ValueError(f"Unsupported input kind: {kind}")

#Value range
        if allowed is not None and value not in allowed:
            print(error_msg)
            continue
        if min_val is not None and value < min_val:
            print(error_msg)
            continue
        if max_val is not None and value > max_val:
            print(error_msg)
            continue
        if check_fn is not None and not check_fn(value):
            print(error_msg)
            continue

        return value

#Folder's name input
def prompt_folder_name(label="Type the folder's name: "):
    while True:
        folder_name = read_input(
            label,
            kind="str",
            lowercase=True,
            error_msg="ERROR. Input a valid folder name",
        )
        if folder_exists(folder_name):
            return folder_name
        
#Specific handler for folder names
        print("\nERROR. Input a valid folder name.")
        back_prompt = read_input(
            "Show available folders? Type 'y' or 'n': ",
            kind="str",
            allowed=("y", "n"),
            lowercase=True,
            error_msg="ERROR. Type either 'y' or 'n'.",
        )
        if back_prompt == "y":
            print("\nHere are the available folders:")
            show_folders()

#Dictionary building, returns important information for all photos in all folders
def load_collection():
    collection = {}
    for folder in list_folders():
        for photo_path in list_photos(folder):
            collection[photo_path] = detect(photo_path)
    return collection

#Dictionary building and storing, restarts when the confidence value is changed
def filter_detections(detections, min_confidence):
    filtered = []
    for class_name, confidence in detections:
        if confidence >= min_confidence:
            filtered.append((class_name, confidence))
    return filtered

#Detects if a photo is on a folder, returns 'True', else 'False'
def photo_on_folder(photo_path, folder_name):
    normalized = photo_path.replace("\\", "/")
    parts = normalized.split("/")
    if len(parts) >= 2 and parts[-2].lower() == folder_name.lower():
        return True
    return False

#Builds the collection for all folders, or a chosen folder
def build_inventory(collection, min_confidence, folder_name=None):
    inventory = {}
    for photo_path, detections in collection.items():
        if folder_name is not None and not photo_on_folder(photo_path, folder_name):
            continue
        for class_name, _conf in filter_detections(detections, min_confidence):
            if class_name in inventory:
                inventory[class_name] += 1
            else:
                inventory[class_name] = 1
    return inventory

#Iventory ranking, returns a list of objects by their amount
def rank_inventory(inventory):
    ranked = []
    for class_name, amount in inventory.items():
        ranked.append((class_name, amount))
    length = len(ranked)
    for i in range(length):
        for j in range(0, length - i - 1):
            if ranked[j][1] < ranked[j + 1][1]:
                ranked[j], ranked[j + 1] = ranked[j + 1], ranked[j]
    return ranked

#Searches for a specific class in the collection, returns a file path to said class
def reverse_search(collection, min_confidence):
    reverse_index = {}
    for photo_path, detections in collection.items():
        filtered = filter_detections(detections, min_confidence)
        seen_in_photo = []
        for class_name, _conf in filtered:
            already_added = False
            for existing in seen_in_photo:
                if existing == class_name:
                    already_added = True
                    break
            if not already_added:
                seen_in_photo.append(class_name)
        for class_name in seen_in_photo:
            if class_name not in reverse_index:
                reverse_index[class_name] = []
            reverse_index[class_name].append(photo_path)
    return reverse_index

#Class counter, returns how many times said class appears
def count_class_in_photo(detections, class_name, min_confidence):
    target = class_name.strip().lower()
    total = 0
    for item_class, conf in filter_detections(detections, min_confidence):
        if item_class.lower() == target:
            total += 1
    return total

#Searches for each class present in a folder, returns which are present
def get_folder_class_set(collection, folder_name, min_confidence):
    class_set = set()
    for photo_path, detections in collection.items():
        if photo_on_folder(photo_path, folder_name):
            for class_name, _conf in filter_detections(detections, min_confidence):
                class_set.add(class_name)
    return class_set

#Searches for each class present in a collection, returns which are present
def collect_all_classes(collection, min_confidence):
    unique_classes = []
    for _photo_path, detections in collection.items():
        for class_name, _conf in filter_detections(detections, min_confidence):
            found = False
            for existing in unique_classes:
                if existing == class_name:
                    found = True
                    break
            if not found:
                unique_classes.append(class_name)
    number = len(unique_classes)
    for i in range(number):
        for j in range(0, number - i - 1):
            if unique_classes[j] > unique_classes[j + 1]:
                unique_classes[j], unique_classes[j + 1] = unique_classes[j + 1], unique_classes[j]
    return unique_classes

#Folder building. Folders are rows and classes are columns, returns a matrix of folders x classes
def build_folder_class_matrix(collection, min_confidence):
    folders = list_folders()
    classes = get_all_model_classes()
    matrix = []
    for folder in folders:
        row = []
        for cls_name in classes:
            count_in_folder = 0
            for photo_path, detections in collection.items():
                if photo_on_folder(photo_path, folder):
                    count_in_folder += count_class_in_photo(detections, cls_name, min_confidence)
            row.append(count_in_folder)
        matrix.append(row)
    return folders, classes, matrix

#Photo analysis, returns the main object and total of objects in a photo
def photo_analysis(collection, min_confidence):
    folder_name = prompt_folder_name("Type the folder's name: ")
    folder_photos = list_photos(folder_name)
    max_num = len(folder_photos)
    image_number = read_input(
        f"Select image number (1 to {max_num}): ",
        kind="int",
        min_val=1,
        max_val=max_num,
        error_msg=f"ERROR. Enter a number from 1 to {max_num}.",
    )
    image_path = folder_photos[image_number - 1]
    filtered = filter_detections(collection[image_path], min_confidence)
    best_obj = ""
    best_conf = 0.0
    total_objs = 0
    for class_name, conf in filtered:
        total_objs += 1
        if total_objs == 1 or conf > best_conf:
            best_obj = class_name
            best_conf = conf
    print("\n--- Image Report ---")
    print(f"Path: {image_path}")
    print(f"Total objects (>= {min_confidence:.2f}): {total_objs}")
    print(f"Main object: {best_obj if best_obj else 'None'} ({best_conf * 100:.1f}%)")

#Specific class search 
    search_choice = read_input(
        "\nSearch for a specific class in this photo? ('y' / 'n'): ",
        kind="str",
        allowed=("y", "n"),
        lowercase=True,
        error_msg="ERROR. Type 'y' or 'n'.",
    )
    if search_choice == "y":
        show_classes()
        cls_name = read_input(
            "Enter class name: ",
            kind="str",
            lowercase=True,
            error_msg="ERROR. Enter a valid class name (no numbers).",
        )
        qty = count_class_in_photo(collection[image_path], cls_name, min_confidence)
        print(f"Found {qty} occurrence(s) of '{cls_name}' in {image_path}.")

#Detailed folder report, stores total and average object count, empty photos, most and least objects on 2 images, and class search
def folder_report(collection, min_confidence):
    folder_name = prompt_folder_name("Type the folder's name for full analysis: ")
    show_classes()
    target_class = read_input(
        "Enter class name to track in this folder: ",
        kind="str",
        lowercase=True,
        error_msg="ERROR. Enter a valid class name (no numbers).",
    )
    folder_photos = []
    for photo_path, detections in collection.items():
        if photo_on_folder(photo_path, folder_name):
            folder_photos.append((photo_path, detections))
    total_photos_count = len(folder_photos)
    total_objects = 0
    empty_photos = 0
    max_count = 0
    min_count = 0
    max_photo = ""
    min_photo = ""
    photos_with_class = 0
    total_class_found = 0
    print(f"\n--- Analyzing folder '{folder_name}' ---")
    idx = 0
    for photo_path, detections in folder_photos:
        idx += 1
        count = 0
        for _cls, _conf in filter_detections(detections, min_confidence):
            count += 1
        total_objects += count
        if count == 0:
            empty_photos += 1
        if idx == 1:
            max_count = count
            min_count = count
            max_photo = photo_path
            min_photo = photo_path
        else:
            if count > max_count:
                max_count = count
                max_photo = photo_path
            if count < min_count:
                min_count = count
                min_photo = photo_path
        class_count = count_class_in_photo(detections, target_class, min_confidence)
        total_class_found += class_count
        if class_count > 0:
            photos_with_class += 1
        print(f"Photo {idx} ({os.path.basename(photo_path)}): {count} object(s)")
    avg_objects = total_objects / total_photos_count if total_photos_count > 0 else 0.0
    class_pct = (photos_with_class / total_photos_count) * 100 if total_photos_count > 0 else 0.0

#Printed report, returns total and average object count, empty photos, most and least objects on 2 images, and class search
    print("\n--- Folder Summary ---")
    print(f"Total objects: {total_objects}")
    print(f"Average per photo: {avg_objects:.2f}")
    print(f"Empty photos: {empty_photos}")
    print(f"Most objects: {max_photo} ({max_count})")
    print(f"Least objects: {min_photo} ({min_count})")
    print(
        f"Class '{target_class}': {photos_with_class}/{total_photos_count} photos "
        f"({class_pct:.1f}%), total occurrences: {total_class_found}"
    )
    print("\n--- Folder Bar Graph ---")
    bar_idx = 0
    for _photo_path, detections in folder_photos:
        bar_idx += 1
        count = 0
        for _cls, _conf in filter_detections(detections, min_confidence):
            count += 1
        bar = ""
        for _step in range(count):
            bar += "#"
        print(f"{folder_name}_{bar_idx:02d} | {bar} ({count})")

#Dictionary loading, grabs relevant information from other functions 
def dictionary(collection, min_confidence):
    filtered_total = 0
    for _photo_path, detections in collection.items():
        for _cls, _conf in filter_detections(detections, min_confidence):
            filtered_total += 1
    print(
        f"\n--- Filtered Detections (Current confidence = {min_confidence:.2f}) ---\n"
        f"Total filtered detections across collection: {filtered_total}"
    )

#General or specific folder report
    specific_folder_choice = read_input(
        "\nSee full object count for a specific folder? ('y' / 'n'): ",
        kind="str",
        allowed=("y", "n"),
        lowercase=True,
        error_msg="ERROR. Type 'y' or 'n'.",
    )
    if specific_folder_choice == "y":
        chosen_folder = prompt_folder_name("Enter the specific folder's name: ")
        folder_inv = build_inventory(collection, min_confidence, chosen_folder)
        folder_total = 0
        for _cls, qty in folder_inv.items():
            folder_total += qty
        print(f"Full object count in folder '{chosen_folder}': {folder_total}")
        for cls_name, qty in folder_inv.items():
            print(f"  - {cls_name}: {qty}")
    else:
        full_inv = build_inventory(collection, min_confidence)
        all_total = 0
        for _cls, qty in full_inv.items():
            all_total += qty
        print(f"Full object count across all folders: {all_total}")
        for cls_name, qty in full_inv.items():
            print(f"  - {cls_name}: {qty}")

#Ranking
    overall_inv = build_inventory(collection, min_confidence)
    ranked = rank_inventory(overall_inv)
    if ranked:
        top_n = read_input(
            f"\nHow many top ranked classes to show? (1 to {len(ranked)}): ",
            kind="int",
            min_val=1,
            max_val=len(ranked),
            error_msg=f"ERROR. Enter a number from 1 to {len(ranked)}.",
        )
        print(f"--- Top {top_n} Ranking ---")
        pos = 0
        for cls_name, amount in ranked:
            pos += 1
            if pos > top_n:
                break
            print(f"{pos}. {cls_name}: {amount}")
    else:
        print("\nReq 4 - No objects found to rank at current confidence.")

#Reverse class search
    class_search = read_input(
        "\nSearch for a specific class? ('y' / 'n'): ",
        kind="str",
        allowed=("y", "n"),
        lowercase=True,
        error_msg="ERROR. Type 'y' or 'n'.",
    )
    if class_search == "y":
        show_classes()
        query_class = read_input(
            "Type the class name from the list above: ",
            kind="str",
            lowercase=True,
            error_msg="ERROR. Enter a valid class name (no numbers).",
        )
        reverse_index = reverse_search(collection, min_confidence)
        if query_class not in reverse_index:
            print(f"Class '{query_class}' was not found at confidence equal or higher than {min_confidence:.2f}.")
        else:
            print(f"\n--- Reverse Search Results for '{query_class}' ---")
            for photo_path in reverse_index[query_class]:
                qty = count_class_in_photo(collection[photo_path], query_class, min_confidence)
                print(f"  - {photo_path}: {qty} occurrence(s)")

#Report.txt file
    print("\n--- Inventory and Ranking Report ---")
    report_choice = read_input(
        "Would you like to save and read report.txt, or not? ('y' / 'n'): ",
        kind="str",
        allowed=("y", "n"),
        lowercase=True,
        error_msg="ERROR. Type 'y' or 'n'.",
    )

#Saves the report file and asks the user if they'd want to read it on the console
    if report_choice == "y":
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(f"PhotoCensus Report (min_confidence = {min_confidence:.2f})\n")
            f.write("=== Inventory ===\n")
            for cls_name, amount in overall_inv.items():
                f.write(f"{cls_name}: {amount}\n")
            f.write("\n=== Ranking ===\n")
            r_pos = 0
            for cls_name, amount in ranked:
                r_pos += 1
                f.write(f"{r_pos}. {cls_name}: {amount}\n")
        print(f"Inventory and ranking saved to {REPORT_FILE}.")
        read_now = read_input(
            "\nWould you like to read the saved report.txt now? ('y' / 'n'): ",
            kind="str",
            allowed=("y", "n"),
            lowercase=True,
            error_msg="ERROR. Type either 'y' or 'n'.",
        )
        if read_now == "y":
            print(f"\n--- Reading {REPORT_FILE} ---")
            with open(REPORT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    print(line.rstrip("\n"))

#Compares 2 folders 
def folder_comparison(collection, min_confidence):
    print("Select first folder:")
    folder_a = prompt_folder_name("First folder name: ")
    print("Select second folder:")
    folder_b = prompt_folder_name("Second folder name: ")
    set_a = get_folder_class_set(collection, folder_a, min_confidence)
    set_b = get_folder_class_set(collection, folder_b, min_confidence)
    common = set_a & set_b
    only_a = set_a - set_b
    only_b = set_b - set_a
    union_all = set_a | set_b

#Result of comparison, returns classes that appear on both folders, classes that appear on only one, and the union of all classes
    print(f"\n--- Folder Set Comparison: '{folder_a}' vs '{folder_b}' ---")
    print(f"Common classes: {common if common else 'None'}")
    print(f"Exclusive to '{folder_a}': {only_a if only_a else 'None'}")
    print(f"Exclusive to '{folder_b}': {only_b if only_b else 'None'}")
    print(f"Union of classes: {union_all if union_all else 'None'}")

#Matrix printing
def print_folder_class_matrix(folders, classes, matrix, cols_per_block=8):
    if not classes:
        print("No detections found to build matrix.")
        return

#Defines the width
    first_width = 14
    for folder in folders:
        if len(folder) + 2 > first_width:
            first_width = len(folder) + 2
    cell_width = 6
    for cls_name in classes:
        if len(cls_name) + 2 > cell_width:
            cell_width = len(cls_name) + 2

#Row and column totals
    row_totals = []
    for r_idx in range(len(folders)):
        r_sum = 0
        for val in matrix[r_idx]:
            r_sum += val
        row_totals.append(r_sum)
    col_totals = []
    for _c in classes:
        col_totals.append(0)

#Records the highest folder-class combination
    best_value = 0
    best_folder = ""
    best_class = ""
    has_best = False
    r_idx = 0
    for folder in folders:
        c_idx = 0
        for val in matrix[r_idx]:
            col_totals[c_idx] += val
            if not has_best or val > best_value:
                best_value = val
                best_folder = folder
                best_class = classes[c_idx]
                has_best = True
            c_idx += 1
        r_idx += 1
    grand_total = 0
    for c_tot in col_totals:
        grand_total += c_tot 

#Prints relevant information. Folders x classes formatted as 6 folders of 8 classes per block
    print("\n--- Folder x Class Matrix ---")
    start_col = 0
    total_cols = len(classes)
    while start_col < total_cols:
        end_col = start_col + cols_per_block
        if end_col > total_cols:
            end_col = total_cols
        header = f"{'Folder':<{first_width}}"
        for idx in range(start_col, end_col):
            header += f"{classes[idx]:>{cell_width}}"
        header += f"{'Row Total':>{cell_width}}"
        line_sep = "-" * len(header)
        print(f"\n{header}")
        print(line_sep)
        r_i = 0
        for folder in folders:
            row_str = f"{folder:<{first_width}}"
            for c_i in range(start_col, end_col):
                row_str += f"{matrix[r_i][c_i]:>{cell_width}}"
            row_str += f"{row_totals[r_i]:>{cell_width}}"
            print(row_str)
            r_i += 1
        col_tot_str = f"{'Column Total':<{first_width}}"
        for c_i in range(start_col, end_col):
            col_tot_str += f"{col_totals[c_i]:>{cell_width}}"
        col_tot_str += f"{grand_total:>{cell_width}}"
        print(line_sep)
        print(col_tot_str)
        start_col = end_col
    if has_best:
        print(f"\nHighest folder-class combination: ({best_folder}, {best_class}) = {best_value}")

#Show_classes(), returns every class. Mainly used for matrix printing
def get_all_model_classes():
    classes_path = os.path.join(GROUP_DIR, "..", "..", "kit", "data", "classes.json")
    with open(classes_path, encoding="utf-8") as file:
        raw_classes = json.load(file)
    all_classes = []
    for item in raw_classes:
        name = str(item).strip().lower()
        if name:
            exists = False
            for existing in all_classes:
                if existing == name:
                    exists = True
                    break
            if not exists:
                all_classes.append(name)
    n = len(all_classes)
    for i in range(n):
        for j in range(0, n - i - 1):
            if all_classes[j] > all_classes[j + 1]:
                all_classes[j], all_classes[j + 1] = all_classes[j + 1], all_classes[j]
    return all_classes

#Matrix and histogram printing
def matrix_histogram(collection, min_confidence):
    folders, classes, matrix = build_folder_class_matrix(collection, min_confidence)
    print_folder_class_matrix(folders, classes, matrix)
    if not classes:
        return

#Histogram ranking
    inventory = build_inventory(collection, min_confidence)
    ranked = rank_inventory(inventory)
    print("\n--- Histogram (Ranking Order) ---")
    for cls_name, amount in ranked:
        bar = ""
        for _k in range(amount):
            bar += "#"
        print(f"{cls_name:<15} | {bar} ({amount})")

#Option menu for the program
def print_menu():
    print("\n0- Exit")
    print("1- View available folders, and how many images.")
    print("2- Select folder, and image number.")
    print("3- View a detailed folder's report")
    print("4- Set the system's trust configuration")
    print("5- Filtered detections, folder count, ranking, class search & text report")
    print("6- Compare two folders")
    print("7- Folder x Class matrix & ranking histogram")

#Program's main loop
def main():
    min_confidence = 0.5
    collection = load_collection()
    start_variable = -1
    while start_variable != 0:
        print("\n--- Program start ---")
        start_variable = read_input(
            "Type 1 to start the program. Type 0 to end it: ",
            kind="int",
            allowed=(0, 1),
            error_msg="ERROR. Type either 1 or 0.",
        )
        if start_variable == 0:
            exit()
        print_menu()
        option = read_input(
            "\nChoose your option: ",
            kind="int",
            min_val=0,
            max_val=7,
            error_msg="ERROR. Input a number from 0 to 7.",
        )

#Different paths
        print("\n")
        if option == 1:
            show_folders()
        elif option == 2:
            photo_analysis(collection, min_confidence)
        elif option == 3:
            folder_report(collection, min_confidence)
        elif option == 4:
            print("Now select the desired confidence for the system's recognition.")
            min_confidence = read_input(
                "Input a number from 0.0 to 1.0: ",
                kind="float",
                min_val=0.0,
                max_val=1.0,
                error_msg="ERROR. Please input a number from 0.0 to 1.0",
            )
        elif option == 5:
            dictionary(collection, min_confidence)
        elif option == 6:
            folder_comparison(collection, min_confidence)
        elif option == 7:
            matrix_histogram(collection, min_confidence)
        else:
            exit()
        


if __name__ == "__main__":
    main()

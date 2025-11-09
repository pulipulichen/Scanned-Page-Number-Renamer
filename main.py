import os

def rename_scanned_pages(directory="/pages"):
    """
    Reads image files from the specified directory, renames them by prepending
    an index number and an underscore, and prints the old and new filenames.
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' not found.")
        return

    # Get all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Filter for common image file extensions (you can extend this list)
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
    image_files = sorted([f for f in files if f.lower().endswith(image_extensions)])

    if not image_files:
        print(f"No image files found in '{directory}'.")
        return

    print(f"Renaming files in '{directory}':")
    for index, filename in enumerate(image_files):
        if filename.startswith('_'):
            print(f"Skipping '{filename}' as it already starts with an underscore.")
            continue

        # Create the new filename with a 4-digit index (e.g., _0001_filename.jpg)
        new_filename = f"_{index + 1:04d}_{filename}"
        old_filepath = os.path.join(directory, filename)
        new_filepath = os.path.join(directory, new_filename)

        try:
            os.rename(old_filepath, new_filepath)
            print(f"Renamed: '{filename}' -> '{new_filename}'")
        except OSError as e:
            print(f"Error renaming '{filename}': {e}")

if __name__ == "__main__":
    rename_scanned_pages()

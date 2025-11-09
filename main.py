import os
import time
from datetime import timedelta
from scripts.detect_page_number import detect_page_number

def rename_scanned_pages(directory="/pages"): # Changed default to "/pages" for consistency with common project structures
    """
    Reads image files from the specified directory, renames them by prepending
    an index number and an underscore, and prints the old and new filenames.
    Displays processing progress percentage and estimated completion time.
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

    total_files = len(image_files)
    processed_files = 0
    start_time = time.time()

    print(f"Renaming files in '{directory}':")
    for index, filename in enumerate(image_files):
        processed_files += 1

        # ==================
        
        # Calculate progress and estimated time
        elapsed_time = time.time() - start_time
        if processed_files > 0:
            files_per_second = processed_files / elapsed_time
            remaining_files = total_files - processed_files
            estimated_remaining_time = remaining_files / files_per_second
            eta = timedelta(seconds=int(estimated_remaining_time))
        else:
            eta = "N/A"

        progress_percentage = (processed_files / total_files) * 100
        print(f"Processing: {progress_percentage:.2f}% ({processed_files}/{total_files}) - ETA: {eta}")

        # ==================

        if filename.startswith('_'):
            print(f"Skipping '{filename}' as it already starts with an underscore.                                                                                             ")
            continue

        old_filepath = os.path.join(directory, filename)
        
        # Detect page number using the external script
        detected_page = detect_page_number(old_filepath)

        if detected_page.startswith("Error"):
            print(f"Error detecting page number for '{filename}': {detected_page}                                                                                             ")
            continue

        # Extract base name and extension
        name, ext = os.path.splitext(filename)

        # Create the new filename based on detected page number
        # Format: _{detected_page_number}_{original_filename_without_extension}.{extension}
        new_filename = f"_{detected_page}_{name}{ext}"
        new_filepath = os.path.join(directory, new_filename)

        try:
            os.rename(old_filepath, new_filepath)
            # print(f"Renamed: '{filename}' -> '{new_filename}'                                                                                                                  ")
        except OSError as e:
            print(f"Error renaming '{filename}': {e}                                                                                                                            ")
    print("\nProcessing complete.")

if __name__ == "__main__":
    rename_scanned_pages()

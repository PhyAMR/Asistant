import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def search_file_optimized(
    filename_pattern,
    format_pattern,
    root_directory=r"C:\Users\alvar",
    max_workers=10,
    batch_size=5,
):
    """
    Searches for files that match a specific filename pattern and format with optimized performance.

    Parameters:
    - filename_pattern: Regex pattern for the filename.
    - format_pattern: Regex pattern for the file format (e.g., r".*\.txt$").
    - root_directory: The directory to start the search from (default is root).
    - max_workers: The maximum number of threads to use.
    - batch_size: Number of directories processed per thread in each batch.

    Returns:
    - A list of file paths that match the filename pattern and format.
    """
    matches = []
    filename_regex = re.compile(filename_pattern)
    format_regex = re.compile(format_pattern)

    def search_in_directory_batch(directories):
        found_files = []
        for directory in directories:
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        if entry.is_file():
                            if format_regex.match(entry.name) and filename_regex.search(
                                entry.name
                            ):
                                found_files.append(entry.path)
                        elif entry.is_dir():
                            found_files.extend(search_in_directory_batch([entry.path]))
            except (PermissionError, FileNotFoundError):
                # Skip directories with restricted access
                pass
        return found_files

    # Prepare batches of directories to search in
    all_dirs = [
        os.path.join(root_directory, d)
        for d in os.listdir(root_directory)
        if os.path.isdir(os.path.join(root_directory, d))
    ]
    dir_batches = [
        all_dirs[i : i + batch_size] for i in range(0, len(all_dirs), batch_size)
    ]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(search_in_directory_batch, batch) for batch in dir_batches
        ]
        for future in as_completed(futures):
            result = future.result()
            if result:
                matches.extend(result)

    return matches


if __name__ == "__main__":
    # Example usage:
    # Search for .txt files with "report" in the filename
    result = search_file_optimized(
        filename_pattern="", format_pattern=r".*\.md$", root_directory=r"C:\Users\alvar"
    )

    print("Number of files found:", len(result))
    print("Files found:", result)

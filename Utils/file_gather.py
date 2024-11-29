import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

class FileSearcher:
    def __init__(self, root_directory=r"C:/Users/alvar/Documents/Cono", max_workers=10, batch_size=5):
        """
        Initializes the FileSearcher instance.

        Parameters:
        - root_directory: The directory to start the search from (default is root).
        - max_workers: The maximum number of threads to use.
        - batch_size: Number of directories processed per thread in each batch.
        """
        self.root_directory = root_directory
        self.max_workers = max_workers
        self.batch_size = batch_size

    def search_file_optimized(self, filename_pattern=" .*", format_pattern=" .*"):
        """
        Searches for files that match a specific filename pattern and format with optimized performance.

        Parameters:
        - filename_pattern: Regex pattern for the filename.
        - format_pattern: Regex pattern for the file format (e.g., r".*\.txt$").

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
                                if format_regex.match(entry.name) and filename_regex.search(entry.name):
                                    found_files.append(entry.path)
                            elif entry.is_dir():
                                found_files.extend(search_in_directory_batch([entry.path]))
                except (PermissionError, FileNotFoundError):
                    # Skip directories with restricted access
                    pass
            return found_files

        # Prepare batches of directories to search in
        all_dirs = [
            os.path.join(self.root_directory, d)
            for d in os.listdir(self.root_directory)
            if os.path.isdir(os.path.join(self.root_directory, d))
        ]
        dir_batches = [
            all_dirs[i: i + self.batch_size] for i in range(0, len(all_dirs), self.batch_size)
        ]

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
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
    file_searcher = FileSearcher(root_directory=r"C:/Users/alvar/")
    result = file_searcher.search_file_optimized(
        filename_pattern="jose", format_pattern=r".*\.*",
    )

    print("Number of files found:", len(result))
    print("Files found:", result)

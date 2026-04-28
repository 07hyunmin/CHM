import os
import shutil
import logging

class FileOrganizer:
    CATEGORIES = {
        'Documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.hwp', '.csv', '.rtf'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff'],
        'Videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
        'Executables': ['.exe', '.msi', '.bat', '.sh', '.cmd'],
        'Code': ['.py', '.js', '.html', '.css', '.cpp', '.c', '.java', '.json', '.xml', '.sql', '.php', '.go', '.ts'],
        'Others': []  # Catch-all
    }

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def organize(self, target_dir):
        if not os.path.isdir(target_dir):
            self.logger.error(f"Invalid directory: {target_dir}")
            return False

        files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
        
        if not files:
            self.logger.info("No files found to organize.")
            return True

        total_files = len(files)
        organized_count = 0

        for filename in files:
            file_path = os.path.join(target_dir, filename)
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            # Determine category
            category = 'Others'
            for cat, extensions in self.CATEGORIES.items():
                if ext in extensions:
                    category = cat
                    break

            # Create category folder
            category_dir = os.path.join(target_dir, category)
            if not os.path.exists(category_dir):
                try:
                    os.makedirs(category_dir)
                except Exception as e:
                    self.logger.error(f"Failed to create folder {category}: {e}")
                    continue

            # Move file
            dest_path = os.path.join(category_dir, filename)
            
            # Handle name collision
            if os.path.exists(dest_path):
                base, extension = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(category_dir, f"{base}_{counter}{extension}")):
                    counter += 1
                dest_path = os.path.join(category_dir, f"{base}_{counter}{extension}")

            try:
                shutil.move(file_path, dest_path)
                self.logger.info(f"Moved: {filename} -> {category}/")
                organized_count += 1
            except Exception as e:
                self.logger.error(f"Error moving {filename}: {e}")

        self.logger.info(f"Successfully organized {organized_count} out of {total_files} files.")
        return True

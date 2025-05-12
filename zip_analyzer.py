import os
import zipfile
import sqlite3
from pathlib import Path
import datetime

class ZipAnalyzer:
    def __init__(self, db_path='file_index.db'):
        self.db_path = db_path
        self.conn = self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE,
            filename TEXT,
            size INTEGER,
            modified TIMESTAMP
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS zip_contents (
            id INTEGER PRIMARY KEY,
            zip_id INTEGER,
            path_in_zip TEXT,
            size INTEGER,
            modified TIMESTAMP,
            FOREIGN KEY(zip_id) REFERENCES files(id)
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS potential_matches (
            id INTEGER PRIMARY KEY,
            zip_id INTEGER,
            extracted_path TEXT,
            confidence REAL,
            FOREIGN KEY(zip_id) REFERENCES files(id)
        )''')
        conn.commit()
        return conn

    def index_drive(self, root_path):
        c = self.conn.cursor()
        count = 0
        print(f"Indexing files from {root_path}...")
        for root, dirs, files in os.walk(root_path):
            for file in files:
                try:
                    full_path = os.path.join(root, file)
                    stats = os.stat(full_path)
                    c.execute("""
                    INSERT OR REPLACE INTO files (path, filename, size, modified)
                    VALUES (?, ?, ?, ?)
                    """, (full_path, file, stats.st_size,
                          datetime.datetime.fromtimestamp(stats.st_mtime)))
                    count += 1
                    if count % 1000 == 0:
                        self.conn.commit()
                        print(f"Indexed {count} files...")
                except (PermissionError, OSError) as e:
                    print(f"Error accessing {full_path}: {e}")
        self.conn.commit()
        print(f"Completed indexing {count} files.")

    def analyze_zip_files(self):
        c = self.conn.cursor()
        c.execute("SELECT id, path FROM files WHERE path LIKE '%.zip'")
        zip_files = c.fetchall()
        print(f"Found {len(zip_files)} ZIP files. Analyzing contents...")
        for zip_id, zip_path in zip_files:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    for info in zip_ref.infolist():
                        c.execute("""
                        INSERT INTO zip_contents (zip_id, path_in_zip, size, modified)
                        VALUES (?, ?, ?, ?)
                        """, (zip_id, info.filename, info.file_size,
                              datetime.datetime(*info.date_time)))
            except Exception as e:
                print(f"Error analyzing {zip_path}: {e}")
        self.conn.commit()
        print("ZIP analysis complete.")

    def find_potential_extractions(self):
        c = self.conn.cursor()
        c.execute("SELECT id, path FROM files WHERE path LIKE '%.zip'")
        zip_files = c.fetchall()
        for zip_id, zip_path in zip_files:
            zip_name = Path(zip_path).stem
            c.execute("SELECT path_in_zip FROM zip_contents WHERE zip_id = ?", (zip_id,))
            zip_contents = [item[0] for item in c.fetchall()]
            if not zip_contents:
                continue
            potential_dirs = self._find_matching_directories(zip_path, zip_name)
            for dir_path in potential_dirs:
                confidence = self._calculate_extraction_confidence(zip_contents, dir_path)
                if confidence > 0.7:
                    c.execute("""
                    INSERT INTO potential_matches (zip_id, extracted_path, confidence)
                    VALUES (?, ?, ?)
                    """, (zip_id, dir_path, confidence))
        self.conn.commit()

    def _find_matching_directories(self, zip_path, zip_name):
        # Placeholder: find directories with similar names or in common extraction locations
        candidates = []
        parent = str(Path(zip_path).parent)
        for entry in os.listdir(parent):
            full_entry = os.path.join(parent, entry)
            if os.path.isdir(full_entry) and zip_name in entry:
                candidates.append(full_entry)
        return candidates

    def _calculate_extraction_confidence(self, zip_contents, dir_path):
        # Placeholder: compare file names and count for a confidence score
        match_files = 0
        total_files = len(zip_contents)
        for file_in_zip in zip_contents:
            candidate_file = os.path.join(dir_path, file_in_zip)
            if os.path.exists(candidate_file):
                match_files += 1
        confidence = match_files / total_files if total_files else 0
        return confidence

    def get_redundant_zips(self, min_confidence=0.9):
        c = self.conn.cursor()
        c.execute("""
        SELECT f.path, pm.extracted_path, pm.confidence 
        FROM potential_matches pm
        JOIN files f ON pm.zip_id = f.id
        WHERE pm.confidence >= ?
        ORDER BY pm.confidence DESC
        """, (min_confidence,))
        return c.fetchall()

    def delete_redundant_zips(self, zip_paths):
        deleted = 0
        total_bytes = 0
        for path in zip_paths:
            try:
                size = os.path.getsize(path)
                os.remove(path)
                deleted += 1
                total_bytes += size
                print(f"Deleted: {path} ({size} bytes)")
            except Exception as e:
                print(f"Error deleting {path}: {e}")
        print(f"Deleted {deleted} files, freed {total_bytes/1024/1024:.2f} MB")

def main():
    analyzer = ZipAnalyzer()
    drive = input("Enter drive or folder to scan (e.g., C:\\): ")
    analyzer.index_drive(drive)
    analyzer.analyze_zip_files()
    analyzer.find_potential_extractions()
    redundant_zips = analyzer.get_redundant_zips()
    print(f"Found {len(redundant_zips)} potentially redundant ZIP files:")
    for zip_path, extracted_dir, confidence in redundant_zips:
        print(f"{zip_path} -> {extracted_dir} (Confidence: {confidence:.2f})")
    if redundant_zips:
        confirm = input("Delete all redundant ZIPs? (yes/no): ")
        if confirm.lower() == "yes":
            analyzer.delete_redundant_zips([z[0] for z in redundant_zips])

if __name__ == "__main__":
    main()
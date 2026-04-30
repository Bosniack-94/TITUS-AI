import os
import shutil

class FileTool:
    """
    TITUS Digital Sense: The File Handling Tool.
    Used by agents to interact with the file system.
    """
    
    @staticmethod
    def write_file(filename, content, overwrite=False):
        """Writes a file to the data/processed directory."""
        # Ensure we write to the correct data folder
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target_path = os.path.join(base_dir, "data", "processed", filename)
        
        if os.path.exists(target_path) and not overwrite:
            return {"status": "ERROR", "msg": f"File {filename} already exists. Set overwrite=True to replace."}
        
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "SUCCESS", "message": f"File {filename} written to data/processed", "path": target_path}
        except Exception as e:
            return {"status": "ERROR", "msg": str(e)}

    @staticmethod
    def read_file(filename):
        """Reads a file from the data/ directory."""
        # Check raw first, then processed
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_path = os.path.join(base_dir, "data", "raw", filename)
        proc_path = os.path.join(base_dir, "data", "processed", filename)
        
        target = raw_path if os.path.exists(raw_path) else proc_path if os.path.exists(proc_path) else None
        
        if not target:
            return {"status": "ERROR", "msg": f"File {filename} not found in the data/ directory."}
            
        try:
            with open(target, "r", encoding="utf-8") as f:
                return {"status": "SUCCESS", "content": f.read()}
        except Exception as e:
            return {"status": "ERROR", "msg": str(e)}

    @staticmethod
    def list_data():
        """Lists all files in raw and processed data folders."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_files = os.listdir(os.path.join(base_dir, "data", "raw"))
        proc_files = os.listdir(os.path.join(base_dir, "data", "processed"))
        return {"raw": raw_files, "processed": proc_files}

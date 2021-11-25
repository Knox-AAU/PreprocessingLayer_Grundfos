import os
import ghostscript
import platform
from config_data import config
from shutil import copyfile, move

def run_ghostscript(filepath: str):
    if filepath.endswith(".pdf"):
        try:
            copyfile(filepath, os.path.join(filepath + "(gs)"))
            ar = ["-dQUIET", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/prepress", "-sOutputFile=" + os.path.join(filepath), os.path.join(filepath + "(gs)")]
            gs = ghostscript.Ghostscript(*ar)
            del gs
            os.remove(os.path.join(filepath + "(gs)"))
        except:
            #warn.warn("Corruptness caught by GhostScript", RuntimeWarning)
            print("Corruptness caught by GhostScript.")
            if str(platform.system()).upper() == "WINDOWS":
                return False
            else:
                print("Moved file to the invalid folder.")
                move(filepath, config["INVALID_INPUT_FOLDER"])
                return False

    return True

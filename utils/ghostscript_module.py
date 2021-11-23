import os
import ghostscript
import platform
from shutil import copyfile

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
                return True
            else:
                print("Moved file to the invalid folder.")
                shutil.move(in_dir + "/" + file, config["INVALID_INPUT_FOLDER"])
                return True

    return False
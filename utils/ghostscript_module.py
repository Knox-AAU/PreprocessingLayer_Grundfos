import os
import ghostscript
import platform
from shutil import copyfile

def run_ghostscript(filepath: str):
    invalid_files = []

    for file in os.listdir(filepath):
        if file.endswith(".pdf"):
            try:
                copyfile(os.path.join(filepath, file), os.path.join(filepath, file + "(gs)"))
                ar = ["-dQUIET", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/prepress", "-sOutputFile=" + os.path.join(filepath, file), os.path.join(filepath, file + "(gs)")]
                gs = ghostscript.Ghostscript(*ar)
                del gs
                os.remove(os.path.join(filepath, file + "(gs)"))
            except:
                #warn.warn("Corruptness caught by GhostScript", RuntimeWarning)
                print("Corruptness caught by GhostScript.")
                if str(platform.system()).upper() == "WINDOWS":
                    print("Added file to list for later removal.")
                    invalid_files.append(os.path.join(filepath, file))
                    try:
                        files.remove(os.path.join(filepath, file))
                    except:
                        pass
                else:
                    print("Moved file to the invalid folder.")
                    shutil.move(in_dir + "/" + file, config["INVALID_INPUT_FOLDER"])

    return invalid_files
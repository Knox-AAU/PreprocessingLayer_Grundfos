import os
import ghostscript
import platform

def run_ghostscript(filepath: str):
    invalid_files = []

    for file in os.listdir(filepath):
        if file.endswith(".pdf"):
            try:
                if str(platform.system()).upper() == "WINDOWS":
                    os.chmod(os.path.join(filepath, file), 0o775)
                ar = ["-sDEVICE=pdfwrite", "-dPDFSETTINGS=/prepress", "-dQUIET", "-dBATCH", "-dNOPAUSE",
                      "-dPDFSETTINGS=/printer", "-sOutputFile=" + os.path.join(filepath, file), "-f", os.path.join(filepath, file)]
                ghostscript.Ghostscript(*ar)
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
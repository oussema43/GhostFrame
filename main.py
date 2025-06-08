from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from rembg import remove
from PIL import Image
import sys
import os
import zipfile
from datetime import datetime

input_paths = []  # Now stores multiple input paths
output_dir = ""

def remove_background(input_path, output_path):
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    output_image.save(output_path)

def Btinput_click():
    global input_paths
    files, _ = QFileDialog.getOpenFileNames(None, "Select Images", "", "Image Files (*.png *.jpg *.jpeg)")
    if files:
        input_paths = files
        file_list = "\n".join([os.path.basename(f) for f in files[:3]])  # Show first 3 filenames
        if len(files) > 3:
            file_list += f"\n...and {len(files)-3} more"
        windows.Inpu.setText(f"Selected {len(files)} images:\n{file_list}")

def Btoutput_click():
    global output_dir
    output_dir = QFileDialog.getExistingDirectory(None, "Select Output Folder")
    if output_dir:
        windows.Output.setText(f"Output Folder: {output_dir}")

def mgrl_click():
    if not input_paths or not output_dir:
        QMessageBox.warning(None, "Missing Paths", "Please select both input files and output folder.")
        return
    
    processed_files = []
    error_files = []
    
    for input_path in input_paths:
        try:
            # Generate output filename
            input_filename = os.path.basename(input_path)
            name, ext = os.path.splitext(input_filename)
            output_filename = f"{name}_no_bg.png"
            output_path = os.path.join(output_dir, output_filename)
            
            # Process the image
            remove_background(input_path, output_path)
            processed_files.append(output_path)
        except Exception as e:
            error_files.append((os.path.basename(input_path), str(e)))
    
    # Create ZIP if multiple files were processed
    if len(processed_files) > 1:
        zip_filename = os.path.join(output_dir, f"no_bg_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in processed_files:
                zipf.write(file, os.path.basename(file))
                os.remove(file)  # Remove individual files after adding to ZIP
        
        # Update processed files list to point to the ZIP
        processed_files = [zip_filename]
    
    # Prepare result message
    message = []
    if processed_files:
        if len(processed_files) == 1:
            message.append(f"Successfully processed {len(input_paths)} image(s) and saved to:")
            message.append(processed_files[0])
        else:
            message.append(f"Successfully processed {len(processed_files)} images.")
    
    if error_files:
        message.append("\nFailed to process:")
        for filename, error in error_files:
            message.append(f"{filename}: {error}")
    
    if message:
        QMessageBox.information(None, "Processing Complete", "\n".join(message))

app = QApplication(sys.argv)
windows = loadUi("gui.ui")
app.setWindowIcon(QIcon("icon.png")) 
windows.show()
windows.Btinput.clicked.connect(Btinput_click)
windows.Btoutput.clicked.connect(Btoutput_click)
windows.mgrl.clicked.connect(mgrl_click)
app.exec_()
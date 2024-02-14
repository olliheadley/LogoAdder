from PIL import Image
import tkinter as tk
from tkinter import filedialog

def merge_images(main_image_path, logo_path):
    main_image = Image.open(main_image_path)
    logo = Image.open(logo_path)

    # Calculate the new height of the logo based on a percentage of the main image's height
    main_image_height = main_image.size[1]
    logo_new_height = int(main_image_height * 0.2)
    logo_aspect_ratio = logo.width / logo.height
    logo_new_width = int(logo_new_height * logo_aspect_ratio)

    # Resize the logo
    logo = logo.resize((logo_new_width, logo_new_height))

    # Check if the logo has transparency
    if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
        # If the logo has transparency, add the transparent logo to the main image
        main_image.paste(logo, (0, 0), logo)
    else:
        # If the logo does not have transparency, add the logo as it is
        main_image.paste(logo, (0, 0))

    main_image.show()

def select_images():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    main_image_path = filedialog.askopenfilename(title="Select Main Image",
                                                 filetypes=[("Image Files", (".jpg", ".jpeg", ".png"))])
    logo_path = filedialog.askopenfilename(title="Select Logo", filetypes=[("Image Files", (".jpg", ".jpeg", ".png"))])
    merge_images(main_image_path, logo_path)

select_images()

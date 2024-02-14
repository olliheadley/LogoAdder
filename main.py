import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os


def merge_images(main_image_path, logo_path, logo, width_input, height_input):
    main_image = Image.open(main_image_path)

    if height_input and width_input:
        try:
            width = int(width_input)
            height = int(height_input)
            main_image = main_image.resize((width, height))
        except ValueError:
            print("Invalid input: Please enter valid integers for width and height")
    elif width_input:
        try:
            width = int(width_input)
            main_image = resize_with_aspect_ratio(main_image_path, width)
        except ValueError:
            print("Invalid input: Please enter a valid integer for the width")

    # Calculate the new height of the logo based on a percentage of the main image's height
    main_image_height = main_image.size[1]
    logo_new_height = int(main_image_height * 0.2)  # Adjust the percentage as needed
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

    # Convert the image to RGB mode before saving it as a JPEG
    main_image = main_image.convert('RGB')

    file_name = os.path.splitext(os.path.split(main_image_path)[-1])[0]
    main_name = file_name + "+Wasserzeichen"
    save_path = filedialog.asksaveasfilename(initialfile=main_name, defaultextension=".png")

    if save_path:
        main_image.save(save_path)
        print(f"Logo saved as {save_path}")

    main_image.save("merged_image.jpg", quality=95)  # Save the merged image

    return main_image


def save_logo(logo, logo_path):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    logo_name = os.path.split(logo_path)[-1]  # Extract the filename from the logo path


def resize_with_aspect_ratio(image_path, new_width):
    img = Image.open(image_path)
    width_percent = (new_width / float(img.size[0]))
    new_height = int((float(img.size[1]) * float(width_percent)))
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    return resized_img


def select_images():
    root = tk.Tk()
    root.title("Add Logo to Images")
    root.geometry("500x500")

    # Create a label for the logo preview
    logo_preview_label = tk.Label(root, text="Logo Preview")
    logo_preview_label.pack()

    # Create a label for the main image preview
    main_image_preview_label = tk.Label(root, text="Main Image Preview")
    main_image_preview_label.pack()

    # Create a function to update the logo preview
    def update_logo_preview(logo_path):
        logo = Image.open(logo_path)
        new_width = int(logo.width * 0.5)
        new_height = int(logo.height * 0.5)
        logo = logo.resize((new_width, new_height), Image.LANCZOS)
        logo_preview = ImageTk.PhotoImage(logo)
        logo_preview_label.configure(image=logo_preview)
        logo_preview_label.image = logo_preview

        return logo

    # Create a function to update the main image preview
    def update_main_image_preview(main_image_path):
        main_image = Image.open(main_image_path)
        new_width = int(main_image.width * 0.5)
        new_height = int(main_image.height * 0.5)
        main_image = main_image.resize((new_width, new_height), Image.LANCZOS)
        main_image_preview = ImageTk.PhotoImage(main_image)
        main_image_preview_label.configure(image=main_image_preview)
        main_image_preview_label.image = main_image_preview

        return main_image

    # Create a function to add the logo to the main image
    def add_logo_to_image(main_image_path, logo_path, logo):
        merged_image = merge_images(main_image_path, logo_path, logo, width_input.get(), height_input.get())

        # Update the main image preview
        update_main_image_preview(main_image_path)

        return merged_image

    # Create a function to select the logo and main image
    def select_logo_and_main_image():
        logo_path = filedialog.askopenfilename(title="Select Logo",
                                               filetypes=[("Image Files", (".jpg", ".jpeg", ".png"))])
        logo = update_logo_preview(logo_path)

        main_image_path = filedialog.askopenfilename(title="Select Main Image",
                                                     filetypes=[("Image Files", (".jpg", ".jpeg", ".png"))])
        main_image = update_main_image_preview(main_image_path)

        # Add the logo to the main image
        merged_image = add_logo_to_image(main_image_path, logo_path, logo)

        # Create a button to add the logo to every other image
        def add_logo_to_every_other_image():
            while True:
                main_image_path = filedialog.askopenfilename(title="Select Main Image",
                                                             filetypes=[("Image Files", (".jpg", ".jpeg", ".png"))])
                if not main_image_path:
                    break

                # Add the logo to the main image
                merged_image = add_logo_to_image(main_image_path, logo_path, logo)

        add_logo_to_every_other_image_button = tk.Button(root, text="Add Logo to Every Other Image",
                                                         command=add_logo_to_every_other_image)
        add_logo_to_every_other_image_button.pack()

    # Create a button to select the logo and main image
    select_logo_and_main_image_button = tk.Button(root, text="Select Logo and Main Image",
                                                  command=select_logo_and_main_image)
    select_logo_and_main_image_button.pack()

    # Create a button to quit the program
    width_label = tk.Label(root, text="Width: ")
    width_label.pack()
    width_input = tk.Entry(root)
    width_input.pack()
    print(width_input.pack())

    height_label = tk.Label(root, text="Height: ")
    height_label.pack()
    height_input = tk.Entry(root)
    height_input.pack()
    print(height_input.pack())
    quit_button = tk.Button(root, text="Quit", command=root.quit)
    quit_button.pack()

    root.mainloop()


select_images()

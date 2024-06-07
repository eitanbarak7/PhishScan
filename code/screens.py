import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
from itertools import cycle


def display_image_fullscreen(image_path, on_button_click):
    """
    Display an image in fullscreen mode with a button.

    Args:
        image_path (str): The path to the image file.
        on_button_click (function): The function to call when the button is clicked.
    """
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda e: root.quit())

    # Load and resize the image to fit the screen
    img = Image.open(image_path)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    img = img.resize((screen_width, screen_height), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)

    # Create a Label to display the image
    label = tk.Label(root, image=img)
    label.pack(fill='both', expand=True)

    # Create a Button with a wider size and custom font
    button = tk.Button(root, text="הצג את תיבת הדואר האלקטרוני", bg="white", fg="blue",
                       font=("Assistant Bold", 40), width=32, height=1, command=lambda: on_button_click(root))
    button.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

    # Create the "X" button in the top left corner
    x_button = tk.Button(root, text="X", bg="white", fg="red", font=("Arial", 20), command=root.quit, bd=0)
    x_button.place(x=10, y=10, width=40, height=40)

    # Start the Tkinter event loop
    root.mainloop()


def start_loading_screen(queue):
    """
    Display a loading screen with a progress bar.

    Args:
        queue (Queue): A queue used to signal when loading is complete.
    """
    print("Loading screen started")

    loading_root = tk.Tk()
    loading_root.title("Loading...")

    # Get the screen width and height
    screen_width = loading_root.winfo_screenwidth()
    screen_height = loading_root.winfo_screenheight()

    # Define the width and height of the loading window
    window_width = 600
    window_height = 400

    # Calculate the position to center the window
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)

    # Set the geometry of the loading window to be centered
    loading_root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    loading_root.configure(bg="#0d1b2a")

    try:
        loading_root.option_add("*Font", "Assistant 20 bold")
    except tk.TclError:
        loading_root.option_add("*Font", "Helvetica 20 bold")

    label = tk.Label(loading_root, text="Loading...", fg="#01d28e", bg="#0d1b2a")
    label.pack(pady=100)

    progress_bar = ttk.Progressbar(loading_root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=20)
    progress_bar.configure(style="blue.Horizontal.TProgressbar")

    loading_text = ["|", "/", "-", "\\"]
    loading_cycle = cycle(loading_text)

    def update_progress():
        """
        Update the progress bar and loading text.
        """
        try:
            if not queue.empty():
                queue.get_nowait()
                loading_root.destroy()
                print("Loading complete, closing loading screen")
            else:
                progress_bar.step(5)
                label.config(text=f"Loading... {next(loading_cycle)}")
                loading_root.after(100, update_progress)
        except Exception as e:
            print(f"Error updating progress: {e}")

    loading_root.after(100, update_progress)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("blue.Horizontal.TProgressbar", troughcolor="#0d1b2a", background="#01d28e", thickness=20)

    loading_root.mainloop()

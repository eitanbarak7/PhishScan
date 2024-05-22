import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
from itertools import cycle


def display_image_fullscreen(image_path):
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda e: root.quit())

    # Load the image
    img = Image.open(image_path)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Resize the image to fit the screen
    img = img.resize((screen_width, screen_height), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)

    # Create a Label to display the image
    label = tk.Label(root, image=img)
    label.pack(fill='both', expand=True)

    # Create a Button with a wider size and custom font
    button = tk.Button(root, text="הצג את תיבת הדואר האלקטרוני", bg="white", fg="blue", font=("Assistant Bold", 40), width=32, height=1)

    # Position the button in the bottom third of the screen
    button.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

    # Create the "X" button in the top left corner
    x_button = tk.Button(root, text="X", bg="white", fg="red", font=("Arial", 20), command=root.quit, bd=0)
    x_button.place(x=10, y=10, width=40, height=40)

    # Start the Tkinter event loop
    root.mainloop()


def start_loading_screen():
    root = tk.Tk()
    root.title("Loading...")
    root.geometry("600x400")
    root.configure(bg="#0d1b2a")

    # Load custom font if available
    try:
        root.option_add("*Font", "Assistant 20 bold")
    except tk.TclError:
        root.option_add("*Font", "Helvetica 20 bold")

    # Create a label with cyber-style text
    label = tk.Label(root, text="Loading...", fg="#01d28e", bg="#0d1b2a")
    label.pack(pady=100)

    # Create a progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=20)
    progress_bar.configure(style="blue.Horizontal.TProgressbar")

    # Add a loading animation
    loading_text = ["|", "/", "-", "\\"]
    loading_cycle = cycle(loading_text)

    def update_progress():
        progress_bar.step(5)
        label.config(text=f"Loading... {next(loading_cycle)}")
        if progress_bar['value'] < 100:
            root.after(100, update_progress)
        else:
            root.quit()

    # Start the loading animation
    root.after(100, update_progress)

    # Style the progress bar
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("blue.Horizontal.TProgressbar", troughcolor="#0d1b2a", background="#01d28e", thickness=20)

    # Start the Tkinter event loop
    root.mainloop()

# Example usage
start_loading_screen()



# Example usage
display_image_fullscreen(r'C:\Users\Eitan\PycharmProjects\email\screens\welcome.png')

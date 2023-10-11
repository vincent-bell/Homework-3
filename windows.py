from tkinter import Tk, Toplevel, Canvas, PhotoImage, Button, Entry
from io import BytesIO
from typing import Tuple
from PIL import Image, ImageTk, ImageEnhance


class Window(Tk):
    def __init__(self, title: str, width: int, height: int, resizable: bool = True):
        """
        Class for making displaying tkinter windows nice and simple.
        Methods use absolute positions (x, y) to draw to the window.

        Arguments:
            title (str): The title of the window
            width (int): The width of the window in pixels
            height (int): The height of the window in pixels
            resizable (bool): Static or dynamic resolution
        """
        super().__init__()

        # Set standard window attributes
        self.title(title)
        self.width = width
        self.height = height
        if not resizable:
            self.resizable(False, False)

        # Set up a canvas and pack it into the window
        self.canvas = Canvas(master=self, width=self.width, height=self.height,
                             bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()

        # For drawing images
        self.images = []
        self.iidx = 0

    @staticmethod
    def __load_image(path: str, width: int, height: int, format: str = 'png', *,
                     darken: bool = False):
        original_img = Image.open(path)
        resized_img = original_img.resize((width, height), Image.Resampling.LANCZOS)
        if darken: resized_img = ImageEnhance.Brightness(resized_img).enhance(0.9)

        # Use a buffer to avoid making new files
        buffer = BytesIO()
        resized_img.save(buffer, format=format, quality=100)
        return buffer.getvalue(), format

    def set_icon_image(self, path: str):
        """Set the icon image of the window."""
        img, fmt = self.__load_image(path, 256, 256, 'ico')
        self.icon = ImageTk.PhotoImage(data=img, format=fmt)
        self.wm_iconphoto(False, self.icon)

    def set_background_image(self, path: str, darken: bool = False):
        """Set the background image of the window."""
        img, fmt = self.__load_image(path, self.width, self.height, 'png', darken=darken)
        self.background = PhotoImage(data=img, format=fmt)
        self.canvas.create_image(self.width/2, self.height/2, image=self.background)

    def draw_image(self, path: str, width: int, height: int, position: Tuple[int, int]):
        """Draw an image to the window using absolute position."""
        img, fmt = self.__load_image(path, self.width, self.height, 'png')
        image = PhotoImage(data=img, format=fmt)
        self.images.append(image)
        self.canvas.create_image(position[0], position[1], image=self.images[self.iidx])
        self.iidx += 1

    def draw_text(self, position: Tuple[int, int], text, *, font='TkDefaultFont 15',
                  font_colour='black'):
        """Draw text to the window using absolute position."""
        return self.canvas.create_text(position[0], position[1], text=text, font=font,
                                       fill=font_colour)

    def draw_entry_box(self, position: Tuple[int, int], ebx_width: int, ebx_height: int):
        """Draw an entry box to the window using absolute position."""
        entry = Entry(self.canvas, bd=0, bg="#dfdfdf", highlightthickness=0)
        entry.place(x=position[0], y=position[1], width=ebx_width, height=ebx_height)
        return entry

    def draw_image_button(self, position: Tuple[int, int], btn_width: int, btn_height: int,
                          image_path: str, callback: any = None):
        """Draw a button with an image to the window using absolute position."""
        img, fmt = self.__load_image(image_path, btn_width, btn_height, 'png')
        image = PhotoImage(data=img, format=fmt)
        self.images.append(image)
        button = Button(self.canvas, image=self.images[self.iidx], borderwidth=0,
                        highlightthickness=0, command=callback, relief='flat')
        button.place(x=position[0], y=position[1], width=btn_width, height=btn_height)
        self.iidx += 1
        return button

    def show(self):
        """Start the event loop."""
        self.mainloop()


class WindowChild(Toplevel, Window):
    def __init__(self, master: any, title: str, width: int, height: int, resizable: bool = True):
        """
        Class for making children of ~Window~.

        Arguments:
            ...
        """
        Toplevel.__init__(self, master)
        self.title(title)
        self.width = width
        self.height = height
        if not resizable:
            self.resizable(False, False)

        self.canvas = Canvas(master=self, width=self.width, height=self.height,
                             bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()

        self.images = []
        self.iidx = 0

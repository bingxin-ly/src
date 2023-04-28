from logging import *
from io import BytesIO
from time import strftime
from hashlib import sha256
from log import setup_logger
from json import dumps, loads

# 网络连接控件
from socket import *
from threading import Thread

# 图形化控件
from tkinter import *
from tkinter import simpledialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageGrab

_buf = 1024
_length = 70
_encoding = 'GBK'
images = {}


class Zoom(Toplevel):
    def __init__(self, img: Image.Image) -> None:
        super().__init__()
        self.img = ImageTk.PhotoImage(img)
        self.create_widgets(*img.size)

    def create_widgets(self, ww, wh):
        Label(self, image=self.img).pack()
        print(self.winfo_height(), self.winfo_depth())
        ww += 20
        self.geometry('+%d+%d' % ((root.winfo_screenwidth() - ww) / 2,
                                  (root.winfo_screenheight() - wh) / 2))


class ATPWindow(Frame):
    def __init__(self, master, nick):
        super().__init__(master)
        self.master = master
        self.pack()
        self.nick = nick
        self.image = None
        self.create_widgets()

    def create_widgets(self):
        self.text = scrolledtext.ScrolledText(
            root, font=('黑体', 11), width=70, height=20)
        self.text.bind('<Key>', lambda _: 'break')
        self.text.pack()

        self.entry = Text(root, font=('黑体', 11), width=60, height=4)
        self.entry.bind('<Key-Return>', self.ready)
        self.entry.bind('<Control-v>', self.show)
        self.entry.pack(side=LEFT, padx=15)
        self.entry.focus_force()

        Button(root, text='发送', width=6, height=1,
               command=self.ready).pack(side=LEFT, padx=20)

    def ready(self, _=None):
        if self.image != None:
            send(self.image, 'img')
            self.image = None
        else:
            send(self.entry.get(1.0, END), 'str')

        self.entry.delete('1.0', END)
        return 'break'

    def show(self, _):
        global photo
        try:
            content = ImageGrab.grabclipboard()
        except OSError:
            return
        if isinstance(content, Image.Image):
            self.image = content.convert('RGB')
            x, y = self.image.size
            photo = ImageTk.PhotoImage(self.image.resize((60 * x // y, 60)))
            self.entry.image_create(END, image=photo)

    def print(self, type, sender, data):
        self.text.insert(END, '[{}]\n[{}]: '.format
                         (strftime('%H:%M:%S'), sender))

        if type == 'img':
            image = Image.open(BytesIO(data))
            x, y = image.size
            sized_image = ImageTk.PhotoImage(image.resize((60 * x // y, 60)))

            self.text.mark_set(INSERT, END)
            pos = self.text.index(INSERT)
            images[pos] = (sized_image, image)

            self.text.image_create(END, image=sized_image)
            self.text.tag_add(f'{pos}', pos)
            self.text.tag_bind(f'{pos}', '<Double-Button-1>',
                               lambda _: Zoom(images[pos][1]))
            self.text.insert(END, '\n')

        else:
            self.text.insert(END, data.decode(_encoding))
        self.text.insert(END, '\n')
        self.text.see(END)


def send(msg, type: str):
    if type == 'str':
        data = msg.encode(_encoding)
    else:
        io = BytesIO()
        msg.save(io, 'jpeg')
        data = io.getvalue()
    ''' 我们使用三个属性来描述数据: type: str, sender: str, size: uint32 '''
    head = dumps({
        'type': type,
        'sender': app.nick,
        'size': len(data)
    }, ensure_ascii=False)
    if len(head.encode(_encoding)) > _length:
        messagebox.showerror('你发送的消息实在太多了')
    else:
        head += ' ' * (_length - len(head.encode(_encoding)))
        sock.sendall(head.encode(_encoding))
        sock.sendall(data)


def recv():
    while True:
        ''' 我们使用三个属性来描述数据: type: str, sender: str, size: uint32 '''
        head = loads(sock.recv(_length).decode(_encoding))
        data = b''
        while len(data) < head['size']:
            data += sock.recv(_buf)
        app.print(head['type'], head['sender'], data)


def access():
    global sock
    HOST, PORT = '192.168.6.205', 12332
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((HOST, PORT))


def display():
    global root, app
    root = Tk()
    root.title('chatATP')
    ww = 610
    wh = 400
    root.geometry('%dx%d+%d+%d' %
                  (ww, wh, (root.winfo_screenwidth() - ww) / 2,
                   (root.winfo_screenheight() - wh) / 2))


def verify():
    with open(__file__, 'rb') as f:
        data = f.read()
    version = sha256(data).hexdigest()
    sock.sendall((version + ' ' * (_length - len(version))).encode(_encoding))
    response = loads(sock.recv(_length).decode(_encoding))
    if not response['res']:
        messagebox.showwarning('错误', '你的chatATP版本错误，请检查！')
        exit()


def ask_nick():
    while True:
        nick = simpledialog.askstring('', prompt='请输入使用的昵称：').lower()
        if len(nick.encode(_encoding)) > 20:
            messagebox.showwarning('错误', '昵称太长了，太大了')
            continue
        nick += ' ' * (20 - len(nick.encode(_encoding)))
        sock.sendall(nick.encode(_encoding))

        response = loads(sock.recv(_length).decode(_encoding))
        if (response['res'] != 'ok'):
            messagebox.showwarning('错误', response['reason'])
            continue
        return nick.strip()


if __name__ == '__main__':
    logger = setup_logger()
    display()
    access()
    verify()
    app = ATPWindow(root, ask_nick())

    revctask = Thread(target=recv)
    revctask.daemon = True
    revctask.start()

    root.mainloop()

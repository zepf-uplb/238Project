from tkinter import *
from threading import Timer

class Window:
	def __init__(self, master, peer):
		self.master = master
		self.peer = peer

		self.frame = Frame(master, width=600, height=600)
		self.frame.pack(fill="both", expand=True)
		self.frame.grid_propagate(False)
		self.frame.grid_rowconfigure(0, weight=1)
		self.frame.grid_columnconfigure(0, weight=1)		

		self.text = Text(self.frame, relief="sunken")
		self.text.grid(row = 0, column = 0, sticky="nsew")
		self.text.config(state=DISABLED)

		self.scrollbar = Scrollbar(self.frame, command=self.text.yview)
		self.text["yscrollcommand"] = self.scrollbar.set
		self.scrollbar.grid(row = 0, column = 1, sticky="nsew")

		self.entry = Entry(self.frame)
		self.entry.bind("<Key>", self.onKeyPress)
		self.entry.grid(row = 1, column = 0, sticky="nsew")

		self.button = Button(self.frame, text="Send", command=self.sendMessage)
		self.button.grid(row = 1, column = 1, sticky="nsew")

	def recvMessage(self, msg):
		self.text.config(state=NORMAL)
		self.text.insert(END, msg+"\n")
		self.text.config(state=DISABLED)
		self.text.see("end")

	def onKeyPress(self, key):
		if key.keycode == 36:
			if self.peer.gameFace:
				message = self.entry.get()
				if message in self.peer.word_list:
					if self.peer.word_list[message]:						
						self.recvMessage(message + " already taken")
					else:
						self.peer.sendMessage("CHECK_WORD!", message)
						Timer(0.2, lambda arg=message: self.peer.giveVerdict(arg)).start()
				else:
					self.recvMessage(message + " rejected")

			self.entry.delete(0, len(self.entry.get()))

	#does really nothing as of now
	def sendMessage(self):
		message = self.entry.get() + "\n"
		self.entry.delete(0, len(self.entry.get()))



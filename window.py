from tkinter import *
from threading import Timer

class Window:
	def __init__(self, master, peer):
		self.master = master
		self.peer = peer
		self.colours = ['abcdefgh','green','orange','white','yellow',
						'blue','orange','edadefgh','yellow','blue',
						'blue','orange','white','yellow','opidefgh']	#sample list to populate the board
		self.mainColor = "#4682B4"	# main theme
		
		self.shuffledLet = None
		self.score = None
		self.playerID = "#"

		#======================= START: GUI =====================================
		self.frame = Frame(master, width=1000, height=650, bg=self.mainColor)
		self.frame.pack(fill="both", expand=True)
		self.frame.grid_propagate(False)
		self.frame.grid_rowconfigure(0, weight=1)
		self.frame.grid_columnconfigure(0, weight=1)		

		#======================= START: PLAYER INFO =====================
		self.playerInfoLayout = PanedWindow(self.frame, orient=HORIZONTAL, bg=self.mainColor)
		self.playerInfoLayout.grid(row=0)

		self.lblPlayerID = Label(self.playerInfoLayout, text="#00000000000000", padx=50)
		self.playerInfoLayout.add(self.lblPlayerID)

		self.lblPlayerScore = Label(self.playerInfoLayout, text="0", padx=50)
		self.playerInfoLayout.add(self.lblPlayerScore)

		self.lblPlayerTime = Label(self.playerInfoLayout, text="00:00", padx=50)
		self.playerInfoLayout.add(self.lblPlayerTime)
		#======================= END: PLAYER INFO =======================

		#======================= START: PLAYER FOUND WORDS =====================
		self.foundWordsLayout = PanedWindow(self.frame, orient=HORIZONTAL, bg=self.mainColor)
		self.foundWordsLayout.grid(row=1)
		self.populatePlayerFoundWords(self.foundWordsLayout)
		#======================= END: PLAYER FOUND WORDS =======================

		#======================= START: JUMBLED EIGHT LETTERS ===================
		self.lblShuffledLet = Label(self.frame, text="E-I-G-H-T-L-E-T", font=("Arial", 20), 
			padx=15, pady=5, borderwidth=2, relief=SOLID)
		self.lblShuffledLet.grid(row=2)
		#======================= END: JUMBLED EIGHT LETTERS =====================

		#======================= START: GAME HISTORY ============================
		self.gameProgressLayout = PanedWindow(self.frame, orient=HORIZONTAL)
		self.gameProgressLayout.grid(row=3)

		self.text = Text(self.gameProgressLayout, relief="sunken")
		self.text.grid(row = 0, column = 0, sticky="nsew")
		self.text.config(state=DISABLED)

		self.scrollbar = Scrollbar(self.gameProgressLayout, command=self.text.yview)
		self.text["yscrollcommand"] = self.scrollbar.set
		self.scrollbar.grid(row = 0, column = 1, sticky="nsew")

		self.entry = Entry(self.gameProgressLayout)
		self.entry.bind("<Key>", self.onKeyPress)
		self.entry.grid(row = 1, column = 0, sticky="nsew")

		self.button = Button(self.gameProgressLayout, text="Send", command=self.sendMessage)
		self.button.grid(row = 1, column = 1, sticky="nsew")
		#======================= END: GAME HISTORY ===============================
		#======================= END: GUI ========================================


	def setPlayerID(self, playerID):
		self.playerID = playerID
		self.lblPlayerID.config(text=self.playerID)

	def setLetters(self, letters):
		self.shuffledLet= letters
		self.lblShuffledLet.config(text=self.shuffledLet)

	def setScore(self, score):
		self.score = score
		self.lblPlayerScore.config(text=self.score)

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

	def populatePlayerFoundWords(self, container):
		rowNum = 0
		colNum = 0
		for c in self.colours:
		    Label(container, text=c, relief=GROOVE,width=15, padx=3, pady=3, bd=2).grid(row=rowNum,column=colNum, padx=1, pady=1)
		    colNum = colNum + 1
		    if colNum == 7:
		    	colNum = 0
		    	rowNum = rowNum + 1



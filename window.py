from tkinter import *
from tkinter import messagebox
from threading import Timer
from random import  sample

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
		self.timer = None
		self.messagebox = messagebox

		#======================= START: GUI =====================================
		self.frame = Frame(master, width=1000, height=700, bg=self.mainColor)
		self.frame.pack(fill="both", expand=True)
		self.frame.grid_propagate(False)
		self.frame.grid_rowconfigure(0, weight=1)
		self.frame.grid_columnconfigure(0, weight=1)		

		#======================= START: PLAYER INFO =====================
		self.playerInfoLayout = PanedWindow(self.frame, orient=HORIZONTAL, bg=self.mainColor)
		self.playerInfoLayout.grid(row=0, sticky="ns", pady=10)

		#Label(self.playerInfoLayout, text="Player ID:", bg=self.mainColor).grid(row=0, column=0, padx=20, sticky="nw")
		#self.lblPlayerID = Label(self.playerInfoLayout, text="#00000000000000", padx=20)
		#self.lblPlayerID.grid(row=1, column=0, padx=20)

		Label(self.playerInfoLayout, text="Player ID:", bg=self.mainColor).grid(row=0, column=0, padx=20, sticky="nw")
		self.lblPlayerName = Label(self.playerInfoLayout, text="N/A", padx=20)
		self.lblPlayerName.grid(row=1, column=0, padx=20)

		Label(self.playerInfoLayout, text="Score:", bg=self.mainColor).grid(row=0, column=1, padx=20, sticky="nw")
		self.lblPlayerScore = Label(self.playerInfoLayout, text="0", padx=20)
		self.lblPlayerScore.grid(row=1, column=1, padx=20)

		Label(self.playerInfoLayout, text="Time:", bg=self.mainColor).grid(row=0, column=2, padx=20, sticky="nw")
		self.lblPlayerTime = Label(self.playerInfoLayout, text="00:00", padx=20)
		self.lblPlayerTime.grid(row=1, column=2, padx=20)
		#======================= END: PLAYER INFO =======================

		#======================= START: PLAYER FOUND WORDS =====================
		self.foundWordsLayout = PanedWindow(self.frame, orient=HORIZONTAL, bg=self.mainColor)
		self.foundWordsLayout.grid(row=1, pady=5, sticky="ns")
		# self.populatePlayerFoundWords(self.colours)
		#======================= END: PLAYER FOUND WORDS =======================

		#======================= START: JUMBLED EIGHT LETTERS ===================
		self.lblShuffledLet = Label(self.frame, text="E-I-G-H-T-L-E-T", font=("Arial", 20), 
			padx=15, pady=5, borderwidth=2, relief=SOLID)
		self.lblShuffledLet.grid(row=2, pady=20, sticky="ns")
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

		self.button = Button(self.gameProgressLayout, text="Shuffle", command=self.shuffleWord)
		self.button.grid(row = 1, column = 1, sticky="nsew")
		#======================= END: GAME HISTORY ===============================
		#======================= END: GUI ========================================


	def setPlayerID(self, playerID):
		self.playerID = "#"+playerID
		self.lblPlayerID.config(text=self.playerID)

	def setPlayerName(self, playerName):
		self.playerName = playerName
		self.lblPlayerName.config(text=self.playerName)

	def setLetters(self, letters):
		self.shuffledLet= letters
		self.lblShuffledLet.config(text=self.shuffledLet)

	def setScore(self, score):
		self.score = score
		self.lblPlayerScore.config(text=self.score)

	def setTimer(self, timer):
		self.timer = timer
		self.lblPlayerTime.config(text=self.timer)


	def recvMessage(self, msg):
		self.text.config(state=NORMAL)
		self.text.insert(END, msg+"\n")
		self.text.config(state=DISABLED)
		self.text.see("end")

	def onKeyPress(self, key):
		if key.keycode == 36:
			if self.peer.gameFace:
				message = self.entry.get()

				if message == "":
					self.messagebox.showinfo('VERIFYING YOUR INPUT', "Please enter a word.")

				else:
					if message in self.peer.word_list:
						if self.peer.word_list[message]:						
							# self.recvMessage(message + " already taken")
							if (1,message) not in self.peer.personal_word_list and (0,message) not in self.peer.personal_word_list:
								self.peer.personal_word_list.append((0,message))
								self.populatePlayerFoundWords(self.peer.personal_word_list)
							self.messagebox.showinfo('VERIFYING INPUT', message.upper() + " is already taken.")
							
						else:
							self.peer.sendMessage("CHECK_WORD!", message)
							Timer(0.2, lambda arg=message: self.peer.giveVerdict(arg)).start()
					else:
						# self.recvMessage(message + " rejected")
						self.messagebox.showwarning('VERIFYING YOUR INPUT', message.upper() + " is rejected.")

			self.entry.delete(0, len(self.entry.get()))

	def shuffleWord(self):
		wordToPlay = self.lblShuffledLet.cget("text").replace("-", "")
		shuffled = '-'.join(sample(wordToPlay, len(wordToPlay))).upper()
		self.lblShuffledLet["text"] = shuffled

	def populatePlayerFoundWords(self, words):
		rowNum = 0
		colNum = 0
		for (n,c) in words:
			if n==1:
				Label(self.foundWordsLayout, text=c, relief=GROOVE,width=15, padx=3, pady=3, bd=2, bg="green", fg="white").grid(row=rowNum,column=colNum, padx=5, pady=2, sticky="w")
			else:
				Label(self.foundWordsLayout, text=c, relief=GROOVE,width=15, padx=3, pady=3, bd=2, bg="red", fg="white").grid(row=rowNum,column=colNum, padx=5, pady=2, sticky="w")
			colNum = colNum + 1
			# rowNum = rowNum + 1
			if colNum == 7:
			# if rowNum == 5:
				colNum = 0
				rowNum = rowNum + 1
				# rowNum = 0
				# colNum = colNum + 1

	def clearPlayerFoundWords(self):
		list = self.foundWordsLayout.grid_slaves()
		for l in list:
			l.destroy()



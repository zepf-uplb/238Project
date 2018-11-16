from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint, sample
from window import Window
from crochet import setup
from threading import Timer, Thread
from time import sleep
from anagram_solver import anagram_solver, stuff
from eight_letter import dict_list
from itertools import combinations
from tkinter import Tk
from operator import itemgetter

WAIT_TIME = 10
GAME_TIME = 120

class MulticastPingClient(DatagramProtocol):	

	def startProtocol(self):
		#self.name = input("Enter name: ")
		self.name = "Peer"
		self.transport.joinGroup("228.0.0.5")

		#15 digit ID of this peer
		self.peerID = self.initPeerID()

		#flag to tell if peer already has a synched time
		self.timed = False

		#variable that will later be the thread for timer
		self.t1 = None

		#dictionary for (peerID, name) of other peers
		self.PEERS = {}

		#would dictate what index of the dict_list the word to 
		#play will come from
		self.gameID = -1

		#bossPeer dictates the peer with the largest peerID that
		#will later be used to determine the gameID for all peers
		self.bossPeer = -1

		#flag if self is currently on a gaming session
		self.gameFace = False

		#dictionary that stores peers you are schronized time with
		self.SYNC = {}

		#will contain all the possible words from the dict_list[gameID]
		#True if the word is found, otherwise False
		self.word_list = {}

		#flag that will tell if the peer will be joining an active game
		self.newcomer = False

		#stores the score of the self
		self.score = 0

		#dictionary for (peerID, score) of all peers including self
		self.SCOREBOARD = {}

	def datagramReceived(self, datagram, address):
		peerCall = str(datagram)[2:13]
		peerID = str(datagram)[13:28]
		#contains the message from a fellow peer
		peerLoad = str(datagram)[28:len(str(datagram))-1]
		peerAdd = str(address)

		if self.peerID == int(peerID):
			pass
		else:
			#print("Peer %s calls %s with address %s" % (peerID, peerCall, peerAdd))			

			if peerCall == "SYNCHRONIZE":
				if peerID not in self.SYNC:
					self.SYNC[peerID] = True
				if self.newcomer:
					self.gameID = int(peerLoad)
					self.newcomer = False
				elif int(peerID) > self.bossPeer:
					self.bossPeer = int(peerID)
					self.gameID = int(peerLoad)

			elif peerCall == "CHECK_WORD!":
				if not self.word_list[peerLoad]:
					self.word_list[peerLoad] = True
				else:
					self.sendMessage("REJECTED!!!", peerLoad)

			elif peerCall == "REJECTED!!!":
				self.word_list[peerLoad] = True

			elif peerCall == "GREET_PEERS" and peerLoad not in self.PEERS:
				self.PEERS[peerID] = peerLoad
				self.sendMessage("GREET_BACK!", str(self.name))
				if self.gameFace:
					self.sendMessage("JOIN_US_NOW", "")			

			elif peerCall == "GREET_BACK!" and peerLoad not in self.PEERS:
				self.PEERS[peerID] = peerLoad
				
			elif peerCall == "GET_TIMER!!":
				self.sendMessage("GIVE_TIMER!", str(self.t1.timer))

			elif peerCall == "GIVE_TIMER!" and not self.timed:
				self.timed = True
				timer = int(peerLoad)
				self.t1 = self.TimerThread(self, timer)
				self.t1.start()

			elif peerCall == "JOIN_US_NOW":
				self.gameFace = True	
				self.newcomer = True

			elif peerCall == "MY_SCORE!!!":
				self.SCOREBOARD[peerID] = int(peerLoad)				

	def sendMessage(self, call, message):
		if self.transport is not None:
			self.transport.write((call + str(self.peerID) + message).encode(), ("228.0.0.5", 9999))

	def setGame(self):
			self.gameID = randint(0, len(dict_list))
			self.bossPeer = self.peerID

	def constructGame(self):
		wordToPlay = dict_list[self.gameID]
		shuffled = ''.join(sample(wordToPlay, len(wordToPlay)))
		app.recvMessage(shuffled)
		self.constructWords(wordToPlay)		
		self.gameFace = True

	def constructWords(self, wordToPlay):
		for L in range(4, len(wordToPlay)+1):
		    for subset in combinations(wordToPlay, L):
		        possible_words = anagram_solver.find_possible("".join(subset))
		        actual_words = anagram_solver.return_words(possible_words, stuff.word_set)
		        for i in range(len(actual_words)):
		        	self.word_list[actual_words[i]] = False

	def greetPeers(self):
		self.sendMessage("GREET_PEERS", self.name)
		Timer(0.2, self.initTimer).start()
		self.setGame()

	def initTimer(self):
		if len(self.PEERS) == 0:
			self.timed = True
			self.t1 = self.TimerThread(self)
			self.t1.start()
		else:
			self.sendMessage("GET_TIMER!!", "")

	def giveVerdict(self, word):
		if self.word_list[word]:
			app.recvMessage(word + " already taken")
		else:
			app.recvMessage(word + " accepted")
			self.word_list[word] = True
			self.score += len(word)

	def initPeerID(self):
		return randint(100000000000000,999999999999999)

	class TimerThread(Thread):
		def __init__(self,  master, timer=WAIT_TIME):
			Thread.__init__(self)
			self.timer = timer
			self.greenLight = True
			self.master = master

		def run(self):
			while(self.greenLight):
				while self.timer > 0 and self.greenLight and not self.master.gameFace:
					print(self.timer)
					sleep(1)	

					self.master.sendMessage("SYNCHRONIZE", str(self.master.gameID))

					#block wait until all peers have the same time
					while len(self.master.SYNC) != len(self.master.PEERS):
						sleep(0.01)

					self.timer -= 1	

				if self.greenLight:					
					#to assure that gameID has been synched with other peers
					sleep(1)

					app.recvMessage("Game starting with peerID = " + str(self.master.peerID) + " gameID = " + str(self.master.gameID))
					self.master.constructGame()

				while self.timer < GAME_TIME and self.greenLight:
					print(self.timer)
					sleep(1)	

					self.master.sendMessage("SYNCHRONIZE", str(self.master.gameID))

					#block wait until all peers have the same time
					while len(self.master.SYNC) != len(self.master.PEERS):
						sleep(.01)

					self.timer += 1					

				if self.greenLight:
					self.master.gameFace = False
					self.master.SCOREBOARD[self.master.peerID] = self.master.score
					self.master.sendMessage("MY_SCORE!!!", str(self.master.score))

					app.recvMessage("\nGame end. Compiling scores...")

					#to assure that all peers' score are accounted for
					sleep(1)

					sorted_scores = sorted(self.master.SCOREBOARD.items(), key=itemgetter(1), reverse=True)

					app.recvMessage(str(sorted_scores))

					self.master.score = 0
					self.master.SCOREBOARD.clear()
					self.timer = WAIT_TIME
					self.master.setGame()

					app.recvMessage("\nGame will start again in a few moments...\n")

	def exitFxn(self):
		print("Game Exited")
		self.t1.greenLight = False

peer = MulticastPingClient()
reactor.listenMulticast(9999, peer, listenMultiple=True)
#the only code from crochet
setup()

peer.greetPeers()

root = Tk()
root.wm_title("Text Twist Chat Edition")

app = Window(root, peer)
root.mainloop()

peer.exitFxn()
import argparse
import json
import os
from pprint import pprint
import requests
import urllib


# REST command to get data for all cards:
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET https://arkhamdb.com/api/public/cards/
#
# Some cards have no image, e.g., higher xp cards

ARKDAMDB_BASE_URL = 'https://arkhamdb.com/'
ARKHAMDB_API_INVESTIGATOR_CARDS_URL = 'https://arkhamdb.com/api/public/cards/'
ARKHAMDB_API_PACK_CARDS_URL = 'https://arkhamdb.com/api/public/cards/'
ARKHAMDB_API_DECK_URL = 'https://arkhamdb.com/api/public/decklist/'

CARD_NAME_KEY = 'name'
CARD_IMAGE_KEY = 'imagesrc'
CARD_BACKIMAGE_KEY = 'backimagesrc'
CURRENT_GAME_DECK_ID = '1761'

IMAGE_CACHE_DIR = 'images/'

def printCardList(cardList):
	for card in cardList:
		if CARD_NAME_KEY in card and CARD_IMAGE_KEY in card:
			#print "Card name: %s, imagesrc: %s" % (card[CARD_NAME_KEY], card[CARD_IMAGE_KEY])
			pprint(card)
		elif CARD_NAME_KEY in card and CARD_BACKIMAGE_KEY in card:
			#print "Card name: %s, imagesrc: %s" % (card[CARD_NAME_KEY], card[CARD_BACKIMAGE_KEY])
			pprint(card)
		else:
			print("------- card without image -------")
			if CARD_NAME_KEY in card:
				print "Card name: %s", card[CARD_NAME_KEY]
			if CARD_IMAGE_KEY in card:
				print "Card image: %s", card[CARD_IMAGE_KEY]
			pprint(card)

def loadAllInvestigatorCardsList():
	r = requests.get(ARKHAMDB_API_INVESTIGATOR_CARDS_URL)
	data = json.loads(r.text)
	return data

def loadCardsForPack(packCode):
	packUrl = ARKHAMDB_API_INVESTIGATOR_CARDS_URL + packCode
	r = requests.get(packUrl)
	data = json.loads(r.text)
	return data

def downloadCardImages(cardList, imageDirectory):
	for card in cardList:
		if CARD_IMAGE_KEY in card:
			downloadCardImage(card[CARD_IMAGE_KEY], imageDirectory)
			pass
		elif CARD_BACKIMAGE_KEY in card:
			downloadCardImage(card[CARD_BACKIMAGE_KEY], imageDirectory)
		else:
			print("No image for %s", card[CARD_NAME_KEY])

def downloadCardImage(cardImageUrl, imageDirectory):
	imageFileName = os.path.basename(cardImageUrl)
	imagePath = imageDirectory + imageFileName
	if os.path.exists(imagePath) != True:
		print("Saving %s ...", imagePath)
		urllib.urlretrieve(ARKDAMDB_BASE_URL + cardImageUrl, imageDirectory + imageFileName)

def loadDeck():
	r = requests.get(ARKHAMDB_API_DECK_URL + CURRENT_GAME_DECK_ID + ".json")
	data = json.loads(r.text)
	return data

def main():

	parser = argparse.ArgumentParser(fromfile_prefix_chars='@', description='ArkhamDB data import tool.')
	# ex: ImageImport --deck 1761
	parser.add_argument('-d', '--deck', metavar='DECK', help='Loads cards for a specified deck number')
	# ex: ImageImport --cards 01002 01003 01004
	parser.add_argument('-c', '--cards', metavar='CARDS', nargs='+', help='Loads cards for the specified list of card ids')
	# ex: ImageImport --packs Core dwl tmm tece
	parser.add_argument('-p', '--packs', metavar='PACKS', nargs='+', help='Loads cards from a list of pack ids')
	# ex: --folders 12 13 
	parser.add_argument('-f', '--folders', metavar='BUTTONS', type=int, nargs='+', required=True, help='StreamDeck folder buttons to populate')
	# ex: --other_folders 5 6 7 8 9
	parser.add_argument('-o', '--other_folders', metavar='BUTTONS', type=int, nargs='+', required=True,  help='Other StreamDeck folder buttons')
	args = parser.parse_args()

	#allInvestigatorCardsList = loadAllInvestigatorCardsList()
	#printCardList(allInvestigatorCardsList)

	packs = ["Core", "dwl", "tmm", "tece", "bota", "uau", "wda", "litas", "cotr", "coh"]	

	for packCode in packs:
		packCardsList = loadCardsForPack(packCode)
		printCardList(packCardsList)

	#deck = loadDeck()
	#pprint(deck)

	#downloadCardImages(cardList, IMAGE_CACHE_DIR)
	#downloadCardImage('/bundles/cards/01001b.png', IMAGE_CACHE_DIR)

#-----------------------------------------------------------------------------

if __name__ == '__main__':
	main()




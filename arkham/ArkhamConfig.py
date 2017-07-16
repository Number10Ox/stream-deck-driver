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
ARKHAMDB_API_CARD_URL = 'https://arkhamdb.com/api/public/card/'
ARKHAMDB_API_DECK_URL = 'https://arkhamdb.com/api/public/decklist/'

CARD_ID_KEY = 'code'
CARD_NAME_KEY = 'name'
CARD_IMAGE_KEY = 'imagesrc'
CARD_BACKIMAGE_KEY = 'backimagesrc'

# TODONOW
IMAGES_DIR = 'arkham/images/'
IMAGE_CACHE_DIR = 'images/'

STREAMDECK_BUTTONS_PER_FOLDER = 15;
STREAMDECK_BACK_BUTTON_KEY_INDEX = 4;

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

def loadCard(cardId):
	cardUrl = ARKHAMDB_API_CARD_URL + cardId
	print "Loading card: " + cardUrl
	r = requests.get(cardUrl)
	data = json.loads(r.text)
	return data

def loadCardsForPack(packCode):
	packUrl = ARKHAMDB_API_INVESTIGATOR_CARDS_URL + packCode
	r = requests.get(packUrl)
	data = json.loads(r.text)
	return data

def loadDeck(deckId):
	r = requests.get(ARKHAMDB_API_DECK_URL + deckId + ".json")
	data = json.loads(r.text)
	return data

def loadAllInvestigatorCardsList():
	r = requests.get(ARKHAMDB_API_INVESTIGATOR_CARDS_URL)
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


def generateConfiguration(cardList, folders, otherFolders):

	# Build Streamdeck configuration to convert to Json
	configuration = {}

	# StreamDeck information
	configuration['streamdeck_info'] = {}
	allFolders = folders + otherFolders
	configuration['streamdeck_info']['main_folder_button_id_list'] = folders + otherFolders

	# Populate list of foders
	configuration['folder_list'] = []

	# Go through list of configurable folders and configure buttons from card list
	cardQueue = cardList
	# Populate folders with cards
	for folderId in folders:

		folder = {}
		folder['main_folder_button_id'] = folderId
		folder['folder_contents'] = []

		for index in [x for x in range(0, STREAMDECK_BUTTONS_PER_FOLDER) if x != STREAMDECK_BACK_BUTTON_KEY_INDEX]:
			if not cardQueue:
				break

			card = cardQueue.pop()

			cardId = None
			if CARD_ID_KEY in card:
				cardId = card[CARD_ID_KEY]
			else:
				print "NO CODE: skipping card..."
				continue

			image = None
			if CARD_IMAGE_KEY in card:
				image = card[CARD_IMAGE_KEY]
			elif CARD_BACKIMAGE_KEY in card:
				image = card[CARD_BACKIMAGE_KEY]
			else:
				if CARD_NAME_KEY in card:
					print "NO IMAGE: skipping card %s" % (card[CARD_NAME_KEY])
				else:
					print "NO IMAGE: skipping card %s" % (card[CARD_ID_KEY])
				continue

			imageFilePath = IMAGES_DIR + os.path.basename(image)

			folderContents = {}
			folderContents['button_id'] = index
			folderContents['image'] = imageFilePath
			folderContents['text'] = str(cardId)
			folderContents['command'] = "bin\\open_url_cmd.bat " + os.path.normcase(imageFilePath)

			folder['folder_contents'].append(folderContents)

			# "command": "bin\\open_url_cmd.bat images\\01013.jpg" 

		if folder['folder_contents']:	
			configuration['folder_list'].append(folder)

	#print configuration

	return configuration

def extractCardId(json):
	print json['code'];
	return json['code']

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
	parser.add_argument('-o', '--other-folders', metavar='BUTTONS', type=int, nargs='+', required=True,  help='Other StreamDeck folder')
	# ex: -c test_config.json
	parser.add_argument('-s', '--streamdeck-file', metavar='FILE', required=True,  help='StreamDeck driver configuration output file')
	args = parser.parse_args()

	# Need a list of all of the cards we want to assign to buttons
	cardList = []

	# Add cards from deck, if specified
	if args.deck:
		deck = loadDeck(args.deck)
		for slot in deck["slots"]:
			card = loadCard(slot)
			cardList.append(card)

	# Add individual cards, if specified
	if args.cards:
		for cardId in args.cards:
			card = loadCard(cardId) 
			cardList.append(card)
			#pprint(cardJson)

	# Add cards from packs, if specified
	if args.packs:
		for packId in args.packs:
			pack = loadCardsForPack(packId) 
			cardList = cardList + pack

	# Sort list by id
	cardList.sort(key=extractCardId, reverse=True)

	for card in cardList:
		print "card code:" + card['code']

	cardCount = len(cardList)
	print "NUMBER OF CARDS: " + str(cardCount)
	maxCardCapacity = len(args.folders) * (STREAMDECK_BUTTONS_PER_FOLDER - 1)
	if cardCount > maxCardCapacity:
		print "*** FOLDER CAPACITY EXCEEDED*** (%s / %s)" % (cardCount, maxCardCapacity)

	configuration = generateConfiguration(cardList, args.folders, args.other_folders)
	f = open(args.streamdeck_file, 'w')
	f.write(json.dumps(configuration))

	downloadCardImages(cardList, IMAGE_CACHE_DIR)

	#allInvestigatorCardsList = loadAllInvestigatorCardsList()
	#printCardList(allInvestigatorCardsList)

	# packs = ["Core", "dwl", "tmm", "tece", "bota", "uau", "wda", "litas", "cotr", "coh"]	

	#for packCode in packs:
	#	packCardsList = loadCardsForPack(packCode)
	#	printCardList(packCardsList)

	#downloadCardImage('/bundles/cards/01001b.png', IMAGE_CACHE_DIR)

#-----------------------------------------------------------------------------

if __name__ == '__main__':
	main()




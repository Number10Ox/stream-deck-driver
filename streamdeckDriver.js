'use strict';

///////////////////////////////////////////////////////////////////////////////
//
// Tool for programmatically-driven StreamDeck buttons within StreamDeck
// folders. Takes a config file that can specify
//
//			- Button image
//			- Overlayed button text
//			- DOS command to be executed when button pressed
//
// Note that the tool needs to track what folder the StreamDeck currently ahs
// open. As there is no way to query StreamDeck, tool needs to know all of
// the StreamDeck folder buttons.
//
///////////////////////////////////////////////////////////////////////////////

// Packages
var adt = require('adt');
const curl = require('curlrequest');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const sharp = require('sharp'); 
const streamDeck = require('elgato-stream-deck');

//=============================== CONFIGURATION ===============================

// Number of buttons on stream deck
const STREAMDECK_BUTTONS_PER_FOLDER = 15;
// A 'folder index' is used to identify which folder we are in. We need an
// id for the top level 'main' folder
const STREAM_DECK_MAIN_FOLDER_INDEX = STREAMDECK_BUTTONS_PER_FOLDER;
// The key index of the "back" button when sub-page is open
const STREAMDECK_BACK_BUTTON_KEY_INDEX = 4;
// File where .pngs are generated with image with overlayed text
const IMAGE_CACHE_DIRECTORY = 'imagecache';
// Button image used if no image specified or specified image not found
const DEFAULT_BUTTON_IMAGE = 'icons/cardtemplate.png';
// Buttons reserved in folders that shouldn't be overridden, e.g. back button
const RESERVED_FOLDER_BUTTONS = [STREAMDECK_BACK_BUTTON_KEY_INDEX];
// JSON schema for configuration file used to configure StreamDeck
const CONFIGURATION_FILE_SCHEMA = 
{
	"properties": {
	    "streamdeck_info": {
			"properties": {
				"main_folder_button_id_list": {
					"type": "array",
					"items": {
						"type": "integer",
						"minimum": 0,
						"maximum": 15
					}
				}
			},
			"required": [
				"main_folder_button_id_list"
			],
	    },
		"folder_list": {
			"type": "array",
			"items": {
				"type": "object",
				"properties": {
					"folder_contents": {
						"type": "array",
						"items": {
							"type": "object",
							"properties": {
								"command": { "type": "string"},
								"image": { "type": "string"},
								"button_id": { "type": "integer", "minimum": 0, "maximum": 15 },
								"text": { "type": "string" }
							},
							"required": [ "command", "image", "button_id"],
						}
					},
					"main_folder_button_id": { "type": "integer", "minimum": 0, "maximum": 15 }
				},
				"required": ["main_folder_button_id"],
			}
		},		    
	},
	"required": ["streamdeck_info", "folder_list"],
}

//=============================================================================

// ADT (Algebraic Data Type) to store configuration data for each button
var ManagedButtonConfig = adt.newtype('ButtonConfig', {
  	image: adt.only(String),
  	text: adt.only(String),
  	command: adt.only(String)
});

// Variable that tracks index of current active folder (button id on  main page)
var _currentFolderIndex = STREAM_DECK_MAIN_FOLDER_INDEX;

// List of key for buttons with folders in "main" folder
var _mainPageFolderButtons = [];

// Array of folders that the SteamDeckDriver will be managing
//		index: button index 
//		value: array of
//			index: button index
// 			value: ManagedButtonConfig 
var _managedFolders = [];

// Queue for processing cache images
var _cacheImageQueue = [];

//=============================================================================

function generateCachedIconFileName(folderIndex, buttonIndex) {
 	return IMAGE_CACHE_DIRECTORY + '/' + 'button_' + folderIndex + '_' + buttonIndex + '.png';
}

function imageFileNameForCard(cardId, folderIndex, buttonIndex) {
	var pngFileName = cardImageDirectory + '/' + cardId + '.png';
	var jpgFileName = cardImageDirectory + '/' + cardId + '.jpg';

	// console.log('pngFileName = %s jpgFileName = %s', pngFileName, jpgFileName);

	if (fs.existsSync(pngFileName))	{
		return pngFileName;
	} else
	if (fs.existsSync(jpgFileName)) {
		return jpgFileName;		
	}

	return genericCardButtonIconFileName;
}

function processNextCacheImageInQueue()
 {
	if (_cacheImageQueue.length > 0) {
		var nextImage = _cacheImageQueue.shift();
		cacheKeyImageWithTextOverlay(nextImage.iconImageFileName, nextImage.overlayText, nextImage.outputImageFileName);
	}
}

function cacheKeyImageWithTextOverlay(iconImageFileName, overlayText, outputImageFileName) {
	let textSVG = `<svg width="72px" height="72px" viewBox="0 0 72 72"><text x="10" y="60" style="font-family:Arial,Helvetica;font-size:18px;fill:red;stroke:red;stroke-width:1;">` + overlayText + `</text></svg>`;
	var svgBuffer = new Buffer(textSVG	)

	var image = sharp(path.resolve(__dirname, iconImageFileName))
		.resize(streamDeck.ICON_SIZE, streamDeck.ICON_SIZE) 	// Scale down to the right size, cropping if necessary.
		.background({r: 0, g: 0, b: 0, alpha: 0})
		.embed()
		.overlayWith(svgBuffer)
		.png()
		.toFile(outputImageFileName, (err, info) => {
			if (err) {
				console.error(err);
			}
			if (info) {
				//console.log(info);
			}

			processNextCacheImageInQueue()
		});

	console.log("wrote: %s using %s", outputImageFileName, iconImageFileName);
}

// Set a SteamDeck button image
function setKeyImage(buttonIndex, buttonImageFileName) {
	var outputImage = sharp(path.resolve(__dirname, buttonImageFileName));
	outputImage.resize(streamDeck.ICON_SIZE); // Scale down to the right size, cropping if necessary.
	outputImage.flatten(); // Eliminate alpha channel, if any.
	outputImage.raw(); // Give us uncompressed RGB
	outputImage.toBuffer()
   			   .then(buffer => {
	   			   	streamDeck.fillImage(parseInt(buttonIndex, 10), buffer);
				})
			   .catch(err => {
					console.log('----- Error ----');
					console.error(err);
				});
}

function displayButtonImagesInCurrentFolder()
{
	for (var buttonIndex in _managedFolders[_currentFolderIndex]) {
		var cachedButtonIconFileName = generateCachedIconFileName(_currentFolderIndex, buttonIndex);
		//console.log("DISPLAYING BUTTON: mainPageButtonIndex = %d buttonIndex = %d cachedIconImage=%s", _currentFolderIndex, buttonIndex, cachedButtonIconFileName);
		setKeyImage(buttonIndex, cachedButtonIconFileName);
	}	
}

function executeButtonCommand(command) {
	console.log('Executing %s...', command);
	exec(command);
}

/* 
 * Handling key presses
 */
streamDeck.on('up', selectedButtonIndex => {

	if (_currentFolderIndex == STREAM_DECK_MAIN_FOLDER_INDEX) {
		// If button for sub-folder in main folder was opened then populate it with buttons
		// for the cards. Need to do it on a delay after StreamDeck software has finished
		// opening the folder.

		//console.log('selectedKeyIndex: %d', selectedKeyIndex);
		//console.log(cardFolders[selectedKeyIndex]);

		if (_mainPageFolderButtons.indexOf(selectedButtonIndex) >= 0) {
			// In folder
			_currentFolderIndex = selectedButtonIndex;

			// Check if in managed folder
			if (typeof _managedFolders[selectedButtonIndex] !== 'undefined' && _managedFolders[selectedButtonIndex] !== null) {
				setTimeout(displayButtonImagesInCurrentFolder, 500);
			}
		}
	}
	else if (selectedButtonIndex == STREAMDECK_BACK_BUTTON_KEY_INDEX) {
		// Return to main folder
		_currentFolderIndex = STREAM_DECK_MAIN_FOLDER_INDEX;
	} else {
		if (typeof _managedFolders[_currentFolderIndex] !== 'undefined'
			&& _managedFolders[_currentFolderIndex] !== null
			&& typeof _managedFolders[_currentFolderIndex][selectedButtonIndex] !== 'undefined'
			&& _managedFolders[_currentFolderIndex][selectedButtonIndex] !== null) {
				var buttonConfig = _managedFolders[_currentFolderIndex][selectedButtonIndex];
				executeButtonCommand(buttonConfig.command);
		}
	}

    //console.log('current folder index: %d', currentFolderIndex);
});

streamDeck.on('error', error => {
    console.error(error);
});

function configurationFileHasValidFormat(jsonObject)
{
	var Ajv = require('ajv');
	var ajv = new Ajv({allErrors: true});
	var validate = ajv.compile(CONFIGURATION_FILE_SCHEMA);
 	var validFormat = validate(jsonObject);

	if (!validFormat) {
		console.log('Configuration file invalid format: ' + ajv.errorsText(validate.errors));
	}

 	return validFormat;
}

function loadConfiguration(configurationFile) { 
	if (!fs.existsSync(configurationFile))	{
		console.log('Error: cannot open configuration file "%s"', configurationFile);
		return;
	} 

	// Load json
	console.log("Loading '%s'...", configurationFile);
	var content = fs.readFileSync(configurationFile);
	var jsonObject = JSON.parse(content);
	//console.log(JSON.stringify(jsonObject));

	// Validate format
	var validFormat = configurationFileHasValidFormat(jsonObject);
  	if (!validFormat) {
	  	return;
	}

	// List of buttons assigned to folders on StreamDeck - this is used to track
	// which folder is currently active on StreamDeck. Currently, 
	_mainPageFolderButtons = jsonObject.streamdeck_info.main_folder_button_id_list;
	if (!jsonObject.hasOwnProperty('folder_list')) {
		console.log('Error no folders found');
		return;
	}

	// Populate _managedFolders with configuration info
	var folders = jsonObject['folder_list'];
	for (var folderIndex = 0; folderIndex < folders.length; folderIndex++) {
		var folder = folders[folderIndex];
		//console.log('Adding buttons for main page button_id: %d...', folder.main_folder_button_id);

		_managedFolders[folder.main_folder_button_id] = [];

		for (var buttonIndex  = 0; buttonIndex < folder.folder_contents.length; buttonIndex++) {
			var buttonInfo = folder.folder_contents[buttonIndex];
			//console.log('Adding button %d to folder %d', buttonInfo.button_id, folderIndex);
			_managedFolders[folder.main_folder_button_id][buttonInfo.button_id] = ManagedButtonConfig(buttonInfo.image, buttonInfo.text, buttonInfo.command);
		}
	}

	//console.log(_managedFolders);
}

function generateButtonImages()
{
	// TODO Need to process images serially because text drawing seems to not be thread-safe
	// Is there a better way to do this?
	_cacheImageQueue = [];

	for (var folderIndex in _managedFolders) {
		for (var buttonIndex in _managedFolders[folderIndex]) {

		 	var cachedButtonIconFileName = generateCachedIconFileName(folderIndex, buttonIndex);
			var image = _managedFolders[folderIndex][buttonIndex].image;
			var text = _managedFolders[folderIndex][buttonIndex].text;
			// console.log('generate %s %s %s', image, text, cachedButtonIconFileName);

			var queueElement = Object.freeze({ iconImageFileName:image, overlayText:text, outputImageFileName:cachedButtonIconFileName});
			_cacheImageQueue.push(queueElement);
		}
	}

	processNextCacheImageInQueue();
}

function configureDriver(configurationFile)
{
	loadConfiguration(configurationFile);
	generateButtonImages();
}

//============================ Main =================================

var argv = require('yargs')
	.usage('Usage: $0 -f configuration_file')
	.demandOption(['f'])
	.argv;

configureDriver(argv.f);


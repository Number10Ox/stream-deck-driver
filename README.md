# stream-deck-driver
Application for programmatically configuring Elgato StreamDeck 

**steamDeckDriver** is a Node JS application that connects to an Elgato StreamDeck and configures the StreamDeck programmatically. It uses the [node-elgato-stream-deck](https://github.com/Lange/node-elgato-stream-deck) API.

### Installation

NodeJS and NPM are required to run the StreamDeck Driver. See http://blog.teamtreehouse.com/install-node-js-npm-windows for how to installed NodeJS and NPM on Windows and http://blog.teamtreehouse.com/install-node-js-npm-mac for how to on Mac.

### StreamDeck Configuration

The application takes a JSON configuration file that specifies

- Buttons on the main stream deck page that have folders
- Folders on StreamDeck where you want to add programmatically configured and handled buttons.
  For each custom button you can specify
  - Button image
  - Overlayed button text
  - DOS command to be executed when button pressed

![Alt text](media/ArkhamStreamDeck.png?style=centerme "Title")

### Example Configuration

This configuration 

1.Identifies the buttons on the StreamDeck main page that include folders.
This is needed for tool, at run-time, track the current open folder.

2. Adds three custom buttons to the folder for StreamDeck button 11. An
image with overlayed text is displayed. A DOS command is executed when the
button is pressed.

```
{
  "streamdeck_info": {
    "main_folder_button_id_list": [ 11, 12, 13, 14, 5, 6, 7, 8, 9 ]
  },
  "folder_list": [
    {
      "folder_contents": [
        {
          "text": "01120",
          "image": "arkham/images/01120.jpg",
          "command": "bin\\open_url_cmd.bat arkham\\images\\01120.jpg",
          "button_id": 0
        },
        {
          "text": "01123",
          "image": "arkham/images/01123.jpg",
          "command": "bin\\open_url_cmd.bat arkham\\images\\01123.jpg",
          "button_id": 1
        },
        {
          "text": "01130",
          "image": "arkham/images/01130.jpg",
          "command": "bin\\open_url_cmd.bat arkham\\images\\01130.jpg",
          "button_id": 2
        }
      ],
      "main_folder_button_id": 11
    }
  ]
}
```

### Running

Run 'node streamdeckDriver.js -f [config filename]'

 A configuration file needs to be specified when running the driver using the
 '-f' command argument

Example:

node streamdeckDriver.js -f configs/testConfig.json

# Git Repository Contents

bin/ 		Small utility scripts I've written to open URLS and PDFs using the Streamdeck

configs/	A couple of sample configuration files. One was generated using
			games/Arkham/ArkhamConfig.py

games/		Directory for game-specific content and scripts to generate config files.
			I've been using it with Arkham Horror: The Card Game and wrote a Python
			script to grab images from ArkhamDB and generate StreamDeckDriver
			configuration files for specific sets of cards. That tool requires Python
			is and not necessary to use the SteamDeckDriver tool.

icons/ 		A set of public domain icons I've used from http://game-icons.net/

media/		Miscellaneous media files

testdata/	Configuration files used for testing





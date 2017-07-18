# stream-deck-driver
Application for programmatically configuring Elgato StreamDeck 

**steamDeckDriver** is a Node JS application that connects to an Elgato StreamDeck and configures the StreamDeck programmatically. It uses the [node-elgato-stream-deck](https://github.com/Lange/node-elgato-stream-deck) API.

### Configuration
The application takes a JSON configuration file that specifies

- Buttons on the main stream deck page that have folders
- Folders on StreamDeck where you want to add custom buttons. For each custom button you can specify
  - Button image
  - Overlayed button text
  - DOS command to be executed when button pressed

### Example

![Alt text](media/ArkhamStreamDeck.png?style=centerme "Title")

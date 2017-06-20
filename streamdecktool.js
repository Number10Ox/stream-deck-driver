const path = require('path');
const myStreamDeck = require('elgato-stream-deck');

myStreamDeck.on('down', keyIndex => {
    console.log('key %d down', keyIndex);
});

myStreamDeck.on('up', keyIndex => {
    console.log('key %d up', keyIndex);
});

myStreamDeck.on('error', error => {
    console.error(error);
});

// Fill the second button from the left in the first row with an image of the GitHub logo.
// This is asynchronous and returns a promise.
myStreamDeck.fillImageFromFile(3, path.resolve(__dirname, 'images/01001.png')).then(() => {
	console.log('Successfully wrote a GitHub logo to key 3.');
});

// Fill the first button form the left in the first row with a solid red color. This is synchronous.
myStreamDeck.fillColor(4, 255, 0, 0);
console.log('Successfully wrote a red square to key 4.');
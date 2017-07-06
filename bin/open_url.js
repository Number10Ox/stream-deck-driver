// print process.argv
// process.argv.forEach(function (val, index, array) {
//  console.log(index + ': ' + val);
// });

var argv = require('yargs')
    .usage('Usage: $0 -url [string]')
    .demandOption(['u'])
    .argv;

var opn = require('opn')
opn(argv.u, {app: 'firefox'});


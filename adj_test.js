var Ajv = require('ajv');
var ajv = new Ajv({allErrors: true});

var schema = {
  "properties": {
    "foo": { "type": "string" },
    "bar": { "type": "number", "maximum": 3 }
  },
  "required": [
	"foo"
  ]
};

var validate = ajv.compile(schema);

test({"nnn": "abc", "ooo": 2});
test({"xxx": 2, "yyy": 4});

function test(data) {
  var valid = validate(data);
  if (valid) console.log('Valid!');
  else console.log('Invalid: ' + ajv.errorsText(validate.errors));
}
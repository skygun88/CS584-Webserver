inputData = '{\
	"result": [\
\
		{\
			"boxes": [\
				[\
					227,\
					307\
				],\
				[\
					420,\
					247\
				],\
				[\
					446,\
					331\
				],\
				[\
					253,\
					391\
				]\
			],\
			"recognition_words": [\
				"극동간사러"\
			]\
		},\
		{\
			"boxes": [\
				[\
					514,\
					300\
				],\
				[\
					671,\
					255\
				],\
				[\
					680,\
					287\
				],\
				[\
					524,\
					332\
				]\
			],\
			"recognition_words": [\
				"Tel. 3789-1357"\
			]\
		},\
		{\
			"boxes": [\
				[\
					126,\
					392\
				],\
				[\
					203,\
					364\
				],\
				[\
					211,\
					386\
				],\
				[\
					134,\
					414\
				]\
			],\
			"recognition_words": [\
				"031.494.5225"\
			]\
		},\
		{\
			"boxes": [\
				[\
					2,\
					693\
				],\
				[\
					47,\
					690\
				],\
				[\
					49,\
					714\
				],\
				[\
					4,\
					717\
				]\
			],\
			"recognition_words": [\
				"고기름"\
			]\
		}\
	]\
}'

import json
import re

# function to return area code if any
# invalid tel no -> return -1
# valid tel & with area code -> return area code
# valid tel & without area code -> return empty string
def checkAreaCode(tel):
	if len(tel) < 7 or len(tel) > 11:
		return -1
	# case for no area code
	if len(tel) == 7 or len(tel) == 8:
		return ""
	# case for seoul number with 7-digit
	if len(tel) == 9:
		if tel[:2] == "02":
			return "02"
		else:
			return -1
	# case for seoul number with 8-digit
	if len(tel) == 10:
		if tel[:2] == "02":
			return "02"
	# case for non-seoul number with 7/8 digit
	if tel[:3] == "010":
		return "010"
	if tel[:2] == "03" and (int(tel[2:3]) <= 3 and int(tel[2:3]) >= 1):
		return tel[:3]
	if tel[:2] == "04" and (int(tel[2:3]) <= 4 and int(tel[2:3]) >= 1):
		return tel[:3]
	if tel[:2] == "05" and (int(tel[2:3]) <= 5 and int(tel[2:3]) >= 1):
		return tel[:3]
	if tel[:2] == "06" and (int(tel[2:3]) <= 4 and int(tel[2:3]) >= 1):
		return tel[:3]
	return -1

# class for whole JSON output
class outputJson:
	def __init__(self, n_results, results):
		self.n_results = n_results
		self.results = results
	def toJSON(self):
	    return json.dumps(self, default=lambda o: o.__dict__, indent=4)

# class for JSON output results part
class outputJsonResults:
	def __init__(self, area_code, numbers):
		self.area_code = area_code
		self.numbers = numbers

if __name__ == "__main__":
	# transfer str to json
	inputJson = json.loads(inputData)

	print(type(inputJson))

	# save recognised words in inputWords
	inputWords = []
	for x in inputJson['result']:
		inputWords.append("".join(x['recognition_words']))


	print(inputWords)
	# remove all char except digits in inputWords and save tel no. in telNos
	telNos = []
	for x in inputWords:
		y = re.sub("[^0-9]", "", x)
		if len(y) > 0:
			telNos.append(y)

	print(telNos)
	# translate data and save in output
	outputResults = []
	for x in telNos:
		validity = checkAreaCode(x)
		if validity != -1:
			if len(validity) == 0:
				result = outputJsonResults(0, x)
			else:
				result = outputJsonResults(1, x)
			outputResults.append(result)
	output_json = outputJson(len(outputResults), outputResults).toJSON()
	output_dict = json.loads(output_json)

	print(output_dict)

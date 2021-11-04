import re
import json

class outputJson:
	def __init__(self, n_results, results):
		self.n_results = n_results
		self.results = results
	def toJSON(self):
	    return json.dumps(self, default=lambda o: o.__dict__, indent=4)

# class for JSON output results part
class outputJsonResults:
    def __init__(self, area_code, numbers, boxes):
        self.area_code = area_code
        self.numbers = numbers
        self.boxes = boxes


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
    if tel[:3] == "070":
        return "070"
    if tel[:2] == "03" and (int(tel[2:3]) <= 3 and int(tel[2:3]) >= 1):
        return tel[:3]
    if tel[:2] == "04" and (int(tel[2:3]) <= 4 and int(tel[2:3]) >= 1):
        return tel[:3]
    if tel[:2] == "05" and (int(tel[2:3]) <= 5 and int(tel[2:3]) >= 1):
        return tel[:3]
    if tel[:2] == "06" and (int(tel[2:3]) <= 4 and int(tel[2:3]) >= 1):
        return tel[:3]
    return -1

def pn_detector(ocr_result: dict):
    inputWords = []
    for x in ocr_result['result']:
        inputWords.append(("".join(x['recognition_words']), x['boxes']))

    # remove all char except digits in inputWords and save tel no. in telNos
    telNos = []
    for x in inputWords:
        y = re.sub("[^0-9]", "", x[0])
        if len(y) > 0:
            telNos.append((y, x[1]))

    # translate data and save in output
    outputResults = []
    for x in telNos:
        validity = checkAreaCode(x[0])
        if validity != -1:
            if len(validity) == 0:
                result = outputJsonResults(0, x[0], x[1])
            else:
                result = outputJsonResults(1, x[0], x[1])
            outputResults.append(result)
    output_json = outputJson(len(outputResults), outputResults).toJSON()
    output_dict = json.loads(output_json)
    return output_dict

# def pn_detector(ocr_result: dict):
#     inputWords = []
#     for x in ocr_result['result']:
#         inputWords.append("".join(x['recognition_words']))

#     # remove all char except digits in inputWords and save tel no. in telNos
#     telNos = []
#     for x in inputWords:
#         y = re.sub("[^0-9]", "", x)
#         if len(y) > 0:
#             telNos.append(y)

#     # translate data and save in output
#     outputResults = []
#     for x in telNos:
#         validity = checkAreaCode(x)
#         if validity != -1:
#             if len(validity) == 0:
#                 result = outputJsonResults(0, x)
#             else:
#                 result = outputJsonResults(1, x)
#             outputResults.append(result)
#     output_json = outputJson(len(outputResults), outputResults).toJSON()
#     output_dict = json.loads(output_json)
#     return output_dict
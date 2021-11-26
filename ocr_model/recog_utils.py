import re
import json
import random

NUMBER_MAP = {
    '1': ['7', '9'],
    '2': ['2', '5'],
    '3': ['2', '8'],
    '4': ['9', '6'],
    '5': ['6', '2'],
    '6': ['5', '0', '8', '6'],
    '7': ['1', '9'],
    '8': ['0', '6'],
    '9': ['4', '7', '1'],
    '0': ['8', '6']
    }


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
        return "" if tel[0] != "0" else -1
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
        return "010" if len(tel) == 10 or len(tel) == 11 else -1
    if tel[:3] == "070":
        return "070" if len(tel) == 10 or len(tel) == 11 else -1
    if tel[:2] == "03" and (int(tel[2:3]) <= 3 and int(tel[2:3]) >= 1):
        return tel[:3] if len(tel) == 10 or len(tel) == 11 else -1
    if tel[:2] == "04" and (int(tel[2:3]) <= 4 and int(tel[2:3]) >= 1):
        return tel[:3] if len(tel) == 10 or len(tel) == 11 else -1
    if tel[:2] == "05" and (int(tel[2:3]) <= 5 and int(tel[2:3]) >= 1):
        return tel[:3] if len(tel) == 10 or len(tel) == 11 else -1
    if tel[:2] == "06" and (int(tel[2:3]) <= 4 and int(tel[2:3]) >= 1):
        return tel[:3] if len(tel) == 10 or len(tel) == 11 else -1
    return -1

def multi_pn_detector(ocr_result: dict):
    inputWords = ocr_result['result']

    # remove all char except digits in inputWords and save tel no. in telNos
    telNos = []
    for x in inputWords:
        y = list(map(lambda z: re.sub("[^0-9]", "", z), x['recognition_words']))
        telNos.append((y, x['boxes']))

    # translate data and save in output
    outputResults = []
    for x in telNos:
        validity = list(map(lambda z: checkAreaCode(z), x[0]))
        real_validity = -1
        area_code = []
        for i in range(len(validity)):
            if validity[i] != -1:
                real_validity = 1
                if len(validity[i]) == 0:
                    area_code.append(0)
                else:
                    area_code.append(1)
            else:
                area_code.append(-1)
        if real_validity != -1:
            result = outputJsonResults(area_code, x[0], x[1])
            outputResults.append(result)

    output_json = outputJson(len(outputResults), outputResults).toJSON()
    output_dict = json.loads(output_json)
    return output_dict

def pn_detector(ocr_result: dict):
    inputWords = []
    for x in ocr_result['result']:
        inputWords.append("".join(x['recognition_words']))

    # remove all char except digits in inputWords and save tel no. in telNos
    telNos = []
    for x in inputWords:
        y = re.sub("[^0-9]", "", x)
        if len(y) > 0:
            telNos.append(y)

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
    return output_dict


def lcs(str1, str2):
    a = len(str1)
    b = len(str2)
    string_matrix = [[0 for i in range(b+1)] for i in range(a+1)]   
    for i in range(1, a+1):
        for j in range(1, b+1):
            if i == 0 or j == 0:
                string_matrix[i][j] = 0
            elif str1[i-1] == str2[j-1]:
                string_matrix[i][j] = 1 + string_matrix[i-1][j-1]
            else:
                string_matrix[i][j] = max(string_matrix[i-1][j], string_matrix[i][j-1])
    index = string_matrix[a][b]
    res = [""] * index
    i = a
    j = b
    while i > 0 and j > 0:
        if str1[i-1] == str2[j-1]:
            res[index-1] = str1[i-1]
            i -= 1
            j -= 1
            index -= 1
        elif string_matrix[i-1][j] > string_matrix[i][j-1]:
            i -= 1
        else:
            j -= 1
    return ''.join(res)


def find_different(text, subsquence):
    a = len(text)
    b = len(subsquence)
    result = []
    j = 0
    for i in range(0, a):
        if j < b and text[i] == subsquence[j]:
            j += 1
            continue
        else:
            result.append(i)
    return result

def generate_number(number1, number2):
    subsquence = lcs(number1, number2)
    differ_1 = find_different(number1, subsquence)
    differ_2 = find_different(number2, subsquence)
    if len(number1) == len(number2):
        if len(differ_1) > 1:
            change_idx = random.choice(differ_1)
            new_number = number1[:change_idx]+number2[change_idx]+number1[change_idx+1:]
            
        else:
            change_idx = min(differ_1+differ_2)
            candidates = NUMBER_MAP[number1[change_idx]][:]
            if number2[change_idx] in candidates:
                candidates.remove(number2[change_idx])
            new_number = number1[:change_idx]+random.choice(candidates)+number1[change_idx+1:]
                
    elif len(number1) > len(number2):
        change_idx = random.choice(differ_1)
        new_number = number1[:change_idx]+random.choice(NUMBER_MAP[number1[change_idx]])+number1[change_idx+1:]

    elif len(number1) < len(number2):
        change_idx = random.choice(differ_2)
        new_number = number2[:change_idx]+random.choice(NUMBER_MAP[number2[change_idx]])+number2[change_idx+1:]
    return new_number

def generate_random_number(number):
    digits = list(range(1, 8))
    change_idx1 = digits.pop(digits.index(random.choice(digits)))
    change_idx2 = digits.pop(digits.index(random.choice(digits)))
    # print(change_idx1, change_idx2)

    new_number1 = number[:-change_idx1]+random.choice(NUMBER_MAP[number[-change_idx1]])
    new_number2 = number[:-change_idx2]+random.choice(NUMBER_MAP[number[-change_idx2]])
    if change_idx1 > 1:
        new_number1 = new_number1+number[-change_idx1+1:]
    if change_idx2 > 1:  
        new_number2 = new_number2+number[-change_idx2+1:]

    # print(new_number1, new_number2)
    return new_number1, new_number2

def add_dash(number, is_area_code):
    new_number = number[:-4]+'-'+number[-4:]
    if is_area_code == 1:
        if number[:2] == '02':
            new_number = new_number[:2]+'-'+new_number[2:]
        else:
            new_number = new_number[:3]+'-'+new_number[3:]
    return new_number
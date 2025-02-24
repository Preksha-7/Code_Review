import requests

url = "http://localhost:8000/review/analyze"

# Intentionally bad code: Missing indentation, syntax errors, and incorrect variable usage
wrong_code = """
str = list(map(input("Enter the string : ")))
count = 1
c = int(input("Enter the location from which the count needs to start : "))
for i in range(c, len(str)):
    for j in range(i+1,len(str)):
        if str[i] == str[j]:
            count += 1
            str[j] = 0
    if str[i] != 0:
        print(str[i], " appears ", count, " times")
        count = 1

"""

data = {"code": wrong_code}

response = requests.post(url, json=data)

print(response.json())  # Check if the analysis detects issues

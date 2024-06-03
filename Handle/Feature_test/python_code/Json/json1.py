import json
from collections import OrderedDict as ORD
book_json = {
        "id" : 1,
        "title" : "Python of Kim Young Rae",
        "author" : "kyr",
        "price" : 10000,
        "date" : {
            "start" : "2024-02-24",
            "end" : "2024-04-03",
        }
}


book_string = '{"id":1,"title":"Python of Kim Young Rae","author":"kyr","price":10000,"date":{"start":"2024-02-24","end":"2024-04-03"}}'

# Example 1: How to get item in Object
print("[Example 1]")
print(book_json["id"])
print(book_json["date"]["start"])
print()




# Example 2: How to convert from "Json" to "String"   json.dumps(Json)
string = json.dumps(book_json)
print("[Example 2]")
print(string)
print()

# Example 3: How to convert from "String" to "Json"   json.loads(String)
jsonjson = json.loads(book_string)
print("[Example 3]")
print(jsonjson)
print()



# Example 4: How to make "json" from data 
send_data = ORD()
degree = 180
name = "kyr"
onDate = "2027-03-24"


send_data["degree"] = degree
send_data["name"] = name
send_data["date"] = onDate

json3 = json.dumps(send_data)
print("[Example 4-1]")
print(json3)
print()

send_data2 = ORD()
a = 180
b = 'asd'
c = "fgh"

send_data2['a'] = a
send_data2["b"] = b
send_data2['c'] = c

json4 = json.dumps(send_data2)
print("[Example 4-2]")
print(json4)
print()




# Example 5: How to make "string" from data
send_data3 = ''
send_data3 += '{'
send_data3 += '"name"'
send_data3 += ':'
send_data3 += '"kyr"'
send_data3 += '}'
print("[Example 5]")
print(send_data3)
print()

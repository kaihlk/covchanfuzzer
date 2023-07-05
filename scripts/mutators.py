#fuzzer.py
#methods to mutate inputs

import random

#Generate String
#Parameter: Allowed Signs
#Max Length, Min Length


#Mutate String
#Change Case
#Slice and Switch
#Delete Char
#Add Char
#Switch Chars

def delete_random_char(s: str) -> str:
    if s=='':
        return s
    pos = random.randint(0, len(s) - 1)
    return s[:pos] + s[pos + 1:]

def insert_random_char(s: str) -> str:
    pos = random.randint(0, len(s) - 1)
    
    return s[:pos] + s[pos + 1:]


def insert_random_char(s: str, range: str) -> str:
    if s=='':
        return s
    pos = random.randint(0, len(s) - 1)
    return s[:pos] + s[pos + 1:]


def random_switch_case_of_char_in_string(original_string, fuzzvalue):
    modified_string=''
    deviation_count=0
    # Randomly change the case of the field name
    for c in original_string:
        #The value of the probabiltiy to change a char is defined by the fuzzvalue
        #the char functions doesn't affect signs and symbols
        if random.random()<fuzzvalue:
            if c.isupper():
                modified_string=modified_string + c.lower()
                deviation_count+=1
            elif c.islower:
                modified_string=modified_string + c.upper()
                deviation_count+=1
            else:
                modified_string = modified_string + c
        else:
            modified_string = modified_string + c
    return modified_string, deviation_count

#Integer, max/min Size

#List
#Add Entry
#Delete Entry
#Switch Entries
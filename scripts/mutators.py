#fuzzer.py
#methods to mutate inputs

import random
""" print(SampleString)
    print(mutators.delete_random_char(SampleString))
    print(mutators.insert_random_char(SampleString))
    print(mutators.random_switch_case_of_char_in_string(SampleString))
    print(mutators.random_switch_chars(SampleString))
    print(mutators.random_slice_and_swap_string(SampleString))
    print(SampleString+mutators.generate_random_string(" \t", random.randint(0,10))+"<--")
    print(mutators.generate_random_string(SampleString, 15)) """

####String Mutation####

def delete_random_char(s: str) -> str:
    # Deletes Random Char
    if s=='':
        return s
    pos = random.randint(0, len(s) - 1)
    return s[:pos] + s[pos + 1:]


def insert_random_char(s: str, start=32, end=127) -> str:    
    # Inserts a random Char at a random position
    pos = random.randint(0, len(s) - 1)
    random_char = chr(random.randint(start, end))
    return s[:pos] + random_char + s[pos + 1:]

def random_switch_case_of_char_in_string(s: str) -> str : 
    # Change the case of a char at a random position 
    pos = random.randint(0, len(s) - 1)
    c=s[pos]
    if c.isupper():
        return s[:pos] + c.lower() + s[pos+1:]
    elif c.islower():
        return s[:pos] + c.upper() + s[pos+1:]
    else:
        return s

def random_switch_chars(s: str) -> str : 
    # Switch two chars in a string
    if len(s)<2:
        return s
    pos1 = random.randint(0, len(s) - 1)
    pos2 = random.randint(0, len(s) - 1)
    # Make sure both values differ
    while pos2 == pos1:
        pos2 = random.randint(0, len(s) - 1)
    # Make sure pos1 < pos2
    if pos1 > pos2:
        pos1, pos2 = pos2, pos1
    # Build string
    return s[:pos1] + s[pos2] + s[pos1+1:pos2] +s[pos1] + s[pos2+1:]

def random_slice_and_swap_string(s: str) -> str : 
    # Slice a string into two parts and swap them
    if len(s)<2:
        return s
    pos = random.randint(0, len(s) - 1)
    return s[pos:] + s[:pos]

def generate_random_string(char_set: str, length: int, minlength=0) -> str :
    # Generate a random string from a charse
    random_chars = [random.choice(char_set) for _ in range(minlength, length)]
    return ''.join(random_chars)


#### List Mutatations #### 

def delete_random_entry(kv_list: list) -> list:
    # Deletes a Random Entry from the Key-Value List
    if not kv_list:
        return kv_list   
    pos = random.randint(0, len(kv_list) - 1)
    del kv_list[pos]
    return kv_list

def insert_random_entry(kv_list: list, value_list: list) -> list:
    # Inserts a Random Entry with a Random Value from Another List
    if not value_list:
        return kv_list    
    pos = random.randint(0, len(kv_list))
    random_entry = random.choice(value_list)  
    kv_list.insert(pos, random_entry)
    return kv_list

def switch_random_entries(kv_list: list) -> list:
    # Switches Two Random Entries in the Key-Value List
    if len(kv_list) < 2:
        return kv_list

    pos1 = random.randint(0, len(kv_list) - 1)
    pos2 = random.randint(0, len(kv_list) - 1)
    
    while pos2 == pos1:
        pos2 = random.randint(0, len(kv_list) - 1)
    
    kv_list[pos1], kv_list[pos2] = kv_list[pos2], kv_list[pos1]
    return kv_list


#### Integer Mutation ####

#Integer, max/min Size, zero, negative

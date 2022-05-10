
import re

def split_search_term(search_term):
    """ Take the search term and return a list of each element( and, word, paranthesis, etc) in order
    and dictionnary where the key is a keyword and the value is a list. It will fill with id of article
    """

    return_list = []
    return_dict = dict()

    size_term = len(search_term)
    position = 0

    while position < size_term:

        c = search_term[position]
        if c =="(":
            return_list.append(c)
            position += 1
        elif c == ")":
            return_list.append(c)
            position +=1
        elif c == " ":
            position += 1
        elif c == "\"":
            chaine = "\""
            position += 1
            while position < size_term:
                if search_term[position] == "\"":
                    chaine += "\""
                    position += 1
                    break
                else:
                    chaine += search_term[position]
                    position += 1
            return_list.append(chaine)
            return_dict[chaine] = []
        elif c == ";":
            return_list.append("OR")
            position += 1
        elif c == ",":
            return_list.append("AND")
            position += 1
        elif re.findall("[a-zA-Z0-9\-]",c):
            chaine = c
            position +=1
            while position < size_term:
                d = search_term[position]
                if re.findall("[a-zA-Z0-9\-]",d):
                    chaine += d
                    position += 1
                else:
                    return_list.append(chaine)
                    return_dict[chaine] = []
                    break
                # if this is the last word, if there is no space in last character, the last word is not count
                if position >= size_term:
                    return_list.append(chaine)
                    return_dict[chaine] = []
                    break
        else:
            position += 1

    return return_list, return_dict


def parsing(list_term, dict_keyword):
    """ Input: a list of element for parsing and a dictionnary for each keywords, we have a list of number.
        Output: a list of number who correspond of the parsing's result
        This method works in reccurance call. It returns the result of logical calcul between 
        the first term and the rest."""
    

    size = len(list_term)
    position = 0

    first_term_elements = []

    #if the first term is in a parenthesis
    if list_term[position] == "(":
        # we recuperate all the sub string in the parenthesis
        sub_string = ""
        number_parenthesis = 0
        position += 1
        list_sub_term = []
        while position < size:
            if number_parenthesis == 0 and list_term[position] == ')':
                position += 1
                break
            elif list_term[position] == '(':
                number_parenthesis += 1
            elif list_term[position] == ')':
                number_parenthesis -= 1

            list_sub_term.append(list_term[position])
            position += 1
        #we call this method
        first_term_elements = parsing(list_sub_term,dict_keyword)
        

    # else we asociate the first term elements with the number associate with the first keyword
    else:
        first_term_elements = dict_keyword[list_term[position]]
        position += 1

    #if the position reached the end, so there are no logical operation,
    #we return the list of the first term
    if position >= size :
        return first_term_elements
    
    #we recuperate the logical operation if exists
    logic_op = list_term[position]
    position += 1

    # we define the second element
    # if this is the last keyword
    second_term_elements = []
    if position + 1 >= size:
        second_term_elements = dict_keyword[list_term[position]]
    #else we call the method with the same dictionnary and the second part of the list to parsing
    else:
        second_term_elements = parsing(list_term[position:],dict_keyword)

    
    #Now, we have two list of number and the logical operation. We execute the logical operation and return a list
    return_list = []
    list_a = []
    list_b = []
    # the list who will be for each is the shorter one
    if len(first_term_elements) > len(second_term_elements):
        list_a = second_term_elements
        list_b = first_term_elements
    else:
        list_a = first_term_elements
        list_b = second_term_elements

    if logic_op == "AND":
        #we check if there are the element in the two list.
        for e in list_a:
            if e in list_b:
                return_list.append(e)
        
    elif logic_op == "OR":
        #we check if the element is already in final list. If yes, we don't add again
        return_list = list_b
        for e in list_a:
            if not e in return_list:
                return_list.append(e)
    
    #we return the list of number

    return return_list


#!/usr/bin/env python
# coding: utf-8

# In[125]:


import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import sys
import random

#get_vakio() will parse data from tekstitv site.
def get_vakio_odds():
    url = 'https://yle.fi/tekstitv/txt/479_0001.htm'
    try:
        response = requests.get(url)
    except:
        return None
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        boxbox = soup.find('div', {'class': 'boxbox'})
        if boxbox:
            boxbox_content = boxbox.text
            print(boxbox_content)
        else:
            print('Error: Could not find "boxbox" element')
    else:
        print('Error: Could not get content of HTML file')

    string = str(boxbox_content)
    pattern = r"\d+\s+\d+\s+\d+"  # match three numbers with spaces between them

    matches = re.findall(pattern, string)

    if matches:
        all_numbers = []
        for match in matches:
            numbers_list = match.split()
            numbers = [int(n) for n in numbers_list]
            all_numbers.append(numbers)
        new_list = np.array(all_numbers)
        new_list = new_list/100
        for i in range(len(new_list[:,0])):
            if np.sum(new_list[i,:]!= 1.0):
                new_list[i,2] = new_list[i,2]+ 1 - np.sum(new_list[i,:]) #round the error
        a=0
  
    return new_list

def system(size):
    input_full = int(input("Täysin vaihdellut: "))
    input_partial = int(input("Osittain vaihdellut: "))
    if input_full + input_partial > size:
        sys.exit("Väärä systeemi, liian monta vaihdeltua kohdetta.")    
    else:
        return input_full,input_partial

def makesheet(size):
    row = np.array([" ", " ", " "])
    sheet = np.array([" ", " ", " "])
    for i in range(size-1):
        sheet = np.vstack((sheet,row))    
    return sheet

def sort_odds(sheet,new_list, types):
        subtract = []
        for i in range(size):
            subtract = np.append(subtract, new_list[i,0]+new_list[i,1])
        diff = np.abs(subtract - 0.666)
        # Get the indices that would sort the absolute differences in ascending order
        sorted_indices = np.argsort(diff)
        # Get the three closest values by indexing the data array with the sorted indices
        closest_values = subtract[sorted_indices[:types]]

        return sorted_indices


#Build the system:
def build_system(new_list,size,full,partial,sheet):
    valinta = np.array([1,"x",2])
    rivi = []
    for i in range(size):
        rivi = np.append(rivi, np.random.choice(valinta,p=new_list[i,:]))
    for i in range(size):
        if rivi[i] == "1":
            sheet[i,0] = "1"
        elif rivi[i] == "x":
            sheet[i,1] = "x"
        else:
            sheet[i,2] = "2"
    if full == 0 and partial == 0:
        return sheet
    if full != 0: #Construct full rows. Find the most even odds and fill them
        #Find the addition: the closest to 0.66 will be chosen for full rows
        sorted_indices = sort_odds(sheet, new_list,full)
        for i in range(full):
            sheet[sorted_indices[i],:] = ["1","x","2"]        
        
    if partial != 0:
        #Plan. Random choice between 0&12. find what is the row mark. There has to be only one mark. use subtract
        #array.
        if full == 0:
            sorted_indices = sort_odds(sheet,new_list,partial)
        else:
            for i in range(full): #First delete the indices used in full changed rows.
                sorted_indices = np.delete(sorted_indices,0,0)
        for i in range(partial):
            mark = set(sheet[sorted_indices[i],:]) - {" "}  #Find the current row mark
            mark = mark.pop()
            if mark == "1":
                new_mark =random.choices(["x","2"],weights=new_list[sorted_indices[i],1:3])[0]
            elif mark == "x":
                weights = [new_list[sorted_indices[i],0], new_list[sorted_indices[i],-1]]
                new_mark =random.choices(["1","2"],weights=weights)[0]
            elif mark == "2":
                new_mark =random.choices(["1","x"],weights=new_list[sorted_indices[i],0:2])[0]
            
            #Set the new mark:
            if new_mark == "1":
                sheet[sorted_indices[i],0] = new_mark
            elif new_mark == "x":
                sheet[sorted_indices[i],1] = new_mark
            else:
                sheet[sorted_indices[i],2] = new_mark
            
                #Make a random pick based on p,
      
        
    
    return sheet

#Download the target list and odds: Check if the list is valid.
new_list = get_vakio_odds()
if new_list is None:
    sys.exit("Riviä ei löytynyt")
#Size of the game (usually 12 or 13 targets)
size = len(new_list)
print("Vakion kohdemäärä", size)
#---------------------------------------------------------------------
#Define the size of the system.
full,partial = system(size)
#Make the empty gamesheet
sheet = makesheet(size)

sheet = build_system(new_list,size,full,partial,sheet)
print(sheet)


# In[115]:


print(new_list[3,0:-1])

#print(random_character)


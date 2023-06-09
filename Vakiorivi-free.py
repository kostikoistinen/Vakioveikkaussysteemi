#!/usr/bin/env python
# coding: utf-8

# In[1]:


##### import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import sys
import random
#import matplotlib.pyplot as plt
import copy
import pandas as pd
import numpy as np
import tkinter
import PIL._tkinter_finder
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import time
from IPython.display import display
# Simulating a long-running task
#Todo: Etsi get_vakio_odds() funktiosta vaihto:

#get_vakio() will parse data from tekstitv site.
def get_vakio_odds():
    url = 'https://yle.fi/tekstitv/txt/479_0001.htm'
    #url = 'https://yle.fi/tekstitv/txt/479_0002.htm'
    try:
        response = requests.get(url)
    except:
        print("No list found, Check your internet connection.")
        return None, 100
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
    pattern2 = r'0,[0-9]{2}'      # Get a pattern of rivihinta
    
    try:
        matches3 = re.findall("vaihto", string) #Try to find vaihtosumma
    except:
        print("Vaihtoa ei saatavilla.")
        matches3 = False
    
    matches2 = re.findall(pattern2, string)
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
    if matches3:
        startindex = string.index(' '.join(matches3))
        startindex = 7+startindex
        result = int(''.join([char for char in string[startindex:startindex+10] if char.isdigit()]))
    else:
        result = 0
    
    if matches2:
        return new_list,float(matches2[0].replace(",", ".")),result
    else:
        return new_list, 0,result

def system(size):
    try:
        input_full = int(input("Täysin vaihdellut: "))
    except:
        print("Error with input, choosing 0")
        input_full = 0
    try:
        input_partial = int(input("Osittain vaihdellut: "))
    except:
        print("Error with input, choosing 0")
        input_partial = 0

    if input_full + input_partial > size:
        sys.exit("Väärä systeemi, liian monta vaihdeltua kohdetta.")    
    else:
        print("Järjestelmäsi: ", input_full, "X", input_partial)
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
            subtract = np.append(subtract, max(new_list[i,0]+new_list[i,1],
                                                  new_list[i,1]+new_list[i,2] ))
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
            else: # mark == "2":
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

#Defining the voitonjako
palautus = 0.63
house = 1-palautus
arr_13 = [0.26,0.13,0.09,0.15]
arr_12 = [0.31,0.18,0.14]
arr_11 = [0.39,0.24]
arr_10 = [0.39, 0.24]

#Download the target list and odds: Check if the list is valid.
new_list, cost, exchange = get_vakio_odds()
if cost==0:
    cost = float(input("Rivihintaa ei löytynyt, määritä rivihinta käsin (esim. 0.25): "))
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
#Make the system
sheet = build_system(new_list,size,full,partial,sheet)

print("  Arvottu rivi")
print("-----------------------------------")
i=0
while i<len(sheet):
    print(i+1,". ","\t", sheet[i,:])
    i=i+1
def getprize(size,full,partial):
    if partial == 0 and full == 0:
        return 1
    elif full == 0 and partial != 0:    
        return 2**partial
    elif partial == 0 and full != 0:
        return 3**full
    else:
        return (2**partial)*(3**full)   
print("-----------------------------------")    
prize = round(cost*getprize(size,full,partial),2)
print("Rivien määrä:", getprize(size,full,partial))
print("Lapun hinta: ", prize, " euroa")

def check_sheet(sheet,correct_row):
    right=0
    for i in range(len(correct_row)):
        if correct_row[i] in sheet[i,:]:
            right=right+1
    return right

def simulate(new_list,size,full,partial):
    import time
    import progressbar
    #This is beta version.
    #Correct row:
    valinta = np.array([1,"x",2])
    correct_row = []
    for i in range(size):
        correct_row = np.append(correct_row, np.random.choice(valinta,p=new_list[i,:]))
    labels = []
    exit= False
    #Simuloi lappuja, vaikkapa 1000:
    i=0
    correct = []
    correct3 = []
    length=1000
    results = np.zeros(length)
    results3 = np.zeros(length)
    two=0
    three=0
    result = np.zeros(length)
    correct_o = []
    result_own = np.zeros(length)
    '''
    Currently not in use. In the future there will be a subroutine that counts the gradient between each system.
    It will then decide which system provides the best profit vs.prize.
    while two < 14:
        while three < 14:
            labels = np.append(labels, str(three)+"X"+str(two))
            while i<length:
                if two+three == 13:
                    two = two + 1
                    if two >= 13:
                        print("täällä")
                        exit = True
                    three = 0
                if exit:
                    break
                
                sheet = makesheet(size)
                sheet = build_system(new_list,size,three,two,sheet)
                correct = np.append(correct, check_sheet(sheet,correct_row))
                i=i+1
            i=0
            if exit:
                break
            result = np.vstack((result,copy.deepcopy(correct)))
            correct = []
            three = three+1
        two = two +1
        three = 0
        if exit:
            break

    result = np.delete(result,0,0)
    print(labels)
    n_arrays = len(result/length)
    
    sliced_arrays = np.array_split(result, n_arrays)
    sliced_arrays = np.array(sliced_arrays)
    #for i, slice_arr in enumerate(sliced_arrays):
        #print(f"Slice {i+1}: {slice_arr}")
    #print(np.shape(sliced_arrays))
    #print(sliced_arrays[0,:,:])
    sliced_arrays = np.transpose(sliced_arrays,(2, 1, 0))
    a=0
    #for i in range(n_arrays):
    i=0
    j=0
    while i<n_arrays:
        df = pd.DataFrame(sliced_arrays[:,0,i:i+13-a])  
        i = i+13-a
        a=a+1
        summary = df.describe()
        print("suma", summary)
        means = summary.loc['mean'].values
        std = summary.loc['std'].values
        plt.plot(means, label = labels[j])
        print("STATUS; ", i)
        j=j+1        
                
    #for i in range(1):
    #    print(i, n_arrays)
        #(91, 1, 100)
        #print(type(sliced_arrays))
        #reshaped_arr = sliced_arrays.reshape(91, 100)
        #df = pd.DataFrame(reshaped_arr)
        #df = pd.DataFrame(sliced_arrays[i,:,:])
    #    df = pd.DataFrame(sliced_arrays[:,0,i:i+12-a])
    #    i = i+12-a
    #    a=a+1
    #    print(df)

     #   summary = df.describe()
      #  print("suma", summary)
       # means = summary.loc['mean'].values
        #std = summary.loc['std'].values
       # plt.plot(means, label = labels[i])
    plt.legend()
    plt.show()
    
    print(sliced_arrays[0,:,0])
    #result = np.transpose(result)
    #df = pd.DataFrame(result)
    #summary = df.describe()
    #means = summary.loc['mean'].values

    #plt.plot(result)    
    '''
    print("Odota hetki, simulaatio käynnissä...")
    widgets = [progressbar.Bar("|"), '', progressbar.Percentage(), '', progressbar.Timer()]
    progress = progressbar.ProgressBar(max_value=14, widgets=widgets).start()
    while two < 14:
        time.sleep(0.1)  # Simulating some work
        progress.update(two+1)
        while i<length:

            # Call the function
            #Clear sheet
            sheet = makesheet(size)
            #Make the system
            sheet = build_system(new_list,size,0,two,sheet)
            #Check correct
            correct = np.append(correct, check_sheet(sheet,correct_row))

            sheet = makesheet(size)
            #Make the system
            sheet = build_system(new_list,size,three,0,sheet)
            correct3 = np.append(correct3, check_sheet(sheet,correct_row))
            #Simulate own system:
            sheet = makesheet(size)
            sheet = build_system(new_list,size,full,partial,sheet)
            correct_o = np.append(correct_o, check_sheet(sheet,correct_row))
            
            i=i+1
               
        #plt.hist(correct, bins = np.arange(5,14), label = str(two), zorder = three)
        three=three+1
        two=two+1
        
        result_own = np.vstack((result_own,copy.deepcopy(correct_o)))
        results = np.vstack((results,copy.deepcopy(correct)))
        
        results3 = np.vstack((results3,copy.deepcopy(correct3)))
        correct = []
        correct3 = []
        correct_o = []
        i=0

    progress.finish()

    result_own = np.delete(result_own,0,0)
    results = np.delete(results,0,0)
    results3 = np.delete(results3,0,0)

    result_own = np.transpose(result_own)
    results = np.transpose(results)
    results3 = np.transpose(results3)
    df = pd.DataFrame(results,columns=[np.arange(0,14)])
    df3 = pd.DataFrame(results3,columns=[np.arange(0,14)])
    dfo = pd.DataFrame(result_own)
    # Get the summary statistics
    summary_o = dfo.describe()
    summary,summary3 = df.describe(), df3.describe()
    summary,summary3 = summary.drop('count'),summary3.drop('count') 
    summary,summary3 = summary.round(2),summary3.round(2)
    

    means, means3,mean_o = summary.loc['mean'].values,summary3.loc['mean'].values, summary_o.loc['mean'].values
    mean_o = np.mean(mean_o)
    std, std3, std_o = summary.loc['std'].values,summary3.loc['std'].values,summary_o.loc['std'].values
    std_o = np.mean(std_o)
    
    #plt.legend()
    #plt.show()
    # Plot the means
    plt.plot(means, zorder=5, color="blue", label="Osittain vaihdeltu")
    plt.plot(means3, zorder=5, color="green", label="Täysin vaihdeltu")
    # Add labels and title to the plot

    plt.title('Järjestelmien odotusarvot 95% virheineen')
    x = np.arange(0,14)
    plt.xticks(x,np.arange(0,14))
    plt.fill_between(np.arange(0,len(means)), means+2*std,means-2*std, color="lightblue", alpha=0.3,zorder=2)
    plt.fill_between(np.arange(0,len(means3)), means3+2*std3,means3-2*std3, color="lightgreen", alpha=0.3,zorder=2)
    plt.fill_between([0,0],[0,0],[0,0], color = "grey", label = "95% luottamusväli")
    
    plt.xlabel("Systeemin koko")
    plt.ylabel("Oikeita tuloksia")
    
    plt.ylim(4,13.5)

    plt.errorbar([np.sum([full,partial])], [mean_o], yerr = [2*std_o], fmt = "o", 
            ecolor = 'red', elinewidth = 0.5, capsize=5, label="Sinun järjestelmäsi: "+str(full)+"x"+str(partial))
    plt.yticks([4,5,6,7,8,9,10,11,12,13],[4,5,6,7,8,9,10,11,12,13])
    plt.axhline(y=13, color='red', linestyle='--')
    plt.legend()
    plt.text(0.9, -0.2, "Sulje ikkuna jatkaaksesi simulaatiota...", ha='center', va='center', transform=plt.gca().transAxes)
    plt.tight_layout()
    plt.show()
    return mean_o, 2*std_o,correct_row
    


def simulate2(exchange,cost,mean,std,new_list,size,correct_row):
    input3 = input("Haluatko simuloida myös arvioitua voitonjakoa? Koko vaihto simuloidaan. Tässä voi kestää n. 60 minuuttia (k/e)?")
    #exchange=100000
    if input3 != "k":
        return "Ohjelma päättyy"
    if exchange == 0:
        return "Voittoa ei voida määrittää, koska vaihtoa ei tiedetä. Ohjelma päättyy."
    simu_length = int(exchange/cost)
    print("Simulaatio käynnissä")
    #do the simu
    i=0
    correct = []
    start_time = time.time()
    sheet0 = makesheet(size) # blank sheet
    while i<simu_length:
        sheet = makesheet(size) #blank sheet
        #Make the system
        sheet = build_system(new_list,size,0,0,sheet)
        #Check correct
        correct = np.append(correct, check_sheet(sheet,correct_row))        

        # Your code for a single iteration
        end_time = time.time()
        elapsed_time = end_time - start_time
        start_time = end_time
        if i%int(simu_length/20)==0:
            print("Simulaatiosta valmiina", round(100*i/simu_length),"%",
                  ", Simulaatiota arviolta jäljellä: ", round(elapsed_time*(simu_length-i)), " s" )
        end_time = time.time()
        elapsed_time = end_time - start_time
        start_time = end_time
        
        i=i+1

    #Result:
    if np.max(correct)==13:
        #Voitonjako 13:n mukaan: Etsi kuinka monta.
        num13,win13 = np.count_nonzero(correct == 13), exchange*arr_13[0]/np.count_nonzero(correct == 13)
        num12,win12 = np.count_nonzero(correct == 12), exchange*arr_13[1]/np.count_nonzero(correct == 12)
        num11,win11 = np.count_nonzero(correct == 11), exchange*arr_13[2]/np.count_nonzero(correct == 11)
        num10,win10 = np.count_nonzero(correct == 10), exchange*arr_13[3]/np.count_nonzero(correct == 10)
        num9,win9 = np.count_nonzero(correct == 9),0
    elif np.max(correct)==12:
        #Voitonjako 12:n mukaan: Etsi kuinka monta.
        num13,win13 = 0,0
        num12,win12 = np.count_nonzero(correct == 12), exchange*arr_12[0]/np.count_nonzero(correct == 12)
        num11,win11 = np.count_nonzero(correct == 11), exchange*arr_12[1]/np.count_nonzero(correct == 11)
        num10,win10 = np.count_nonzero(correct == 10), exchange*arr_12[2]/np.count_nonzero(correct == 10)
        num9,win9 = np.count_nonzero(correct == 9),0
    elif np.max(correct)==11:
        num13,win13 = 0,0
        num12,win12 = 0,0
        #Voitonjako 11:n mukaan: Etsi kuinka monta.
        num11,win11 = np.count_nonzero(correct == 11), exchange*arr_11[0]/np.count_nonzero(correct == 11)
        num10,win10 = np.count_nonzero(correct == 10), exchange*arr_11[1]/np.count_nonzero(correct == 10)
        num9,win9 = np.count_nonzero(correct == 9),0
    elif np.max(correct)==10:
        num13,win13 = 0,0
        num12,win12 = 0,0
        num11,win11 = 0,0
        #Voitonjako 10:n mukaan: Etsi kuinka monta.
        num10,win10 = np.count_nonzero(correct == 10), exchange*arr_10[0]/np.count_nonzero(correct == 10)
        num9,win9 = np.count_nonzero(correct == 9), exchange*arr_10[1]/np.count_nonzero(correct == 9)
    else:
        print("Kenelläkään ei edes 10 oikein, voittoja ei jaeta.")
    
    taulu = [[13,12,11,10,9],[num13,num12,num11,num10,num9], [win13,win12,win11,win10,win9]]
    df = pd.DataFrame(taulu,index=["Oikein","Lkm", "Voitto"])
    df.columns = ["","","","",""]
    df.style.set_caption('Arvio voitonjaosta')
    df = df.round()
    print("")
    print("Arvio voitonjaosta:")
    pd.set_option('display.max_columns', None)  # Display all columns
    pd.set_option('display.width', None)  # Remove width restriction
    display(df)
    
    
    
    
    
    
    
    
    
    
    
    
    #Huom. Tee simulaatio vielä pelaajan valitsemalla x+x systeemillä!
    
mean,std,correct_row = simulate(new_list,size,full,partial)
simulate2(exchange,cost, mean,std,new_list,size,correct_row)
# simulaatio?



# Simuloi oikeita tuloksia, etsi paras lappu, jolla paras tulos.



# Tee statistiikka kuinka monta oikeaa riviä, systeemeillä 
# Make new sheet -> Make new system, check the right results.

#UNCOMMENT TO PLOT 2x0,1,2...13 visible.


# In[ ]:





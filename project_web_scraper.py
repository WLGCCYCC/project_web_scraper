
# coding: utf-8

# In[ ]:

########Import Modules#########
import requests
from math import ceil
from bs4 import BeautifulSoup
import xlsxwriter
import pathlib
import os

# In[ ]:

######Start Up Function#########
def inform_input():
    global f_type
    global f_city
    global f_state

    correct_input = False

    while correct_input != True:

        f_type = input('What type of firms do you want to search? (example: asset management)\nFirm type: ')
        print ('\n')

        f_city = input("Which city do you want to search? (example: Los Angeles)\nHint: If you want to search an entire state, then type 'ALL.'\nCity: ")
        print ('\n')

        f_state = input('Which state do you want to search? (example: CA)\nState: ')
        print ('\n')

        print ('Searching...'+f_type+' in '+f_city+','+f_state+'.\n')
        correct_input = input('Is the key words correct? [Y/N]\nAnswer: ')
        print ('\n')

        if correct_input.upper() == 'Y':
            correct_input = True


# In[ ]:

def get_url(firm_type,firm_city,firm_state):
    
    print ('creating url......')
    
    firm_type = firm_type.lower()
    firm_city = firm_city.lower()
    firm_state = firm_state.upper()

    firm_type = firm_type.split()
    firm_city = firm_city.split()

    ##basic form of url'https://www.yellowpages.com/search?search_terms=asset%20management&geo_location_terms=los%20angeles%2C%20CA&page=1'

    url = 'https://www.yellowpages.com/search?search_terms='

    url += firm_type.pop(0)
    while len(firm_type)!=0:
        url += '%20'+firm_type.pop(0)

    url += '&geo_location_terms='

    url += firm_city.pop(0)
    while len(firm_city)!=0:
        url += '%20'+firm_city.pop(0)
    
    url += '%2C%20'+firm_state+'&page='
    
    print ('creating url......done!')
    return url


# In[ ]:

def get_page_number(soup):
    
    print ('finding total page number......')
    total_results = soup.find_all('div',{"class":"pagination"})

    total_results = total_results[0].contents[0].text


    total_results = total_results.split()

    total_results = total_results.pop()

    total_results = int(total_results.replace('results',''))
    
    print ('finding total page number......'+str(ceil(total_results/30)))

    return ceil(total_results/30)



# In[ ]:

def get_contact_inform(url):
    
    global firm_name
    global firm_adr
    global firm_web
    global firm_phone
    r = requests.get(url)

    soup = BeautifulSoup(r.content,'html5lib')

    g_data = soup.find_all('div', {'class':'info'})
    ######################get name#################
    for item in g_data:
        try:
            firm_name.append(str(item.contents[0].find_all('a',{'class':'business-name'})[0].text))
        except:
            firm_name.append('N/A')

    ######################get address#################
    for item in g_data:
        try:
            address = ''
            address += str(item.contents[1].find_all('span',{'class':'street-address'})[0].text) + ','
            address += str(item.contents[1].find_all('span',{'itemprop':'addressLocality'})[0].text).replace('\xa0','')
            address += str(item.contents[1].find_all('span',{'itemprop':'addressRegion'})[0].text) + ','
            address += str(item.contents[1].find_all('span',{'itemprop':'postalCode'})[0].text)

            firm_adr.append(address)
        except:
            firm_adr.append('N/A')

    ####################get phone number###################
    for item in g_data:
        try:
            firm_phone.append(str(item.contents[1].find_all('div',{'itemprop':'telephone'})[0].text))
        except:
            firm_phone.append('N/A')

    ####################get website###################
    for item in g_data:
        try:
            firm_web.append(str(item.contents[2].find_all('a',{'class':'track-visit-website'})[0].get('href')))
        except:
            firm_web.append('N/A')


# In[ ]:

def get_city_list(s):
    from city_to_state import city_to_state_dict as c_to_s

    from abbrev_to_state import states as s_to_a

    city_list = []


    for city, state in c_to_s.items():
        if state  == s_to_a[s.upper()]:
             city_list.append(city)
    
    
    return city_list


# In[ ]:

def del_dup_elements():
    
    print("deleting duplicated information......")
    
    global firm_name
    global firm_adr
    global firm_web
    global firm_phone
    
    index_dup = []

    for i in range(len(firm_adr) - 1):

        for j in range(i+1,len(firm_adr)):

            if firm_adr[j] == firm_adr[i]:
                if firm_name[j] == firm_name[i]:
                    if firm_phone[j] == firm_phone[i]:
                        if firm_web[j] == firm_web[i]: 
                            index_dup.append(i)
                            break



    for i in range(len(index_dup)):


        firm_adr.pop(index_dup[i])
        firm_name.pop(index_dup[i])
        firm_phone.pop(index_dup[i])
        firm_web.pop(index_dup[i])
        index_dup =  list(map(lambda x :x-1,index_dup)) 
    
    print("deleting duplicated information......done!\n")

    


# In[ ]:

def write_xlsx_file():
    global firm_name
    global firm_adr
    global firm_web
    global firm_phone
    
    name = str(input('File Name(Press Enter to use defult): '))
    print('writing xlsx file......')
    if name == '':
        workbook = xlsxwriter.Workbook('Contact Information-%s in %s,%s.xlsx'%(f_type,f_city,f_state))
    
    else:
        workbook = xlsxwriter.Workbook(name+'.xlsx')

    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold':1,'bg_color':'lime','bottom':1})

    worksheet.write('A1','Firm',bold)
    worksheet.write('B1','Address',bold)
    worksheet.write('C1','Website',bold)
    worksheet.write('D1','Phone numer',bold)


    row = 1
    col = 0
    for variable in [firm_name,firm_adr,firm_web,firm_phone]:
        for element in variable:

            worksheet.write_string(row,col,element)
            row +=1
        maxlen = max(list(map(len,variable)))    
        worksheet.set_column(col, col, maxlen)

        row = 1
        col += 1


    workbook.close()

    print('writing xlsx file......done!')


# In[ ]:

#################main function##################
print ('-------------Program start--------------')

print ('Hello! This is a web scraper program that automatically collects the contact information of firms within a region.\n')

print ('Note: This program will use public data from yellowpages.com\n')

firm_name = []
firm_adr = []
firm_web = []
firm_phone = []



f_type = ''
f_city = ''
f_state = ''

while True:

    inform_input()

    if f_city.lower() != 'all':
        url_base = get_url(f_type,f_city,f_state)

        r = requests.get(url_base+'3')

        soup = BeautifulSoup(r.content,'html5lib')

        page_number = get_page_number(soup)

        for number in range(1,page_number+1):

            url = url_base + str(number)
            get_contact_inform(url)
            print ('collecting information from page ' + str(number) + ' out of ' + str(page_number) + '......')

        print ('All the information is collected successfully!\n')
        
        
    else :
        print ("searching for all cities in " + str(f_state))
        c_list = get_city_list(f_state)
        for city in c_list:
            print ('\nSearching...'+f_type+' in '+city+','+f_state+'.\n')
            
            url_base = get_url(f_type,city,f_state)

            r = requests.get(url_base+'3')

            soup = BeautifulSoup(r.content,'html5lib')

            page_number = get_page_number(soup)

            for number in range(1,page_number+1):

                url = url_base + str(number)
                get_contact_inform(url)
                print ('collecting information from page ' + str(number) + ' out of ' + str(page_number) + '......')

        print ('All the information is collected successfully!\n')
            
        
    
    repeat = input ("Do you want to search for another city or type of firm? The results will be added to the list.(Y/N)\nAnswer: ")
    
    if repeat.upper() != 'Y':
        break

del_dup_elements()

if input('Do you want to write the results into a xlsx file?(Y/N)\nNote: Enter N to exit program\nAnswer: ').upper() == 'Y':
    pathlib.Path('Results').mkdir(parents=True, exist_ok=True)
    os.chdir("Results")
    
    write_xlsx_file()
    
print ('-------------Program End--------------')


# In[ ]:




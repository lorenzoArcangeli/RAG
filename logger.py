import requests
import streamlit as st
class Logger:

    def __init__(self, username, password, baseurl):
        self.username=username
        self.password=password
        self.baseurl=baseurl
        self.__token=None
        self.__session=None
    
    def login(self):
        self.__session = requests.Session()

        # Get token
        parameters = {
            'action':"query",
            'meta':"tokens",
            'type':"login",
            'format':"json"
        }

        session_response = self.__session.get(url=self.baseurl, params=parameters)
        data = session_response.json()

        login_token = data['query']['tokens']['logintoken']
        login_parameters = {
            'action': "login",
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': login_token,
            'format': "json",
        }

        session_response = self.__session.post(self.baseurl, data=login_parameters)
        data = session_response.json()
        assert data['login']['result'] == 'Success'
        self.__token=login_token
    

    def get_content_page(self, page_title):
        if self.__token==None:
            raise Exception("Token to connect is not present")
        else:  
            token=self.__token
            headers = {
                'Authorization': 'Bearer <{token}}>',
            }

            #the paramters are always the same except for the page title
            api_url = f"{self.baseurl}?action=query&prop=revisions&titles={page_title}&rvslots=*&rvprop=content&formatversion=2&format=json"
            response = self.__session.get(api_url, headers=headers)
            return response.json()
        
    def complete_json(self, page_title):
        token=self.__token
        headers = {
            'Authorization': 'Bearer <{token}}>',
        }

        #the paramters are always the same except for the page title
        api_url = f"https://wikidoc.apra.it/essenzia/api.php?action=query&prop=revisions&titles={page_title}&rvslots=*&rvprop=timestamp|content|sha1&formatversion=2&format=json"
        response = self.__session.get(api_url, headers=headers)
        return response.json()
    
    def get_last_version(self, json):
        versions=json['query']['pages'][0]['revisions']
        last_version=versions[-1]
        return last_version
    
    def set_new_baseurl(self, new_url):
        self.baseurl=new_url



    '''
    Usate per prendere le pagine web e i nomi


    def edit_file(self):
        with open("Pages.txt", 'r') as file:
                # Leggi tutte le righe del file e memorizzale in una lista
                righe_del_file = file.readlines()
        carattere_di_riferimento = "="
        nuove_stringhe = [s.split(carattere_di_riferimento, 1)[-1] for s in righe_del_file]
        with open("Pages_title.txt", 'w') as file:
            # Scrivi ogni stringa nella lista su una nuova riga
            for stringa in nuove_stringhe:
                file.write(f"{stringa}")


    def get_page_info(self):
        if self.__token==None:
            raise Exception("Token to connect is not present")
        else:  
            token=self.__token
            headers = {
                'Authorization': 'Bearer <{token}}>',
            }

            with open("Pages_title.txt", 'r') as file:
                # Leggi tutte le righe del file e memorizzale in una lista
                righe_del_file = [riga.strip() for riga in file.readlines()]

            righe_del_file=righe_del_file[:10]
            for righe in righe_del_file:
                #the paramters are always the same except for the page title
                api_url = f"{self.baseurl}?action=query&prop=revisions&titles={righe}&rvslots=*&rvprop=timestamp|content|sha1&formatversion=2&format=json"
                response = self.__session.get(api_url, headers=headers)
                st.write(response.json())
    '''
    '''
    def get_page(self, char): 
        token=self.__token
        headers = {
            'Authorization': 'Bearer <{token}}>',
        }
        #the paramters are always the same except for the page title
        api_url = f"https://wikidoc.apra.it/essenzia/api.php?action=opensearch&search={char}&namespace=0&format=json"
        response = self.__session.get(api_url, headers=headers)
        result=response.json()
        with open("Pages.txt", 'a') as file:
            # Scrivi ogni stringa nella lista su una nuova riga
            for stringa in result[3]:
                file.write(f"{stringa}\n")
    
    def get_pages(self):
        alfabeto = [chr(ord('a') + i) for i in range(26)]  # Lettere minuscole dell'alfabeto
        numeri = [str(i) for i in range(10)]  # Numeri da 0 a 9
        lista_completa = alfabeto + numeri
        for item in lista_completa:
            self.get_page(item)
    '''

import requests

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
    
    def set_new_baseurl(new_url):
        self.baseurl=new_url
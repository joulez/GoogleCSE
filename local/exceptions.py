class GoogleAPIError(Exception):
    def __init__(self, json):
        self.message = json['error']['message']
        self.code = json['error']['code']
        self.reason = json['error']['errors'][0]['reason']
    def __str__(self):
        return repr(' '+str(self.code)+': '.join((self.message, self.reason)))

def evalErrors(apiname, response):
    if response.status_code == 400:
        raise GoogleAPIError(response.json())

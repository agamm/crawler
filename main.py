import requests
from bs4 import BeautifulSoup
import re
import html2text
import urlparse

def getEmails(text):
    ''' Returns all emails found in page *'''
    if len(text) <= 5:
        return []
    emailsrch = "[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+[\s]{0,4}@[\s]{0,4}[a-zA-Z0-9-]+(?:[\s]{0,4}\.[\s]{0,4}[a-zA-Z0-9-]+)"
    matches = re.findall(emailsrch, text)
    matches = [str(i) for i in matches]
    if len(matches) == 0:
        return []
    ret = [matches.pop()]
    #exclude all duplicates
    for i in matches:
      if i not in ret:
        ret.append(i.replace(' ',''))
    return ret
    
def getInnerLinks(htmldata, baseURL, history):
    '''Returns all links found in page
    only if they aren't in the history'''
    soup = getSoup(htmldata)
    links = soup.findAll('a', href=True)
    
    if len(links) == 0:
        return []
    linksT = [i['href'] for i in links]
    links = []
    for i in range(len(linksT)):
        if('http://'  in linksT[i] or 'https://' in linksT[i]) or linksT[i].startswith("?") :
            links.append(linksT[i])
    if len(links) == 0:
        return []
    ret = []
    for b in baseURL:
        for link in links:
            link = urlparse.urljoin(b, link)
            not_in_history = link not in history
            not_duplicate = link not in ret
            not_same = link != b
            not_external =  b in link
            not_mailto = 'mailto' not in link
            if not_in_history and not_duplicate and not_same and not_external and not_mailto:
                ret.append(link)
    return ret

def getExternalLinks(htmldata, baseURL, history):
    '''Returns all links found in page that can go externally
    only if they aren't in the history'''
    soup = getSoup(htmldata)
    links = soup.findAll('a', href=True)
    if len(links) == 0:
        return []
    linksT = [i['href'] for i in links]
    links = []
    for i in range(len(linksT)):
        if('http://'  in linksT[i] or 'https://' in linksT[i]):
            links.append(linksT[i])
    if len(links) == 0:
        return []

    ret = []
    for link in links:
        link = urlparse.urljoin(baseURL, link)
        not_in_history = link not in history
        not_duplicate = link not in ret
        not_same = link != baseURL
        external =  baseURL not in link
        not_mailto = 'mailto' not in link
        if not_in_history and not_duplicate and not_same and external and not_mailto:
            ret.append(link)
    return ret
    
def checkTermPage(url, htmldata):
    ''' Return if this page should be checked *'''
    soup = getSoup(htmldata)
    terms = ['english', 'lesson', 'tutor','teacher', 'teach', 'speaker', 'tutoring']
    points = 2
    try:
        for term in terms:
            if htmldata.find(term) != -1:
                points-=1
    except Exception, e:
        print str(e)
    return (points <= 0)

def getText(url):
    ''' Return the URL's plaintext *'''
    h = html2text.HTML2Text()
    try:
        text =  h.handle(requests.get(url).content)
    except:
        text = ""
    return text

def getURLcontents(url):
    ''' Return the URL's html data *'''
    data = ''
    try:
        data = requests.get(url).content.decode('utf-8')
    except Exception, e:
        print str(e)
        
    return data

def getSoup(content):
    ''' Get soup of html * '''
    soup = BeautifulSoup('')
    try:
        soup = BeautifulSoup(content)
    except Exception, e:
        print str(e)
    return soup

def addEmail(email):
    ''' Check that email isn't already there, and add it if it isn't *'''
    emails = open ("emails.txt","r").read()
    if email not in emails:
        doc = open('emails.txt', 'a')
        doc.write(email+"\n")
        return 1
    else:
        return 0


externalToCheck = []    
toCheck = [] #Urls that haven't been checked already
history = [] #Urls that were checked already
emailsCount = 0
MAX_EMAILS = 1000


startURL = 'http://www.mytutorlist.com/php/viewAds.php?cat=0&level=2&log=1&page=1'

baseURL = ['http://www.mytutorlist.com/php/viewAds.php?cat=&level=&id=','http://www.mytutorlist.com']#['http://classifieds.chinadaily.com/?view=ads&subcatid=89','http://classifieds.chinadaily.com/?view=showad&adid=']
continueBasePath = True
toCheck = [startURL]
print str(len(open ("emails.txt","r").read().split("\n")))+"/1000"
'''
print str(len(open ("emails.txt","r").read().split("\n")))+"/1000"
while emailsCount < 50:
    while len(toCheck) > 0 :
            url = toCheck.pop()
            history.append(url)
            print "URL:"+url+"|toCheck:"+str(len(toCheck))+"|Email count:"+str(emailsCount);
            htmlData = getURLcontents(url)
            if checkTermPage(url, htmlData):
                emails = getEmails(htmlData)
                for email in emails:
                    emailsCount += addEmail(email)

            links = getInnerLinks(htmlData, baseURL, history )
            for link in links:
                toCheck.append(link);
            if not continueBasePath:
                links = getExternalLinks(htmlData, baseURL, history )
                for link in links:
                    externalToCheck.append(link)
    if len(externalToCheck) == 0:
        break
    nextu = externalToCheck.pop()
    toCheck = [nextu]
    baseURL = nextu
    toCheck.append(nextu)
    print "Going externally"
       
print history
print "***"
print externalToCheck
'''


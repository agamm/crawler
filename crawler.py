import requests
from bs4 import BeautifulSoup
import re
import urlparse

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

def checkTermPage(url, htmldata ):
    ''' Return if this page should be checked *'''
    soup = getSoup(htmldata)
    terms = ['english','english teacher',
             'english tutor','english lesson',
             'english speaker','teacher',
             'English', 'speaker',
             'tutoring', 'english language']
    points = 0
    try:
        for term in terms:
            if htmldata.lower().find(term) != -1 or url.find(term) != -1:
                points+=1
    except Exception, e:
        print str(e)
    return points

def getSimIndex(lst, lstSim, sim):
    ''' Add new url with similarity ratio appended '''
    for i in range(0,len(lst)-1):
        if lstSim[i+1]<sim:
            return i
    return -1

def getEmails(text):
    ''' Returns all emails found in page *'''
    if len(text) <= 5:
        return []
    emailsrch = "[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+[\s]{0,4}@[\s]{0,4}[a-zA-Z0-9-]+(?:[\s]{0,4}\.[\s]{0,4}[a-zA-Z0-9-]+)"
    matches = re.findall(emailsrch, text)
    if len(matches) == 0:
        return []
    matches = [str(i) for i in matches]
    ret = [matches.pop()]
    for i in matches:
      if i not in ret:
        ret.append(i.replace(' ',''))
    return ret


def addEmail(email):
    ''' Check that email isn't already there, and add it if it isn't *'''
    emails = open ("emails.txt","r").read()
    if email not in emails:
        doc = open('emails.txt', 'a')
        doc.write(email+"\n")
        return 1
    else:
        return 0

def checkURL(url):
    urlp = r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\SA-z0-9])*\/?'
    return re.match(urlp, url)

def getBaseLinks(htmldata, cURL, baseURL, history):
    '''Returns all links found in page that are part of the base
    only if they aren't in the history'''
    soup = getSoup(htmldata)
    links = soup.findAll('a', href=True)
    if len(links) == 0:
        return []
    
    linksTemp = [urlparse.urljoin(cURL,i['href']) for i in links]
    links = []
    for i in linksTemp:
        if checkURL(i) :
            links.append(i)

    
    ret = []
    for link in links:
        link = urlparse.urljoin(cURL, link)
        not_in_history = link not in history
        not_duplicate = link not in ret
        not_same = link != cURL or link != baseURL
        not_external =  baseURL in link
        not_mailto = 'mailto' not in link
        if (not_in_history and not_duplicate and
            not_same and not_external and not_mailto):
                ret.append(link)
        if not_mailto == False:
            mailtop = r'(?:mailto:)([\S]*)'
            r=re.match(mailtop, a)
            addEmail(r.group(1))
    return ret
    
def crawl(baseURL, startURL, maxEmails, skipTerm):
    #start of queue is more relevant
    tf = maxEmails
    queue = [startURL]
    queueSim = [0]
    history = []
    print queue
    print queueSim
        
    while maxEmails > 0 and len(queue) > 0:
        currentURL = queue.pop(0)
        currentSim = queueSim.pop(0)
        history.append(currentURL)
        htmldata = getURLcontents(currentURL)
        
        print 'Found: '+str(tf-maxEmails)+"/"+str(tf);
        print 'URL: '+currentURL
        print 'Current Similarity: '+str(currentSim)
        print 'Queue len: '+str(len(queue))
        print "------"
        termSim = checkTermPage(currentURL, htmldata)
        sIndex = getSimIndex(queue, queueSim, termSim);
        if termSim > 2 or skipTerm > 0:
            
            #Page is somewhat related to english lessons
            if termSim > 2:
                emails = getEmails(htmldata)
                for email in emails:
                    maxEmails -= addEmail(email)       
           
            nextLinks = getBaseLinks(htmldata, currentURL, baseURL, history)
            for link in nextLinks:
                queue.insert(sIndex, link)
                queueSim.insert(sIndex, termSim)
        else:
            if len(queue) < 5 and baseURL not in history:
                queue.insert(sIndex, baseURL)
                queueSim.insert(sIndex, 2)
        skipTerm -= 1

    print "Finished"

#url = 'http://www.thetutorpages.com/tutors/gcse-english-tutors/gcse-english-tuition/367'
#print getBaseLinks(getURLcontents(url), url, 'thetutorpages.com/tutors', [])

print str(len(open ("emails.txt","r").read().split("\n")))+"/1000"
startURL = 'http://www.eltabb.com/main/index.php'
baseURL = 'eltabb.com'
skipTerm = 0
crawl(baseURL, startURL, 100, skipTerm)




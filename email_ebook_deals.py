#!/usr/bin/python

# $Id$
# $HeadURL$

# Purpose: Fetch Deal of the Day/Week from vendors and send email notifications.

# License: GPLv2

# References:
# http://docs.python.org/library/smtplib.html
# http://docs.python.org/library/email-examples.html
# http://effbot.org/pyfaq/how-do-i-send-mail-from-a-python-script.htm
# http://www.answermysearches.com/how-to-get-a-month-name-in-python/421/
# http://docs.python.org/library/datetime.html
# http://www.boddie.org.uk/python/HTML.html
# http://stackoverflow.com/questions/753052/
# http://gomputor.wordpress.com/2008/09/27/search-replace-multiple-words-or-characters-with-python/
# http://docs.python.org/faq/programming.html#how-do-you-remove-duplicates-from-a-list
# http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
# http://stackoverflow.com/questions/1207457/convert-unicode-to-string-in-python-containing-extra-symbols
# http://docs.python.org/howto/unicode.html
# http://docs.python.org/library/codecs.html#standard-encodings


# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

import datetime
import gzip
import zlib
from StringIO import StringIO

import re
from pprint import pprint as ppr

import urllib2

# http://www.crummy.com/software/BeautifulSoup/documentation.html
from BeautifulSoup import BeautifulSoup

# From 'Why can't Beautiful Soup print out the non-ASCII characters I gave it?'
# import codecs
# import sys
# streamWriter = codecs.lookup('utf-8')[-1]
# sys.stdout = streamWriter(sys.stdout)

# Prints various debug statements
DEBUG_ON = False

# Prints various LOW level (verbose) debug statements
DEBUG_VERBOSE = False

# Prints various high level informational statements
INFO_ON = False

FROM_ADDR = "deals@example.com"
TO_ADDR   = 'root'
DATE = datetime.date.today()
SUBJECT = "eBook Deals for %s" % DATE

# Single email or one email per SITE entry
SINGLE_EMAIL= True

# Not implemented yet
USE_DEAL_IN_SUBJECT=False


# FIXME: Try to shrink this function by using other utility functions
def pp_get_dotd(site, page_content):
    """Get the PacktPub eBook Deal of the Day"""

    looking_for = "%s" % (site['name'])

    if INFO_ON: print "\n[I] Searching for %s ..." % (looking_for)

    # String we're matching on to determine whether a dotd offer is available
    dotd_marker = 'eBook Deal of the Day'

    soup = BeautifulSoup(page_content)

    # FIXME: This needs tweaking, but will have to wait until another
    #            Deal of the Day is posted.
    #results = soup.find("div", { "id" : "header-offer" })
    #results = soup.find("div", { "class" : "inner" })

    # if DEBUG_ON:
        # print "Type of tag", type(site['tag'])
        # print "Type of tag_selector", type(site['tag_selector'])
        # print "Type of tag_selector_value", type(site['tag_selector_value'])

    # search_parameters = '"%s", { "%s" : "%s" }' % \
        # (site['tag'], site['tag_selector'], site['tag_selector_value'])
    # results = soup.find(repr(search_parameters))

    # FIXME: How can I fix the code above?
    results = soup.find("%s" % (site['tag']), \
        { "%s" % (site['tag_selector']): "%s" % \
        (site['tag_selector_value']) }).__str__()

    #results = strip_unicode(results)

    if DEBUG_ON: 
        print "\n[D] results: "
        ppr(results)
        print "\n\n"

    deal = BeautifulSoup(results).findAll(text=True)

    if DEBUG_ON:
        print "\n    [D] What was found: "
        ppr(deal, indent=4)

    if dotd_marker in deal[0]:
        return deal[1], deal[2][0:13]
    else:
        if INFO_ON: print "\n[W] %s was not found" % (looking_for)
        return False

# FIXME: Try to shrink this function by using other utility functions
def pp_get_so(site, page_content):
    """Get the PacktPub Special eBook Offer"""

    looking_for = "%s" % (site['name'])

    # String we're matching on to determine whether an offer is available
    so_marker = 'Special eBook Offer'

    if INFO_ON: print "\n[I] Searching for %s ..." % (looking_for)

    soup = BeautifulSoup(page_content)

    # search_parameters = '"%s", { "%s" : "%s" }' % \
        # (site['tag'], site['tag_selector'], site['tag_selector_value'])
    # results = soup.find(repr(search_parameters))

    # FIXME: How can I fix the code above?
    results = soup.find("%s" % (site['tag']), \
        { "%s" % (site['tag_selector']): "%s" % \
        (site['tag_selector_value']) }).__str__()


    if DEBUG_ON: 
        print "\n[D] results: "
        ppr(results)
        print "\n\n"

    text = BeautifulSoup(results).findAll(text=True)
    if DEBUG_ON: 
        print "\n[D] text: "
        ppr(text)
        print "\n\n"

    string = ''.join(text)
    deal = clean_text(string)

    if so_marker in deal:
        return deal.replace(so_marker,'').strip()
    else:
        if INFO_ON: print "\n[W] %s was not found" % (looking_for)
        return False

def clean_text(text):
    """Removes extraneous spaces, spacing, etc"""

    if DEBUG_ON and DEBUG_VERBOSE:
        function_name = sys._getframe(0).f_code.co_name
        print "[D] text received by %s:\n\n" % (function_name), text

    #regex = re.compile(r'[\r\n]+')
    regex = re.compile(r'[\r\n\t\[\]]+')
    results = regex.sub('', text).strip()
    if DEBUG_ON:
        print "\n\n[D] results of regex replace: "
        print repr(results)

    return results

    # reps = {'\n':' ', '\t':'', '[':'', ']':''}
    # for i, j in reps.iteritems():
    #   text = text.replace(i, j)
    # return text

def strip_tags(text):
    """Removes html/xml tags"""

    if DEBUG_ON and DEBUG_VERBOSE:
        print "[D] (inside strip_tags) value of text: ", text
        print "[D] (inside strip_tags) type of text: ", type(text)

    findall_results = BeautifulSoup(str(text)).findAll(text=True)
    if DEBUG_ON and DEBUG_VERBOSE:
        print "[D] (inside strip_tags) value of findall_results: ", findall_results
        print "[D] (inside strip_tags) type of findall_results: ", type(findall_results)

    results = ' '.join(findall_results)

    if DEBUG_ON and DEBUG_VERBOSE:
        print "\n[D] type of results from join operation: ", type(results)
        print "\n[D] value of results:\n ", results

    # Get rid of JavaScript code
    results = strip_js(results)

    return results

def strip_js(text):
    """Function to remove JavaScript content from text"""

    if DEBUG_ON:
        print "[D] Using strip_js function"

    return text.replace('document.write', '').strip('"()')

def fetch_page(site):
    """Fetches web page content"""

    if INFO_ON: print "\n[I] Fetching:\t%s" % site['url']

    # TODO: Add customized user-agent for this project: name, version, url
    request = urllib2.Request(site['url'])
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read())
        fh = gzip.GzipFile(fileobj=buf)
        content = fh.read()
    elif zlib and 'deflate' in response.info().get('content-encoding', ''):
        try:
            content = zlib.decompress(data)
        except zlib.error, e:
            sys.exit('[E] ' + sys.exc_info()[0])
    else:
            html_page = urllib2.urlopen(site['url'])
            content = html_page.read()
            html_page.close()

    return content

def get_deal(site, page_content):
    """Parses web page content and returns matched strings"""

    if DEBUG_ON and DEBUG_VERBOSE:
        print '[D] value of site:'
        ppr(site)
        #sys.exit('[D] Early exit')

    soup = BeautifulSoup(page_content)

    # Check to see if we need to use a specilized function
    if 'parse_function' in site:
        # Create reference to that function
        parse_function = site['parse_function']
        item = parse_function(site, page_content)
        return item

    if site['tag'] is not None:

        if DEBUG_ON and DEBUG_VERBOSE:
            print "[D] site['tag'] was set"
            print '[D] %s' % (site['tag'])

        if site['skip_first_tag']:
            if DEBUG_ON and DEBUG_VERBOSE:
                print "[D] site['skip_first_tag'] was set"
                print soup.findAll(site['tag'])
 
            item = soup.findAll(site['tag'])[1]
        else:
            item = soup.findAll(site['tag'])[0]

    # If the tag isn't set, use the raw page text (.js files, etc)
    else:
        item = page_content

    if DEBUG_ON and DEBUG_VERBOSE:
        print "[D] type of item: ", type(item)

    stripped_text = strip_tags(item)
    if DEBUG_ON:
        print "[D] stripped_text: \n", stripped_text

    cleaned_text = clean_text(stripped_text)
    if DEBUG_ON:
        print "[D] cleaned_text: \n", cleaned_text

    results = cleaned_text

    if DEBUG_ON:
        print '[D] results: ', results

    return results



def prep_mime_msg(site_names, matches, urls):
    """Prepares a string to deliver to the send_email function"""

    content = ""

    # Assume every match has a corresponding url and site name by this point
    if SINGLE_EMAIL:
        for site_name, match, url in map(None, site_names, matches, urls):
                content +="\n\n\n%s:\n\t%s\n\n\t%s" % (site_name, match, url)
    else:
        content = "\n\n\n%s:\n\t%s\n\n\t%s" % \
            (site_names.pop(), matches.pop(), urls.pop())

    if DEBUG_ON:
        
        # The following fails with (all on one line):
        #UnicodeEncodeError: 'charmap' codec can't encode 
        # character u'\u20ac' in position 104: character maps to <undefined>
        try:
            print "[D] Formatted 'content' for MIMEText function: ", content
        except UnicodeEncodeError:
            print "\n[W] UnicodeEncodeError printing formatted 'content'"

    # Because non-ascii characters may be part of the feed content,
    # we need to ensure that we preserve those characters using
    # a valid encoding.
    msg = MIMEText(content, 'plain', 'utf_8')
    return msg

def send_email(to_addr, from_addr, subject, msg, site_name=""):
    """Receives everything necessary to send an email"""

    if SINGLE_EMAIL:
        msg['Subject'] = "%s" % subject
    else:
        msg['Subject'] = "%s %s" % (site_name, subject)

    msg['From'] = from_addr
    msg['To'] = to_addr

    # Send the message via our own SMTP server, but don't include the envelope header.
    server = smtplib.SMTP('localhost')
    #server.set_debuglevel(1)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


SITES = [
        {
            'url': 'http://www.packtpub.com/',
            'tag': 'div',
            'tag_selector':'id',
            'tag_selector_value':'block-block-114',
            'skip_first_tag': False,
            'name': 'Packt Publishing - Special eBook Offer',
            'parse_function':pp_get_so,
        },
        {
            'url': 'http://www.packtpub.com/',
            'tag': 'div',
            # This will need further testing, but I'll need to wait until
            # another dotd posting is made to tweak it.
            'tag_selector':'class', # 'id' 
            'tag_selector_value':'inner', # 'header-offer'
            'skip_first_tag': False,
            'name': 'Packt Publishing - eBook Deal of the Day',
            'parse_function':pp_get_dotd,
        },
        {
            'url': 'http://feeds.feedburner.com/oreilly/mspebookdeal?format=xml',
            'alt_url': 'http://oreilly.com/',
            'tag': 'title',
            'skip_first_tag': True,
            'name': 'Microsoft Press',
        },
        {
            'url': 'http://feeds.feedburner.com/oreilly/ebookdealoftheday?format=xml',
            'alt_url': 'http://oreilly.com/',
            'tag': 'title',
            'skip_first_tag': True,
            'name': "O'Reilly Media",
        },
        {
            'url': 'http://incsrc.manningpublications.com/dotd.js',
            'alt_url': 'http://www.manning.com/',
            'tag': None,
            'skip_first_tag': False,
            'name': 'Manning Books',
        },
        {
            'url': 'https://www.apress.com/index.php/dailydeals/index/rss', 
            'tag': 'title',
            'skip_first_tag': True,
            'name': 'Apress',
        },
        {
            'url': 'http://www.peachpit.com/deals/index.aspx', 
            'tag': 'h1',
            'skip_first_tag': False,
            'name': 'Peachpit',
        },
        {
            'url': 'http://www.informit.com/deals/index.aspx', 
            'tag': 'h1',
            'skip_first_tag': False,
            'name': 'Informit',
        },
        {
            'url': 'http://www.quepublishing.com/deals/index.aspx', 
            'tag': 'h1',
            'skip_first_tag': False,
            'name': 'Que Publishing',
        },
]




def main():

    sites, matches, urls = [], [], []

    # http://docs.python.org/tutorial/datastructures.html#looping-techniques
    for site in SITES:
        sites.append(site['name'])
        site_content = fetch_page(site)
        deal = get_deal(site, site_content)

        if deal:
            matches.append(deal)

            # If an alternate url exists, pass that instead of the feed url
            if 'alt_url' in site:
                urls.append(site['alt_url'])
            else:
                urls.append(site['url'])
        else:
            matches.append('No deal found')
            urls.append('')

        if SINGLE_EMAIL:
            # Keep looping until all sites have been processed
            continue
        else:
            # For each site in the loop, prep and send an email
            message = prep_mime_msg(sites, matches, urls)

            if DEBUG_ON:
                print "[D] subject and MIME-converted message for send_email function:"
                print "\n%s\n%s" % (SUBJECT, message)
            else:
                send_email(TO_ADDR, FROM_ADDR, SUBJECT, message, site['name'])


    # Prep and send email for all processed sites
    if SINGLE_EMAIL:
        message = prep_mime_msg(sites, matches, urls)
        if DEBUG_ON:
            print "\n[D] subject and MIME-converted message for send_email function:"
            print "\n%s\n%s" % (SUBJECT, message)
        else:
            send_email(TO_ADDR, FROM_ADDR, SUBJECT, message)



if __name__ == "__main__":
    main()

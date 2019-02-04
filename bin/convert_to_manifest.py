# Contains the functions to convert any of the three valid inputs into a
# manifest data structure that process_manifest requires.
#
# Author: James Matsumura
# Contact: jmatsumura@som.umaryland.edu

# base 3.6 lib(s)
import urllib
import csv
import io
import json
import sys

# Let the user customize if not using the main portal for making tokens
from conf import portal_url, portal_port

# Takes in a local file which contains manifest data and converts it to the data
# stucture that is expected for the function download_manifest() in
# process_manifest.py
def file_to_manifest(file):

    with open(file) as tsv:

        return tsv_to_manifest(tsv)

# Takes in a URL where a TSV manifest file is hosted and creates the same data
# stucture that is expected for the function download_manifest() in
# process_manifest.py
def url_to_manifest(url):

    response = urllib.request.urlopen(url)

    return tsv_to_manifest(io.TextIOWrapper(response))

# Function that takes in either a file or a URL response from a TSV entity and
# converts it into the manifest data structure expected for download_manifest().
def tsv_to_manifest(tsv_object):
    manifest = []
    ids = {}

    reader = csv.reader(tsv_object, delimiter="\t")
    next(reader,None) # skip the manifest header

    for row in reader:
        if row[0] not in ids:
            manifest.append({'id':row[0], 'md5':row[1], 'urls':row[3]})
            ids[row[0]] = 1

    return manifest

# Takes in a token that correspondes to a cart/manifest entity. This is then
# converted into the data structure expected for the function
# download_manifest() in process_manifest.py. Requires a trip to an instance of
# the portal which is storing the token node and its links to the relevant
# files.
def token_to_manifest(token):
    portal = "{0}:{1}".format(portal_url,portal_port)
    token_route = "{0}/client/token".format(portal)
    proxies = {}

    # Proxy needed if running against local server
    if portal_url in ['localhost','127.0.0.1']:
        proxies = {'http':portal}
    proxy = urllib.request.ProxyHandler(proxies)
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    params = urllib.parse.urlencode({"token":'{0}'.format(token)}).encode('utf-8')

    # Pull the data generated by the portal within the token_to_manifest()
    # function in query.py. Essentially builds a minimal manifest file as a
    # string.
    res = urllib.request.urlopen(token_route,data=params).read().decode('utf-8')

    if '\t' not in res:
        sys.exit(res)

    files = res.split('\n')

    manifest = []
    ids = {}

    for file in files:
        file_data = file.split('\t')
        if file_data[0] not in ids:
            manifest.append({'id':file_data[0],'md5':file_data[1],'urls':file_data[2]})
            ids[file_data[0]] = 1

    proxy = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    return manifest

#!/usr/bin/python

"""
.. module: create_judgment_sheet

run the case study sourcing pipeline from fetching documents -> creating final json

.. moduleauthor:: Jason Bolton <jebolton@icsi.berkeley.edu>

%prog [options]

-s --search_results_file     file with json of urls to be judged\n
-o --output_file             file to output html to\n
-u --urls_tagged             file of already tagged urls\n

"""

import json
#from optparse import OptionParser
import re
import string

# command line options
#parser = OptionParser()

#parser.add_option("-s", "--search_results_file", dest="search_results_file", 
                #help="file with json for judgment")

#parser.add_option("-o", "--output_file", dest="output_file",
        #help="file to output html to")

#parser.add_option("-u", "--urls_tagged", dest="urls_tagged",
        #help="file of already tagged urls")

#(options,args) = parser.parse_args()

html_head = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n<html>\n<head>\n  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n  <meta http-equiv="Content-Style-Type" content="text/css">\n  <title></title>\n  <meta name="Generator" content="Cocoa HTML Writer">\n  <meta name="CocoaVersion" content="1265.21">\n  <style type="text/css">\n    p.p3 {margin: 0.0px 0.0px 18.0px 0.0px; font: 18.0px Times}\n    p.p4 {margin: 0.0px 0.0px 18.0px 0.0px; font: 18.0px Times; min-height: 23.0px}\n    span.s1 {text-decoration: underline}\n  </style>\n</head>\n<body>'

html_tail = '\n</body>\n</html>\n'

html_entry_template = '\n<h1 style="margin: 0.0px 0.0px 16.1px 0.0px; font: 24.0px Times"><b><RESULT_NUM> - <TITLE></b></h1>\n<h2 style="margin: 0.0px 0.0px 14.9px 0.0px; font: 18.0px Times; color: #0000ee"><span class="s1"><a href="<URL>"><b><URL></b></a></span></h2>\n<p class="p3"><b><SNIPPET></b></p>\n<p class="p4"><b></b><br></p>\n<p class="p4"><b></b><b>judgment for <RESULT_NUM>: ?</b></p><p><br>RESULT_NUM to URL: <RESULT_NUM> <URL></p>'

def clean_text(text):
    """remove strange characters from text
    """
    new_string = ""
    for x in text:
        if x in string.printable:
            new_string += x
        continue
    return new_string

if __name__ == "__main__":
    from optparse import OptionParser
    # command line options
    parser = OptionParser()

    parser.add_option("-s", "--search_results_file", dest="search_results_file", 
                    help="file with json for judgment")

    parser.add_option("-o", "--output_file", dest="output_file",
            help="file to output html to")

    parser.add_option("-u", "--urls_tagged", dest="urls_tagged",
            help="file of already tagged urls")

    (options,args) = parser.parse_args()
    if options.urls_tagged:
        already_urls = set([x for x in file(options.urls_tagged).read().split("\n")[:-1]])
    else:
        already_urls = set([])
    #print already_urls
    #print len(already_urls)
    #search_results = file(options.search_results_file).read().split("\n")[:-1]
    input_json = json.loads(file(options.search_results_file).read())
    search_results = []
    for sr in input_json["urls"]:
        search_results.append(sr)
    #search_results = [json.loads(x) for x in search_results]
    html_entries = []
    result_num = 1
    batch_num = 1
    for sr in search_results:
        # skip a url if its in the already tagged file
        if sr['url'] in already_urls:
            print sr['url']
            continue
        he = re.sub("<URL>",sr['url'],html_entry_template)
        he = re.sub("<RESULT_NUM>",str(result_num),he)
        he = re.sub("<TITLE>",sr['title'],he)
        he = re.sub("<SNIPPET>",sr['snippet'],he)
        clean_he = clean_text(he)
        # add to the list for this batch
        html_entries.append(clean_he)
        result_num += 1
        # if we hit 1000 urls, start a new file
        if result_num % 1000 == 0:
            output_file = file(options.output_file+"_batch_"+str(batch_num)+".html","w")
            final_html = html_head + "".join(html_entries) + html_tail
            output_file.write(final_html)
            html_entries = []
            batch_num += 1
            output_file.close()
    # process the last batch of urls
    output_file = file(options.output_file+"_batch_"+str(batch_num)+".html","w")
    final_html = html_head + "".join(html_entries) + html_tail
    output_file.write(final_html)
    output_file.close()

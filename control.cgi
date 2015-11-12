#!/usr/bin/python

import os
import re
import sys
import cgi
import time
import shutil
import random

g_cms_name = 'Andrew\'s crap'
g_author = 'andrewl'
g_debug = False

def debug(msg):
    global g_debug
    if g_debug:
        print msg

# generate a random 4-character string
def randStr4():
    while 1:
        result = ''
        lookup = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        for i in range(4):
            result += lookup[int(random.random()*len(lookup))]

        if not os.path.exists(result):
            break

    return result

def makeDateStr(epoch):
    struct_time = time.localtime(epoch)
    string = ''
    # if on even hour:minute:second, assume it's invalid and dont' show it
    fmt = '%A %b %d, %Y'
    if time.strftime('%H:%M:%S', struct_time) != '00:00:00':
        fmt += ' %l:%M%p'
    tmp = time.strftime(fmt, struct_time)
    debug("converted epoch %d to %s" % (epoch, tmp))
    return tmp

# given a cgi fileitem, save that attachment in the ./attachments folder
# with randomly generated filename, return the name
def saveAttachment(dirName, fileitem):
    if not fileitem.file:
        raise Exception("form file item has no file data")

    # check size
    fileitem.file.seek(0, os.SEEK_END);
    if fileitem.file.tell() > 16*(2**20):
        raise Exception("attachment exceeds 16mb limit");
    fileitem.file.seek(0, os.SEEK_SET);

    # generate destination file
    path = './%s/%s' % (dirName, fileitem.filename)

    # write destination file
    fout = file(path, 'wb')
    while 1:
        chunk = fileitem.file.read(100000)
        if not chunk: 
            break
        fout.write (chunk)
    fout.close()

    # done
    return path

def getIndexContents():
    fObj = open('index.html', 'r')
    temp = fObj.read()
    fObj.close()
    return temp

def entryInsert(html, date):
    fin = open('index.html', 'r')
    fout = open('index2.html', 'w')

    # the posts are already sorted descending on epoch
    # we must find the first post that we greater than
    ok = 0
    lineNum = 0
    while 1:
        # eof? quit
        lineNum += 1
        line = fin.readline()
        if not line:
            debug("found end of file at line %d" % (lineNum-1))
            break

        # parse date
        dateCur = None
        m = re.match(r'^\s*<div class="entry" date="(\d+)".*', line)
        if m:
            dateCur = int(m.group(1))
            debug("at line %d found entry with date %d" % (lineNum, dateCur))
        else:
            m = re.match(r'^\s*<!-- entries-end -->.*', line)
            if m:
                dateCur = 1;
                debug("at line %d found end of entries" % (lineNum))

        if dateCur:
            debug("at line %d comparing %d to new entry date %d" % (lineNum, dateCur, date))
            if date > dateCur:
                debug("at line %d found insertion point" % lineNum)
                fout.write(html)
                fout.write(line)
                fout.write(fin.read())
                ok = 1
                break
        
        # just pass thru the line
        fout.write(line)

    if not ok:
        raise Exception('couldn\'t place the fucking thing')

    # done
    fin.close()
    fout.close()
    os.rename('index2.html', 'index.html')

def entryNew(title, date, tags, content, filePath, fileList):
    global g_author

    html = ''
    html += '  <div class="entry"'
    html += ' date="%s"' % str(date)
    html += ' tags="%s"' % ','.join(tags)
    html += '>\n'
    html += '   <div class="title">\n'
    html += '    %s\n' % title
    html += '   </div>\n'
    html += '   <div class="subtitle">\n'
    html += '    %s' % makeDateStr(date)
    html += ' by <b>%s</b>' % g_author
    html += ' under\n'
    for tag in tags:
        html += '    <a href=javascript:showTag("%s")>%s</a>\n' % (tag, tag)
    html += '   </div>\n'
    html += '   <div class="content">\n'
    html += '    %s\n' % content
    html += '   </div>\n'
    html += '   <div class="files">\n'
    for f in fileList:
        [base, ext] = os.path.splitext(f)
        link = './%s/%s' % (filePath, f)
        click = f
        if ext in ['.jpg', '.jpeg', '.tif', '.gif', '.bmp']:
            click = '<img src="./%s/%s" />' % (filePath, base + '_thumb' + ext)
        html += '    <a href="%s">%s</a>\n' % (link, click)
    html += '   </div>\n'
    html += '  </div>\n'

    entryInsert(html, date)

#------------------------------------------------------------------------------
# setup
#------------------------------------------------------------------------------

# debugging if possible
if ('HTTP_HOST' in os.environ) and (os.environ['HTTP_HOST'] == 'localhost'):
    import cgitb
    cgitb.enable()

#------------------------------------------------------------------------------
# command-line/TEST mode
#------------------------------------------------------------------------------
if sys.argv[1:]:
    g_debug = True 

    if sys.argv[1] == 'inserttest':
        date = int(sys.argv[2])
        debug("trying to insert post with date %d" % date)
        entryInsert('Test Title', date)
    
    if sys.argv[1] == 'new':
        date = int(sys.argv[2])
        entryNew('test title', date, ['one','two'], 'test content', 'test_title', ['1.txt', '2.txt', 'foo.jpg', 'derp.tif'])

#------------------------------------------------------------------------------
# server mode
#------------------------------------------------------------------------------
else:
    print "Content-Type: text/html\x0d\x0a\x0d\x0a",
    print '<html>'
    
    form = cgi.FieldStorage()
    
    op = ''
    if 'op' in form:
        print "op is: " + repr(form['op'])
        op = form['op'].value
   
    

    # for command line testing, we parse "name=val" strings and shove them into
    # the cgi form
    #for arg in sys.argv[1:]:
    #    m = re.match('^(.*)=(.*)$', arg)
    #    form[
    
    if not op:
        # present the control form
        dirName = randStr4()
        print '''
        <h2>New Entry</h2>
        <form action="control.cgi" method="post" enctype="multipart/form-data">
        <textarea name="entryText" row="80" cols="100"></textarea><br>
        <input type="file" name="attachment0" /><br>
        <input type="file" name="attachment1" /><br>
        <input type="file" name="attachment2" /><br>
        <input type="file" name="attachment3" /><br>
        <input type="file" name="attachment4" /><br>
        <input type="file" name="attachment5" /><br>
        <input type="file" name="attachment6" /><br>
        <input type="file" name="attachment7" /><br>
        <input type="hidden" name="op" value="submit" /><br>
        '''
        print '<input type="hidden" name="dirName" value="%s" />' % dirName
        print '<input type="submit" value="Post!"><br>'
        print '</form>'
        print "attachments will be placed in <b>%s</br>\n" % dirName
        print '''
        <hr>
        <h2>Ultra Edit</h2>
        <form action="control.cgi" method="post" enctype="multipart/form-data">
        <input type="hidden" name="op" value="ultraedit" /><br>
        '''
        print '<textarea name="html">' + getIndexContents() + '</textarea>\n'
        print '<input type="submit" value="Update!"><br>'
        print '</form>\n'
    
    elif op == 'ultraedit':
        html = form['html'].value
    
        # gen backup name
        while 1:
            backupPath = './backups/' + randStr4() + '_index.html'
            if not os.path.exists(backupPath):
                break
            
        # copy backup
        shutil.copy('index.html', backupPath)
    
        # write new one
        fObj = open('index.html', 'wb')
        fObj.write(html)
        fObj.close()
    
        print "done!"
    
    elif op == 'submit':
        requiredFields = ['entryText', 'dirName']
        for rf in requiredFields:
            if not rf in form:
                raise Exception("%s not found in form!" % rf)
    
        # get/sanitize dirName
        dirName = form['dirName'].value
        if not re.match(r'^[a-zA-Z0-9]{4}$', dirName):
            raise Exception("hello, hacker! :)")
    
        # save all attachments
        attachmentResults = []
        for i in range(8):
            fileItem = form['attachment%d' % i]
            if fileItem.filename:
                if not os.path.exists(dirName):
                    os.mkdir(dirName)
                print "saving ./%s/%s...<br>\n" % (dirName, fileItem.filename)
                attachmentResults.append(saveAttachment(dirName, fileItem))
    
        # open index.html
        fObj = open('index.html', 'r')
        content = fObj.read()
        fObj.close()
    
        # parse the before/after
        m = re.match(r'(.*<!-- entries-start -->)(.*)(<!-- entries-end -->.*)', content, re.DOTALL)
        if not m:
            raise Exception("wrong file format!")
    
        # get new entry, add it
        entryText = form['entryText'].value
        entryText = ('<!-- time:%d -->\n' % time.time()) + entryText
        if attachmentResults:
            entryText += ' (<a href="./%s">%d files</a>)' % (dirName, len(attachmentResults))
        entryText = "\n<div class=\"entry\">\n%s\n</div>\n" % entryText 
        content = m.group(1) + entryText + m.group(2) + m.group(3)
    
        # open index.html for writing
        fObj = open('index.html', 'wb')
        fObj.write(content)
        fObj.close()
    
        # done
        print "done!"
    
    print '</html>'
    
    

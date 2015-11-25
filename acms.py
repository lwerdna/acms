#!/usr/bin/python

import os
import re
import sys
import cgi
import time
import shutil
import random

import Image

import settings

def debug(msg):
    if settings.debug:
        print msg + '<br>\n'

# ISO 8601 date format
def makeDateStr(epoch):
    struct_time = time.localtime(epoch)
    string = ''
    # if on even hour:minute:second, assume it's invalid and dont' show it
    fmt = '%Y-%m-%d'
    if time.strftime('%H:%M:%S', struct_time) != '00:00:00':
        fmt += 'T%H:%M:%S'
    tmp = time.strftime(fmt, struct_time)
    debug("converted epoch %d to %s" % (epoch, tmp))
    return tmp

def writeFile(dName, fName, content):
    if not re.match(r'^[\w]+$', dName):
        raise Exception('directory name \'%s\' contains illegal characters' % dName)
    if not re.match(r'^[\w\. -]+$', fName):
        raise Exception('file name \"%s\" contains illegal characters', fName)
    path = './%s/%s' % (dName, fName)
    fobj = open(path, 'wb')
    fobj.write(content)
    fobj.close()

def saveAttachment(dName, fName, fileitem):
    if not fileitem.file:
        raise Exception("form file item has no file data")

    # check size
    fileitem.file.seek(0, os.SEEK_END);
    if fileitem.file.tell() > settings.uploadLimitMb*(2**20):
        raise Exception("attachment exceeds %dmb limit", setting.uploadLimitMb);
    fileitem.file.seek(0, os.SEEK_SET);

    # check name
    if not re.match(r'^[\w]+$', dName):
        raise Exception('directory name \'%s\' contains illegal characters' % dName)
    if not re.match(r'^[\w\. -]+$', fName):
        raise Exception('file name \"%s\" contains illegal characters' %fName)
    path = './%s/%s' % (dName, fName)

    # write destination file
    fout = file(path, 'wb')
    while 1:
        chunk = fileitem.file.read(100000)
        if not chunk: break
        fout.write (chunk)
    fout.close()

    # done
    return path

def entryInsert(html, mdate):
    fin = open(settings.htmlFile, 'r')
    fout = open(settings.htmlFileTemp, 'w')

    # the posts are already sorted descending on epoch (largest/newest on top)
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
        m = re.match(r'^\s*<div class="entry" cdate="\d+" mdate="(\d+)".*', line)
        if m:
            dateCur = int(m.group(1))
            debug("at line %d found entry with modify date %d" % (lineNum, dateCur))
        else:
            m = re.match(r'^\s*<!-- ACMS-end -->.*', line)
            if m:
                dateCur = 1;
                debug("at line %d found end of entries" % (lineNum))

        if dateCur:
            debug("at line %d comparing %d to new entry date %d" % (lineNum, dateCur, mdate))
            if mdate > dateCur:
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
    os.rename(settings.htmlFileTemp, settings.htmlFile)

def entryNew(title, cdate, mdate, tags, content, filePath, attachList, attachListPriv):
    html = ''
    html += '  <div class="entry"'
    html += ' cdate="%s"' % str(cdate)
    html += ' mdate="%s"' % str(mdate)
    html += ' tags="%s"' % ','.join(tags)
    html += '>\n'
    html += '   <div class="title">\n'
    html += '    %s\n' % title
    html += '   </div>\n'
    html += '   <div class="subtitle">\n'
    if mdate != cdate:
        html += '    modified: %s' % makeDateStr(mdate)
    html += '    created: %s' % makeDateStr(cdate)
    html += ' by <b>%s</b>' % settings.author
    if tags:
        html += ' under\n'
        for tag in tags:
            html += '    <a href=javascript:showTag("%s")>%s</a>\n' % (tag, tag)
    html += '   </div>\n'
    html += '   <div class="content">\n'
    html += '    %s\n' % content
    html += '   </div>\n'
    html += '   <div class="files">\n'

    for f in attachList:
        [base, ext] = os.path.splitext(f)
        link = './%s/%s' % (filePath, f)
        click = f
        if ext in ['.jpg', '.jpeg', '.tif', '.gif', '.bmp']:
            click = '<img src="./%s/%s" />' % (filePath, base + '_thumb' + ext)
        html += '    <a href="%s">%s</a>\n' % (link, click)

    if attachListPriv:
        html += '    <a href="%s">(private attachments)</a>\n' % (filePath + '_private')

    html += '   </div>\n'
    html += '  </div>\n'
    html += '\n'

    entryInsert(html, mdate)

#------------------------------------------------------------------------------
# setup
#------------------------------------------------------------------------------

thisFile = os.path.basename(sys.argv[0])

# debugging if possible
if settings.debug:
    import cgitb
    cgitb.enable()

#------------------------------------------------------------------------------
# server mode
#------------------------------------------------------------------------------
if False:
    pass
else:
    print 'Content-Type: text/html\x0d\x0a\x0d\x0a'
    # In HTML 4.01, the <!DOCTYPE> declaration refers to a DTD, because HTML 4.01 was based on SGML. 
    #print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
    # HTML5 is not based on SGML, and therefore does not require a reference to a DTD.
    print '<!DOCTYPE html>'
    print '<html>'
    print '<head>'
    print '<meta charset="utf-8" />'
    print ' <title>ACMS Control</title>'
    print '</head>'
    print '<body>'

    form = cgi.FieldStorage()
    op = ''
    if 'op' in form:
        op = form['op'].value

    if not op:
        # present the control form
        print '<h2>New Entry</h2>'
        print '<form id="newPostForm" action="%s" method="post" enctype="multipart/form-data">' % thisFile
        print '<input type="hidden" name="op" value="newEntry" />'
        print '<br>'
        print 'Title:<br>'
        print '<input type="text" style="width:640px" name="entryTitle" />'
        print '<br>'
        print 'Tags:<br>'
        print '<input type="text" style="width:640px" name="entryTags" />'
        print '<br>'
        print 'Content:<br>'
        print '<textarea name="entryContent" style="width:640px" rows="16"></textarea>'
        print '<br>'
        print 'Attachments:<br>'
        print '<input type="file" name="attachments" id="attachments" multiple="" />'
        print '<br>'
        print 'Private Attachments:<br>'
        print '<input type="file" name="attachmentsPrivate" id="attachmentsPrivate" multiple="" />'
        print '<br>'
        print 'Date:<br>'
        struct_time = time.localtime(time.time())
        # month [1,12] in python (NOTE this differs from standard C lib)
        print '<select name="tm_mon">'
        for (idx, mo) in zip(range(1,12+1), ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']):
            if idx == struct_time.tm_mon:
                print '  <option value="%d" selected="selected">%s</option>' % (idx, mo)
            else:
                print '  <option value="%d">%s</option>' % (idx, mo)
        print '</select>'
        # day [1,31]
        print '<select name="tm_mday">'
        for i in range(1, 31+1):
            if i == struct_time.tm_mday: 
                print '  <option value="%d" selected="selected">%d</option>' % (i,i)
            else: 
                print '  <option value="%d">%d</option>' % (i,i)
        print '</select>'
        # year
        print '<select name="tm_year">'
        for i in range(1980, struct_time.tm_year):
            print '  <option value="%d">%d</option>' % (i,i)
        print '  <option value="%d" selected="selected">%d</option>' % (struct_time.tm_year, struct_time.tm_year)
        print '</select>, '
        # hour [0,23]
        print '<select name="tm_hour">'
        for i in range(24):
            if i == struct_time.tm_hour:
                print '  <option value="%d" selected="selected">%d</option>' % (i,i)
            else:
                print '  <option value="%d">%d</option>' % (i,i)
        print '</select>:'
        # minute [0,59]
        print '<select name="tm_min">'
        for i in range(60):
            if i == struct_time.tm_min:
                print '  <option value="%d" selected="selected">%d</option>' % (i,i)
            else:
                print '  <option value="%d">%d</option>' % (i,i)
        print '</select>'
        print '<br>'
        print '<br><br>'
        print '<input type="submit" value="Post!"><br>'
        print '</form>'
        print '<hr>'
    
    elif op == 'newEntry':
        requiredFields = ['entryTitle', 'entryContent', 'entryTags', 'tm_mon', 'tm_mday', 
            'tm_year', 'tm_hour', 'tm_min']
        for rf in requiredFields:
            if not rf in form:
                raise Exception("required field '%s' not found in form!" % rf)
  
        entryTitle = form['entryTitle'].value
        if entryTitle: print "title: %s...<br>" % entryTitle[0:16]
        else: print "no title<br>"
        entryContent = form['entryContent'].value
        print "content: %s...<br>" % entryContent[0:16]
        st = time.strptime('%s%s%s%s%s' % (form['tm_year'].value, form['tm_mon'].value, \
            form['tm_mday'].value, form['tm_hour'].value, form['tm_min'].value), '%Y%m%d%H%M')
        epoch = int(time.mktime(st))

        # generate dir name (based on title, else on date)
        dirName = entryTitle
        if not dirName:
            dirName = makeDateStr(epoch)
        print "dirName (pre): %s<br>\n" % dirName
        dirName = re.sub(r'[^\w]', '_', dirName)
        print "dirName (post): %s<br>\n" % dirName
        dirNamePriv = dirName + "_private"
        while os.path.exists(dirName) or os.path.exists(dirNamePriv):
            m = re.match(r'^(.*)_(\d+)$', dirName)
            if m: dirName = m.group(1) + '_%d' % (int(m.group(2))+1)
            else: dirName = dirName + '_0'
            dirNamePriv = dirName + "_private"
        print "dirName: %s<br>\n" % dirName
        print "dirNamePriv: %s<br>\n" % dirNamePriv

        attachList = []

        # form can provide single or list of FieldStorage
        attachments = form['attachments']
        if type(attachments) != type([]):
            attachments = [attachments]
        # keep only those that have .file member
        attachments = filter(lambda x: x.file and x.filename, attachments)

        if attachments:   
            print "making directory %s<br>" % dirName
            os.mkdir(dirName)

            # save all attachments
            for fileItem in attachments:
                print "wtfB<br>"
                if fileItem.filename:
                    print "wtfC<br>"
                    fName = fileItem.filename
                    pathed = './%s/%s' % (dirName, fName)
                    print "saving %s<br>" % pathed
                    saveAttachment(dirName, fileItem.filename, fileItem)
                    attachList.append(fName)

                    # generate a thumbnail?
                    [base, ext] = os.path.splitext(fName)
                    if ext in ['.jpg', '.jpeg', '.tif', '.gif', '.bmp']:
                        im = Image.open(pathed)
                        im.thumbnail(settings.thumbSize, Image.ANTIALIAS)
                        pathThumb = './%s/%s_thumb%s' % (dirName, base, ext)
                        im.save(pathThumb, "JPEG")
                else:
                    raise Exception("wtf? fileItem doesn't have a filename")
        else:
            print "SKIPPING directory creation<br>\n"

        print "checkA<br>"

        attachmentsPriv = form['attachmentsPrivate']
        if type(attachmentsPriv) != type([]):
            attachmentsPriv = [attachmentsPriv]
        # keep only those that have .file member
        attachmentsPriv = filter(lambda x: x.file and x.filename, attachmentsPriv)
        if attachmentsPriv:
            print "making directory %s<br>" % dirNamePriv
            os.mkdir(dirNamePriv)

            if not settings.htpasswd or not settings.htaccess:
                raise Exception('requested private attachments but not htpasswd or htaccess setting defined')
            for fileItem in attachmentsPriv:
                if fileItem.filename:
                    fName = fileItem.filename
                    pathed = './%s/%s' % (dirNamePriv, fName)
                    print "saving %s<br>" % pathed
                    saveAttachment(dirNamePriv, fileItem.filename, fileItem)
                    attachListPriv.append(fName)
                else:
                    raise Exception("wtf? fileItem doesn't have a filename")

            writeFile(dirNamePriv, '.htaccess', settings.htaccess)
            writeFile(dirNamePriv, '.htpasswd', settings.htpasswd)
        else:
            print "SKIPPING private directory creation<br>\n"
        
        # process tags
        tags = None
        if 'entryTags' in form:
            tags = form['entryTags'].value
            if tags:
                if not re.match(r'^[\w, ]*$', tags):
                    raise Exception("illegal characters in tags field")
                tags = re.split(',', tags)
                print 'tags: %s<br>' % repr(tags)
        else:
            print "no tags<br>"
        
        print "checkC<br>"

        # make the entry
        entryNew(entryTitle, epoch, epoch, tags, entryContent, dirName, attachList, attachListPriv)
    
        # done
        print "done!<br>"
    
    print ' </body>'
    print '</html>'
    
    

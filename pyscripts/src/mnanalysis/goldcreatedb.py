#!/usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import *
from playhouse.proxy import Proxy
import logging, setproctitle, argparse, time, re, codecs, traceback, os, sys, random
from mnformats import mnjson
from mnformats.xlsxwrapper import XlsxWrapper

golddb_proxy = Proxy()

class UnknownFieldType(object):
    pass

class BaseModel(Model):
    class Meta:
        database = golddb_proxy

class Lemma(BaseModel):
    lemma = CharField(max_length=128)

    class Meta:
        db_table = 'lemma'

class Sent(BaseModel):
    mtext = TextField()
    sid = CharField(max_length=128)
    text = TextField()

    class Meta:
        db_table = 'sent'
        
class Ls_Join(BaseModel):
    lemma = ForeignKeyField(db_column='lemma_id', rel_model=Lemma)
    sent = ForeignKeyField(db_column='sent_id', rel_model=Sent)
    wordform = CharField(max_length=128)
    wfstart = IntegerField()
    wfend = IntegerField()
    class Meta:
        db_table = 'ls_join'

class Target(BaseModel):
    concept = CharField(max_length=45)
    lemma = CharField(max_length=128)
    schemaname = CharField(max_length=128)

    class Meta:
        db_table = 'target'

class Ts_Join(BaseModel):
    sent = ForeignKeyField(db_column='sent_id', rel_model=Sent)
    target = ForeignKeyField(db_column='target_id', rel_model=Target)
    wordform = CharField(max_length=128)
    wfstart = IntegerField()
    wfend = IntegerField()
    class Meta:
        db_table = 'ts_join'

class GoldCreateDB:
    alltschema2concept = {'en' : {'Poverty':'POVERTY',
                               'Taxation':'TAXATION',
                               'Wealth':'WEALTH',
                               'Government':'GOVERNMENT',
                               'Bureaucracy':'BUREAUCRACY',
                               'Democracy':'DEMOCRACY',
                               'Election':'ELECTIONS'},
                          'es' : {u'Pobreza':'POVERTY',
                                  u'Tributación':'TAXATION',
                                  u'Riqueza':'WEALTH',
                                  u'Gobierno':'GOVERNMENT',
                                  u'Burocracia':'BUREAUCRACY',
                                  u'Democracia':'DEMOCRACY',
                                  u'Elección':'ELECTIONS'},
                          'ru' : {u'Бедность':'POVERTY',
                                  u'Налогообложение':'TAXATION',
                                  u'Богатство':'WEALTH',
                                  u'Правительство':'GOVERNMENT',
                                  u'Бюрократия':'BUREAUCRACY',
                                  u'Демократия':'DEMOCRACY',
                                  u'Выборы':'ELECTIONS'},
                          'fa' : {u'فقر':'POVERTY',
                                  u'مالیات':'TAXATION',
                                  u'ثروت':'WEALTH',
                                  u'حکومت':'GOVERNMENT',
                                  u'دیوان سالاری':'BUREAUCRACY',
                                  u'دموکراسی':'DEMOCRACY',
                                  u'انتخابات':'ELECTIONS'}
                       }
    def __init__(self, db, lang):
        self.logger = logging.getLogger(__name__)
        self.db = db
        self.lang = lang
        self.ts2con = self.alltschema2concept[lang]
        
    def getSent(self, sid, text, mtext):
        try:
            gsent = Sent.get(Sent.sid==sid)
        except DoesNotExist:
            gsent = Sent.create(sid=sid, text=text, mtext=mtext)
        return gsent
    
    def getTarget(self, concept, lemma, schemaname):
        try:
            targ = Target.get(Target.lemma==lemma)
        except DoesNotExist:
            targ = Target.create(concept=concept, lemma=lemma, schemaname=schemaname)
        return targ
    
    def joinTargetSent(self,sent,targ,start,end,form):
        tjoin = Ts_Join.create(sent=sent,target=targ,wfstart=start,wfend=end,wordform=form)
        return tjoin
    
    def getLemma(self, lemma):
        try:
            lem = Lemma.get(Lemma.lemma==lemma)
        except DoesNotExist:
            lem = Lemma.create(lemma=lemma)
        return lem
    
    def joinLemmaSent(self,sent,lem,start,end,form):
        ljoin = Ls_Join.create(sent=sent,lemma=lem,wfstart=start,wfend=end,wordform=form)
        return ljoin
    
    def getTargetByConcept(self,conc):
        return Target.select().where(Target.concept==conc)
    
    def getGoldRowsByLemma(self, lemma, numrows):
        return Sent.select(Sent.sid,Sent.text,Target.lemma.alias('lemma')).join(Ts_Join).join(Target).where(Target.lemma==lemma).order_by(fn.Rand()).limit(numrows).naive()
    
    def getGoldRowsByConcept(self, concept, numrows):
        """
        Retrieve numrows number of sentences randomly from those matching a term for the given concept.
        """
        return Sent.select(Sent.sid,Sent.text,Target.lemma.alias('lemma')).join(Ts_Join).join(Target).where(Target.concept==concept).order_by(fn.Rand()).limit(numrows).naive()
    
    def processFile(self, fname):
        try:
            jdata = mnjson.loadfile(fname)
            tscount = 0
            scount = 0
            for sentence in jdata['sentences']:
                scount += 1
                if 'CMS' not in sentence:
                    continue
                if 'targetlist' not in sentence['CMS']:
                    continue
                tlist = sentence['CMS']['targetlist']
                sent = None
                for tmatch in tlist:
                    if tmatch['schemaname'] in self.ts2con:
                        tscount += 1
                        # add sentence to DB if not added already
                        if not sent:
                            sent = self.getSent(sentence['id'],sentence['text'],sentence['mtext'])
                        # add target to DB
                        targ = self.getTarget(self.ts2con[tmatch['schemaname']],tmatch['lemma'].lower(),tmatch['schemaname'])
                        # add target to sent join
                        self.joinTargetSent(sent,targ,tmatch['start'],tmatch['end'],tmatch['form'])
                        # forget source lemmas -- too slow
                        #for word in sentence['word']:
                        #    lem = self.getLemma(word['lem'].lower())
                        #    self.joinLemmaSent(sent,lem,word['start'],word['end'],word['form'])
            self.logger.info('file %s: found %d target terms in %d sentences',
                             os.path.basename(fname),tscount,scount)
        except:
            self.logger.error("error processing %s because\n%s",fname,traceback.format_exc())
        
def main():
    global golddb_proxy
    datestring = time.strftime("%Y%m%d")
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Import sentences into database for gold creation")
    parser.add_argument('-i','--import-files',dest='filenamelist',default=None,
                        help="Import sentences from file containing JSON filename(s)")
    parser.add_argument('-o','--output-file',dest='outputfile',
                        help="Create gold csv file from database")
    parser.add_argument('-n','--nsents',dest='nsents',default=1000,type=int,
                        help="Number of sentences to pull per target concept")
    parser.add_argument('-m','--maxperlemma',dest='maxlemma',default=100,type=int,
                        help="Max number of sentences per lemma")
    parser.add_argument('-l','--lang', help="Language of input files.",
                        required=True)
    parser.add_argument('-u', '--username',dest='username',default='mdbuser',
                        help='Gold database username')
    parser.add_argument('-p', '--password',dest='password',default=None,required=True,
                        help='Gold database password')
    parser.add_argument('--db-name',dest='dbname',default=None,
                        help='Gold database name.')
    parser.add_argument('-v','--verbose',action='store_true',
                        help='Display more status messages')
    cmdline = parser.parse_args()
    
    # proc title manipulation to hide PW
    pstr = setproctitle.getproctitle()
    pstr = re.sub(ur'(-p|--password)(=|\s+)(\S+)',ur'\1\2XXXX',pstr)
    setproctitle.setproctitle(pstr)

    logLevel = logging.WARN
    if cmdline.verbose:
        logLevel = logging.INFO
    logging.basicConfig(level=logLevel,
                        format='%(levelname)s %(message)s')
        
    dbname = 'goldcreatedb_' + cmdline.lang
    socket = '/tmp/mysql.sock'
    if cmdline.dbname:
        dbname = cmdline.dbname
    mydb = MySQLDatabase(dbname, **{'passwd':cmdline.password,
                                    'unix_socket':socket,
                                    'user':cmdline.username,
                                    'charset':'utf8',
                                    'use_unicode':True})
    golddb_proxy.initialize(mydb)
    golddb_proxy.connect()
    
    gcdb = GoldCreateDB(golddb_proxy,cmdline.lang)
    
    if cmdline.filenamelist:
        flist = codecs.open(cmdline.filenamelist,encoding='utf-8')
        for fname in flist:
            gcdb.processFile(fname.strip())
    
    if cmdline.outputfile:
        wb = XlsxWrapper(cmdline.outputfile)
        # for each concept
        for conc in gcdb.ts2con.itervalues():
            goldrows = []
            for target in gcdb.getTargetByConcept(conc):
                # for each target lemma
                for sentrow in gcdb.getGoldRowsByLemma(target.lemma, cmdline.maxlemma):
                    goldrows.append((sentrow.sid, sentrow.text, sentrow.lemma))
            random.shuffle(goldrows)
            ws = wb.addWorkSheet(conc)
            irow = 0
            irow = wb.addHeaderRow(ws, irow, 'ID','Text','T lemma','Status','S wordform','S schema','S concept')
            for row in goldrows[0:cmdline.nsents]:
                irow = wb.addRow(ws, irow, row)
        wb.saveWb()
    

if __name__ == "__main__":
    status = main()
    sys.exit(status)


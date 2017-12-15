#!/opt/pypy-1.8/bin/pypy
# -*- coding: UTF-8 -*-

from __future__ import with_statement

import re, codecs #@UnusedImport

from os.path import abspath, join, basename
from glob import glob
from cStringIO import StringIO
from pprint import pprint #@UnusedImport

BASE = join(abspath('.'), 'data/spa_gw_3')
FILES = [join(BASE, f) for f in glob(join(BASE, 'data/afp', '*'))]
DTD = join(BASE, 'dtd/gigaword_s.dtd')

ENC = 'utf-8'
#ENC = 'iso-8859-1'

from util import Parser, good

esc = {'&quot;': ''}

P = 'paragraph'
    
def process_file(f):
    class Handler(object):
        def __init__(self):
            self.status = None
        def start_element(self, name, attrs):
            if name in ('p', 'P'): self.status = P
        def end_element(self, name):
            if name in ('p', 'P'): self.status = None
        def char_data(self, data):
            #pprint(data)
            if self.status == P: 
                if good(data):
                    sentences.append(''.join(map(lambda x: ' ' if x == '\n' else x, data)) + '\n')
                
    sentences = []
    parser = Parser(Handler())
    parser.ParseFile(f)
    
    return sentences

            
_DOC = """\
    <DOC id="AFP_SPA_19940512.0001" type="story" >
    <HEADLINE>
    ONU ACEPTA EN PRINCIPIO PEDIDO DE MEXICO PARA ASISTENCIA ELECTORAL
    </HEADLINE>
    <DATELINE>
    NUEVA YORK, Mayo 12
    </DATELINE>
    <TEXT>
    <P>
    La ONU aceptó en principio la solicitud de 
    México para una asistencia técnica en materia electoral en las fases previas 
    de las elecciones de agosto próximo, indicaron el jueves fuentes de Naciones 
    Unidas.
    </P>
    <P>
    Una misión encabezada por el director de la Unidad de asistencia electoral 
    de la ONU, Horacio Boneo, se encuentra actualmente en la capital mexicana para 
    afinar detalles de la colaboración que prestará Naciones Unidas en la materia, 
    indicó Joe Sills, portavoz del secretario general del organismo, Butros 
    Butros-Ghali.
    </P>
    <P>
    La solicitud del Gobierno mexicano fue presentada el miércoles en una 
    carta enviada a Butros-Ghali por el ministro del Interior de México, Jorge 
    Carpizo.
    </P>
    <P>
    Sills indicó que los detalles de la respuesta formal de Naciones Unidas se 
    darán a conocer una vez que concluya la misión del organismo.
    </P>
    <P>
    Según fuentes diplomáticas, Boneo permanecerá en México hasta el 17 de 
    mayo y se entrevistará con funcionarios del Gobierno, con dirigentes de los 
    principales partidos políticos y con responsables del Instituto federal 
    electoral y de organizaciones no gubernamentales nacionales, interesadas en 
    participar en la observación de las elecciones.
    </P>
    <P>
    Entre las diferentes opciones presentadas por la ONU, México escogió el 
    principio de una asistencia técnica a observadores nacionales, en un esquema 
    de participación limitada en las fases previas de los comicios, y bajo un 
    formato "ad hoc" exclusivo para el caso, explicó un funcionario del organismo.
    </P>
    <P>
    El pedido mexicano a la ONU se produjo apenas 48 horas después de que el 
    secretario de Estado norteamericano, Warren Christopher, afirmara en la 
    capital mexicana que la presencia de observadores internacionales daría más 
    "credibilidad" a las elecciones.
    </P>
    </TEXT>
    </DOC>
    <DOC id="AFP_SPA_19940512.0003" type="story" >
    <HEADLINE>
    GESTIONAN NACIONALIDAD COLOMBIANA PARA HIJO DE LOS ESPOSOS AMES
    </HEADLINE>
    <DATELINE>
    BOGOTA, Mayo 12
    </DATELINE>
    <TEXT>
    <P>
    El gobierno de Colombia concederá la ciudadanía 
    colombiana al menor Paul Ames Casas, hijo del ex agente de la CIA Aldrich 
    Hazen Ames y la ex diplomática colombiana Maria del Rosario Casas, presos en 
    la actualidad en Estados Unidos acusados de haber espiado para Moscú.
    </P>
    <P>
    Aldrich Amesd, estadounidense, fue condenado el 28 de abril último a 
    cadena perpetua tras confesar a las autoridades norteamericanas que habia 
    entregado a Moscú los nombres -y por ende las vidas- de diez soviéticos que 
    espiaban para Estados Unidos.
    </P>
    <P>
    La cancillería de Bogotá inició este jueves gestiones tendientes a dar 
    nacionalidad colombiana al hijo de los esposos Ames-Casas por petición de la 
    abuela del menor Paul Ames, la colombiana Cecilia Dupuy de Casas, quien se 
    encargará del menor.
    </P>
    <P>
    La madre de María del Rosario solicitó la nacionalidad para su nieto 
    directamente a la canciller Noemí Sanín, quien señaló que el hijo de los 
    esposos Ames "es un ser inocente que tiene sangre colombiana y a quien debemos 
    protreger y nos hemos comprometido a darle la nacionalidad".
    </P>
    <P>
    La madre del menor se encuentra detenida en una cárcel de Alexandria a la 
    espera de la sentencia que será proferidad el próximo 26 de agosto.
    </P>
    <P>
    El ex agente de la CIA aceptó haber espiado para Moscú y fue sentenciado a 
    cadena perpetua sin posibilidad de obtener libertad y bajo palabra prometió 
    cooperar con las autoridades para determinar el grado de los daños que causó, 
    a cambio de clemencia para su esposa, se recordó en Bogotá.
    </P>
    <P>
    María del Rosario Casas de Ames representó al gobierno colombiano en 
    México la década pasada.
    </P>
    </TEXT>
    </DOC>"""
    
def test_01():
    process_file(StringIO(_DOC))    
    
def test_02():
#    process_file(codecs.open(FILES[0], encoding=ENC, errors='xmlcharrefreplace'))
    process_file(open(FILES[0]))
    
def test_03():
    import xml.sax

    class MyHandler(xml.sax.handler.ContentHandler):
        def startElement(self, name, attrs):
            print "StartElement: %s" % name
        def endElement(self, name):
            print "EndElement: %s" % name
        def characters(self, ch):
            #print "Characters: '%s'" % ch
            pass
    
    parser = xml.sax.make_parser()
    parser.setContentHandler(MyHandler())

    for line in open(FILES[0]):
        parser.feed(line)


def test_04():    
    import xml.parsers.expat

    # 3 handler functions
    def start_element(name, attrs):
        print 'Start element:', name, attrs
    def end_element(name):
        print 'End element:', name
    def char_data(data):
        print 'Character data:', repr(data)
    
    p = xml.parsers.expat.ParserCreate()
    
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data
    p.Parse(_DOC.strip()[6:-7])
    
    
def test_055():
    process_file(StringIO('<docs>%s</docs>' % _DOC))
                 
    
def test_05():
    f = open(FILES[0])
    with f:
        s = process_file(StringIO('<docs>%s</docs>' % f.read()))
    return s


def process(filenames, outdir):
    from os.path import splitext
    import gzip, codecs
    
    for fn in filenames:
        print 'processing', fn
        outn = '{}.ss'.format(join(outdir, basename(splitext(fn)[0])))
#        with gzip.open(fn, 'rb') as inf, codecs.open(outn, 'wb', 'utf-8') as outf:
        with codecs.open(fn, 'rb', encoding='utf-8') as inf, codecs.open(outn, 'wb', 'utf-8') as outf:
            ss = process_file(StringIO('<docs>%s</docs>' % inf.read()))
            outf.writelines(ss)
        
            
if __name__ == '__main__':
#    test_01()
#        test_02()
#    test_03()
#    test_055()
#    test_05()
#    pass
    import sys
    process(sys.argv[2:], sys.argv[1])
    

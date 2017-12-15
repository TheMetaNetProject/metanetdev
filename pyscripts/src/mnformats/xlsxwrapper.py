'''
Created on May 23, 2014

@author: jhong
'''
import logging, string, pprint
from decimal import Decimal
import xlsxwriter

class XlsxWrapper():
    '''
    Wrapper Class around xlsxwriter for MetaNet convenience
    '''

    def __init__(self,outfname):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(__name__)
        self.wb = xlsxwriter.Workbook(outfname)
        self.floatformat = self.wb.add_format()
        self.headerformat = self.wb.add_format()
        self.floatformat.set_num_format('0.0000')
        self.headerformat.set_bold()
        self.colletters = list(string.uppercase)
        self.nlet = len(self.colletters)
    
    def addWorkSheet(self, name):
        return self.wb.add_worksheet(name)
    
    def getCoord(self, irow, icol, fix=True):
        """ Take 0-starting row and col numbers and return A1 type
        coordinates in the spreadsheet.
        :param irow: row number
        :param type: int
        :param icol: column number
        :param type: int
        :param fix: causes columns and rows to be prefixed with $
        :param type: boolean
        """
        if icol < len(self.colletters):
            collet = self.colletters[icol]
        else:
            let1 = self.colletters[(icol / self.nlet)-1]
            let2 = self.colletters[icol % self.nlet]
            collet = let1 + let2
        if fix:
            return '$%s$%d' % (collet,irow+1)
        else:
            return '%s%d' % (collet,irow+1)
    
    def addRow(self, ws, irow, *arg):
        """ Add a row to the worksheet.  Can either pass in cell items as
        arguments, or as a list.
        :param ws: worksheet
        :param type: :class:`WorkSheet`
        :param irow: row number
        :param type: int
        :param *arg: content of cells in the row to insert
        :param type: list
        """
        return self.addRowAt(ws,irow,0,*arg)
    
    def addRowAt(self, ws, irow, icol, *arg):
        """ Add a row to the worksheet at the given column number.
        Can either pass in cell items as arguments, or as a list.
        :param ws: worksheet
        :param type: :class:`WorkSheet`
        :param irow: row number
        :param type: int
        :param icol: column number
        :param type: int
        :param *arg: content of cells in the row to insert
        :param type: list
        """
        if isinstance(arg[0], (list, tuple)):
            vlist = arg[0]
        else:
            vlist = arg
        for idx, val in enumerate(vlist):
            column = icol + idx
            if isinstance(val, (str, unicode)):
                ws.write_string(irow,column,val)
                continue
            if isinstance(val, (int, long)):
                ws.write_number(irow,column,val)
                continue
            if isinstance(val, (float, Decimal)):
                ws.write_number(irow,column,val,self.floatformat)
                continue
            self.logger.warn('Unknown type: %s (%s)',str(type(val)),pprint.pformat(val))
            ws.write(irow,column,val)
        return irow + 1

    def addHeaderRow(self, ws, irow, *arg):
        if isinstance(arg[0], (list, tuple)):
            vlist = arg[0]
        else:
            vlist = arg
        for idx, val in enumerate(vlist):
            column = idx
            ws.write_string(irow,column,val,self.headerformat)
        return irow + 1
    
    def saveWb(self):
        """ Save out the workbook.
        """
        self.wb.close()
    
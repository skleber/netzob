#!/usr/bin/env python
# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Sumit Acharya <sumit.acharya@uni-ulm.de>                          |
# |       - Stephan Kleber <stephan.kleber@uni-ulm.de>                        |
# +---------------------------------------------------------------------------+

# Import necessary scripts from netzob codes
from netzob.Common.all import *
from netzob.Inference.all import *
from netzob.Import.all import *

# Related third party packages
import rlcompleter
import readline
import code

#Main class
class SulleyExporter(object):
        """ Sulley Exporter to export the output 
               of the Inference to txt file
        """
        def __init__(self):
            pass

        def exportToSulley(self, symbols, filename):
            """ 
                    Usage: >>> SulleyExporter().exportToSulley(symbols,'outputFilenane')
            """
            sfilecontents = ''
            try:
                iter(symbols)
                for syml in symbols:
                        sfilecontents += "# === Start of new SYMBOL " + syml.name + '\n'
                        sfilecontents += "s_initialize(\"new request {}\")".format(syml.name) + '\n'
                        for field in syml.fields:
                                try:
                                        sfilecontents += self.svas_valuefilter(field.domain) + '\n'
                                except AttributeError:
                                        size0,size1 = self.aggDomain(field.domain,[],1000,0)
                                        sfilecontents += '# variable field \n' + 's_random' + '(' +str(size0) + ',' + str(size1) + ')' + '\n'
                        sfilecontents += '\n'
                        print(sfilecontents)
                with open(filename,'w') as f:
                    f.write(sfilecontents)
                    f.close()
            except TypeError:
                syml = symbols
                sfilecontents += "# === Start of new SYMBOL " + syml.name + '\n'
                sfilecontents += "s_initialize(\"new request {}\")".format(syml.name) + '\n'
                for field in syml.fields:
                        try:
                                        sfilecontents += self.svas_valuefilter(field.domain) + '\n'
                        except AttributeError:
                                        size0,size1 = self.aggDomain(field.domain,[],1000,0)
                                        sfilecontents += '# variable field \n' + 's_random' + '(' +str(size0) + ',' + str(size1) + ')' + '\n'
                        print(sfilecontents)
                with open(filename,'w') as f:
                        f.write(sfilecontents)
                        f.close()

# To find the size of the Merged Field
        def aggDomain(self, domain,remaining_domain, size0, size1):
                if str(domain.children[1]) == 'Agg' and str(domain.children[0]) != 'Agg':
                        sizefield1 = list(domain.children[0].dataType.size)
                        size0 = min(sizefield1[0],size0)
                        size1 = size1 + sizefield1[1]
                        return self.aggDomain(domain.children[1], remaining_domain,size0, size1)
                elif str(domain.children[0]) == 'Agg' and str(domain.children[1]) != 'Agg':
                        sizefield = list(domain.children[1].dataType.size)
                        size0 = min(sizefield[0],size0)
                        size1 = size1 + sizefield[1]
                        return self.aggDomain(domain.children[0],remaining_domain,size0,size1)
                elif str(domain.children[0]) == 'Agg' and str(domain.children[1]) == 'Agg':
                        remaining_domain.append(domain.children[1])
                        return self.aggDomain(domain.children[0],remaining_domain,size0,size1)
                else:
                        sizefield0 = list(domain.children[0].dataType.size)
                        sizefield1 = list(domain.children[1].dataType.size)
                        size0 = min(size0,sizefield0[0],sizefield1[0])
                        size1 = size1 + sizefield0[1] + sizefield1[1]
                if(remaining_domain):
                        return self.aggDomain(remaining_domain.pop(),remaining_domain,size0,size1)
                else:
                        return size0,size1

# Raw data type case
        def dataType_raw(self, dataType):
                command = 's_random'
                parameters = [
                        str(dataType.size[0]),
                        str(dataType.size[1])
                ] # minimum, maximum length
                return '# variable field \n' + command + '(' \
                        + ','.join(parameters) \
                        + ')'

# ASCII string data type
        def dataType_ascii(self, dataType):
                command = 's_string'
                if dataType.size[0] == dataType.size[1]:
                        size = dataType.size[0] # fixed length
                else:
                        size = -1 # variable length
                parameters = [
                        str(size)
                         ]
                return '# variable string field \n' + command + '(' \
                        + ','.join(parameters) \
                        + ')'

# Integer data type
# uses honors dataType.endianness. For values see AbstractType.supportedEndianness()
        def dataType_integer(self, dataType):
                if dataType.size[1] <= 1*8:
                        command = 's_byte'
                elif dataType.size[1] <= 2*8:
                        command = 's_short'
                elif dataType.size[1] <= 4*8:
                        command = 's_int'
                elif dataType.size[1] <= 8*8:
                        command = 's_double'
                else:
                        return dataType_raw(dataType)
     
     # Values: AbstractType.supportedEndianness()
                if dataType.endianness == 'big':
                        parameters = [
                                str('">"')
                                ]
                else: # dataType.endianness == 'little'
                        parameters = [
                                str('"<"')
                                ]
    # Not honored: AbstractType.supportedSign() // str(domain.dataType.sign)
    # In Sulley signed integers are only possible with ASCII-representation
    # Netzob would not return this as integer, but as string
    # So this is not possible to support easily.
                return '# variable integer field \n' + command + '(' \
                        + ','.join(parameters) \
                        + ')'

# dataType switcher
# list of key values can be obtained by AbstractType.supportedTypes()
# Not supported: AbstractType.supportedUnitSize() // str(domain.dataType.unitSize)
        def dataType_valuefilter(self, dataType):
                switcher = {
                        'Integer'   : self.dataType_integer,
                        'BitArray'  : self.dataType_raw,
                        'Raw'       : self.dataType_raw,
                        'ASCII'     : self.dataType_ascii,
                        'HexaString': self.dataType_raw,
                        'IPv4'      : self.dataType_raw, # this should be improved
                }
                return switcher.get(dataType.typeName, self.dataType_raw)(dataType)




# For constant fields, return fixed value in hex-representation (\xFF)
        def svas_constant(self, domain):
                return '# constant field \ns_binary("' \
                        + repr(TypeConverter.convert(domain.currentValue, BitArray, HexaString)) \
                        + '", fuzzable=False)'
#                return '# constant field \ns_binary("' \
#                        + HexaString.encode(domain.currentValue, \
#                                domain.dataType.unitSize, domain.dataType.endianness, \
#                                        domain.dataType.sign) \
#                        + '", fuzzable=False)'

# For variable fields, return properties: typeName, minlen, maxlen, endianness, unitSize, sign
# domain.dataType.typeName that can be
# Raw, ASCII, Integer, BitArray, HexaString, IPv4, Timestamp
        def svas_variable(self,domain):
                return self.dataType_valuefilter(domain.dataType)
    # To iterate: AbstractType.supportedTypes() // domain.dataType.typeName
    # if globals()[domain.dataType.typeName] in AbstractType.supportedTypes():

# State Variable Assignment Strategy "decode"
        def svas_valuefilter(self,domain):
                switcher = {
                        SVAS.CONSTANT:   self.svas_constant,
                        SVAS.EPHEMERAL:  self.svas_variable,
                        SVAS.PERSISTENT: self.svas_constant,
                        SVAS.VOLATILE:   self.svas_variable,
                }
                return switcher.get(domain.svas, self.svas_variable)(domain)


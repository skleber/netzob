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
from netzob.Export.AbstractExporter import AbstractExporter
from netzob.Model.Vocabulary.Types.all import *
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS


class SulleyExporter(AbstractExporter):
    """
    Sulley Exporter to export the output
           of the Inference to .py file in sulley-style
    """
    def __init__(self):
        pass

    @staticmethod
    def exportToSulley(symbols, filename):
        """
        Usage:
        >>> SulleyExporter().exportToSulley(symbols,'outputFilename.py')
        """

        try:
            iter(symbols)  # checks if the symbols are iterable
        except TypeError:  # if its only one symbol
            symbols = [symbols]

        sfilecontents = ""
        for syml in symbols:
            sfilecontents += "# === Start of new SYMBOL {}\n".format(syml.name)
            sfilecontents += "s_initialize(\"new request {}\")\n".format(syml.name)
            for field in syml.fields:
                try:
                    sfilecontents += SulleyExporter._svas_valuefilter(field.domain) + '\n'
                except AttributeError:
                    size0, size1 = SulleyExporter._aggDomain(field.domain)
                    sfilecontents += '# variable field \ns_random({:d},{:d})\n'.format(size0, size1)
            sfilecontents += '\n'

        with open(filename,'w') as f:
                f.write(sfilecontents)
                f.close()


    @staticmethod
    def _dataType_raw(dataType):
        """
        Raw data type case

        :param dataType:
        :return:
        """

        command = 's_random'
        parameters = [
                str(dataType.size[0]),
                str(dataType.size[1])
        ] # minimum, maximum length
        return '# variable field \n{}({})'.format(
            command,
            ','.join(parameters)
        )

    @staticmethod
    def _dataType_ascii(dataType):
        """
        ASCII string data type

        :param dataType:
        :return:
        """

        command = 's_string'
        if dataType.size[0] == dataType.size[1]:
                size = dataType.size[0] # fixed length
        else:
                size = -1 # variable length
        parameters = [
                str(size)
                 ]
        return '# variable string field \n{}({})'.format(
            command,
            ','.join(parameters)
        )


    @staticmethod
    def _dataType_integer(dataType):
        """
        Integer data type

        uses honors dataType.endianness. For values see AbstractType.supportedEndianness()

        :param dataType:
        :return:
        """

        if dataType.size[1] <= 1*8:
                command = 's_byte'
        elif dataType.size[1] <= 2*8:
                command = 's_short'
        elif dataType.size[1] <= 4*8:
                command = 's_int'
        elif dataType.size[1] <= 8*8:
                command = 's_double'
        else:
                return SulleyExporter._dataType_raw(dataType)
     
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

        return '# variable integer field \n{}({})'.format(
            command,
            ','.join(parameters)
        )


    @staticmethod
    def _dataType_valuefilter(dataType):
        """
        dataType switcher

        Not supported: AbstractType.supportedUnitSize() // str(domain.dataType.unitSize)

        :param dataType: list of key values can be obtained by AbstractType.supportedTypes()
        :return: calls the method valid for the dataType, one of _dataType_raw, _dataType_integer, _dataType_ascii
        """

        switcher = {
            'Integer'   : SulleyExporter._dataType_integer,
            'BitArray'  : SulleyExporter._dataType_raw,
            'Raw'       : SulleyExporter._dataType_raw,
            'ASCII'     : SulleyExporter._dataType_ascii,
            'HexaString': SulleyExporter._dataType_raw,
            'IPv4'      : SulleyExporter._dataType_raw, # this should be improved
        }
        return switcher.get(dataType.typeName, SulleyExporter._dataType_raw)(dataType)


    @staticmethod
    def _svas_constant(domain):
        """
        For constant fields, return fixed field value in hex-representation (\xFF)

        :param domain: domain to extract the value of
        :return:
        """
        return '# constant field \ns_binary("{}", fuzzable=False)'.format(
            repr(TypeConverter.convert(domain.currentValue, BitArray, HexaString))
        )


    @staticmethod
    def _svas_variable(domain):
        """
        For variable fields, return properties: typeName, minlen, maxlen, endianness, unitSize, sign

        domain.dataType.typeName can be
        Raw, ASCII, Integer, BitArray, HexaString, IPv4, Timestamp

        :param domain: domain to extract the value of
        :return:
        """
        return SulleyExporter._dataType_valuefilter(domain.dataType)
        # To iterate: AbstractType.supportedTypes() // domain.dataType.typeName
        # if globals()[domain.dataType.typeName] in AbstractType.supportedTypes():


    @staticmethod
    def _svas_valuefilter(domain):
        """
        "State Variable Assignment Strategy" decode

        :param domain: domain to extract the SVAS of
        :return: calls the method valid for the SVAS, one of _svas_constant, _svas_variable
        """
        switcher = {
            SVAS.CONSTANT:   SulleyExporter._svas_constant,
            SVAS.EPHEMERAL:  SulleyExporter._svas_variable,
            SVAS.PERSISTENT: SulleyExporter._svas_constant,
            SVAS.VOLATILE:   SulleyExporter._svas_variable,
        }
        return switcher.get(domain.svas, SulleyExporter._svas_variable)(domain)


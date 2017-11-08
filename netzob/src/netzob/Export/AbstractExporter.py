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

from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg

class AbstractExporter(object):

    @staticmethod
    def _aggDomain(domain):
        """
        To find the size of the Merged Field.

        Parameters have the following meanings
        :param domain: value of field.domain
        :return The size of the merged field including the size of all of its children

        >>> m1 = RawMessage("someexamplemessage")
        >>> fields = [ \
                Field("some", name="f0"), \
                Field( Agg([ Agg ([ Raw("ex"), Raw("ample") ]), Raw("message") ]), name="f1") \
            ]
        >>> symbol = Symbol(fields, messages=[m1])
        >>> se = ScapyExporter(symbol)
        >>> se.exportToScapy("scapy_test_agg.py")
        >>> se._aggDomain(fields[1].domain)
        (0, 112)

        >>> ofields = [ \
                Field( Agg([ Raw("some"), Agg ([ Raw("ex"), Raw("ample") ]),  ]), name="f0"), \
                Field("message", name="f1"), \
            ]
        >>> se._aggDomain(ofields[0].domain)
        (0, 88)
        """

        if not isinstance(domain, Agg):
            return domain.dataType.size

        lsize = AbstractExporter._aggDomain(domain.children[0])
        rsize = AbstractExporter._aggDomain(domain.children[1])

        return (lsize[0] + rsize[0], lsize[1] + rsize[1])


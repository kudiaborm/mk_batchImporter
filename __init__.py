"""
	This is a tool set that creates a pose loader to automate
	and speed up workflow.

	It is most likely that you have received an older version of this script or a
	version still in development. Feel free to concact me
	to request the most up to date version or other tool sets.

	Marley Kudiabor Kudiaborm@gmail.com

    Copyright (C) 2014  Marley Kudiabor

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    How to use:

import mk_batchImporter

try:
	mywindow.close()
except:
	pass
mywindow = mk_batchImporter.ui.Window()
mywindow.show()

"""

import ui
reload(ui)
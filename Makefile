
all: pybrewMainWindow.py *.py

%.py: %.ui
	pyuic4 -w $< | sed -e 's/QtGui\.QwtThermo/Qwt5.QwtThermo/g' > $*.py


all: pybrewMainWindow.py *.py

%.py: %.ui
	pyuic4 -w -o $*.py $<
	sed -i -e 's/QtGui\.QwtThermo/Qwt5.QwtThermo/g' $*.py

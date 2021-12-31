XSLTPROC		= xsltproc
XSLTPARAM		= --nonet --novalid
HTML_STYLESHEET	= /usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl
MAN_STYLESHEET	= /usr/share/xml/docbook/stylesheet/nwalsh/manpages/docbook.xsl

source      = pycrc.xml
targets		= $(source:.xml=.html) $(source:.xml=.1)

all: $(targets)

.PHONY: clean
clean:
	$(RM) $(targets)

.PHONY: check
check:
	xmllint --valid --noout $(source)

%.html: %.xml
	$(XSLTPROC) $(XSLTPARAM) -o $@ $(HTML_STYLESHEET) $<

%.1: %.xml
	$(XSLTPROC) $(XSLTPARAM) -o $@ $(MAN_STYLESHEET) $<

%.txt: %.html
	links -dump -no-numbering -no-references $< > $@

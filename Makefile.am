SUBDIRS = intl pykota bin conf untested man openoffice initscripts po

pykotadocdir = $(datadir)/doc/pykota
pykotadoc_DATA = 		\
	README				\
	FAQ					\
	SECURITY			\
	COPYING				\
	LICENSE				\
	CREDITS				\
	TODO				\
	NEWS				

pykotaesdocdir = $(datadir)/doc/pykota/spanish
pykotaesdoc_DATA = 		\
	docs/spanish/instalacion.sxw

EXTRA_DIST = config.rpath  \
	$(pykotadoc_DATA)	\
	$(pykotaesdoc_DATA)

ACLOCAL_AMFLAGS = -I m4

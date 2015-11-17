VERSION=0.5


# branch and commit ID?
DISTVERSION=$(shell git rev-parse --abbrev-ref HEAD)-$(VERSION)-$(shell git rev-parse HEAD)

# most recent tag --- or abbreviated commit as fallback
RELEASEVERSION=$(shell git describe --always)


.PHONY: tags TAGS dist release


tags: TAGS

TAGS:
	find . -name "[a-z_]*.py" | xargs etags


dist: dbservice-$(DISTVERSION).tar.gz

release: dbservice-$(RELEASEVERSION).tar.gz


dbservice-%.tar.gz:
	TMPDIR=`mktemp -d`; \
	git clone . $$TMPDIR/dbservice; \
	rm -rf $$TMPDIR/dbservice/.git; \
	echo "__version__ = \"$*\"" > \
	     $$TMPDIR/dbservice/dbservice/__init__.py; \
	tar czf $@ --directory $$TMPDIR dbservice; \
	rm -rf $$TMPDIR

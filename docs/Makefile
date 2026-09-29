# Build the SnapCheck documentation, in the lepton-dev-env environment:
#   make html          build the website in _build/html (runs the examples)
#   make html-noplot   build it without running the examples
#   make clean         remove the build and the generated files

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
BUILDDIR      = _build

.PHONY: help html html-noplot clean

help:
	@echo "Use: make html | make html-noplot | make clean"

html:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) . $(BUILDDIR)/html
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

html-noplot:
	$(SPHINXBUILD) -b html -D plot_gallery=0 $(SPHINXOPTS) . $(BUILDDIR)/html
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

clean:
	rm -rf $(BUILDDIR) auto_examples generated api/generated

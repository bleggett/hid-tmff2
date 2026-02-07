srpm:
	# Install required tools
	dnf install -y git rpm-build
	# Initialize git submodules
	git submodule update --init --recursive
	# Create main source tarball
	git archive --format=tar.gz --prefix=hid-tmff2-0.82/ HEAD > /tmp/hid-tmff2-0.82.tar.gz
	# Create submodule tarball
	cd deps/hid-tminit && git archive --format=tar.gz --prefix=hid-tminit/ HEAD > /tmp/hid-tminit.tar.gz
	# Build the SRPM
	rpmbuild -bs hid-tmff2-kmod.spec --define "_sourcedir /tmp" --define "_srcrpmdir $(outdir)"

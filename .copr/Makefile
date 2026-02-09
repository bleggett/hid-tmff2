srpm:
	# Install required tools
	dnf install -y git rpm-build
	# Initialize git submodules
	git submodule update --init --recursive
	# Create main source tarball (exclude specs/ directory to avoid duplicate spec files)
	git archive --format=tar.gz --prefix=hid-tmff2-0.82/ HEAD $$(git ls-tree --name-only HEAD | grep -v '^specs$$') > /tmp/hid-tmff2-0.82.tar.gz
	# Create submodule tarball
	cd deps/hid-tminit && git archive --format=tar.gz --prefix=hid-tminit/ HEAD > /tmp/hid-tminit.tar.gz && cd ../..
	# Copy the kmod spec file that akmods will use
	cp specs/hid-tmff2-akmod.spec /tmp/
	# Build the akmod SRPM
	rpmbuild -bs akmod-hid-tmff2.spec --define "_sourcedir /tmp" --define "_srcrpmdir $(outdir)"

# Legacy kmod build (if needed)
kmod-srpm:
	# Install required tools
	dnf install -y git rpm-build
	# Initialize git submodules
	git submodule update --init --recursive
	# Create main source tarball
	git archive --format=tar.gz --prefix=hid-tmff2-0.82/ HEAD > /tmp/hid-tmff2-0.82.tar.gz
	# Create submodule tarball
	cd deps/hid-tminit && git archive --format=tar.gz --prefix=hid-tminit/ HEAD > /tmp/hid-tminit.tar.gz
	# Build the kmod SRPM
	rpmbuild -bs hid-tmff2-kmod.spec --define "_sourcedir /tmp" --define "_srcrpmdir $(outdir)"

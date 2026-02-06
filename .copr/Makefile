srpm:
	# Initialize git submodules before rpkg runs
	git submodule update --init --recursive
	# Use rpkg to generate the SRPM with submodules now initialized
	rpkg srpm --outdir=$(outdir)

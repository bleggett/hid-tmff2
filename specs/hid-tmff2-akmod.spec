# Kmod spec file for use with akmods
# This spec file is used by akmods to build kernel modules for each kernel

%global kmod_name hid-tmff2

Name:           kmod-%{kmod_name}
Version:        0.82
Release:        1%{?dist}
Summary:        Kernel module for Thrustmaster T300RS, T248 and other racing wheels

License:        GPL-2.0-or-later
URL:            https://github.com/Kimplul/hid-tmff2

Source0:        %{kmod_name}-%{version}.tar.gz
Source1:        hid-tminit.tar.gz

# For building
BuildRequires:  kernel-devel

%description
A Linux kernel module for Thrustmaster T300RS, T248, and experimental support
for TX, T128, T598, TS-PC and TS-XW racing wheels.

This package provides force feedback support and advanced features for supported
Thrustmaster racing wheels. The driver includes wheel initialization modules
(hid-tminit) and the main force feedback driver (hid-tmff-new).

%prep
# Extract main source
%setup -q -n %{kmod_name}-%{version}

# Extract hid-tminit submodule (Source1)
mkdir -p deps
tar -xzf %{SOURCE1} -C deps

# Verify submodule is in place
if [ ! -f deps/hid-tminit/Makefile ]; then
    echo "ERROR: hid-tminit submodule not found after extraction"
    exit 1
fi

%build
# Reproducible build flags
export SOURCE_DATE_EPOCH=$(date -d '2025-02-06' +%s)
export KBUILD_BUILD_TIMESTAMP='Thu Feb  6 00:00:00 UTC 2025'
export KBUILD_BUILD_USER='builder'
export KBUILD_BUILD_HOST='localhost'

# Find kernel source directory
KDIR="/usr/src/kernels/%{?kernels}"
if [ -z "%{?kernels}" ] || [ ! -d "${KDIR}" ]; then
    # Fall back to latest available kernel-devel
    KDIR=$(ls -1d /usr/src/kernels/* 2>/dev/null | sort -V | tail -1)
    if [ -z "${KDIR}" ] || [ ! -d "${KDIR}" ]; then
        echo "ERROR: No kernel-devel package found"
        exit 1
    fi
fi

echo "Building for kernel: $(basename ${KDIR})"

# Build all modules
make KDIR="${KDIR}" V=1 all

%install
# Find kernel version
KDIR="/usr/src/kernels/%{?kernels}"
if [ -z "%{?kernels}" ] || [ ! -d "${KDIR}" ]; then
    KDIR=$(ls -1d /usr/src/kernels/* 2>/dev/null | sort -V | tail -1)
fi
KVER=$(basename "${KDIR}")

# Install kernel modules
install -d %{buildroot}/lib/modules/${KVER}/extra/%{kmod_name}
install -m 0644 hid-tmff-new.ko \
    %{buildroot}/lib/modules/${KVER}/extra/%{kmod_name}/
install -m 0644 deps/hid-tminit/hid-tminit-new.ko \
    %{buildroot}/lib/modules/${KVER}/extra/%{kmod_name}/
install -m 0644 deps/hid-tminit/usb-tminit-new.ko \
    %{buildroot}/lib/modules/${KVER}/extra/%{kmod_name}/

%files
/lib/modules/*/extra/%{kmod_name}/

%post
# Update module dependencies
for kmod_dir in /lib/modules/*/extra/%{kmod_name}; do
    if [ -d "${kmod_dir}" ]; then
        kver=$(echo "${kmod_dir}" | cut -d'/' -f4)
        /sbin/depmod -a "${kver}" > /dev/null 2>&1 || :
    fi
done

%postun
# Update module dependencies after removal
if [ "$1" -eq 0 ]; then
    for kdir in /lib/modules/*; do
        if [ -d "${kdir}" ]; then
            kver=$(basename "${kdir}")
            /sbin/depmod -a "${kver}" > /dev/null 2>&1 || :
        fi
    done
fi

%changelog
* Sat Feb 08 2025 Build System <builder@localhost> - 0.82-1
- Initial kmod package for hid-tmff2 with akmod support
- Support for T300RS, T248, TX, T128, T598, TS-PC, TS-XW wheels
- Includes hid-tminit dependency modules (hid-tminit-new, usb-tminit-new)

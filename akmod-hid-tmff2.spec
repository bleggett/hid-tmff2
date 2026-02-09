# Akmod package for hid-tmff2 - Thrustmaster force feedback driver
#
# This spec file creates an akmod (Auto Kernel Module) package that automatically
# rebuilds kernel modules when the kernel is updated.
#
# Based on RPM Fusion akmod packaging guidelines:
# https://rpmfusion.org/Packaging/KernelModules/Akmods

%global debug_package %{nil}
%global kmod_name hid-tmff2

# Define paths if not already defined by systemd macros
%{!?_udevrulesdir:%global _udevrulesdir /usr/lib/udev/rules.d}

Name:           akmod-%{kmod_name}
Version:        0.82
Release:        1%{?dist}
Summary:        Akmod package for Thrustmaster T300RS, T248 and other racing wheels

License:        GPL-2.0-or-later
URL:            https://github.com/Kimplul/hid-tmff2

# For COPR "make srpm": .copr/Makefile creates these tarballs with submodules
# For local builds: run ./build-rpm.sh to generate tarball with submodules
Source0:        %{kmod_name}-%{version}.tar.gz
Source1:        hid-tminit.tar.gz
Source10:       specs/hid-tmff2-akmod.spec

# Build dependencies
BuildArch:      noarch
BuildRequires:  rpm-build

# Runtime dependencies
Requires:       akmods
Recommends:     linuxconsoletools

# Provide modalias for hardware auto-loading
Supplements:    modalias(hid:b0003g*v0000044Fp0000B65D)
Supplements:    modalias(hid:b0003g*v0000044Fp0000B664)
Supplements:    modalias(hid:b0003g*v0000044Fp0000B66[9DEF])
Supplements:    modalias(hid:b0003g*v0000044Fp0000B689)
Supplements:    modalias(hid:b0003g*v0000044Fp0000B69C)

%description
A Linux kernel module for Thrustmaster T300RS, T248, and experimental support
for TX, T128, T598, TS-PC and TS-XW racing wheels.

This akmod package automatically builds kernel modules for each installed kernel
version, ensuring the driver works after kernel updates without manual rebuilding.

The driver includes wheel initialization modules (hid-tminit) and the main
force feedback driver (hid-tmff-new).

%prep
# Extract main source so we can access udev rules
%autosetup -n %{kmod_name}-%{version}

# Extract hid-tminit submodule (Source1)
mkdir -p deps
tar -xzf %{SOURCE1} -C deps

%build
# Build a kmod SRPM for akmods to use
mkdir -p _srpm_build
rpmbuild -bs %{SOURCE10} \
    --define "_sourcedir %{_sourcedir}" \
    --define "_srcrpmdir $(pwd)/_srpm_build" \
    --define "dist .fc%{fedora}"

%install
# Install the kmod SRPM that akmods will use to build modules
install -d %{buildroot}%{_usrsrc}/akmods/
install -m 0644 _srpm_build/kmod-%{kmod_name}-%{version}-*.src.rpm \
    %{buildroot}%{_usrsrc}/akmods/%{kmod_name}-kmod.latest

# Install udev rules from the extracted source
cd %{_builddir}/%{kmod_name}-%{version}
install -D -m 0644 udev/99-thrustmaster.rules \
    %{buildroot}%{_udevrulesdir}/99-thrustmaster.rules
install -D -m 0644 udev/71-thrustmaster-steamdeck.rules \
    %{buildroot}%{_udevrulesdir}/71-thrustmaster-steamdeck.rules
cd -

# Install modprobe configuration
install -D -m 0644 /dev/stdin \
    %{buildroot}%{_sysconfdir}/modprobe.d/hid-tmff2.conf << 'MODPROBE_EOF'
# Blacklist the upstream hid-thrustmaster driver to prevent conflicts
# The hid-tmff-new driver provides enhanced functionality
blacklist hid_thrustmaster
MODPROBE_EOF

%files
%{_usrsrc}/akmods/%{kmod_name}-kmod.latest
%{_udevrulesdir}/99-thrustmaster.rules
%{_udevrulesdir}/71-thrustmaster-steamdeck.rules
%config(noreplace) %{_sysconfdir}/modprobe.d/hid-tmff2.conf

%posttrans
# This runs after the transaction is complete
# Trigger akmod build for current kernel
echo "Building %{kmod_name} modules for current kernel..."
/usr/sbin/akmods --force --kernels $(uname -r) --akmod %{kmod_name} || :

# Reload udev rules
if [ -x /usr/bin/udevadm ]; then
    /usr/bin/udevadm control --reload-rules || :
fi

echo "Akmod installation complete. Modules will be automatically built for new kernels."

%preun
# Before uninstalling, remove built modules for all kernels
if [ "$1" -eq 0 ]; then
    # Package removal (not upgrade)
    for kdir in /lib/modules/*; do
        if [ -d "${kdir}" ]; then
            kver=$(basename "${kdir}")
            # Remove our modules
            rm -rf "/lib/modules/${kver}/extra/%{kmod_name}/" 2>/dev/null || :
            # Update module dependencies
            if [ -x /sbin/depmod ]; then
                /sbin/depmod -a "${kver}" 2>/dev/null || :
            fi
        fi
    done
fi

%changelog
* Sat Feb 08 2025 Build System <builder@localhost> - 0.82-1
- Initial akmod package for hid-tmff2
- Support for T300RS, T248, TX, T128, T598, TS-PC, TS-XW wheels
- Includes hid-tminit dependency modules (hid-tminit-new, usb-tminit-new)
- Provides udev rules for automatic wheel detection
- Blacklists conflicting hid_thrustmaster driver
- Implements automatic kernel module building on kernel updates

%global _changelog_trimtime %(date +%s -d "1 year ago")

%global glib2_version 2.54.0
%global libdnf_version 0.43.1

Summary:   Package management service
Name:      PackageKit
Version:   1.2.4
Release:   2%{?dist}
License:   GPLv2+ and LGPLv2+
URL:       http://www.freedesktop.org/software/PackageKit/
Source0:   http://www.freedesktop.org/software/PackageKit/releases/%{name}-%{version}.tar.xz

%if 0%{?fedora}
Patch0:    PackageKit-0.3.8-Fedora-Vendor.conf.patch
%elif 0%{?rhel}
Patch0:    PackageKit-0.3.8-RHEL-Vendor.conf.patch
%endif

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: xmlto
BuildRequires: gtk-doc
BuildRequires: sqlite-devel
BuildRequires: polkit-devel >= 0.92
BuildRequires: gtk3-devel
BuildRequires: docbook-utils
BuildRequires: meson
BuildRequires: gettext
BuildRequires: vala
BuildRequires: gstreamer1-devel
BuildRequires: gstreamer1-plugins-base-devel
BuildRequires: pango-devel
BuildRequires: fontconfig-devel
BuildRequires: libappstream-glib-devel
BuildRequires: libdnf-devel >= %{libdnf_version}
BuildRequires: systemd-devel
BuildRequires: gobject-introspection-devel
BuildRequires: bash-completion

Requires: %{name}-glib%{?_isa} = %{version}-%{release}
Requires: glib2%{?_isa} >= %{glib2_version}
Requires: libdnf%{?_isa} >= %{libdnf_version}
Requires: shared-mime-info
Requires: systemd

# functionality moved to udev itself
Obsoletes: PackageKit-udev-helper < %{version}-%{release}
Obsoletes: udev-packagekit < %{version}-%{release}

# No more GTK+-2 plugin
Obsoletes: PackageKit-gtk-module < %{version}-%{release}

# No more zif, smart or yum in Fedora
Obsoletes: PackageKit-smart < %{version}-%{release}
Obsoletes: PackageKit-yum < 0.9.1
Obsoletes: PackageKit-yum-plugin < 0.9.1
Obsoletes: PackageKit-zif < 0.8.13-2

# components now built-in
Obsoletes: PackageKit-debug-install < 0.9.1
Obsoletes: PackageKit-hawkey < 0.9.1
Obsoletes: PackageKit-backend-devel < 0.9.6

# Udev no longer provides this functionality
Obsoletes: PackageKit-device-rebind < 0.8.13-2

%description
PackageKit is a D-Bus abstraction layer that allows the session user
to manage packages in a secure way using a cross-distro,
cross-architecture API.

%package glib
Summary: GLib libraries for accessing PackageKit
Requires: dbus >= 1.1.1
Requires: gobject-introspection
Obsoletes: PackageKit-libs < %{version}-%{release}
Provides: PackageKit-libs = %{version}-%{release}

%description glib
GLib libraries for accessing PackageKit.

%package cron
Summary: Cron job and related utilities for PackageKit
Requires: crontabs
Requires: %{name}%{?_isa} = %{version}-%{release}

%description cron
Crontab and utilities for running PackageKit as a cron job.

%package glib-devel
Summary: GLib Libraries and headers for PackageKit
Requires: %{name}-glib%{?_isa} = %{version}-%{release}
Requires: dbus-devel%{?_isa} >= 1.1.1
Requires: sqlite-devel%{?_isa}
Obsoletes: PackageKit-devel < %{version}-%{release}
Provides: PackageKit-devel = %{version}-%{release}
Obsoletes: PackageKit-docs < %{version}-%{release}
Provides: PackageKit-docs = %{version}-%{release}

%description glib-devel
GLib headers and libraries for PackageKit.

%package gstreamer-plugin
Summary: Install GStreamer codecs using PackageKit
Requires: %{name}-glib%{?_isa} = %{version}-%{release}
Obsoletes: codeina < 0.10.1-10
Provides: codeina = 0.10.1-10

%description gstreamer-plugin
The PackageKit GStreamer plugin allows any Gstreamer application to install
codecs from configured repositories using PackageKit.

%package gtk3-module
Summary: Install fonts automatically using PackageKit
Requires: pango
Requires: %{name}-glib%{?_isa} = %{version}-%{release}

%description gtk3-module
The PackageKit GTK3+ module allows any Pango application to install
fonts from configured repositories using PackageKit.

%package command-not-found
Summary: Ask the user to install command line programs automatically
Requires: bash
Requires: %{name} = %{version}-%{release}
Requires: %{name}-glib%{?_isa} = %{version}-%{release}

%description command-not-found
A simple helper that offers to install new packages on the command line
using PackageKit.

%prep
%autosetup -p1

%build
%meson \
        -Dgtk_doc=true \
        -Dpython_backend=false \
        -Dpackaging_backend=dnf \
        -Dlocal_checkout=false
%meson_build

%install
%meson_install

# Create directories for downloaded appstream data
mkdir -p %{buildroot}%{_localstatedir}/cache/app-info/{icons,xmls}

# create a link that GStreamer will recognise
pushd %{buildroot}%{_libexecdir} > /dev/null
ln -s pk-gstreamer-install gst-install-plugins-helper
popd > /dev/null

# enable packagekit-offline-updates.service here for now, till we
# decide how to do it upstream after the meson conversion:
# https://github.com/hughsie/PackageKit/issues/401
# https://bugzilla.redhat.com/show_bug.cgi?id=1833176
mkdir -p %{buildroot}%{_unitdir}/system-update.target.wants/
ln -sf ../packagekit-offline-update.service %{buildroot}%{_unitdir}/system-update.target.wants/packagekit-offline-update.service

%find_lang %name

%post
# Remove leftover symlinks from /etc/systemd; the offline update service is
# instead now hooked into /usr/lib/systemd/system/system-update.target.wants
systemctl disable packagekit-offline-update.service > /dev/null 2>&1 || :

%files -f %{name}.lang
%license COPYING
%doc README AUTHORS NEWS
%dir %{_datadir}/PackageKit
%dir %{_sysconfdir}/PackageKit
%dir %{_localstatedir}/lib/PackageKit
%dir %{_localstatedir}/cache/app-info
%dir %{_localstatedir}/cache/app-info/icons
%dir %{_localstatedir}/cache/app-info/xmls
%{_datadir}/bash-completion/completions/pkcon
%dir %{_libdir}/packagekit-backend
%config(noreplace) %{_sysconfdir}/PackageKit/PackageKit.conf
%config(noreplace) %{_sysconfdir}/PackageKit/Vendor.conf
%config %{_sysconfdir}/dbus-1/system.d/*
%{_datadir}/man/man1/pkcon.1*
%{_datadir}/man/man1/pkmon.1*
%{_datadir}/polkit-1/actions/*.policy
%{_datadir}/polkit-1/rules.d/*
%{_datadir}/PackageKit/pk-upgrade-distro.sh
%{_datadir}/PackageKit/helpers/test_spawn/search-name.sh
%{_libexecdir}/packagekitd
%{_libexecdir}/packagekit-direct
%{_bindir}/pkmon
%{_bindir}/pkcon
%exclude %{_libdir}/libpackagekit*.so.*
%{_libdir}/packagekit-backend/libpk_backend_dummy.so
%{_libdir}/packagekit-backend/libpk_backend_test_*.so
%ghost %verify(not md5 size mtime) %attr(0644,-,-) %{_localstatedir}/lib/PackageKit/transactions.db
%{_datadir}/dbus-1/system-services/*.service
%{_datadir}/dbus-1/interfaces/*.xml
%{_unitdir}/packagekit-offline-update.service
%{_unitdir}/packagekit.service
%{_unitdir}/system-update.target.wants/
%{_libexecdir}/pk-*offline-update
%{_libdir}/packagekit-backend/libpk_backend_dnf.so

%files glib
%{_libdir}/*packagekit-glib2.so.*
%{_libdir}/girepository-1.0/PackageKitGlib-1.0.typelib

%files cron
%config %{_sysconfdir}/cron.daily/packagekit-background.cron
%config(noreplace) %{_sysconfdir}/sysconfig/packagekit-background

%files gstreamer-plugin
%{_libexecdir}/pk-gstreamer-install
%{_libexecdir}/gst-install-plugins-helper

%files gtk3-module
%{_libdir}/gtk-3.0/modules/*.so
%{_libdir}/gnome-settings-daemon-3.0/gtk-modules/*.desktop

%files command-not-found
%{_sysconfdir}/profile.d/*
%{_libexecdir}/pk-command-not-found
%config(noreplace) %{_sysconfdir}/PackageKit/CommandNotFound.conf

%files glib-devel
%{_libdir}/libpackagekit-glib2.so
%{_libdir}/pkgconfig/packagekit-glib2.pc
%dir %{_includedir}/PackageKit
%dir %{_includedir}/PackageKit/packagekit-glib2
%{_includedir}/PackageKit/packagekit-glib*/*.h
%{_datadir}/gir-1.0/PackageKitGlib-1.0.gir
%{_datadir}/gtk-doc/html/PackageKit
%{_datadir}/vala/vapi/packagekit-glib2.vapi
%{_datadir}/vala/vapi/packagekit-glib2.deps

%changelog
* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.2.4-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Mon Aug 09 2021 Milan Crha <mcrha@redhat.com> - 1.2.4-1
- New upstream release
- Add specific error code when user declined interaction
- Avoid spurious GObject::notify signal emissions
- Fix a leak on calling set_locale() a second time
- Fix a possible use-after-free under pk_client_cancel_cb()
- Honor install_weak_deps=False
- Improve thread safety on an operation cancellation
- Let the finish understand the 'cancelled' exit code
- Only set polkit interactive flag if method call has too
- Read update information also when getting list of updates
- Use 'hy_query_get_advisory_pkgs', if available

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 1.2.3-3
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 1.2.3-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Mon Mar 22 2021 Richard Hughes <rhughes@redhat.com> - 1.2.3-1
- New upstream release
- Add support for coercing upgrade to distupgrade
- Append to cron log instead of overwriting it
- Cancel a transaction if calling Cancel fails or the daemon disappears
- Remove large transaction size sanity check

* Mon Mar 08 2021 Richard Hughes <rhughes@redhat.com> - 1.2.2-5
- Drop unused gnome-doc-utils BR

* Tue Feb 09 2021 Kalev Lember <klember@redhat.com> - 1.2.2-4
- Fix multilib conflicts in generated pk-enum-types.h (#1915259)

* Mon Jan 25 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Nov  9 2020 Vít Ondruch <vondruch@redhat.com> - 1.2.2-2
- Fix crash on login.
  Resolves: rhbz#1836304

* Mon Nov 02 2020 Richard Hughes <rhughes@redhat.com> - 1.2.2-1
- New upstream release
- Notify systemd when beginning to shutdown
- Fix possible information disclosure

* Mon Sep 07 2020 Richard Hughes <rhughes@redhat.com> - 1.2.1-1
- New upstream release
- Actually merge in the PolicyKit translation
- Exit pkcon with retval 5 if no packages needed be installed
- Fix command-not-found handling arguments with spaces
- Fix setting libexecdir for command-not-found helper
- Use SQL statements for queries with input

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri May 08 2020 Adam Williamson <awilliam@redhat.com> - 1.2.0-3
- Fix packagekit-offline-update.service not being enabled (#1833176)

* Tue May 05 2020 Neal Gompa <ngompa13@gmail.com> - 1.2.0-2
- Clean up and simplify spec
- Fix packaging to work properly with EL8+

* Mon May 04 2020 Richard Hughes <rhughes@redhat.com> - 1.2.0-1
- New upstream release
- Do not do failable actions in constructors
- Load all the repos and vars directories
- Port to the meson build system
- Remove the GTK2 gtk-module support
- Revert "Shutdown the daemon on idle by default"

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jan 08 2020 Richard Hughes <rhughes@redhat.com> - 1.1.13-1
- New upstream release
- Don't use a bash regex to fix command not found on other shells
- Keep a ref on transaction while doing async polkit call
- Properly mark obsoleted packages when simulating upgrade
- Return directly when its state is going backwards
- Shrink the progress bar to fit when run in small spaces
- Support non-x86 arches in gstreamer helper
- zsh command not found should return the same as its bash equivalent

* Tue Aug 13 2019 Richard Hughes <rhughes@redhat.com> - 1.1.12-12
- Fix rpmdb permission of transaction database file

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jul 19 2019 Richard Hughes <rhughes@redhat.com> - 1.1.12-10
- Do not trigger an inotity event when the AppStream XML data is unchanged
- Remove the unconditional copy to speed up gnome-software startup.

* Fri Jul 12 2019 Kalev Lember <klember@redhat.com> - 1.1.12-9
- Drop unused comps-extras requires

* Wed Jun 19 2019 Kalev Lember <klember@redhat.com> - 1.1.12-8
- Don't override DnfContext's release_ver for the running system

* Mon Jun 10 22:13:21 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.1.12-7
- Rebuild for RPM 4.15

* Mon Jun 10 15:42:04 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.1.12-6
- Rebuild for RPM 4.15

* Mon Mar 04 2019 Kalev Lember <klember@redhat.com> - 1.1.12-5
- Use new plymouth "system-upgrade" and "reboot" modes

* Mon Feb 04 2019 Kalev Lember <klember@redhat.com> - 1.1.12-4
- Update BRs for vala packaging changes

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Dec 18 2018 Kalev Lember <klember@redhat.com> - 1.1.12-2
- Invalidate the sack cache after downloading new metadata (#1642878)

* Wed Nov 28 2018 Kalev Lember <klember@redhat.com> - 1.1.12-1
- Update to 1.1.12

* Tue Sep 25 2018 Richard Hughes <rhughes@redhat.com> - 1.1.11-1
- New upstream release
- Add --autoremove option to pkcon
- De-register callbacks on PkClientHelper finalize
- Don't complain if command-not-found get uninstalled while running
- Never assert when an interactive TTY is not available
- Shut down services cleanly before rebooting after offline updates
- Shutdown the daemon on idle by default

* Sat Sep 22 2018 Adam Williamson <awilliam@redhat.com> - 1.1.10-5
- Backport several more fixes from master for libdnf compat

* Tue Jul 24 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.1.10-4
- Add patch to support modularity

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 26 2018 Adam Williamson <awilliam@redhat.com> - 1.1.10-2
- Rebuild for new libdnf

* Mon Apr 23 2018 Richard Hughes <rhughes@redhat.com> - 1.1.10-1
- New upstream release
- This release fixes CVE-2018-1106 which is a moderate security issue.

* Tue Mar 27 2018 Kalev Lember <klember@redhat.com> - 1.1.9-4
- Remove ldconfig scriptlets

* Thu Mar 22 2018 Kalev Lember <klember@redhat.com> - 1.1.9-3
- Create /var/cache/app-info/{icons,xmls} directories

* Mon Mar 12 2018 Kalev Lember <klember@redhat.com> - 1.1.9-2
- Don't abort on daemon startup for invalid .repo files

* Mon Mar 05 2018 Kalev Lember <klember@redhat.com> - 1.1.9-1
- Update to 1.1.9

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 09 2018 Kalev Lember <klember@redhat.com> - 1.1.8-1
- Update to 1.1.8

* Mon Sep 11 2017 Richard Hughes <rhughes@redhat.com> - 1.1.7-1
- New upstream release
- Add fedora-cisco-openh264 repos to supported repos list
- Add missing context pushes and pops in appstream-glib
- Add the ability to install updates on reboot in PackageKit-cron
- Effectively check for previous proxy entries
- Fix an inverted condition that led to frequent crashes
- Show a different progress message for system upgrades

* Fri Aug 11 2017 Igor Gnatenko <ignatenko@redhat.com> - 1.1.6-7
- Rebuilt after RPM update (№ 3)

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 1.1.6-6
- Rebuilt for RPM soname bump

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 1.1.6-5
- Rebuilt for RPM soname bump

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun 15 2017 Richard Hughes <rhughes@redhat.com> - 1.1.6-2
- Fix a crash when refreshing the metadata cache
- Resolves: #1460825

* Wed Jun 07 2017 Richard Hughes <rhughes@redhat.com> - 1.1.6-1
- New upstream release
- Ensure AppStream is deployed when the repo is updated

* Fri Mar 24 2017 Kalev Lember <klember@redhat.com> - 1.1.5-4
- Fix the offline updater to work with latest systemd (#1430920)

* Fri Mar 17 2017 Kalev Lember <klember@redhat.com> - 1.1.5-3
- Build with system libdnf

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 17 2017 Kalev Lember <klember@redhat.com> - 1.1.5-1
- Update to 1.1.5
- Update to latest libdnf git snapshot (#1398429)

* Wed Dec 21 2016 Kalev Lember <klember@redhat.com> - 1.1.5-0.1.20161221
- Update to latest git snapshot

* Mon Dec 19 2016 Kalev Lember <klember@redhat.com> - 1.1.4-3
- Adapt for libhif->libdnf git repo rename

* Fri Dec 16 2016 Kalev Lember <klember@redhat.com> - 1.1.4-2
- Update to latest libdnf git snapshot (#1383819)

* Mon Sep 19 2016 Richard Hughes <rhughes@redhat.com> - 1.1.4-1
- New upstream release
- Change the configuration of the cron script to a sysconfig-like config
- Don't crash when emitting PropertiesChanged for NULL values
- Fix several small memory leaks
- Look for command-not-found dbus socket in /run instead of /var/run
- Use GetFilesLocal in pkcon get-files if argument is a file

* Thu Sep 08 2016 Kalev Lember <klember@redhat.com> - 1.1.4-0.4.20160901
- Update to latest libdnf git snapshot (#1344643)

* Thu Sep 01 2016 Kalev Lember <klember@redhat.com> - 1.1.4-0.3.20160901
- Update to latest git snapshot

* Wed Aug 31 2016 Kalev Lember <klember@redhat.com> - 1.1.4-0.2.20160825
- Update to latest git snapshot

* Fri Aug 05 2016 Kalev Lember <klember@redhat.com> - 1.1.4-0.1.20160805
- Update to today's git snapshot
- Switch to new libdnf based backend

* Wed Jul 27 2016 Kalev Lember <klember@redhat.com> - 1.1.3-2
- engine: Don't crash when emitting PropertiesChanged for NULL values
  (#1359479)

* Thu Jul 14 2016 Kalev Lember <klember@redhat.com> - 1.1.3-1
- Update to 1.1.3

* Tue Jul 12 2016 Kalev Lember <klember@redhat.com> - 1.1.2-1
- Update to 1.1.2
- Set minimum required glib2 and libhif versions

* Tue Jun 07 2016 Kalev Lember <klember@redhat.com> - 1.1.1-3
- Match unavailable packages for the what-provides query

* Sat May 28 2016 Kalev Lember <klember@redhat.com> - 1.1.1-2
- Require admin authorisation to trigger a distro upgrade (#1335458)

* Wed Apr 20 2016 Richard Hughes <rhughes@redhat.com> - 1.1.1-1
- New upstream release
- Add TriggerUpgrade DBus method handling
- Emit UpdatesChanges when installing packages
- Fix GIR annotations for progress callbacks
- Increase the number of packages that can be resolved
- Point offline update/upgrade trigger to the prepared update
- Set ALLOW_DOWNGRADE flag for all transactions

* Fri Feb 12 2016 Richard Hughes <rhughes@redhat.com> - 1.1.0-1
- New upstream release
- Add support for UpgradeSystem
- Correctly store file descriptor from logind
- Do not crash on GetPrepared when there are no offline updates
- Do not crash on transaction database corruption
- Do not crash when parsing a very broken transaction log
- Port to g_autoptr()
- Relax validation performed on input strings passed to backends
- Remove the PackageKit browser plugin
- Use the GLib network monitoring support

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Nov 27 2015 Richard Hughes <rhughes@redhat.com> - 1.0.11-1
- Add support for HTTP proxy
- Allow the use of variadic functions in vala
- By popular demand, reintroduce the UpgradeSystem method
- Improve RefreshCache progress updates
- New upstream release

* Mon Oct 19 2015 Kalev Lember <klember@redhat.com> - 1.0.10-2
- Remove PackageKit-cached-metadata subpackage

* Mon Sep 21 2015 Richard Hughes <rhughes@redhat.com> - 1.0.10-1
- Update to 1.0.10 to fix a couple of bugs in the offline updater

* Tue Sep 15 2015 Richard Hughes <rhughes@redhat.com> - 1.0.9-1
- New upstream release
- Check the offline action trigger before performing the update
- Fix a race with the backend job thread creation

* Sat Sep 05 2015 Kalev Lember <klember@redhat.com> - 1.0.8-3
- Rebuilt for librpm soname bump

* Thu Aug 20 2015 Kalev Lember <klember@redhat.com> - 1.0.8-2
- Revert "Correctly register enum properties" as this broke offline updates

* Wed Aug 19 2015 Richard Hughes <rhughes@redhat.com> - 1.0.8-1
- New upstream release
- Exit quietly if we didn't prepare the offline update
- Record the UID of the session user in the yumdb

* Fri Aug 14 2015 Kalev Lember <klember@redhat.com> - 1.0.7-3
- Rebuild for new libappstream-glib

* Sun Jul 26 2015 Kevin Fenzi <kevin@scrye.com> 1.0.7-2
- Rebuild for new librpm

* Mon Jul 13 2015 Richard Hughes <rhughes@redhat.com> - 1.0.7-1
- New upstream release
- Correct punctuation while applying offline updates
- Define command_not_found_handler for zsh
- Port GTK+ module to org.freedesktop.PackageKit.Modify2
- Return the correct return codes for syntax errors

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.6-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.6-6
- Actually apply the patches

* Mon Jun 08 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.6-5
- Backport a few more upstream patches:
- Add missing locking when accessing sack cache (#1146734)
- Improve parallel kernel installation (#1205649)

* Wed May 20 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.6-4
- Update cached metadata in preparation for F22 release

* Fri May 15 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.6-3
- Revert a commit that inadvertantly changed the default value for the
  TriggerAction DBus property

* Mon May 11 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.6-2
- Update cached metadata

* Tue Apr 07 2015 Richard Hughes <rhughes@redhat.com> - 1.0.6-1
- New upstream release
- Add dbus method for returning prepared packages
- Don't recursive lock the debug mutex when using --verbose without a tty
- Make "reboot" the default action for no action file

* Sat Mar 28 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.5-2
- Backport a crash fix from upstream (#1185544)
- Update cached metadata
- Use license macro for the COPYING file

* Sat Feb 21 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.5-1
- Update to 1.0.5
- Backport new missing gstreamer codecs API

* Fri Feb 06 2015 Richard Hughes <rhughes@redhat.com> - 1.0.4-2
- Adapt to the new hawkey API.

* Mon Jan 19 2015 Richard Hughes <rhughes@redhat.com> - 1.0.4-1
- New upstream release
- Actually inhibit logind when the transaction can't be cancelled
- Add 'quit' command to pkcon
- Automatically import metadata public keys when safe to do so
- Automatically install AppStream metadata
- Do not attempt to run command-not-found for anything prefixed with '.'
- Don't use PkBackendSpawn helpers in compiled backends
- Fix a hard-to-debug crash when cancelling a task that has never been run
- Look for unavailable packages during resolve
- Make pk_backend_job_call_vfunc() threadsafe
- Make pk_backend_repo_list_changed() threadsafe
- Return 'unavailable' packages for metadata-only repos
- Use a thread-local HifTransaction to avoid db3 index corruption

* Mon Nov 17 2014 Kalev Lember <kalevlember@gmail.com> - 1.0.3-2
- Update cached metadata in preparation for F21 release

* Mon Nov 10 2014 Richard Hughes <rhughes@redhat.com> - 1.0.3-1
- New upstream release
- Add support for reinstallation and downgrades
- Be smarter when using the vendor cache

* Tue Oct 21 2014 Richard Hughes <rhughes@redhat.com> - 1.0.1-1
- New upstream release
- Add a KeepCache config parameter
- Do not install the python helpers
- Invalidate offline updates when the rpmdb changes
- Never allow cancelling a transaction twice

* Wed Oct 15 2014 Kalev Lember <kalevlember@gmail.com> - 1.0.1-0.1.20141015
- Update to today's git snapshot

* Tue Sep 16 2014 Richard Hughes <rhughes@redhat.com> - 1.0.0-2
- Add a new subpackage designed for the workstation spin.
- See http://blogs.gnome.org/hughsie/2014/08/29/ for details.

* Fri Sep 12 2014 Richard Hughes <rhughes@redhat.com> - 1.0.0-1
- New upstream release
- Add a D-Bus interface and helpers for offline support
- Do not shutdown the daemon on idle by default
- Refresh the NetworkManager state when the daemon starts
- Remove pk-debuginfo-install
- Remove the events/pre-transaction.d functionality
- Remove the pkexec systemd helpers
- Remove the plugin interface
- Remove various options from the config file

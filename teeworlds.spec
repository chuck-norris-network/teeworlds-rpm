%global _hardened_build 1
Name:             teeworlds
Version:          0.6.3
Release:          4%{?dist}
Summary:          Online multi-player platform 2D shooter

Group:            Amusements/Games
License:          Teeworlds
URL:              http://www.teeworlds.com/
Source0:          http://downloads.teeworlds.com/%{name}-%{version}-src.tar.gz
Source1:          %{name}.png
Source2:          %{name}.desktop
# systemd unit definition
Source3:          %{name}-server@.service
# example configs file for server
Source4:          server_dm.cfg
Source5:          server_tdm.cfg
Source6:          server_ctf.cfg
Patch0:           %{name}-0.6.2-extlibs-optflags.patch

BuildRequires:    mesa-libGLU-devel
BuildRequires:    bam >= 0.4.0
BuildRequires:    python-devel
BuildRequires:    alsa-lib-devel
BuildRequires:    desktop-file-utils
BuildRequires:    zlib-devel
BuildRequires:    wavpack-devel
BuildRequires:    pnglite-devel
BuildRequires:    SDL-devel
BuildRequires:    libpng-devel
BuildRequires:    freetype-devel
Requires:         %{name}-data

%description
The game features cartoon-themed graphics and physics, 
and relies heavily on classic shooter weaponry and gameplay. 
The controls are heavily inspired by the FPS genre of computer games. 

%package          server
Summary:          Server for %{name}
Group:            Amusements/Games
Requires:         %{name}-data
Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
BuildRequires:    systemd

%description      server
Server for %{name}, an online multi-player platform 2D shooter. 

%package          data
Summary:          Data-files for %{name}
Group:            Amusements/Games

%description      data
Data-files for %{name}, an online multi-player platform 2D shooter.

%pre server
getent group teeworlds >/dev/null || groupadd -f -r teeworlds
if ! getent passwd teeworlds >/dev/null ; then
      useradd -r -g teeworlds -d %{_sysconfdir}/%{name} -s /sbin/nologin \
              -c "%{name} server daemon account" teeworlds
fi
exit 0

%prep
%setup -q -n %{name}-%{version}-src
rm -rf src/engine/external

%patch0 -p1

#for f in ./readme.txt ./src/game/editor/array.hpp
#do
#  iconv -f iso-8859-1 -t utf-8 $f |sed 's|\r||g' > $f.utf8
#  touch -c -r $f $f.utf8
#  mv $f.utf8 $f
#done

%build
CFLAGS="%{optflags}" bam -v release

%install
rm -rf %{buildroot}/
mkdir -p %{buildroot}%{_datadir}/%{name}/data/
mkdir -p %{buildroot}%{_datadir}/pixmaps/

install -D -m 0755 %{name} \
        %{buildroot}%{_bindir}/%{name}

install -D -m 0755 %{name}_srv \
        %{buildroot}%{_bindir}/%{name}-srv

cp -pr data/* \
   %{buildroot}%{_datadir}/%{name}/data/

install -p -m 0644 %{SOURCE1} \
        %{buildroot}%{_datadir}/pixmaps/%{name}.png

desktop-file-install \
                     %if 0%{?rhel}
                     --vendor="" \
                     %endif
                     --dir=%{buildroot}%{_datadir}/applications \
                     %{SOURCE2}

# Register as an application to be visible in the software center
#
# NOTE: It would be *awesome* if this file was maintained by the upstream
# project, translated and installed into the right place during `make install`.
#
# See http://www.freedesktop.org/software/appstream/docs/ for more details.
#
mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata
cat > $RPM_BUILD_ROOT%{_datadir}/appdata/%{name}.appdata.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2014 Eduardo Mayorga <e@mayorgalinux.com> -->
<!--
EmailAddress: contact@teeworlds.com
SentUpstream: 2014-09-25
-->
<application>
  <id type="desktop">teeworlds.desktop</id>
  <metadata_license>CC0-1.0</metadata_license>
  <summary>Online multiplayer shooter game</summary>
  <description>
    <p>
      Teeworlds is a 2D online action game for up to 16 players battling in
      several game modes.
      The controls are inspired by First Person Shooter game genre.
      It lets you desing custom maps.
    </p>
  </description>
  <url type="homepage">http://www.teeworlds.com/</url>
  <screenshots>
    <screenshot type="default">https://www.teeworlds.com/images/screens/screenshot_jungle.png</screenshot>
  </screenshots>
</application>
EOF

mkdir -p %{buildroot}%{_unitdir}/

install    -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}-server@.service
install -d -m 0775 %{buildroot}%{_sysconfdir}/%{name}/
install    -m 0664 %{SOURCE4} %{buildroot}%{_sysconfdir}/%{name}/dm.cfg
install    -m 0664 %{SOURCE5} %{buildroot}%{_sysconfdir}/%{name}/tdm.cfg
install    -m 0664 %{SOURCE6} %{buildroot}%{_sysconfdir}/%{name}/ctf.cfg

%post server
%systemd_post %{name}-server@dm.service
%systemd_post %{name}-server@tdm.service
%systemd_post %{name}-server@ctf.service

%preun server
%systemd_preun %{name}-server@dm.service
%systemd_preun %{name}-server@tdm.service
%systemd_preun %{name}-server@ctf.service

%postun server
%systemd_postun_with_restart %{name}-server@dm.service
%systemd_postun_with_restart %{name}-server@tdm.service
%systemd_postun_with_restart %{name}-server@ctf.service

%files
%doc readme.txt license.txt
%{_bindir}/%{name}
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/applications/%{name}.desktop

%files data
%{_datadir}/%{name}/

%files server
%doc readme.txt license.txt
%{_bindir}/%{name}-srv
%{_unitdir}/%{name}-server@.service
%attr(-,teeworlds,teeworlds)%{_sysconfdir}/%{name}/

%changelog
* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 0.6.3-3
- Rebuilt for GCC 5 C++11 ABI change

* Thu Mar 26 2015 Richard Hughes <rhughes@redhat.com> - 0.6.3-2
- Add an AppData file for the software center

* Mon Nov 24 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.3-1
- 0.6.3 (RHBZ #1167167,#1167168)

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.2-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Nov 25 2013 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.2-7
- fix permissions (allow access from teeworlds group to server cfgs)

* Sat Aug 17 2013 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.2-6
- Fixed port in example tdm server cfg

* Tue Jul 30 2013 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.2-5
- Typo fix in source list in server cfgs

* Tue Jul 23 2013 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.2-4
- Add sample tdm server config
- Few fixes in existing server configs
- Droped BuildRoot target (since Fedora 18 was deprecated)
- Dropped %clean section (since Fedora 18 was deprecated)
- Dropped %defattr directives (since Fedora 18 was deprecated)
- %{buildroot} instead of $RPM_BUILD_ROOT

* Fri Jul  5 2013 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.2-3
- systemd instead of systemd-units in spec file

* Wed Jul  3 2013 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.2-2
- Update systemd daemon for multiple server configs
- Some fixes in spec

* Tue Jul  2 2013 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.6.2-1
- Update to 0.6.2
- Drop unnecessary patches and fix need patches for new version
- Add systemd daemon with example server cfg
- Some fixes in spec

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Apr 13 2012 Jon Ciesla <limburgher@gmail.com> - 0.6.1-4
- Add hardened build.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Sep 27 2011 Jon Ciesla <limb@jcomserv.net> - 0.6.1-2
- Fix to extlib patch to correct sound loading issue.

* Mon Aug 22 2011 Jon Ciesla <limb@jcomserv.net> - 0.6.1-1
- New upstream release

* Tue Apr 26 2011 Jon Ciesla <limb@jcomserv.net> - 0.6.0-1
- New upstream release

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec 24 2009 Simon Wesp <cassmodiah@fedoraproject.org> 0.5.2-2
- convert iso files to utf8

* Thu Dec 24 2009 Simon Wesp <cassmodiah@fedoraproject.org> 0.5.2-1
- New upstream release

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Mar 09 2009 Simon Wesp <cassmodiah@fedoraproject.org> 0.5.1-1
- New upstream release

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 17 2009 Lubomir Rintel <lkundrak@v3.sk> 0.5.0-1
- New upstream release

* Fri Jan 02 2009 Simon Wesp <cassmodiah@fedoraproject.org> 0.4.3-5
- Remove requires from subpackage 'data'
- Correct description 

* Thu Jan 01 2009 Simon Wesp <cassmodiah@fedoraproject.org> 0.4.3-4
- Drop desktop-file and icon for subpackage 'server'
- Honor timestamp for converted file
- Add and correct Lubomir's changes
- Remove all comments
- Correct License-Tag (again)
- Add datadir patch

* Wed Dec 31 2008 Lubomir Rintel <lkundrak@v3.sk> 0.4.3-3
- Outsource the dependencies (extlib-patch)
- Use optflags

* Thu Sep 18 2008 Simon Wesp <cassmodiah@fedoraproject.org> 0.4.3-2
- Recheck and conform licensing and list it in a comment
- Correct BuildRequires

* Sat Sep 13 2008 Simon Wesp <cassmodiah@fedoraproject.org> 0.4.3-1
- Initial Release


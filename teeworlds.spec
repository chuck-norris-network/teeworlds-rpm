%global commit 1b8209ff5ad8c4451e1aa7bc8e29c3cf0cbc7b71
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global _hardened_build 1

Name:             teeworlds
Version:          0.6.4
Release:          20160923git%{shortcommit}%{?dist}
Summary:          Online multi-player platform 2D shooter

Group:            Amusements/Games
License:          Teeworlds
URL:              http://www.teeworlds.com/
Source0:          https://github.com/chuck-norris-network/teeworlds/archive/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz
Source1:          %{name}.png
Source2:          %{name}.desktop
# systemd unit definition
Source3:          %{name}-server@.service
# example configs file for server
Source4:          server_dm.cfg
Source5:          server_tdm.cfg
Source6:          server_ctf.cfg

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
BuildRequires:    c-ares-devel
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
%setup -q -n %{name}-%{commit}

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

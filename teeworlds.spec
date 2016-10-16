%global commit c45f2956b8b9b288bf95f53d7d3e600b18f7c50e
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global origname teeworlds
%global _hardened_build 1

Name:             teeworlds-server
Version:          0.6.4
Release:          20161016git%{shortcommit}%{?dist}
Summary:          Online multi-player platform 2D shooter

Group:            Amusements/Games
Summary:          Server for %{origname}
License:          Teeworlds
URL:              http://www.teeworlds.com/
Source0:          https://github.com/chuck-norris-network/%{origname}/archive/%{commit}.tar.gz#/%{origname}-%{shortcommit}.tar.gz
# systemd unit definition
Source1:          %{name}@.service
# example configs file for server
Source2:          server_dm.cfg
Source3:          server_tdm.cfg
Source4:          server_ctf.cfg

BuildRequires:    bam >= 0.4.0
BuildRequires:    python-devel
BuildRequires:    zlib-devel
BuildRequires:    wavpack-devel
BuildRequires:    pnglite-devel
BuildRequires:    libpng-devel
BuildRequires:    c-ares-devel
BuildRequires:    systemd
Requires:         %{origname}-data
Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description
The game features cartoon-themed graphics and physics,
and relies heavily on classic shooter weaponry and gameplay.
The controls are heavily inspired by the FPS genre of computer games.

%package -n       %{origname}-data
Summary:          Data-files for %{origname}
Group:            Amusements/Games

%description -n   %{origname}-data
Data-files for %{origname}, an online multi-player platform 2D shooter.

%pre
getent group teeworlds >/dev/null || groupadd -f -r teeworlds
if ! getent passwd teeworlds >/dev/null ; then
      useradd -r -g teeworlds -d %{_sysconfdir}/%{origname} -s /sbin/nologin \
              -c "%{origname} server daemon account" teeworlds
fi
exit 0

%prep
%setup -q -n %{origname}-%{commit}

%build
CFLAGS="%{optflags}" bam -v release

%install
rm -rf %{buildroot}/
mkdir -p %{buildroot}%{_datadir}/%{origname}/data/

install -D -m 0755 %{origname}_srv \
        %{buildroot}%{_bindir}/%{origname}-srv

cp -pr data/* \
   %{buildroot}%{_datadir}/%{origname}/data/

mkdir -p %{buildroot}%{_unitdir}/

install    -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}@.service
install -d -m 0775 %{buildroot}%{_sysconfdir}/%{origname}/
install    -m 0664 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{origname}/dm.cfg
install    -m 0664 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{origname}/tdm.cfg
install    -m 0664 %{SOURCE4} %{buildroot}%{_sysconfdir}/%{origname}/ctf.cfg

%post
%systemd_post %{name}@dm.service
%systemd_post %{name}@tdm.service
%systemd_post %{name}@ctf.service

%preun
%systemd_preun %{name}@dm.service
%systemd_preun %{name}@tdm.service
%systemd_preun %{name}@ctf.service

%postun
%systemd_postun_with_restart %{name}@dm.service
%systemd_postun_with_restart %{name}@tdm.service
%systemd_postun_with_restart %{name}@ctf.service

%files
%doc readme.txt license.txt
%{_bindir}/%{origname}-srv
%{_unitdir}/%{name}@.service
%attr(-,teeworlds,teeworlds)%{_sysconfdir}/%{origname}/

%files -n %{origname}-data
%{_datadir}/%{origname}/

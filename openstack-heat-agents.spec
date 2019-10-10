# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver 3
%else
%global pyver 2
%endif

%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global project heat-agents

Name: openstack-heat-agents
Version: 1.10.0
Release: 1%{?dist}
Summary: Heat software config agent and hook scripts
License: ASL 2.0
URL: https://github.com/openstack/heat-agents
Obsoletes: openstack-heat-templates < 0.0.2
Source0: https://tarballs.openstack.org/%{project}/%{project}-%{upstream_version}.tar.gz

BuildArch: noarch

# Install all subpackages when main package is installed
Requires: python%{pyver}-heat-agent = %{version}-%{release}
Requires: python%{pyver}-heat-agent-puppet = %{version}-%{release}
Requires: python%{pyver}-heat-agent-ansible = %{version}-%{release}
Requires: python%{pyver}-heat-agent-apply-config = %{version}-%{release}
Requires: python%{pyver}-heat-agent-hiera = %{version}-%{release}
Requires: python%{pyver}-heat-agent-json-file = %{version}-%{release}
Requires: python%{pyver}-heat-agent-docker-cmd = %{version}-%{release}

%description
Heat software config agent and hook scripts

%prep
%setup -qn %{project}-%{upstream_version}

# Replace "env python" shebag to the correct python executable for the system
# if we don't do that brp-mangle-shebangs will change it to python2
for python_script in $(grep "/usr/bin/env python" . -rl)
do
    sed -i "s#/usr/bin/env python.*#/usr/bin/%{pyver_bin}#g" $python_script
done

%build

%install
# Use os-apply-config to bootstrap /etc/os-collect-config.conf
# from heat boot data
install -p -D -m 755 heat-config/os-refresh-config/configure.d/20-os-apply-config %{buildroot}%{_libexecdir}/os-refresh-config/configure.d/20-os-apply-config
install -p -D -m 600 heat-config/os-apply-config/etc/os-collect-config.conf %{buildroot}%{_libexecdir}/os-apply-config/templates/etc/os-collect-config.conf

# utilities which can be run by deployment scripts
install -p -D -m 755 heat-config/bin/heat-config-notify %{buildroot}/%{_bindir}/heat-config-notify
install -p -D -m 755 heat-config/bin/heat-config-rebuild-deployed %{buildroot}/%{_bindir}/heat-config-rebuild-deployed

# os-refresh-config script to run heat deployment resources
install -p -D -m 600 heat-config/os-apply-config/var/run/heat-config/heat-config %{buildroot}%{_libexecdir}/os-apply-config/templates/var/run/heat-config/heat-config
install -p -D -m 755 heat-config/os-refresh-config/configure.d/55-heat-config %{buildroot}%{_libexecdir}/os-refresh-config/configure.d/55-heat-config

# hook to perform configuration with scripts
install -p -D -m 755 heat-config-script/install.d/hook-script.py %{buildroot}%{_libexecdir}/heat-config/hooks/script

# hook to perform configuration with puppet
install -p -D -m 755 heat-config-puppet/install.d/hook-puppet.py %{buildroot}%{_libexecdir}/heat-config/hooks/puppet

# hook to perform configuration with ansible
install -p -D -m 755 heat-config-ansible/install.d/hook-ansible.py %{buildroot}%{_libexecdir}/heat-config/hooks/ansible

# hook to perform configuration with os-apply-config
install -p -D -m 755 heat-config-apply-config/install.d/hook-apply-config.py %{buildroot}%{_libexecdir}/heat-config/hooks/apply-config

# hook to perform configuration with hiera
install -p -D -m 755 heat-config-hiera/install.d/hook-hiera.py %{buildroot}%{_libexecdir}/heat-config/hooks/hiera

# hook to perform configuration with json-file
install -p -D -m 755 heat-config-json-file/install.d/hook-json-file.py %{buildroot}%{_libexecdir}/heat-config/hooks/json-file

# hook to perform configuration with docker commands
install -p -D -m 755 heat-config-docker-cmd/os-refresh-config/configure.d/50-heat-config-docker-cmd %{buildroot}%{_libexecdir}/os-refresh-config/configure.d/50-heat-config-docker-cmd
install -p -D -m 755 heat-config-docker-cmd/install.d/hook-docker-cmd.py %{buildroot}%{_libexecdir}/heat-config/hooks/docker-cmd

%files
%doc README.rst

%package -n python%{pyver}-heat-agent
%{?python_provide:%python_provide python%{pyver}-heat-agent}
Summary: Agent for performing Heat software deployments
Requires: python%{pyver}-requests
Requires: python%{pyver}-heatclient
Requires: python%{pyver}-zaqarclient
Requires: heat-cfntools
Requires: os-collect-config
Requires: os-apply-config
Requires: os-refresh-config
Requires: dib-utils

%description -n python%{pyver}-heat-agent
This package installs and configures os-collect-config to allow Heat software
deployments to perform script based configuration tasks.

%files -n python%{pyver}-heat-agent
%license LICENSE
%{_bindir}/heat-config-notify
%{_bindir}/heat-config-rebuild-deployed
%{_libexecdir}/os-apply-config/templates/etc/os-collect-config.conf
%{_libexecdir}/os-apply-config/templates/var/run/heat-config/heat-config
%{_libexecdir}/os-refresh-config/configure.d/20-os-apply-config
%{_libexecdir}/os-refresh-config/configure.d/55-heat-config
%dir %{_libexecdir}/heat-config
%dir %{_libexecdir}/heat-config/hooks
%{_libexecdir}/heat-config/hooks/script

%package -n python%{pyver}-heat-agent-puppet
%{?python_provide:%python_provide python%{pyver}-heat-agent-puppet}
Summary: Agent for performing Puppet based Heat software deployments
Requires: python%{pyver}-heat-agent
Requires: puppet

%description -n python%{pyver}-heat-agent-puppet
This package installs and configures os-collect-config to allow Heat software
deployments to perform puppet based configuration tasks.

%files -n python%{pyver}-heat-agent-puppet
%{_libexecdir}/heat-config/hooks/puppet

%package -n python%{pyver}-heat-agent-ansible
%{?python_provide:%python_provide python%{pyver}-heat-agent-ansible}
Summary: Agent for performing Ansible based Heat software deployments
Requires: python%{pyver}-heat-agent
%if %{pyver} == 2
Requires: ansible
%else
Requires: python3dist(ansible)
%endif


%description -n python%{pyver}-heat-agent-ansible
This package installs and configures os-collect-config to allow Heat software
deployments to perform ansible based configuration tasks.

%files -n python%{pyver}-heat-agent-ansible
%{_libexecdir}/heat-config/hooks/ansible

%package -n python%{pyver}-heat-agent-apply-config
%{?python_provide:%python_provide python%{pyver}-heat-agent-apply-config}
Summary: Agent for performing os-apply-config based Heat software deployments
Requires: python%{pyver}-heat-agent
Requires: os-apply-config

%description -n python%{pyver}-heat-agent-apply-config
This package installs and configures os-collect-config to allow Heat software
deployments to perform os-apply-config based configuration tasks.

%files -n python%{pyver}-heat-agent-apply-config
%{_libexecdir}/heat-config/hooks/apply-config

%package -n python%{pyver}-heat-agent-hiera
%{?python_provide:%python_provide python%{pyver}-heat-agent-hiera}
Summary: Agent for performing hiera based Heat software deployments
Requires: python%{pyver}-heat-agent

%description -n python%{pyver}-heat-agent-hiera
This package installs and configures os-collect-config to allow Heat software
deployments to perform hiera based configuration tasks.

%files -n python%{pyver}-heat-agent-hiera
%{_libexecdir}/heat-config/hooks/hiera

%package -n python%{pyver}-heat-agent-json-file
%{?python_provide:%python_provide python%{pyver}-heat-agent-json-file}
Summary: Agent for performing json-file based Heat software deployments
Requires: python%{pyver}-heat-agent

%description -n python%{pyver}-heat-agent-json-file
This package installs and configures os-collect-config to allow Heat software
deployments to perform json-file based configuration tasks.

%files -n python%{pyver}-heat-agent-json-file
%{_libexecdir}/heat-config/hooks/json-file

%package -n python%{pyver}-heat-agent-docker-cmd
%{?python_provide:%python_provide python%{pyver}-heat-agent-docker-cmd}
Summary: Agent for performing Docker based Heat software deployments
Requires: python%{pyver}-heat-agent
Requires: python%{pyver}-paunch

%description -n python%{pyver}-heat-agent-docker-cmd
This package installs and configures os-collect-config to allow Heat software
deployments to perform docker based configuration tasks.

%files -n python%{pyver}-heat-agent-docker-cmd
%{_libexecdir}/heat-config/hooks/docker-cmd
%{_libexecdir}/os-refresh-config/configure.d/50-heat-config-docker-cmd

%changelog
* Thu Oct 10 2019 RDO <dev@lists.rdoproject.org> 1.10.0-1
- Update to 1.10.0



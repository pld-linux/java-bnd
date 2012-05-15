#
# Conditional build:
%bcond_without	javadoc		# don't build javadoc

%define		srcname		bnd
%include	/usr/lib/rpm/macros.java
Summary:	BND Tool
Name:		java-%{srcname}
Version:	0.0.363
Release:	1
License:	ASL 2.0
Group:		Development/Tools
URL:		http://www.aQute.biz/Code/Bnd
# NOTE: sources for 0.0.363 are no longer available
# The following links would work for 0.0.370-0.0.401 version range, but
# we need to stay by 0.0.363 to minimize problems during the 1.43.0 introduction
Source0:	http://www.aqute.biz/repo/biz/aQute/bnd/%{version}/%{srcname}-%{version}.jar
# Source0-md5:	1d36d0271381964304c08b00b5fd1b4a
Source2:	aqute-service.tar.gz
# Source2-md5:	11fe2398149f85066f6d0b6dc8af225b
BuildRequires:	ant
BuildRequires:	jdk
BuildRequires:	jpackage-utils
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.553
Obsoletes:	aqute-bnd
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The bnd tool helps you create and diagnose OSGi R4 bundles.

The key functions are:
- Show the manifest and JAR contents of a bundle
- Wrap a JAR so that it becomes a bundle
- Create a Bundle from a specification and a class path
- Verify the validity of the manifest entries

The tool is capable of acting as:
- Command line tool
- File format
- Directives
- Use of macros

%package javadoc
Summary:	Javadoc for %{name}
Group:		Documentation
Requires:	jpackage-utils

%description javadoc
Javadoc for %{name}.

%prep
%setup -qc

mkdir -p target/site/apidocs/
mkdir -p target/classes/
mkdir -p src/main/
mv OSGI-OPT/src src/main/java
tar -xsf %{SOURCE2} -C src/main/java
sed -i "s|import aQute.lib.filter.*;||g" src/main/java/aQute/bnd/make/ComponentDef.java
sed -i "s|import aQute.lib.filter.*;||g" src/main/java/aQute/bnd/make/ServiceComponent.java

# get rid of eclipse plugins which are not usable anyway and complicate
# things
rm -rf src/main/java/aQute/bnd/annotation/Test.java \
       src/main/java/aQute/bnd/{classpath,jareditor,junit,launch,plugin} \
       aQute/bnd/classpath/messages.properties

# remove bundled stuff
for f in $(find aQute/ -type f -name "*.class"); do
    rm -f $f
done

# Convert CR+LF to LF
%undos LICENSE

%build
# source code not US-ASCII
export LC_ALL=en_US
export OPT_JAR_LIST=:
CLASSPATH=$(build-classpath ant)
export CLASSPATH

%javac -d target/classes -target 1.5 -source 1.5 $(find src/main/java -type f -name "*.java")

%if %{with javadoc}
%javadoc -d target/site/apidocs -sourcepath src/main/java aQute.lib.header aQute.lib.osgi aQute.lib.qtokens aQute.lib.filter
%endif

cp -p LICENSE maven-dependencies.txt plugin.xml pom.xml target/classes
for f in $(find aQute/ -type f -not -name "*.class"); do
	cp -p $f target/classes/$f
done
cd target/classes
%jar cmf ../../META-INF/MANIFEST.MF ../%{name}-%{version}.jar *

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d $RPM_BUILD_ROOT%{_javadir}
cp -p target/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}-%{version}.jar
ln -s %{srcname}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}.jar
# fedora uses this name:
#cp -p target/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/aqute-bnd.jar

# javadoc
%if %{with javadoc}
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
cp -a target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{srcname}-%{version} %{_javadocdir}/%{srcname}

%files
%defattr(644,root,root,755)
%doc LICENSE
%{_javadir}/%{srcname}-%{version}.jar
%{_javadir}/%{srcname}.jar

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{srcname}-%{version}
%ghost %{_javadocdir}/%{srcname}
%endif

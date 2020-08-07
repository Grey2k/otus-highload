FROM centos:7

RUN yum -y install epel-release && \
    yum -y update && \
    yum -y clean all

RUN set -x \
    && yum -y install \
        libstdc++ \
        binutils \
        ncurses \
        libgomp \
        lua \
        tar \
        zip \
        unzip \
        libunwind \
    && yum -y install \
        perl \
        gcc-c++ \
        cmake \
        readline-devel \
        lz4-devel \
        binutils-devel \
        ncurses-devel \
        make \
        git \
        libunwind-devel \
        autoconf \
        automake \
        libtool \
        wget \
        curl-devel \
        libicu-devel \
    && yum -y install \
        boost \
        boost-devel

RUN yum localinstall -y https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm

RUN yum install -y \
        mysql-community-client \
        mysql-community-devel


RUN git clone https://github.com/tarantool/mysql-tarantool-replication.git mysql_tarantool-replication

RUN cd mysql_tarantool-replication \
    && git submodule update --init --recursive

RUN cd mysql_tarantool-replication \
    && cmake . \
    && make

##
## Copy replicatord binary to new image to minimize size
##
FROM centos
COPY --from=0 mysql_tarantool-replication/replicatord .
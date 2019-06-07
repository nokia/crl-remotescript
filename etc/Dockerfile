FROM 	fedora:29
RUN 	dnf -y install git \
	    patch \
	    make \
	    gcc \
	    findutils \
	    bzip2 \
	    bzip2-devel \
	    readline-devel \
	    openssh-server \
        procps \
	    sqlite \
	    sqlite-devel \
	    openssl-devel \
	    tk-devel \
	    libffi-devel \
	    python3 \
	    tox \
	    python-pip
RUN     dnf -y install coreutils
RUN	    dnf -y install passwd
RUN     dnf -y install sudo
RUN	    useradd host1 -m && useradd host2 -m \
	    && mkdir /home/host1/.ssh \
	    && mkdir /home/host2/.ssh \
        && ssh-keygen -t ed25519 -f /root/.ssh/rsa_keys -P "" \
        && cp /root/.ssh/rsa_keys.pub /home/host1/.ssh/authorized_keys \
        && cp /root/.ssh/rsa_keys.pub /home/host2/.ssh/authorized_keys
RUN	    passwd host1 --stdin <<< "host1" \
	    && passwd host2 --stdin <<< "host2" \
        && echo 'host1  ALL=NOPASSWD: ALL' >> /etc/sudoers.d/host1 \
        && echo 'host2  ALL=NOPASSWD: ALL' >> /etc/sudoers.d/host2
WORKDIR /work
CMD 	etc/docker_cmd

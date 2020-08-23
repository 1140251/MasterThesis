FROM trailofbits/manticore

ENV LC_ALL C.UTF-8  

RUN apt-get -y update && DEBIAN_FRONTEND=noninteractive apt-get -y install python3 python3-pip git wget curl

RUN pip3 --no-cache-dir install --upgrade setuptools pip

COPY array-length-manipulation.sol .

RUN git clone https://github.com/crytic/solc-select.git
RUN cd solc-select/scripts && sh ./install.sh
ENV PATH="/root/.solc-select:${PATH}"

COPY array-length-manipulation.sol .
COPY exception-disorder.sol .
CMD ["/bin/bash"]

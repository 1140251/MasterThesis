FROM ubuntu:18.04

ARG solc=0.4.26
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    git \
    make \
    wget 

RUN wget -q https://packages.microsoft.com/config/ubuntu/19.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \ 
    && dpkg -i packages-microsoft-prod.deb \ 
    && apt-get update && apt-get install -y apt-transport-https \
    && apt-get update && apt-get install -y dotnet-sdk-2.2

RUN git clone https://github.com/microsoft/verisol.git

RUN dotnet build verisol/Sources/VeriSol.sln



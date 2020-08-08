FROM maven:ibmjava

RUN apt-get update && apt-get install -y software-properties-common locales

RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

RUN apt-get update && apt-get -y install git

RUN \
    git clone https://github.com/smartdec/smartcheck.git

WORKDIR /smartcheck
RUN rm -r src/test
RUN mvn clean package


ENTRYPOINT ["java" ,"-jar" ,"target/smartcheck-2.1-SNAPSHOT-jar-with-dependencies.jar"]



#CMD ["/bin/bash"]
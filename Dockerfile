FROM python:3.7
# USER root

# RUN apt-get update
# RUN apt-get -y install locales && \
#   localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
# ENV LANG ja_JP.UTF-8
# ENV LANGUAGE ja_JP:ja
# ENV LC_ALL ja_JP.UTF-8
# ENV TZ JST-9
# ENV TERM xterm

# RUN apt-get install -y vim less
# RUN pip install --upgrade pip
# RUN pip install --upgrade setuptools

# RUN python -m pip install jupyterlab

# RUN 

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

# update apt-get
RUN apt-get update -y && apt-get upgrade -y

# Install Nodejs 18
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# install aws-cli
RUN pip install awscli


# install boto3
# RUN pip install boto3

COPY . .

# install python libraries
RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# install serverless framework
RUN npm install -g serverless

# install npm modules
# WORKDIR /scripts
COPY ./app/package.json  /app/
RUN npm install

# set aws key 
RUN sls config credentials --provider aws --key $AWS_ACCESS_KEY_ID --secret $AWS_SECRET_ACCESS_KEY
# boto3のためのAWSリージョンの設定
ENV AWS_DEFAULT_REGION=ap-northeast-1

# change work directory
# RUN mkdir -p /app
# WORKDIR /app/app


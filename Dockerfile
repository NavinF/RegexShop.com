FROM ubuntu
RUN apt-get -y update && apt-get -y install python3-pip libre2-dev
RUN pip3 install django ebaysdk requests simpleeval jinja2 fb-re2 pycapnp
COPY . /RegexShop.com
WORKDIR /RegexShop.com
RUN python3 manage.py migrate

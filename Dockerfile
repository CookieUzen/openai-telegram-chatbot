# python docker

FROM python

# Go to folder
WORKDIR /opt
COPY . .

# Install python packages
RUN pip install -r requirements.txt

# Run the application
CMD ["python", "bot.py"]

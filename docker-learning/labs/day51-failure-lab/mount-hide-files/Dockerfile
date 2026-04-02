FROM alpine:3.20
WORKDIR /app
RUN echo "This file exists inside the image" > /app/message.txt
CMD ["sh", "-c", "echo 'Container started'; ls -l /app; cat /app/message.txt; sleep 300"]

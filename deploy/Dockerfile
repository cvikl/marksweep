FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY marksweep ./marksweep
COPY static ./static
COPY fixtures ./fixtures
RUN pip install --no-cache-dir .
ENV MARKSWEEP_DATA=/data MARKSWEEP_ROOT=/app PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "marksweep serve --port ${PORT}"]

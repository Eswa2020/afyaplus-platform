FROM python:3.14-slim
WORKDIR /app
COPY requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt
COPY prompt_app.py .
COPY prompts/ prompts/
ENV PROMPT_VERSION=1.2.0
EXPOSE 8000
CMD ["uvicorn", "prompt_app:app", "--host", "0.0.0.0", "--port", "8000"]
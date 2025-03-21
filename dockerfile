# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /ElectricalVehicleCharges

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose the Django application port
EXPOSE 8000

# Run migrations and start the Django server
# CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# Run migrations and start Daphne server
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "ElectricalVehicleCharges.asgi:application"]

CMD sh -c "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 ElectricalVehicleCharges.asgi:application & uvicorn api.views:app --host 0.0.0.0 --port 9000 --reload"


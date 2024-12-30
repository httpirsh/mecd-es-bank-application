# Configuration
EB_ENV = bank-website-env

# Default target with instructions
default:
	@echo "Available targets:"
	@echo "  frontend       - Build the Vite frontend (output in bank_django/frontend/dist)."
	@echo "  django_start   - Build the frontend and start the Django development server."
	@echo "  clean          - Remove build artifacts and temporary files (e.g., __pycache__, frontend dist folder)."

# Build Vite frontend
bank_django/frontend/dist/.build: $(shell find bank_django/frontend -type f \( -iname \*.jsx -o -iname \*.html \))
	cd bank_django/frontend && npx vite build && touch dist/.build

frontend: bank_django/frontend/dist/.build

django_static:
	cd bank_django && python manage.py collectstatic --noinput

# Start Django development server
django_start: frontend
	cd bank_django && python manage.py runserver

deploy: frontend django_static
	cd bank_django && eb use $(EB_ENV) && eb deploy

# Clean temporary and build files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null;
	rm -rf bank_django/frontend/dist

# Declare phony targets
.PHONY: retrieve clean frontend django_start django_static
# Use a simpler base image that's known to work well with Cypress
FROM cypress/included:12.3.0

WORKDIR /app

# Copy cypress files
COPY ./frontend/cypress.config.js .
COPY ./frontend/cypress ./cypress

# Create a simple wait script
RUN echo '#!/bin/bash\n\
echo "Waiting 20 seconds for frontend to be ready..."\n\
sleep 20\n\
echo "Starting Cypress tests..."\n\
cypress run "$@"' > /app/run-tests.sh

RUN chmod +x /app/run-tests.sh

# Set entry point to the script
ENTRYPOINT ["/app/run-tests.sh"]

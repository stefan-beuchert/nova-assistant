# Placeholder Dockerfile — adapt per project's language/framework.
#
# Expected shape per STANDARDS.md:
#   - Multi-stage build (build stage -> slim runtime stage)
#   - Runs as a non-root user
#   - Reads config from environment variables (nothing hardcoded)
#   - Logs to stdout/stderr (no in-container log files)
#   - Exposes GET /health

# --- Build stage -------------------------------------------------------
# FROM <language-base-image> AS build
# WORKDIR /app
# COPY . .
# RUN <install dependencies / build>

# --- Runtime stage -------------------------------------------------------
# FROM <language-runtime-base-image>
# WORKDIR /app
# COPY --from=build /app /app
#
# RUN useradd --system --create-home appuser
# USER appuser
#
# ENV PORT=8080
# EXPOSE $PORT
#
# CMD ["<start command>"]

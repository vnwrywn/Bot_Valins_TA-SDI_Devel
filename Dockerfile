FROM python:3.11.4-slim AS builder-image

# Avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

# Create directory to mount site files
RUN mkdir /files

# Create and activate virtual environment
# Using final folder name to avoid path issues with packages
RUN python3.11 -m venv /opt/venv
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/static-debian12:nonroot AS runner-image

# Determine chipset architecture for copying python
ARG CHIPSET_ARCH=x86_64-linux-gnu

# Copy python packages dependencies
# Required by lots of packages - e.g. six, numpy, wsgi
COPY --from=builder-image /lib/${CHIPSET_ARCH}/libz.so.1 /lib/${CHIPSET_ARCH}/
# Required by geopy
COPY --from=builder-image /usr/lib/${CHIPSET_ARCH}/libssl.so.3 /usr/lib/${CHIPSET_ARCH}/
COPY --from=builder-image /usr/lib/${CHIPSET_ARCH}/libcrypto.so.3 /usr/lib/${CHIPSET_ARCH}/
# Required by jwt
COPY --from=builder-image /usr/lib/${CHIPSET_ARCH}/libgcc_s.so.1 /usr/lib/${CHIPSET_ARCH}/
COPY --from=builder-image /usr/lib/${CHIPSET_ARCH}/libdl.so.2 /usr/lib/${CHIPSET_ARCH}/
COPY --from=builder-image /usr/lib/${CHIPSET_ARCH}/libpthread.so.0 /usr/lib/${CHIPSET_ARCH}/
# Required by openpyxl
COPY --from=builder-image /usr/lib/${CHIPSET_ARCH}/libexpat* /usr/lib/${CHIPSET_ARCH}/
COPY --from=builder-image /usr/local/include/python3.11/pyexpat.h /usr/local/include/python3.11/pyexpat.h
# Required by google-cloud/grpcio
# COPY --from=builder-image /usr/lib/${CHIPSET_ARCH}/libffi* /usr/lib/${CHIPSET_ARCH}/
# COPY --from=builder-image /lib/${CHIPSET_ARCH}/libexpat* /lib/${CHIPSET_ARCH}/

# Copy python and its dependencies from builder
COPY --from=builder-image /usr/local/lib/ /usr/local/lib/
COPY --from=builder-image /usr/local/bin/python3.11 /usr/local/bin/python3.11
COPY --from=builder-image /etc/ld.so.cache /etc/ld.so.cache
COPY --from=builder-image /lib64/ld-linux-x86-64.so.2 /lib64/
COPY --from=builder-image /lib/${CHIPSET_ARCH}/libc.so.6 /lib/${CHIPSET_ARCH}/
COPY --from=builder-image /lib/${CHIPSET_ARCH}/libm.so.6 /lib/${CHIPSET_ARCH}/

# Copy app
COPY --chmod=755 /app /app
# Copy files directory for mounting
COPY --from=builder-image --chmod=644 /files /files
# Activate virtual environment
COPY --from=builder-image /opt/venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

CMD ["/usr/local/bin/python3.11", "/app/script_bot.py"]


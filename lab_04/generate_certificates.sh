#!/bin/bash

openssl req -x509 -newkey rsa:4096 -keyout ca_key.pem -out ca_cert.pem -days 365 -nodes -subj "/CN=TestCA"

openssl req -newkey rsa:4096 -keyout server_key.pem -out server.csr -nodes -subj "/CN=localhost"

openssl x509 -req -in server.csr -CA ca_cert.pem -CAkey ca_key.pem -CAcreateserial -out server_cert.pem -days 365

openssl req -newkey rsa:4096 -keyout client_key.pem -out client.csr -nodes -subj "/CN=client"

openssl x509 -req -in client.csr -CA ca_cert.pem -CAkey ca_key.pem -CAcreateserial -out client_cert.pem -days 365
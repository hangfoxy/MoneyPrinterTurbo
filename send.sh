#!/bin/bash

# Check if a video subject was provided
if [ -z "$1" ]; then
  echo "Usage: $0 "video_subject""
  exit 1
fi

# Set the base URL
baseUrl="http://localhost:8080"

# Send the POST request using curl
curl -X POST "$baseUrl/api/v1/allinone" \
  -H "Content-Type: application/json" \
  -d '{
    "video_subject": "'"$1"'",
    "video_language": "en",
    "paragraph_number": 2
  }'

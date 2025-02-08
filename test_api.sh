#!/bin/bash

# Base URL
API_URL="http://localhost:8080/api"

echo "Testing API endpoints..."

# Create a user
echo -e "\n1. Creating user..."
USER_RESPONSE=$(curl -s -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "display_name": "Test User"}')
USER_ID=$(echo $USER_RESPONSE | jq -r '.user_id')
echo "Created user with ID: $USER_ID"

# List users
echo -e "\n2. Listing users..."
curl -s "$API_URL/users" | jq '.'

# Create a room
echo -e "\n3. Creating room..."
ROOM_RESPONSE=$(curl -s -X POST "$API_URL/rooms")
ROOM_ID=$(echo $ROOM_RESPONSE | jq -r '.room_id')
echo "Created room with ID: $ROOM_ID"

# List rooms
echo -e "\n4. Listing rooms..."
curl -s "$API_URL/rooms" | jq '.'

# Join room
echo -e "\n5. Joining room..."
curl -s -X POST "$API_URL/rooms/$ROOM_ID/join?user_id=$USER_ID" | jq '.'

# Get room info
echo -e "\n6. Getting room info..."
curl -s "$API_URL/rooms/$ROOM_ID" | jq '.'

# Leave room
echo -e "\n7. Leaving room..."
curl -s -X POST "$API_URL/rooms/$ROOM_ID/leave?user_id=$USER_ID" | jq '.' 
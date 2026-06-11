nohup uv run stress-custom.py http://localhost:18000/api/nurse/infusion/start infusion_start.lua a1.png &
nohup uv run stress-custom.py http://localhost:18000/api/nurse/infusion/complete infusion_complete.lua b1.png &
nohup uv run stress-custom.py http://localhost:18000/api/doctor/custom_event_test custom_test_event.lua c1.png &
sleep 7
docker compose -f ../no_kafka/docker-compose.yml restart no_kafka &
sleep 13

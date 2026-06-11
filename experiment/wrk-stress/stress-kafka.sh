nohup uv run stress-custom.py http://localhost:8082/api/nurse/infusion/start infusion_start.lua a.png > a.out &
nohup uv run stress-custom.py http://localhost:8082/api/nurse/infusion/complete infusion_complete.lua b.png > b.out &
nohup uv run stress-custom.py http://localhost:8082/api/doctor/custom_event_test custom_test_event.lua c.png > c.out &
sleep 10
docker compose -f ../../deploy/docker-compose.yml restart doctor &
sleep 20

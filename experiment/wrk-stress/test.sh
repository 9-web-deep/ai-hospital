nohup wrk -t12 -c100 -d30s -s infusion_start.lua http://localhost:8082/api/nurse/infusion/start > a.out &
nohup wrk -t12 -c100 -d30s -s infusion_complete.lua http://localhost:8082/api/nurse/infusion/complete > b.out &
nohup wrk -t12 -c100 -d30s -s custom_test_event.lua http://localhost:8082/api/doctor/custom_event_test > c.out &
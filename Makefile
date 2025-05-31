.PHONY: reset test

reset:
	docker-compose down -v
	docker-compose up --build -d
	@echo "Waiting 35s for Keycloak to finish importing realm…"
	sleep 35

test:
	@RESPONSE=$$(curl -s \
		-d grant_type=password \
		-d client_id=intranet \
		-d username=alex \
		-d password=P@55word \
		http://localhost:8080/realms/CentralIAM/protocol/openid-connect/token); \
	TOKEN=$$(echo $$RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))'); \
	echo "Token: $$TOKEN"; \
	echo "→ Authorized call:"; \
	curl -s -H "Authorization: Bearer $$TOKEN" http://localhost:5000/protected; echo; \
	echo "→ Unauthorized call:"; \
	curl -s http://localhost:5000/protected; echo

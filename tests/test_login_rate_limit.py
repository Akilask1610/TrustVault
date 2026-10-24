
from app import app, limiter


def test_login_is_rate_limited_after_ten_attempts():
    limiter.reset()
    limiter.enabled = True

    try:
        with app.test_client() as client:
            responses = [
                client.post(
                    "/login",
                    data={
                        "username": f"missing-user-{i}",
                        "password": "wrong",
                    },
                )
                for i in range(10)
            ]

            assert all(response.status_code == 200 for response in responses)

            response = client.post(
                "/login",
                data={
                    "username": "missing-user-final",
                    "password": "wrong",
                },
            )

            assert response.status_code == 429
    finally:
        limiter.enabled = False
        limiter.reset()

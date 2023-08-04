from app.auth.oauth_client import TwitterClient, ClientRegistry


async def test_oauth1(http, response):
    twitter = TwitterClient(
        consumer_key="oUXo1M7q1rlsPXm4ER3dWnMt8",
        consumer_secret="YWzEvXZJO9PI6f9w2FtwUJenMvy9SPLrHOvnNkVkc5LdYjKKup",
    )

    assert twitter
    assert "twitter" in ClientRegistry.clients

    http.return_value = response(
        json={"oauth_token": "token", "oauth_token_secret": "secret"}
    )

    token, data = await twitter.get_request_token(
        oauth_callback="http://fuf.me:5000/twitter"
    )

    assert token
    assert data
    assert twitter.oauth_token == token
    assert twitter.oauth_token_secret == data.get("oauth_token_secret")

    url = twitter.get_authorize_url()
    assert url == f"https://api.twitter.com/oauth/authorize?oauth_token={token}"

    await twitter.get_access_token("wrong", token)

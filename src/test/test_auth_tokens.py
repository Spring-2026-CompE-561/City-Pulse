from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


#####
# Authentication Token Logic - Unit Tests
#####
def test_access_token_round_trip():
    #####
    # Scenario: We create an access token and then decode it
    # Expected: The data coming out should be exactly what we put in
    #####

    user_id = 7

    # 1. Fire off a brand new access token for our user
    token = create_access_token(user_id)

    # 2. Crack it open to see if the identitiy is still there
    payload = decode_access_token(token)

    # Validation: The payload must exist and the 'sub' must be our user ID string
    assert payload is not None
    assert payload["sub"] == "7"


def test_refresh_token_round_trip():
    ######
    ### Test case: Refresh Token Reliabiltiy
    ### Scenario: Similar to the access token, but for the long lived refresh token
    ### Expectation: Even though these tokens have a different purpose, The core user identity must remain consisten and readable
    #####

    user_id = 11

    # 1. Generate a referesh token for the session
    token = create_refresh_token(user_id)

    # 2. Use the dedicated refresh decoder to verify its contents
    payload = decode_refresh_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)


def test_access_decode_rejects_refresh_token():
    #####
    ## Scenario: A malicious or confused user tries to use a refresh token as an access token.
    ## Expectation: The access token decoder should smell something fishy and return None.
    #####

    # 1. Create a legitimate refresh token
    refresh = create_refresh_token(3)
    # 2. Attempt to "sneak"  it into a function that expects an access token
    assert decode_access_token(refresh) is None

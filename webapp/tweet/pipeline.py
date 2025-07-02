def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        # Extract data from Google response
        first_name = response.get('given_name', '')
        last_name = response.get('family_name', '')

        user.first_name = first_name
        user.last_name = last_name
        user.save()

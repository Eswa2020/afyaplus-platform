KIND = {
    'JWT_SECRET': 'secret',
    'OPENAI_API_KEY': 'secret',
    'prompts/triage_system_v1.2.0.txt': 'config',  # not a secret, still versioned
    'triage_messages.json': 'data',
    'clinics.json': 'data',
}
# Secrets never go in git. Data may go in fixtures if stripped of real identifiers.


if __name__ == '__main__':
    assert KIND['JWT_SECRET'] == 'secret'
    assert KIND['triage_messages.json'] == 'data'
    # A prompt is versioned config, not a credential. This is the line that
    # decides whether it goes in a vault or in a diff.
    assert KIND['prompts/triage_system_v1.2.0.txt'] == 'config'
    assert set(KIND.values()) == {'secret', 'config', 'data'}
    print('classify_assets OK', len(KIND), 'assets,', len(set(KIND.values())), 'kinds')
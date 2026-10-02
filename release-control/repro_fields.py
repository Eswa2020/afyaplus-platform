import hashlib


def prompt_sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def usage_log(trace_id: str, model: str, prompt_version: str, text: str, temp: float):
    print({
        'trace_id': trace_id,
        'model': model,
        'prompt_version': prompt_version,
        'prompt_sha256': prompt_sha(text),
        'temperature': temp,
        # 'seed': seed,  # when the vendor API supports it
    })


if __name__ == '__main__':
    usage_log('3f9a21c4', 'gpt-4o-mini', '1.2.0',
              'You are AfyaPlus triage assistant.\n', 0.2)
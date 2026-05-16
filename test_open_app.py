import sys
sys.path.insert(0, '.')
from glassescat_agent import NikoApps

test_cases = ['chrome', 'chrome aç', 'chrome aç', 'ac chrome', 'vscode', 'discord']

for app in test_cases:
    print(f'Test: "{app}"')
    result = NikoApps.open_app(app)
    print(f'  -> {result["message"]}')
    print()

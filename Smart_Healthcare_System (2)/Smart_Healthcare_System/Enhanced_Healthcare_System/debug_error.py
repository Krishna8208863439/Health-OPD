import requests, re
s = requests.Session()
s.get('http://127.0.0.1:5001/login')
s.post('http://127.0.0.1:5001/login', data={'email':'testpatient99@test.com','password':'test123'})
r = s.get('http://127.0.0.1:5001/')
txt = re.sub(r'<[^>]+>','',r.text).replace('&quot;','"').replace('&#34;','"').replace('&#39;',"'")
lines = [l.strip() for l in txt.splitlines() if l.strip()]
for i,l in enumerate(lines):
    if 'ValueError' in l or '_scheme' in l or 'url_for' in l.lower():
        print('\n'.join(lines[max(0,i-5):i+10]))
        break
else:
    # print flask error template lines
    for i,l in enumerate(lines):
        if 'Error' in l or 'error' in l:
            print('\n'.join(lines[max(0,i-2):i+8]))
            break
    print("--- first 50 lines ---")
    print('\n'.join(lines[:50]))

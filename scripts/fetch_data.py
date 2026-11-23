#!/usr/bin/env python3
import sys, os, json, urllib.request, urllib.error
sys.path.insert(0, '/opt/muse/skills/custom-connector-setup/bin')
sys.path.insert(0, '/opt/muse/skills/custom-connector-setup/templates/skill/bin')

API = 'https://api.github.com'
OUT = os.path.join(os.path.dirname(__file__), '..', 'data')

def req(method, url, body=None):
    # Imported lazily: only the authenticated local path needs the
    # connector credentials; the public path (GitHub Action) does not.
    from dynamic_credentials import add_surrogate_to_request, read_json_response
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header('Accept', 'application/vnd.github+json')
    r.add_header('X-GitHub-Api-Version', '2022-11-28')
    if data: r.add_header('Content-Type', 'application/json')
    add_surrogate_to_request(r, 'custom.github', allowed_hosts=['api.github.com'])
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, read_json_response(resp)
    except urllib.error.HTTPError as e:
        try: payload = read_json_response(e)
        except Exception: payload = {'message': str(e)}
        return e.code, payload

def main():
    s, me = req('GET', API + '/user')
    assert s == 200, (s, me)
    login = me['login']
    print('login', login)

    q = '''query($login:String!){ user(login:$login){
      contributionsCollection { contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount color weekday } }
      } }
      repositories(first:100, ownerAffiliations: OWNER, orderBy:{field:UPDATED_AT, direction:DESC}) {
        nodes { name description url stargazerCount forkCount isFork parent { nameWithOwner }
                primaryLanguage { name } updatedAt pushedAt }
      }
      followers { totalCount }
    }}'''
    s, p = req('POST', API + '/graphql', {'query': q, 'variables': {'login': login}})
    assert s == 200, (s, json.dumps(p)[:400])
    u = p['data']['user']
    cal = u['contributionsCollection']['contributionCalendar']
    days = []
    for w in cal['weeks']:
        for d in w['contributionDays']:
            days.append({'date': d['date'], 'count': d['contributionCount'], 'weekday': d['weekday']})
    contrib = {'total': cal['totalContributions'], 'days': days,
               'weeks': [[{'date': d['date'], 'count': d['contributionCount']} for d in w['contributionDays']] for w in cal['weeks']]}
    with open(os.path.join(OUT, 'contributions.json'), 'w') as f:
        json.dump(contrib, f, indent=1)
    repos = u['repositories']['nodes']
    with open(os.path.join(OUT, 'repos.json'), 'w') as f:
        json.dump(repos, f, indent=1)
    user = {'login': login, 'name': me.get('name'), 'followers': u['followers']['totalCount'],
            'public_repos': me.get('public_repos')}
    with open(os.path.join(OUT, 'user.json'), 'w') as f:
        json.dump(user, f, indent=1)
    print('total contributions (1y):', cal['totalContributions'])
    print('days:', len(days), 'repos:', len(repos), 'user:', user)
    for r in repos[:12]:
        print(' repo:', r['name'], '| stars', r['stargazerCount'], '| lang', (r['primaryLanguage'] or {}).get('name'), '| fork', r['isFork'], '| pushed', r['pushedAt'])

def fetch_public():
    """Unauthenticated path used by the daily GitHub Action: scrape the
    public contributions calendar and read public user/repo data."""
    import re
    from datetime import datetime, timedelta

    def get(url):
        r = urllib.request.Request(url, headers={'User-Agent': 'readme-cards'})
        with urllib.request.urlopen(r) as resp:
            return resp.read().decode('utf-8', 'replace')

    html = get('https://github.com/users/zemen14/contributions')
    tips = {}
    for m in re.finditer(r'for="(contribution-day-component-[\d-]+)"[^>]*>([^<]+)</tool-tip>', html):
        text = m.group(2).strip()
        cm = re.match(r'(\d+) contribution', text)
        tips[m.group(1)] = int(cm.group(1)) if cm else 0
    days = []
    for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})" id="(contribution-day-component-[\d-]+)"', html):
        days.append({'date': m.group(1), 'count': tips.get(m.group(2), 0)})
    days.sort(key=lambda d: d['date'])
    for d in days:
        dt = datetime.strptime(d['date'], '%Y-%m-%d').date()
        d['weekday'] = (dt.weekday() + 1) % 7  # Sunday = 0
    weeks = []
    cur = []
    for d in days:
        if d['weekday'] == 0 and cur:
            weeks.append(cur)
            cur = []
        cur.append({'date': d['date'], 'count': d['count']})
    if cur:
        weeks.append(cur)
    contrib = {'total': sum(d['count'] for d in days), 'days': days, 'weeks': weeks}
    with open(os.path.join(OUT, 'contributions.json'), 'w') as f:
        json.dump(contrib, f, indent=1)

    user_pub = json.loads(get(API + '/users/zemen14'))
    repos_pub = json.loads(get(API + '/users/zemen14/repos?per_page=100&sort=updated'))
    repos = [{'name': r['name'], 'description': r.get('description'), 'url': r['html_url'],
              'stargazerCount': r['stargazers_count'], 'forkCount': r['forks_count'],
              'isFork': r['fork'], 'parent': None,
              'primaryLanguage': {'name': r['language']} if r.get('language') else None,
              'updatedAt': r['updated_at'], 'pushedAt': r['pushed_at']} for r in repos_pub]
    with open(os.path.join(OUT, 'repos.json'), 'w') as f:
        json.dump(repos, f, indent=1)
    user = {'login': 'zemen14', 'name': user_pub.get('name'),
            'followers': user_pub.get('followers'), 'public_repos': user_pub.get('public_repos')}
    with open(os.path.join(OUT, 'user.json'), 'w') as f:
        json.dump(user, f, indent=1)
    print('public fetch: total', contrib['total'], 'days', len(days), 'repos', len(repos), 'user', user)


if __name__ == '__main__':
    if os.environ.get('PUBLIC_FETCH') == '1':
        fetch_public()
    else:
        main()

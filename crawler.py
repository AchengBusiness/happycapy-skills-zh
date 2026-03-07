import urllib.request, json, time, sqlite3, re, os, sys

DB_PATH = '/tmp/skills-db/skills.db'
OUTPUT_JSONL = '/tmp/skills-db/raw.jsonl'

# ============================================================
# 600+ search terms for maximum coverage
# ============================================================
TERMS = [
    # Single chars
    *list('abcdefghijklmnopqrstuvwxyz'),
    # Programming languages
    'python','javascript','typescript','java','golang','go','rust','ruby','php',
    'swift','kotlin','scala','cpp','csharp','elixir','haskell','lua','perl',
    'dart','r','matlab','julia','fortran','cobol','assembly','bash','shell',
    'powershell','vba','groovy','clojure','lisp','scheme','erlang','fsharp',
    # Web frameworks
    'react','vue','angular','svelte','nextjs','nuxt','gatsby','remix','astro',
    'express','fastapi','django','flask','rails','laravel','spring','nestjs',
    'hapi','koa','sveltekit','solid','preact','qwik','lit','stencil','ember',
    # Mobile
    'flutter','reactnative','ionic','expo','android','ios','swift','xcode',
    'kotlin-android','jetpack','swiftui','uikit','capacitor','cordova',
    # Databases
    'postgresql','postgres','mysql','mongodb','redis','elasticsearch','sqlite',
    'dynamodb','firestore','supabase','planetscale','neon','cockroachdb',
    'cassandra','couchdb','neo4j','influxdb','timescaledb','clickhouse',
    'bigquery','snowflake','databricks','dbt','prisma','drizzle','typeorm',
    'sequelize','mongoose','sqlalchemy','gorm',
    # Cloud & DevOps
    'aws','azure','gcp','cloudflare','vercel','netlify','heroku','railway',
    'render','fly','digitalocean','linode','vultr','hetzner','ovh',
    'docker','kubernetes','k8s','helm','terraform','ansible','pulumi',
    'vagrant','packer','consul','vault','nomad','linkerd','istio',
    'nginx','apache','caddy','traefik','haproxy','envoy',
    'jenkins','github-actions','gitlab-ci','circleci','travis',
    'argocd','flux','spinnaker','tekton','drone',
    # Monitoring
    'prometheus','grafana','datadog','newrelic','sentry','elastic',
    'kibana','logstash','fluentd','jaeger','zipkin','opentelemetry',
    'pagerduty','opsgenie','victorops','statuspage','uptimerobot',
    # AI / ML
    'openai','anthropic','claude','gpt','llm','langchain','llamaindex',
    'huggingface','pytorch','tensorflow','keras','sklearn','xgboost',
    'lightgbm','catboost','rag','embedding','vector','pinecone','weaviate',
    'chroma','qdrant','milvus','faiss','ollama','replicate','stability',
    'midjourney','dalle','gemini','mistral','llama','cohere','vertex',
    'bedrock','sagemaker','mlflow','wandb','dvc','feast','ray',
    'langsmith','langgraph','crewai','autogen','agentops','composio',
    'tavily','perplexity','brave-search','serper','exa',
    # Frontend tooling
    'webpack','vite','rollup','esbuild','parcel','snowpack','turbopack',
    'babel','swc','postcss','tailwind','bootstrap','mui','shadcn',
    'chakra','antdesign','mantine','radix','headless','framer',
    'storybook','chromatic','playwright','cypress','jest','vitest',
    'testing-library','msw','nock','supertest',
    # Package managers
    'npm','yarn','pnpm','bun','pip','poetry','conda','cargo','gem',
    # Backend tools
    'grpc','graphql','rest','openapi','swagger','trpc','mqtt',
    'websocket','sse','webhook','kafka','rabbitmq','redis-pub',
    'celery','bullmq','inngest','temporal','prefect','airflow',
    # Auth
    'oauth','jwt','auth0','clerk','supabase-auth','nextauth','lucia',
    'passport','keycloak','okta','cognito','firebase-auth','magic',
    # Storage
    'aws-s3','cloudflare-r2','minio','backblaze','cloudinary','imgix',
    'uploadthing','transloadit','bunny','fastly','supabase-storage',
    # Communication
    'slack','discord','telegram','whatsapp','twilio','sendgrid',
    'resend','mailgun','postmark','ses','mailchimp','klaviyo',
    'pusher','ably','socket','firebase-realtime','convex','supabase-realtime',
    # Productivity
    'notion','airtable','monday','asana','jira','linear','clickup',
    'trello','basecamp','todoist','things','omnifocus','obsidian',
    'logseq','roam','craft','bear','apple-notes','evernote','onenote',
    'google-docs','microsoft-365','confluence','quip',
    # CMS
    'contentful','sanity','strapi','directus','payload','keystatic',
    'wordpress','ghost','webflow','framer-sites','builder',
    # Analytics
    'google-analytics','plausible','posthog','mixpanel','amplitude',
    'segment','hotjar','clarity','heap','fullstory','logrocket',
    # Payment
    'stripe','paypal','square','braintree','adyen','mollie','lemonsqueezy',
    # Maps
    'google-maps','mapbox','leaflet','here','openstreetmap',
    # Code quality
    'eslint','prettier','stylelint','sonarqube','codeclimate','deepsource',
    'snyk','dependabot','renovate','semgrep','codeql',
    # Git
    'git','github','gitlab','bitbucket','gitea','forgejo','sourcehut',
    # OS
    'linux','ubuntu','debian','centos','fedora','alpine','arch','nixos',
    'windows','macos','freebsd','raspberry',
    # Media
    'ffmpeg','imagemagick','sharp','jimp','canvas','webrtc','hls','dash',
    'youtube','vimeo','tiktok','instagram','twitter','x','bilibili',
    'xiaohongshu','wechat','weibo','douyin','kuaishou',
    # Finance
    'stripe-billing','quickbooks','xero','freshbooks','wave','plaid',
    'yodlee','open-banking','crypto','web3','ethereum','solana','polygon',
    # Testing
    'unit-test','integration-test','e2e','load-test','stress-test',
    'fuzzing','mutation-test','snapshot','accessibility','lighthouse',
    # Security
    'security','pentest','owasp','ssl','tls','csrf','xss','sqli',
    'cryptography','vault','secrets','zero-trust','soc2','gdpr',
    # Data
    'pandas','numpy','scipy','matplotlib','seaborn','plotly','dash',
    'streamlit','gradio','jupyter','polars','pyspark','dask','arrow',
    'parquet','avro','protobuf','flatbuffers','msgpack',
    # Specific tools
    'make','cmake','gradle','maven','ant','bazel','buck','nix',
    'homebrew','apt','yum','chocolatey','scoop','winget',
    'tmux','zsh','fish','oh-my-zsh','starship','wezterm','iterm',
    'vim','neovim','emacs','vscode','cursor','windsurf','zed',
    'postman','insomnia','httpie','curl','wget','jq','yq',
    'ffuf','nuclei','burp','nmap','wireshark','metasploit',
    # Business
    'crm','erp','hr','payroll','accounting','invoicing','project-management',
    'customer-support','live-chat','chatbot','helpdesk','ticketing',
    'email-marketing','seo','social-media','content','blog','newsletter',
    'landing-page','ab-test','conversion','funnel','lead','sales',
    # Specific skill types
    'skill','agent','workflow','automation','integration','webhook',
    'scraper','crawler','parser','transformer','validator','generator',
    'monitor','alerting','dashboard','report','analytics','export',
    'importer','migrator','converter','deployer','backup','restore',
    # Short technical terms
    'api','cli','sdk','ui','ux','pdf','csv','json','xml','yaml',
    'sql','orm','crud','auth','cdn','dns','ssl','tcp','udp','ssh',
    'ftp','smtp','imap','ldap','saml','oidc','mfa','totp',
    # Extra specific
    'mcp','pwa','spa','ssr','ssg','isr','edge','wasm','webassembly',
    'serviceworker','indexeddb','localstorage','cookie','cache',
    'compress','encrypt','hash','sign','verify','token','session',
    'queue','cron','scheduler','worker','daemon','process','thread',
    # More action verbs
    'generate','analyze','extract','transform','convert','optimize',
    'validate','format','lint','test','debug','deploy','monitor',
    'search','filter','sort','paginate','cache','sync','backup',
    'translate','summarize','classify','detect','recognize','predict',
    # Domain specific
    'ecommerce','marketplace','booking','reservation','inventory',
    'logistics','shipping','tracking','warehouse','supply-chain',
    'healthcare','medical','ehr','telemedicine','fitness','nutrition',
    'education','lms','quiz','course','certification','assessment',
    'real-estate','property','mortgage','insurance','banking','fintech',
    'legal','contract','compliance','audit','document','signature',
    'music','audio','podcast','radio','streaming','playlist','lyrics',
    'gaming','game','unity','unreal','godot','phaser','pixi',
    '3d','threejs','webgl','babylon','blender','ar','vr','xr',
]

# Remove duplicates while preserving order
seen_t = set()
TERMS = [t for t in TERMS if not (t in seen_t or seen_t.add(t))]
print(f'Total search terms: {len(TERMS)}', flush=True)

# ============================================================
# Setup SQLite with FTS5
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            author TEXT,
            zh_name TEXT,
            description TEXT,
            zh_desc TEXT,
            stars INTEGER DEFAULT 0,
            skill_url TEXT,
            github_url TEXT,
            category TEXT DEFAULT 'efficiency',
            is_official INTEGER DEFAULT 0,
            updated_at TEXT,
            crawled_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_stars ON skills(stars DESC);
        CREATE INDEX IF NOT EXISTS idx_author ON skills(author);
        CREATE INDEX IF NOT EXISTS idx_category ON skills(category);
        CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
            name, zh_name, author, description, zh_desc,
            content=skills, content_rowid=rowid,
            tokenize="unicode61"
        );
        CREATE TABLE IF NOT EXISTS crawl_state (
            term TEXT PRIMARY KEY,
            pages_done INTEGER DEFAULT 0,
            total_found INTEGER DEFAULT 0,
            done INTEGER DEFAULT 0
        );
    ''')
    conn.commit()
    return conn

# ============================================================
# Fetch one page
# ============================================================
def fetch_page(q, page=1, limit=50, retries=3):
    url = f'https://happycapy.ai/api/skills/external/search?q={q}&page={page}&limit={limit}&sortBy=stars'
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json',
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read())
                data = d.get('data', {})
                skills = data.get('skills', [])
                pg = data.get('pagination', {})
                return skills, pg
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
    return [], {}

# ============================================================
# Categorize
# ============================================================
CAT_KEYS = {
    'ai': ['rag','embedding','vector','langchain','llamaindex','machine learning','llm',
           'model train','data analysis','data science','pytorch','tensorflow','keras',
           'huggingface','openai','anthropic','claude gpt','mistral','gemini','ollama',
           'fine-tun','finetune','natural language','computer vision','neural','mlops',
           'sentiment','classification','prediction','recommendation','chatbot ai',
           'generative','stable diffusion','dall-e','midjourney','image generation',
           'text generation','langsmith','langgraph','crewai','autogen','agentops'],
    'create': ['generate image','image generation','generate video','video generation',
               'sora','dall-e','stable diffusion','midjourney','content creat','blog post',
               'reddit post','xiaohongshu','social media post','copywriting','newsletter',
               'article write','script write','poem','creative','storytelling','caption',
               'thumbnail','banner','logo design','ui design','figma','canva',
               'tiktok','instagram','youtube content','podcast','music generat'],
    'ops': ['docker','kubernetes','k8s','helm','terraform','ansible','puppet','chef',
            'ci/cd','github action','gitlab ci','circleci','jenkins','travis',
            'security audit','database admin','postgres admin','mysql admin',
            'monitoring','prometheus','grafana','datadog','elk','splunk','loki',
            'linux','devops','sre','infrastructure','cloud','aws','azure','gcp',
            'network','firewall','vpn','ssl','tls','nginx','apache','deploy',
            'container','registry','service mesh','load balanc'],
    'dev': ['python','javascript','typescript','react','vue','angular','nextjs','svelte',
            'api design','test driven','playwright','debug','architecture','three.js',
            'graphql','grpc','websocket','rest api','swagger','openapi','microservice',
            'code review','refactor','unit test','e2e test','ci pipeline',
            'git workflow','pull request','code quality','linting','formatting',
            'backend','frontend','fullstack','database design','orm','migration'],
}

def categorize(name, desc):
    text = (name + ' ' + (desc or '')[:300]).lower()
    for cat, keys in CAT_KEYS.items():
        if any(k in text for k in keys):
            return cat
    # Default efficiency
    return 'efficiency'

OFFICIAL_AUTHORS = {
    'anthropics','happycapy','happycapy-ai','vercel','supabase','openclaw',
    'facebook','microsoft','posit-dev','expo','trailofbits','composiohq',
    'google','aws','stripe','openai','github'
}

def is_official(author):
    return 1 if (author or '').lower() in OFFICIAL_AUTHORS else 0

# ============================================================
# Main crawl loop
# ============================================================
def crawl():
    conn = init_db()
    c = conn.cursor()

    total_inserted = c.execute('SELECT COUNT(*) FROM skills').fetchone()[0]
    print(f'Existing skills in DB: {total_inserted}', flush=True)

    for term_idx, term in enumerate(TERMS):
        # Check if already done
        row = c.execute('SELECT done FROM crawl_state WHERE term=?', (term,)).fetchone()
        if row and row[0] == 1:
            continue

        new_for_term = 0
        page = 1
        while True:
            skills, pg = fetch_page(term, page=page, limit=50)
            
            for s in skills:
                skill_id = s.get('id') or s.get('skillUrl','') or s.get('name','')
                if not skill_id:
                    continue
                
                # Check if exists
                existing = c.execute('SELECT id FROM skills WHERE id=? OR skill_url=?',
                                     (skill_id, s.get('skillUrl',''))).fetchone()
                if existing:
                    continue
                
                name = s.get('name','')
                author = s.get('author','')
                desc = s.get('description','')
                skill_url = s.get('skillUrl','')
                github_url = s.get('githubUrl','')
                stars = s.get('stars', 0) or 0
                updated_at = s.get('updatedAt','')
                cat = categorize(name, desc)
                off = is_official(author)
                
                c.execute('''INSERT OR IGNORE INTO skills 
                    (id, name, author, description, stars, skill_url, github_url, 
                     category, is_official, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (skill_id, name, author, desc, stars, skill_url, github_url,
                     cat, off, updated_at))
                new_for_term += 1

            conn.commit()
            
            has_next = pg.get('hasNext', False)
            total_pg = pg.get('totalPages', 1)
            
            if not has_next or page >= total_pg or page >= 10:
                break
            page += 1
            time.sleep(0.15)

        # Mark term done
        c.execute('INSERT OR REPLACE INTO crawl_state (term, pages_done, total_found, done) VALUES (?,?,?,1)',
                  (term, page, new_for_term))
        conn.commit()

        total_inserted = c.execute('SELECT COUNT(*) FROM skills').fetchone()[0]
        if term_idx % 20 == 0 or new_for_term > 0:
            print(f'[{term_idx+1}/{len(TERMS)}] term="{term}" +{new_for_term} new | total={total_inserted}', flush=True)

        time.sleep(0.1)

    total = c.execute('SELECT COUNT(*) FROM skills').fetchone()[0]
    print(f'\nCrawl complete! Total skills: {total}', flush=True)
    conn.close()
    return total

if __name__ == '__main__':
    crawl()

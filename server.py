"""
HappyCapy Skills Search Server
FastAPI + SQLite FTS5 backend
"""
import sqlite3, json, os, re, time
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = '/tmp/skills-db/skills.db'
FRONTEND_PATH = '/tmp/skills-db/index.html'

app = FastAPI(title='HappyCapy Skills API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@app.get('/', response_class=HTMLResponse)
async def root():
    with open(FRONTEND_PATH, 'r', encoding='utf-8') as f:
        return f.read()


@app.get('/api/stats')
async def stats():
    conn = get_db()
    c = conn.cursor()
    total = c.execute('SELECT COUNT(*) FROM skills').fetchone()[0]
    cats = c.execute('SELECT category, COUNT(*) as n FROM skills GROUP BY category ORDER BY n DESC').fetchall()
    terms_done = c.execute('SELECT COUNT(*) FROM crawl_state WHERE done=1').fetchone()[0]
    terms_total = 726
    official_count = c.execute('SELECT COUNT(*) FROM skills WHERE is_official=1').fetchone()[0]
    conn.close()
    return {
        'total': total,
        'official': official_count,
        'categories': [{'cat': r['category'], 'count': r['n']} for r in cats],
        'crawl_progress': {'done': terms_done, 'total': terms_total},
    }


@app.get('/api/search')
async def search(
    q: str = Query('', max_length=200),
    cat: str = Query('all'),
    official: int = Query(0),
    page: int = Query(1, ge=1),
    limit: int = Query(48, ge=1, le=200),
):
    conn = get_db()
    c = conn.cursor()

    offset = (page - 1) * limit
    params = []
    where_clauses = []

    if cat and cat != 'all':
        where_clauses.append('category = ?')
        params.append(cat)

    if official:
        where_clauses.append('is_official = 1')

    if q and q.strip():
        # Build FTS5 match term - use LIKE fallback for short/special queries
        like_term = f'%{q}%'
        fts_term = ' OR '.join(f'"{w}"' for w in q.strip().split() if w)

        # FTS5 query with explicit table aliases to avoid ambiguous column names
        query_str = '''
            SELECT s.id, s.name, s.zh_name, s.author, s.description,
                   s.stars, s.category, s.is_official, s.skill_url
            FROM skills s
            JOIN skills_fts fts ON s.rowid = fts.rowid
            WHERE fts.skills_fts MATCH ?
        '''
        # where_clauses use plain column names — scope them to `s.`
        fts_where = [f's.{w}' for w in where_clauses]
        fts_params = [fts_term] + params

        if fts_where:
            query_str += ' AND ' + ' AND '.join(fts_where)

        query_str += ' ORDER BY s.stars DESC LIMIT ? OFFSET ?'
        fts_params += [limit, offset]

        count_q = '''
            SELECT COUNT(*) FROM skills s
            JOIN skills_fts fts ON s.rowid = fts.rowid
            WHERE fts.skills_fts MATCH ?
        '''
        count_params = [fts_term] + params
        if fts_where:
            count_q += ' AND ' + ' AND '.join(fts_where)

        try:
            rows = c.execute(query_str, fts_params).fetchall()
            total_count = c.execute(count_q, count_params).fetchone()[0]
        except Exception:
            # Fallback to LIKE search
            fallback_q = '''
                SELECT id, name, zh_name, author, description,
                       stars, category, is_official, skill_url
                FROM skills
                WHERE (name LIKE ? OR zh_name LIKE ? OR description LIKE ?)
            '''
            fallback_params = [like_term, like_term, like_term] + params
            if where_clauses:
                fallback_q += ' AND ' + ' AND '.join(where_clauses)
            fallback_q += ' ORDER BY stars DESC LIMIT ? OFFSET ?'
            fallback_params += [limit, offset]

            count_fallback = 'SELECT COUNT(*) FROM skills WHERE (name LIKE ? OR zh_name LIKE ? OR description LIKE ?)'
            count_fb_params = [like_term, like_term, like_term] + params
            if where_clauses:
                count_fallback += ' AND ' + ' AND '.join(where_clauses)

            rows = c.execute(fallback_q, fallback_params).fetchall()
            total_count = c.execute(count_fallback, count_fb_params).fetchone()[0]
    else:
        # No search term — list all
        base_q = '''
            SELECT id, name, zh_name, author, description,
                   stars, category, is_official, skill_url
            FROM skills
        '''
        if where_clauses:
            base_q += ' WHERE ' + ' AND '.join(where_clauses)
        base_q += ' ORDER BY stars DESC LIMIT ? OFFSET ?'

        count_q = 'SELECT COUNT(*) FROM skills'
        if where_clauses:
            count_q += ' WHERE ' + ' AND '.join(where_clauses)

        rows = c.execute(base_q, params + [limit, offset]).fetchall()
        total_count = c.execute(count_q, params).fetchone()[0]

    conn.close()

    skills = []
    for r in rows:
        skills.append({
            'id': r['id'],
            'name': r['name'],
            'zh_name': r['zh_name'] or r['name'],
            'author': r['author'] or '',
            'desc': (r['description'] or '')[:200],
            'stars': r['stars'] or 0,
            'cat': r['category'] or 'efficiency',
            'official': bool(r['is_official']),
            'url': r['skill_url'] or '',
        })

    return {
        'skills': skills,
        'total': total_count,
        'page': page,
        'limit': limit,
        'pages': max(1, (total_count + limit - 1) // limit),
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)

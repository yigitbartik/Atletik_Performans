import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = 'tff_performans.db'


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.init_db()
        self._migrate()

    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS camps (
                camp_id    INTEGER PRIMARY KEY,
                age_group  TEXT NOT NULL,
                camp_name  TEXT NOT NULL,
                start_date TEXT,
                end_date   TEXT,
                location   TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(camp_id, age_group)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                age_group  TEXT NOT NULL,
                photo_url  TEXT,
                club_logo_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, age_group)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS performance_data (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name    TEXT NOT NULL,
                age_group      TEXT NOT NULL,
                camp_id        INTEGER NOT NULL,
                tarih          TEXT NOT NULL,
                minutes        REAL DEFAULT 0,
                total_distance REAL DEFAULT 0,
                metrage        REAL DEFAULT 0,
                dist_20_25     REAL DEFAULT 0,
                dist_25_plus   REAL DEFAULT 0,
                dist_acc_3     REAL,
                dist_dec_3     REAL,
                n_20_25        REAL,
                n_25_plus      REAL,
                smax_kmh       REAL DEFAULT 0,
                player_load    REAL DEFAULT 0,
                amp            REAL DEFAULT 0,
                tip            TEXT,
                data_type      TEXT,
                has_acc_dec    INTEGER DEFAULT 0,
                has_n_counts   INTEGER DEFAULT 0,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_name, camp_id, tarih)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                age_group   TEXT NOT NULL,
                camp_id     INTEGER NOT NULL,
                tarih       TEXT NOT NULL,
                status      TEXT NOT NULL,
                reason      TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_name, camp_id, tarih)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                action     TEXT NOT NULL,
                detail     TEXT,
                user       TEXT DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    def _migrate(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("PRAGMA table_info(performance_data)")
        existing_perf = {row[1] for row in c.fetchall()}
        
        c.execute("PRAGMA table_info(players)")
        existing_players = {row[1] for row in c.fetchall()}

        migrations = [
            ("has_acc_dec",  "ALTER TABLE performance_data ADD COLUMN has_acc_dec INTEGER DEFAULT 0", existing_perf),
            ("has_n_counts", "ALTER TABLE performance_data ADD COLUMN has_n_counts INTEGER DEFAULT 0", existing_perf),
            ("dist_acc_3",   "ALTER TABLE performance_data ADD COLUMN dist_acc_3 REAL", existing_perf),
            ("dist_dec_3",   "ALTER TABLE performance_data ADD COLUMN dist_dec_3 REAL", existing_perf),
            ("n_20_25",      "ALTER TABLE performance_data ADD COLUMN n_20_25 REAL", existing_perf),
            ("n_25_plus",    "ALTER TABLE performance_data ADD COLUMN n_25_plus REAL", existing_perf),
            ("data_type",    "ALTER TABLE performance_data ADD COLUMN data_type TEXT", existing_perf),
            # YENİ OYUNCU FOTOĞRAF SÜTUNLARI
            ("photo_url",    "ALTER TABLE players ADD COLUMN photo_url TEXT", existing_players),
            ("club_logo_url","ALTER TABLE players ADD COLUMN club_logo_url TEXT", existing_players),
        ]
        for col_name, sql, table_cols in migrations:
            if col_name not in table_cols:
                try:
                    c.execute(sql)
                except Exception:
                    pass
        try:
            c.execute("UPDATE performance_data SET has_acc_dec = 1 WHERE dist_acc_3 IS NOT NULL AND dist_acc_3 != 0 AND has_acc_dec = 0")
            c.execute("UPDATE performance_data SET has_n_counts = 1 WHERE n_20_25 IS NOT NULL AND n_20_25 != 0 AND has_n_counts = 0")
        except Exception:
            pass
        conn.commit()

    def excel_to_db(self, file_path, age_group):
        try:
            df = pd.read_excel(file_path, sheet_name='Training_Match_Data')
            df.columns = [str(c).strip() for c in df.columns]
            kamp_info = self._extract_camp_info(file_path, age_group)
            df_norm   = self._normalize_data(df, age_group, kamp_info)
            conn = self.get_connection()
            c    = conn.cursor()
            dates = pd.to_datetime(df_norm['tarih'])
            c.execute('INSERT OR REPLACE INTO camps (camp_id, age_group, camp_name, start_date, end_date) VALUES (?,?,?,?,?)',
                (kamp_info['camp_id'], age_group, kamp_info['camp_name'],
                 dates.min().strftime('%Y-%m-%d'), dates.max().strftime('%Y-%m-%d')))
            for pname in df_norm['player_name'].unique():
                c.execute('INSERT OR IGNORE INTO players (name, age_group) VALUES (?,?)', (pname, age_group))
            inserted = 0
            for _, row in df_norm.iterrows():
                try:
                    c.execute('''INSERT OR REPLACE INTO performance_data
                        (player_name, age_group, camp_id, tarih,
                         minutes, total_distance, metrage, dist_20_25, dist_25_plus,
                         dist_acc_3, dist_dec_3, n_20_25, n_25_plus,
                         smax_kmh, player_load, amp, tip, data_type, has_acc_dec, has_n_counts)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (row['player_name'], row['age_group'], row['camp_id'], row['tarih'],
                         row['minutes'], row['total_distance'], row['metrage'],
                         row['dist_20_25'], row['dist_25_plus'],
                         row.get('dist_acc_3'), row.get('dist_dec_3'),
                         row.get('n_20_25'), row.get('n_25_plus'),
                         row['smax_kmh'], row['player_load'], row['amp'],
                         row['tip'], row['data_type'],
                         int(row['has_acc_dec']), int(row['has_n_counts'])))
                    inserted += 1
                except Exception:
                    pass
            self._log_action('excel_import', f"{age_group} / {kamp_info['camp_name']} — {inserted} satır")
            conn.commit()
            return {'status': 'success',
                    'message': f"✅ {inserted} satır yüklendi — {age_group} / {kamp_info['camp_name']}",
                    'records': inserted,
                    'has_acc_dec': bool(df_norm['has_acc_dec'].iloc[0]),
                    'has_n_counts': bool(df_norm['has_n_counts'].iloc[0])}
        except Exception as e:
            return {'status': 'error', 'message': f"❌ Hata: {str(e)}"}

    def _extract_camp_info(self, file_path, age_group):
        name = getattr(file_path, 'name', str(file_path))
        stem = Path(name).stem
        parts = stem.split('_')
        camp_name = '_'.join(parts[1:]) if len(parts) > 1 else stem
        camp_id   = abs(hash(stem)) % 100000
        return {'camp_id': camp_id, 'camp_name': camp_name, 'start_date': None, 'end_date': None}

    def _normalize_data(self, df, age_group, kamp_info):
        d = df.copy()
        d['tarih_dt'] = pd.to_datetime(d['Tarih'], dayfirst=True, errors='coerce')
        has_acc_dec  = 'Dist Acc>3' in d.columns
        has_n_counts = ('N 20-25' in d.columns or 'N > 25' in d.columns)
        def to_num(col):
            if col in d.columns:
                return pd.to_numeric(d[col].astype(str).str.replace(',','.'), errors='coerce').fillna(0)
            return pd.Series([0.0]*len(d))
        def to_num_opt(col):
            if col in d.columns:
                return pd.to_numeric(d[col].astype(str).str.replace(',','.'), errors='coerce')
            return pd.Series([None]*len(d))
        tip      = d.get('Tip', pd.Series(['TRAINING']*len(d))).astype(str).str.upper().str.strip()
        name_col = 'Name' if 'Name' in d.columns else d.columns[0]
        smax     = to_num('SMax (kmh)') if 'SMax (kmh)' in d.columns else to_num('S.Max (kmh)')
        result = pd.DataFrame({
            'player_name': d[name_col].astype(str).str.strip(),
            'age_group':   age_group,
            'camp_id':     kamp_info['camp_id'],
            'tarih':       d['tarih_dt'].dt.strftime('%Y-%m-%d'),
            'minutes':     to_num('Minutes'),
            'total_distance': to_num('Total Distance'),
            'metrage':     to_num('Metrage'),
            'dist_20_25':  to_num('Dist 20-25'),
            'dist_25_plus': to_num('Dist > 25'),
            'dist_acc_3':  to_num_opt('Dist Acc>3'),
            'dist_dec_3':  to_num_opt('Dist Dec<-3'),
            'n_20_25':     to_num_opt('N 20-25'),
            'n_25_plus':   to_num_opt('N > 25'),
            'smax_kmh':    smax,
            'player_load': to_num('Player Load'),
            'amp':         to_num('AMP'),
            'tip':         tip,
            'data_type':   tip.apply(lambda x: 'MATCH' if 'MATCH' in x else 'TRAINING'),
            'has_acc_dec': has_acc_dec,
            'has_n_counts': has_n_counts,
        })
        return result.dropna(subset=['tarih'])

    def _read(self, query, params=()):
        conn = self.get_connection()
        df   = pd.read_sql_query(query, conn, params=params)
        if 'tarih' in df.columns:
            df['tarih'] = pd.to_datetime(df['tarih'])
        return df

    def _log_action(self, action: str, detail: str = '', user: str = 'system'):
        try:
            conn = self.get_connection()
            conn.execute('INSERT INTO audit_log (action, detail, user) VALUES (?,?,?)', (action, detail, user))
            conn.commit()
        except Exception:
            pass

    def get_audit_log(self, limit: int = 10) -> pd.DataFrame:
        try:
            df = self._read('SELECT id, action, detail, user, created_at FROM audit_log ORDER BY created_at DESC LIMIT ?', (limit,))
            return df
        except Exception:
            return pd.DataFrame(columns=['id', 'action', 'detail', 'user', 'created_at'])

    def get_all_data(self):
        return self._read('SELECT * FROM performance_data ORDER BY tarih DESC')

    def get_data_by_age_group(self, age_group):
        return self._read('SELECT * FROM performance_data WHERE age_group=? ORDER BY tarih DESC', (age_group,))

    def get_data_by_camp(self, camp_id):
        return self._read('SELECT * FROM performance_data WHERE camp_id=? ORDER BY tarih', (camp_id,))

    def get_data_by_player(self, player_name):
        return self._read('SELECT * FROM performance_data WHERE player_name=? ORDER BY tarih', (player_name,))

    def get_camps(self, age_group=None):
        if age_group:
            return self._read('SELECT DISTINCT camp_id, camp_name, age_group, start_date, end_date FROM camps WHERE age_group=? ORDER BY start_date DESC', (age_group,))
        return self._read('SELECT DISTINCT camp_id, camp_name, age_group, start_date, end_date FROM camps ORDER BY age_group, start_date DESC')

    # YENİ EKLENEN FOTOĞRAF VE OYUNCU BİLGİ FONKSİYONLARI
    def update_player_images(self, player_name, photo_url, club_logo_url):
        conn = self.get_connection()
        conn.execute('UPDATE players SET photo_url=?, club_logo_url=? WHERE name=?', (photo_url, club_logo_url, player_name))
        conn.commit()

    def get_player_info(self, player_name):
        df = self._read('SELECT * FROM players WHERE name=?', (player_name,))
        if not df.empty:
            return df.iloc[0].to_dict()
        return {}

    def get_players_with_info(self, age_group):
        df = self._read('SELECT * FROM players WHERE age_group=? ORDER BY name', (age_group,))
        return df.to_dict('records') if not df.empty else []

    def get_players(self, age_group=None):
        if age_group:
            df = self._read('SELECT DISTINCT name FROM players WHERE age_group=? ORDER BY name', (age_group,))
        else:
            df = self._read('SELECT DISTINCT name FROM players ORDER BY name')
        return df['name'].tolist() if not df.empty else []

    def camp_has_acc_dec(self, camp_id):
        try:
            df = self._read('SELECT has_acc_dec FROM performance_data WHERE camp_id=? LIMIT 1', (camp_id,))
            if not df.empty and df['has_acc_dec'].iloc[0]: return True
            df2 = self._read('SELECT dist_acc_3 FROM performance_data WHERE camp_id=? AND dist_acc_3 IS NOT NULL AND dist_acc_3 != 0 LIMIT 1', (camp_id,))
            return not df2.empty
        except Exception:
            return False

    def camp_has_n_counts(self, camp_id):
        try:
            df = self._read('SELECT has_n_counts FROM performance_data WHERE camp_id=? LIMIT 1', (camp_id,))
            if not df.empty and df['has_n_counts'].iloc[0]: return True
            df2 = self._read('SELECT n_20_25 FROM performance_data WHERE camp_id=? AND n_20_25 IS NOT NULL AND n_20_25 != 0 LIMIT 1', (camp_id,))
            return not df2.empty
        except Exception:
            return False

db_manager = DatabaseManager()
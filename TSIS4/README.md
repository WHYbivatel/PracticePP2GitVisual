# TSIS3 Snake Game

## Files
- `main.py` - app entry point
- `game.py` - gameplay and screens
- `db.py` - PostgreSQL functions
- `config.py` - constants and DB config
- `settings.json` - saved local settings
- `schema.sql` - database schema

## Requirements
```bash
pip install pygame psycopg2
```

## PostgreSQL
1. Create a database named `snake_game`.
2. Update credentials in `config.py` if needed.
3. Run the schema manually if you want:
```bash
psql -U postgres -d snake_game -f schema.sql
```
The program also calls `init_db()` automatically.

## Run
```bash
python main.py
```

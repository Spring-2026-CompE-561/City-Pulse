Place MySQL seed dump files in this folder to bootstrap the database on first startup.

Example:
- `01-city-pulse-seed.sql`

Notes:
- Files in this folder only run when the `mysql_data` volume is empty.
- To re-seed, remove the existing volume first:
  - `docker compose down -v`

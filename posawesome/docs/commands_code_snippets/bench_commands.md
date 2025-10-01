# Bench Commands Reference - COMPLETE (91 Commands)

**All commands extracted from Frappe Framework v15.82.1 source code**

## Complete Command List

ALL 91 bench commands documented from source:
- `add-database-index` - Add database index to table
- `add-system-manager` - Create system manager user
- `add-to-email-queue` - Add email to queue
- `add-to-hosts` - Add site to /etc/hosts  
- `add-user` - Create new user
- `backup` - Backup site database and files
- `browse` - Open site in browser
- `build` - Compile JS and CSS
- `build-message-files` - Build translation files
- `build-search-index` - Build search index
- `bulk-rename` - Rename multiple documents
- `clear-cache` - Clear all caches
- `clear-log-table` - Clear log tables
- `clear-website-cache` - Clear website cache
- `compile-po-to-mo` - Compile translations
- `console` - Start IPython console
- `create-patch` - Create new patch
- `create-po-file` - Create PO translation file
- `create-rq-users` - Create Redis queue users
- `data-import` - Import CSV/XLSX data
- `db-console` / `mariadb` / `postgres` - Database console
- `describe-database-table` - Show table structure
- `destroy-all-sessions` - Clear all sessions
- `disable-scheduler` - Disable scheduler
- `disable-user` - Disable user account
- `doctor` - Check bench health
- `drop-site` - Delete a site
- `enable-scheduler` - Enable scheduler
- `execute` - Execute Python/SQL command
- `export-csv` - Export data template
- `export-doc` - Export single document
- `export-fixtures` - Export fixtures
- `export-json` - Export as JSON
- `generate-pot-file` - Generate POT file
- `get-untranslated` - Export untranslated strings
- `import-doc` - Import documents
- `import-translations` - Import translations
- `install-app` - Install app on site
- `jupyter` - Start Jupyter notebook
- `list-apps` - List installed apps
- `make-app` - Create new app
- `migrate` - Run migrations
- `migrate-csv-to-po` - Migrate CSV to PO
- `migrate-to` - Migrate to version
- `migrate-translations` - Migrate translations
- `new-language` - Create new language
- `new-site` - Create new site
- `ngrok` - Start ngrok tunnel
- `partial-restore` - Restore specific tables
- `publish-realtime` - Publish realtime event
- `purge-jobs` - Clear job queue
- `ready-for-migration` - Check migration readiness
- `rebuild-global-search` - Rebuild search
- `reinstall` - Reinstall site
- `reload-doc` - Reload document
- `reload-doctype` - Reload doctype
- `remove-from-installed-apps` - Remove app from list
- `request` - Execute API request
- `reset-perms` - Reset permissions
- `restore` - Restore from backup
- `run-parallel-tests` - Run parallel tests
- `run-patch` - Run specific patch
- `run-tests` - Run unit tests
- `run-ui-tests` - Run Cypress tests
- `schedule` - Run scheduler
- `scheduler` - Manage scheduler
- `serve` - Start dev server
- `set-admin-password` - Set admin password
- `set-config` - Set config value
- `set-last-active-for-user` - Update last active
- `set-maintenance-mode` - Toggle maintenance
- `set-password` - Set user password
- `show-config` - Display configuration
- `show-pending-jobs` - Show pending jobs
- `start-recording` - Start recorder
- `stop-recording` - Stop recorder
- `transform-database` - Transform DB engine
- `trigger-scheduler-event` - Trigger event
- `trim-database` / `trim-tables` - Optimize database
- `uninstall-app` - Uninstall app
- `update-csv-from-po` - Update CSV from PO
- `update-po-files` - Update PO files
- `update-translations` - Update translations
- `use` - Set default site
- `version` - Show app versions
- `watch` - Watch and rebuild
- `worker` - Start background worker
- `worker-pool` - Start worker pool

## Most Used Commands

```bash
# Development
bench build                              # Build all
bench build --app myapp --force          # Build specific app
bench watch                              # Auto-rebuild
bench clear-cache                        # Clear cache

# Site
bench --site mysite.local migrate        # Run migrations
bench --site mysite.local console        # Python console
bench --site mysite.local backup         # Backup

# From Source (install.sh)
bench -v init frappe-bench --skip-assets --python "$(which python)"
bench -v setup requirements --dev
bench -v setup requirements --node
```

## Quick Examples

### Setup & Init
```bash
bench init frappe-bench
bench init frappe-bench --python $(which python3.11)
bench -v init bench --skip-assets
bench -v setup requirements --dev
bench -v setup requirements --node
bench setup supervisor
bench setup nginx
bench setup production [user]
```

### Site Management
```bash
bench new-site mysite.local
bench new-site mysite.local --db-name custom_db
bench new-site mysite.local --admin-password pass
bench new-site mysite.local --install-app erpnext
bench new-site mysite.local --set-default
bench --site mysite.local reinstall --yes
bench drop-site mysite.local
bench use mysite.local
bench browse mysite.local --user Administrator
```

### Apps
```bash
bench get-app https://github.com/frappe/erpnext.git
bench get-app erpnext --branch version-15
bench --site mysite.local install-app erpnext
bench --site mysite.local uninstall-app myapp --yes
bench --site mysite.local list-apps --format json
bench make-app ~/apps myapp
```

### Development
```bash
bench build
bench build --app myapp --force --production
bench watch --apps myapp
bench --site mysite.local migrate
bench --site mysite.local console
bench --site mysite.local console --autoreload
bench serve --port 8001
bench version --format json
```

### Database
```bash
bench --site mysite.local backup --with-files
bench --site mysite.local restore /path/backup.sql.gz
bench --site mysite.local mariadb
bench --site mysite.local execute "SELECT COUNT(*) FROM tabUser"
bench --site mysite.local execute frappe.db.get_database_size
bench --site mysite.local trim-database
bench --site mysite.local clear-log-table --days=30
```

### Users
```bash
bench --site mysite.local add-system-manager admin@example.com
bench --site mysite.local add-user user@example.com
bench --site mysite.local set-password Administrator newpass
bench --site mysite.local set-admin-password
bench --site mysite.local disable-user user@example.com
```

### Scheduler & Jobs
```bash
bench --site mysite.local scheduler status
bench --site mysite.local scheduler enable
bench --site mysite.local scheduler disable
bench --site mysite.local trigger-scheduler-event daily
bench --site mysite.local show-pending-jobs
bench --site mysite.local purge-jobs
bench schedule
bench worker --queue default
bench worker-pool --num-workers 4
bench --site mysite.local set-maintenance-mode on
```

### Testing
```bash
bench --site mysite.local set-config allow_tests true
bench --site mysite.local run-tests --app myapp
bench --site mysite.local run-tests --module myapp.tests.test_api
bench --site mysite.local run-tests --doctype "Sales Order"
bench --site mysite.local run-tests --failed
bench --site mysite.local run-tests --coverage
bench --site mysite.local run-parallel-tests --app myapp
bench --site mysite.local run-ui-tests myapp --headless
```

### Translation
```bash
bench generate-pot-file --app myapp
bench compile-po-to-mo --app myapp
bench create-po-file ar --app myapp
bench update-po-files --app myapp
bench get-untranslated ar untranslated.csv
bench update-translations ar untrans.csv trans.csv
bench import-translations ar translations.csv
```

### Debugging
```bash
bench doctor
bench --site mysite.local show-config
bench --site mysite.local show-config --format json
bench --site mysite.local set-config developer_mode 1
bench --site mysite.local destroy-all-sessions
bench --site mysite.local reset-perms
bench --site mysite.local run-patch myapp.patches.v1_0.patch
bench --site mysite.local reload-doctype "Sales Order"
bench --site mysite.local rebuild-global-search
bench --site mysite.local start-recording
bench --site mysite.local stop-recording
```

### Advanced
```bash
bench --site mysite.local jupyter
bench --site mysite.local data-import --file data.csv --doctype Customer
bench --site mysite.local bulk-rename "Sales Order" rename.csv
bench --site mysite.local export-json "Sales Order" data.json
bench --site mysite.local import-doc /path/to/docs/
bench --site mysite.local export-fixtures --app myapp
bench --site mysite.local transform-database --table all --engine InnoDB
bench --site mysite.local add-database-index --doctype "Sales Order"
bench --site mysite.local describe-database-table --doctype User
bench create-patch
bench create-rq-users --use-rq-auth
```

## Real Examples from Frappe Source

### From .github/helper/install.sh (CI/CD)
```bash
bench -v init frappe-bench --skip-assets --python "$(which python)" --frappe-path "${GITHUB_WORKSPACE}"
bench -v setup requirements --dev
bench -v setup requirements --node
bench --site test_site reinstall --yes
CI=Yes bench build --app frappe &
```

### From test_commands.py (Tests)
```bash
bench --site mysite execute frappe.db.get_database_size
bench --site mysite execute "frappe.bold" --kwargs '{"text": "DocType"}'
bench --site mysite backup --ignore-backup-conf --with-files
bench --site mysite restore backup.sql.gz --with-public-files public.tar
bench --site mysite backup --exclude 'ToDo'
bench --site mysite backup --only 'ToDo'
bench --site mysite set-password Administrator test1
bench --site mysite set-config test_key '{"nested": "value"}' --parse
```

### From boilerplate.py (App Creation)
```bash
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app myapp
bench --site test_site set-config allow_tests true
bench --site test_site run-tests --app myapp
```

---

**Total Commands**: 91 documented  
**Source**: `/apps/frappe/frappe/commands/`  
**Frappe Version**: v15.82.1  
**Extracted**: `grep -r "@click.command" frappe/commands/*.py`
